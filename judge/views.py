from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
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
from django.conf import settings
from django.utils import timezone
from datetime import datetime

# TODO: superuser gets infinite redirects when visiting /judge because
# superuser doesn't have the judge group, so there's a redirect from /judge to
# /accounts/login...but superuser is already logged in so it redirects back to
# the next GET arg, which is set to /judge


def judge_required(function=None, redirect_field_name="next", login_url=None):
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
def index(request):
    if not request.user.annotator.read_welcome:
        return redirect("judge:welcome")
    return render(request, "judge/judge_home.html")


@login_required
@judge_required
def welcome(request):
    if request.method == "POST":
        request.user.annotator.read_welcome = True
        request.user.annotator.save()
        return redirect("judge:begin")
    return render(request, "judge/welcome.html")


@login_required
@judge_required
@require_http_methods(["GET", "POST"])
def begin(request):
    annotator = request.user.annotator
    if request.method == "GET":
        if not annotator.current:
            init_annotator(annotator)
            return render(request, "judge/begin.html", {"current": annotator.current})
    elif request.method == "POST":
        if annotator.current_id == int(request.POST["project_id"]):
            if request.POST["action"] == "Done":
                annotator.viewed.add(annotator.current)
                annotator.current.timesSeen = F("timesSeen") + 1
                annotator.current.save()
                annotator.prev = annotator.current
                annotator.prev.save()
                annotator.update_current(choose_next(annotator))
                annotator.current.save()
                annotator.save()
                # request.user.save()
            elif request.POST["action"] == "Skip":
                annotator.current.timesSkipped = F("timesSkipped") + 1
                annotator.current.save()
                annotator.current = None
                annotator.save()
                return redirect("judge:begin")
    return redirect("judge:vote")


@login_required
@judge_required
@never_cache
@require_http_methods(["GET", "POST"])
def vote(request):
    annotator = request.user.annotator
    if request.method == "GET":
        if not annotator.read_welcome:
            return redirect("judge:welcome")
        if annotator.current:
            if annotator.current == annotator.prev:
                return render(request, "judge/done.html")
            return render(
                request,
                "judge/vote.html",
                {
                    "prev": annotator.prev,
                    "current": annotator.current,
                    "criteria": settings.LIVE_JUDGE_CRITERIA,
                },
            )
        return redirect("judge:begin")  # current is not set yet
    elif request.method == "POST":
        if annotator.prev_id == int(
            request.POST["prev_id"]
        ) and annotator.current_id == int(request.POST["current_id"]):
            annotator.viewed.add(annotator.current)
            annotator.current.timesSeen = F("timesSeen") + 1
            annotator.current.save()
            for criterion_index, criterion_id in enumerate(
                settings.LIVE_JUDGE_CRITERIA
            ):
                criterion_winner = request.POST[f"criterion_{criterion_id}"]
                assert isinstance(criterion_winner, str)
                if criterion_winner == "previous":
                    perform_vote(
                        annotator,
                        current_won=False,
                        criterion_index=criterion_index,
                    )
                    decision = Decision(
                        annotator=annotator,
                        criterion=criterion_index,
                        winner=annotator.prev,
                        loser=annotator.current,
                    )
                    decision.save()
                elif criterion_winner == "current":
                    perform_vote(
                        annotator,
                        current_won=True,
                        criterion_index=criterion_index,
                    )
                    decision = Decision(
                        annotator=annotator,
                        criterion=criterion_index,
                        winner=annotator.current,
                        loser=annotator.prev,
                    )
                    decision.save()

            annotator.prev.numberOfVotes = F("numberOfVotes") + 1
            annotator.prev.save()

        if request.POST["criterion_overall"] == "current":
            # if the current project won overall, shift it to prev
            annotator.prev = annotator.current
            annotator.prev.save()
        annotator.update_current(choose_next(annotator))
        annotator.current.save()
        annotator.save()

        if annotator.current == annotator.prev:
            return render(request, "judge/done.html")

        return redirect("judge:vote")


@require_GET
# @login_required
def scoreboard(request):
    def render_stats():
        projects = serialize("json", Project.objects.order_by("-mean"))
        return render(
            request,
            "judge/scoreboard/stats.html",
            {
                "projects": projects,
            },
        )

    def render_rankings():
        projects = serialize(
            "json",
            Project.objects.order_by("-mean"),
            fields=("name", "description"),
        )
        return render(
            request,
            "judge/scoreboard/rankings.html",
            {
                "projects": projects,
            },
        )

    # if both LIVE_JUDGE_START_TIME and LIVE_JUDGE_END_TIME are None, the
    # event times have no effect on scoreboard viewability.

    # if LIVE_JUDGE_START_TIME is None and LIVE_JUDGE_END_TIME is not, the
    # scoreboard can only be viewed after the event.

    # if LIVE_JUDGE_START_TIME is not None and LIVE_JUDGE_END_TIME is, the
    # event times have no effect on scoreboard viewability.

    # if both LIVE_JUDGE_START_TIME and LIVE_JUDGE_END_TIME are not None, the
    # scoreboard can only be viewed after the event.

    # note: LIVE_JUDGE_START_TIME is still useful, because when it's set,
    # it renders more useful templates. for example, setting it renders three
    # different templates:
    #     - not-started (before the event judging has started)
    #     - unavailable (during the event judging)
    #     - {stats,rankings} (after the event)

    # the goal of this is to ensure that judges cannot view results during the
    # event (to be sure that their judging is completely objective)

    if request.user.is_authenticated and request.user.is_staff:
        # event organizers can view statistics at any time
        return render_stats()

    now = timezone.make_aware(datetime.utcnow())
    if getattr(settings, "LIVE_JUDGE_END_TIME"):
        event_end_time = timezone.make_aware(settings.LIVE_JUDGE_END_TIME)

        if getattr(settings, "LIVE_JUDGE_START_TIME"):
            event_start_time = timezone.make_aware(settings.LIVE_JUDGE_START_TIME)
        else:
            event_start_time = None

        if now < event_end_time:
            # event has not ended
            if event_start_time and event_start_time < now:
                # event has started but not ended
                return render(request, "judge/scoreboard/unavailable.html")
            elif event_start_time and now < event_start_time:
                # event has not started or ended
                return render(request, "judge/scoreboard/not-started.html")
            else:  # event_start_time is None
                return render(request, "judge/scoreboard/unavailable.html")

    if request.user.is_authenticated and (
        request.user.is_staff or request.user.groups.filter(name="judge").exists()
    ):
        # only show statistics to those authorized:
        # the organizing team and the judges
        return render_stats()
    else:
        # participants are only allowed to see rankings,
        # not numerical statistics
        return render_rankings()


@require_GET
@login_required
def queue(request):
    return render(
        request,
        "judge/queue.html",
        {
            "queue": serialize(
                "json",
                [
                    *Annotator.objects.all(),
                    *get_user_model().objects.filter(groups__name="judge"),
                    *Project.objects.all(),
                ],
                fields=(
                    "judge",  # Annotator.judge
                    "current",  # Annotator.current
                    "username",  # User.username
                    "first_name",  # User.first_name
                    "last_name",  # User.last_name
                    "name",  # Project.name
                    "description",  # Project.description
                ),
            ),
        },
    )
