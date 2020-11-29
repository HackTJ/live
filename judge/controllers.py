from django.conf import settings
from django.utils import timezone
from judge.models import Project, Annotator
import judge.crowd_bt as crowd_bt
from numpy.random import shuffle, random, choice
from datetime import datetime, timedelta


def preferred_items(annotator):
    ignored_ids = annotator.ignore.values_list("id", flat=True)

    available_projects = Project.objects.filter(active=True)
    if ignored_ids:
        available_projects = available_projects.exclude(id__in=ignored_ids)

    prioritized_projects = available_projects.filter(prioritize=True)
    items = prioritized_projects if prioritized_projects else available_projects

    annotators = Annotator.objects.filter(current__isnull=False, judge__is_active=True)

    nonbusy = available_projects.filter(
        annotator_current__updated__gte=timezone.make_aware(datetime.utcnow())
        + timedelta(seconds=settings.LIVE_JUDGE_TIMEOUT * 60)
    )
    preferred = nonbusy if nonbusy else items

    less_seen = preferred.filter(timesSeen__lt=settings.LIVE_JUDGE_MIN_VIEWS)

    out = less_seen if less_seen else preferred
    return list(out.distinct())


def init_annotator(annotator):
    if not annotator.current:
        items = preferred_items(annotator)
        if items:
            annotator.update_current(choice(items))
            annotator.save()


def choose_next(annotator):
    items = preferred_items(annotator)

    shuffle(items)
    if items:
        if random() < crowd_bt.EPSILON:
            return items[0]
        else:
            return crowd_bt.argmax(
                lambda i: crowd_bt.expected_information_gain(
                    float(annotator.alpha),
                    float(annotator.beta),
                    float(annotator.prev.mean),
                    float(annotator.prev.variance),
                    float(i.mean),
                    float(i.variance),
                ),
                items,
            )


def perform_vote(annotator, current_won):
    if current_won:
        winner = annotator.current
        loser = annotator.prev
    else:
        winner = annotator.prev
        loser = annotator.current
    (
        u_alpha,
        u_beta,
        u_winner_mean,
        u_winner_variance,
        u_loser_mean,
        u_loser_variance,
    ) = crowd_bt.update(
        float(annotator.alpha),
        float(annotator.beta),
        float(winner.mean),
        float(winner.variance),
        float(loser.mean),
        float(loser.variance),
    )
    annotator.alpha = u_alpha
    annotator.beta = u_beta
    winner.mean = u_winner_mean
    winner.variance = u_winner_variance
    loser.mean = u_loser_mean
    loser.variance = u_loser_variance
