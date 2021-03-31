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


def get_mean_and_variance(project, criterion_id):
    if criterion_id == "overall":
        return project.overallMean, project.overallVariance
    elif criterion_id == "innovation":
        return project.innovationMean, project.innovationVariance
    elif criterion_id == "functionality":
        return project.functionalityMean, project.functionalityVariance
    elif criterion_id == "design":
        return project.designMean, project.designVariance
    elif criterion_id == "complexity":
        return project.complexityMean, project.complexityVariance


def set_mean_and_variance(project, mean, variance, criterion_id):
    if criterion_id == "overall":
        project.overallMean = mean
        project.overallVariance = variance
        project.save(update_fields=["overallMean", "overallVariance"])
    elif criterion_id == "innovation":
        project.innovationMean = mean
        project.innovationVariance = variance
        project.save(update_fields=["innovationMean", "innovationVariance"])
    elif criterion_id == "functionality":
        project.functionalityMean = mean
        project.functionalityVariance = variance
        project.save(update_fields=["functionalityMean", "functionalityVariance"])
    elif criterion_id == "design":
        project.designMean = mean
        project.designVariance = variance
        project.save(update_fields=["designMean", "designVariance"])
    elif criterion_id == "complexity":
        project.complexityMean = mean
        project.complexityVariance = variance
        project.save(update_fields=["complexityMean", "complexityVariance"])


def perform_vote(annotator, current_won, criterion_id="overall"):
    if current_won:
        winner = annotator.current
        loser = annotator.prev
    else:
        winner = annotator.prev
        loser = annotator.current

    winner_mean, winner_variance = get_mean_and_variance(winner, criterion_id)
    loser_mean, loser_variance = get_mean_and_variance(loser, criterion_id)

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

    annotator.save()
    set_mean_and_variance(winner, winner_mean, winner_variance, criterion_id)
    set_mean_and_variance(loser, loser_mean, loser_variance, criterion_id)
