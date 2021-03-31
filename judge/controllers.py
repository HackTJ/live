from datetime import datetime, timedelta
from random import shuffle, random, choice
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
            annotator.save(update_fields=["current"])
        else:
            import logging

            logger = logging.getLogger(__name__)
            logger.debug("preferred_items() returned no projects")


def choose_next(annotator):
    items = preferred_items(annotator)

    if items:
        if random() < crowd_bt.EPSILON:
            return choice(items)
        return crowd_bt.argmax(
            lambda project: crowd_bt.expected_information_gain(
                float(annotator.alpha),
                float(annotator.beta),
                float(annotator.prev.overallMean),
                float(annotator.prev.overallVariance),
                float(project.overallMean),
                float(project.overallVariance),
            ),
            items,
        )


def get_mean_and_variance(project, criterion_index):
    if criterion_index == 0:
        return project.overallMean, project.overallVariance
    elif criterion_index == 1:
        return project.innovationMean, project.innovationVariance
    elif criterion_index == 2:
        return project.functionalityMean, project.functionalityVariance
    elif criterion_index == 3:
        return project.designMean, project.designVariance
    elif criterion_index == 4:
        return project.complexityMean, project.complexityVariance


def set_mean_and_variance(project, mean, variance, criterion_index):
    if criterion_index == 0:
        project.overallMean = mean
        project.overallVariance = variance
    elif criterion_index == 1:
        project.innovationMean = mean
        project.innovationVariance = variance
    elif criterion_index == 2:
        project.functionalityMean = mean
        project.functionalityVariance = variance
    elif criterion_index == 3:
        project.designMean = mean
        project.designVariance = variance
    elif criterion_index == 4:
        project.complexityMean = mean
        project.complexityVariance = variance

    project.save()


def perform_vote(annotator, current_won, criterion_index=0):
    if current_won:
        winner = annotator.current
        loser = annotator.prev
    else:
        winner = annotator.prev
        loser = annotator.current

    winner_mean, winner_variance = get_mean_and_variance(winner, criterion_index)
    loser_mean, loser_variance = get_mean_and_variance(loser, criterion_index)

    (
        annotator.alpha,
        annotator.beta,
        winner_mean,
        winner_variance,
        loser_mean,
        loser_variance,
    ) = crowd_bt.update(
        float(annotator.alpha),
        float(annotator.beta),
        float(winner_mean),
        float(winner_variance),
        float(loser_mean),
        float(loser_variance),
    )

    set_mean_and_variance(winner, winner_mean, winner_variance, criterion_index)
    set_mean_and_variance(loser, loser_mean, loser_variance, criterion_index)
