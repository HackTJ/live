from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import (
    require_http_methods,
    require_GET,
    require_POST,
)
from django.core.serializers import serialize
from django.contrib.auth import get_user_model
from django.db.models import F
from judge.controllers import perform_vote, choose_next, init_annotator
from judge.models import Decision, Project, Annotator

# TODO: superuser gets infinite redirects when visiting /judge because
# superuser doesn't have the judge group, so there's a redirect from /judge to
# /accounts/login...but superuser is already logged in so it redirects back to
# the next GET arg, which is set to /judge


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
        return render(request, 'judge/welcome.html')


@login_required
@judge_required
@require_POST
def begin(request):
    annotator = request.user.annotator
    if annotator.current.id == int(request.POST['project_id']):
        if request.POST['action'] == 'Done':
            annotator.viewed.add(annotator.current)
            annotator.current.timesSeen = F('timesSeen') + 1
            annotator.current.save()
            annotator.prev = annotator.current
            annotator.prev.save()
            annotator.update_current(choose_next(annotator))
        elif request.POST['action'] == 'Skip':
            annotator.current.timesSkipped = F('timesSkipped') + 1
            annotator.current.save()
            annotator.current = None
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
        if annotator.current:
            if not annotator.prev:
                return render(request, 'judge/begin.html', {"current": annotator.current})
            else:
                if annotator.current == annotator.prev:
                    return render(request, 'judge/done.html')
                else:
                    return render(request, 'judge/vote.html', {
                        "prev": annotator.prev,
                        "current": annotator.current,
                    })
        init_annotator(annotator)
        return render(request, 'judge/begin.html', {"current": annotator.current})
    else:
        annotator = request.user.annotator
        if annotator.prev_id == int(request.POST['prev_id']) and annotator.current_id == int(request.POST['current_id']):
            if request.POST['action'] == 'skip':
                annotator.current.timesSkipped = F('timesSkipped') + 1
                annotator.current.save()
            elif annotator.prev.active and annotator.current.active:
                annotator.viewed.add(annotator.current)
                annotator.current.timesSeen = F('timesSeen') + 1
                annotator.current.save()

                if request.POST['action'] == 'previous':
                    perform_vote(annotator, current_won=False)
                    decision = Decision(
                        annotator=annotator, winner=annotator.prev, loser=annotator.current)
                    decision.save()
                elif request.POST['action'] == 'current':
                    perform_vote(annotator, current_won=True)
                    decision = Decision(
                        annotator=annotator, winner=annotator.current, loser=annotator.prev)
                    decision.save()
                    annotator.prev = annotator.current

                annotator.prev.numberOfVotes = F('numberOfVotes') + 1
                annotator.prev.save()

        annotator.update_current(choose_next(annotator))
        annotator.save()

        if annotator.current == annotator.prev:
            return render(request, 'judge/done.html')

        return render(request, 'judge/vote.html', {
            "current": request.user.annotator.current,
            "prev": request.user.annotator.prev,
        })


@require_GET
# @login_required
def scoreboard(request):
    if request.user.is_authenticated and (request.user.is_staff or request.user.groups.filter(name="judge").exists()):
        # only show statistics to those authorized: the organizing team and the judges
        projects = serialize("json", Project.objects.order_by('-mean').all())
        return render(request, 'judge/scoreboard/stats.html', {
            'projects': projects,
        })
    else:
        # participants are only allowed to see rankings, not numerical statistics
        projects = serialize("json", Project.objects.order_by(
            '-mean').all(), fields=('name', 'description'))
        return render(request, 'judge/scoreboard/rankings.html', {
            'projects': projects,
        })


@require_GET
@login_required
def queue(request):
    return render(request, 'judge/queue.html', {
        'queue': serialize(
            "json",
            [
                *Annotator.objects.all(),
                *get_user_model().objects.filter(groups__name='judge'),
                *Project.objects.all(),
            ],
            fields=(
                'judge', 'current',  # Annotator
                'username', 'first_name', 'last_name',  # User
                'name', 'description',  # Project
            ),
        ),
    })
