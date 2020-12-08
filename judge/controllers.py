from datetime import datetime, timedelta
from numpy.random import shuffle, random, choice
from django.conf import settings
from django.utils import timezone
from judge.models import Project
import judge.crowd_bt as crowd_bt


def preferred_items(annotator):
    ignored_ids = annotator.ignore.values_list("id", flat=True)

    available_projects = Project.objects.filter(
        active=True, annotator_current__isnull=True
    ).exclude(id__in=ignored_ids)

    prioritized_projects = available_projects.filter(prioritize=True)
    items = prioritized_projects if prioritized_projects else available_projects

    nonbusy = available_projects.filter(
        annotator_current__updated__gte=timezone.make_aware(datetime.utcnow())
        + timedelta(minutes=settings.LIVE_JUDGE_TIMEOUT)
    )
    preferred = nonbusy if nonbusy else items

    less_seen = preferred.filter(timesSeen__lt=settings.LIVE_JUDGE_MIN_VIEWS)

    out = less_seen if less_seen else preferred
    return list(out.distinct())


def init_annotator(annotator):
    if not annotator.current:
        items = preferred_items(annotator)
        if items:
            # assert not any(hasattr(project, "annotator_current") for project in items)
            annotator.update_current(choice(items))
            annotator.current.save()
            annotator.save(update_fields=['current'])
        else:
            import logging

            logger = logging.getLogger(__name__)
            logger.debug("preferred_items() returned no projects")


def choose_next(annotator):
    items = preferred_items(annotator)

    shuffle(items)
    if items:
        if random() < crowd_bt.EPSILON:
            return items[0]
        return crowd_bt.argmax(
            lambda project: crowd_bt.expected_information_gain(
                float(annotator.alpha),
                float(annotator.beta),
                float(annotator.prev.means[0]),
                float(annotator.prev.variances[0]),
                float(project.means[0]),
                float(project.variances[0]),
            ),
            items,
        )


def perform_vote(annotator, current_won, criterion_index=0):
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
        float(winner.means[criterion_index]),
        float(winner.variances[criterion_index]),
        float(loser.means[criterion_index]),
        float(loser.variances[criterion_index]),
    )
    annotator.alpha = u_alpha
    annotator.beta = u_beta
    winner.means[criterion_index] = u_winner_mean
    winner.variances[criterion_index] = u_winner_variance
    loser.means[criterion_index] = u_loser_mean
    loser.variances[criterion_index] = u_loser_variance
