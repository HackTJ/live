from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_http_methods
from django.conf import settings
from judge.controllers import perform_vote, choose_next, init_annotator
from judge.models import Decision

# redirect non-judge users to scoreboard
def judge_required(function=None, login_url='/judge/scoreboard', redirect_field_name=None):
    dec = user_passes_test(
        lambda user: user.groups.filter(name="judge").exists(),
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return dec(function)
    return dec


@login_required
@judge_required
def home(request):
    if not request.user.annotator.read_welcome:
        return redirect('/judge/welcome')
        
    return render(request, 'judge/judge_home.html', {
        'welcome_message': settings.JUDGE_WELCOME_MESSAGE
    })


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
    if annotator.next.id == int(request.form['project_id']):
        annotator.ignore.add(annotator.next)
        if request.form['action'] == 'Done':
            annotator.next.viewed.add(annotator)
            annotator.next.save()
            annotator.prev = annotator.next
            annotator.prev.save()
            annotator.update_next(choose_next(annotator))
        elif request.form['action'] == 'Skip':
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
                return render('/judge/begin', {"project": annotator.next})
            else:
                return render('/judge/vote', {
                    "prev": annotator.prev,
                    "next": annotator.next
                })
        return render(request, 'judge/vote.html', {
            "next": annotator.next,
            "prev": annotator.prev
        })
    else:
        annotator = request.user.annotator
        if annotator.prev.id == int(request.form['prev_id']) and annotator.next.id == int(request.form['next_id']):
            if request.form['action'] == 'Skip':
                annotator.ignore.add(annotator.next)
            else:
                if annotator.prev.active and annotator.next.active:
                    if request.form['action'] == 'previous':
                        perform_vote(annotator, next_won=False)
                        decision = Decision(annotator, winner=annotator.prev, loser=annotator.next)
                    elif request.form['action'] == 'current':
                        perform_vote(annotator, next_won=True)
                        decision = Decision(annotator, winner=annotator.next, loser=annotator.prev)
                    decision.save()
            annotator.next.viewed.append(annotator)
            annotator.next.save()
            annotator.prev = annotator.next
            annotator.prev.save()
        annotator.update_next(choose_next(annotator)) 
        annotator.save()
        return render(request, 'judge/vote.html', {
            "next": request.user.annotator.next,
            "prev": request.user.annotator.prev
        })


def scoreboard(request):
    return render(request, 'judge/scoreboard.html')
