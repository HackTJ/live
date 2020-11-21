from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_http_methods
from django.conf import settings
from judge.controllers import perform_vote, choose_next, init_annotator
from judge.models import Decision, Project
import pytz

# redirect non-judge users to scoreboard


def judge_required(function=None, redirect_field_name='next', login_url=None):
    actual_decorator = user_passes_test(
        lambda user: user.groups.filter(name="judge").exists(),
        login_url=login_url,
        redirect_field_name=redirect_field_name,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


@login_required
@judge_required
def home(request):
    if not request.user.annotator.read_welcome:
        return redirect('/judge/welcome')
    return render(request, 'judge/judge_home.html')


@login_required
@judge_required
def welcome(request):
    if request.method == "POST":
        request.user.annotator.read_welcome = True
        request.user.annotator.save()
        return redirect('/judge')
    else:
        return render(request, 'judge/welcome.html', {
            'welcome_message': settings.JUDGE_WELCOME_MESSAGE
        })


@login_required
@judge_required
@require_http_methods(["POST"])
def begin(request):
    annotator = request.user.annotator
    if annotator.next.id == int(request.POST['project_id']):
        if request.POST['action'] == 'Done':
            annotator.viewed.add(annotator.next)
            annotator.next.timesSeen += 1
            annotator.next.save()
            annotator.prev = annotator.next
            annotator.prev.save()
            annotator.update_next(choose_next(annotator))
        elif request.POST['action'] == 'Skip':
            annotator.next.timesSkipped += 1
            annotator.next.save()
            annotator.next = None
        annotator.save()
    return redirect('/judge/vote')


@login_required
@judge_required
@require_http_methods(["GET", "POST"])
def vote(request):
    if request.method == 'GET':
        annotator = request.user.annotator
        if not annotator.read_welcome:
            return redirect('/judge/welcome')
        if annotator.next is not None:
            if annotator.prev is None:
                return render(request, 'judge/begin.html', {"next": annotator.next})
            else:
                if annotator.next == None or annotator.next == annotator.prev:
                    return render(request, 'judge/done.html')
                else:
                    return render(request, 'judge/vote.html', {
                        "prev": annotator.prev,
                        "next": annotator.next
                    })
        init_annotator(annotator)
        return render(request, 'judge/begin.html', {"next": annotator.next})
    else:
        annotator = request.user.annotator
        if annotator.prev.id == int(request.POST['prev_id']) and annotator.next.id == int(request.POST['next_id']):
            if request.POST['action'] == 'skip':
                    annotator.next.timesSkipped += 1
                    annotator.next.save()
            elif annotator.prev.active and annotator.next.active:
                annotator.viewed.add(annotator.next)
                annotator.next.timesSeen += 1
                annotator.next.save()

                if request.POST['action'] == 'previous':
                    perform_vote(annotator, next_won=False)
                    decision = Decision(annotator=annotator, winner=annotator.prev, loser=annotator.next)
                    decision.save()
                elif request.POST['action'] == 'current':
                    perform_vote(annotator, next_won=True)
                    decision = Decision(annotator=annotator, winner=annotator.next, loser=annotator.prev)
                    decision.save()
                    annotator.prev = annotator.next

                annotator.prev.numberOfVotes += 1
                annotator.prev.save()

        annotator.update_next(choose_next(annotator))
        annotator.save()

        return render(request, 'judge/vote.html', {
            "next": request.user.annotator.next,
            "prev": request.user.annotator.prev
        })


# @login_required
# @judge_required
@require_http_methods(["GET"])
def scoreboard(request):
    from django.core import serializers
    projects = serializers.serialize("json", Project.objects.order_by('-mean').all())
    return render(request, 'judge/scoreboard.html', {
        'projects': projects
    })
