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
                float(annotator.prev.overall_mean),
                float(annotator.prev.overall_variance),
                float(project.overall_mean),
                float(project.overall_variance),
            ),
            items,
        )


def get_mean_and_variance(project, criterion_id):
    if criterion_id == "overall":
        return project.overall_mean, project.overall_variance
    elif criterion_id == "innovation":
        return project.innovation_mean, project.innovation_variance
    elif criterion_id == "functionality":
        return project.functionality_mean, project.functionality_variance
    elif criterion_id == "design":
        return project.design_mean, project.design_variance
    elif criterion_id == "complexity":
        return project.complexity_mean, project.complexity_variance


def set_mean_and_variance(project, mean, variance, criterion_id):
    if criterion_id == "overall":
        project.overall_mean = mean
        project.overall_variance = variance
        project.save(update_fields=["overall_mean", "overall_variance"])
    elif criterion_id == "innovation":
        project.innovation_mean = mean
        project.innovation_variance = variance
        project.save(update_fields=["innovation_mean", "innovation_variance"])
    elif criterion_id == "functionality":
        project.functionality_mean = mean
        project.functionality_variance = variance
        project.save(update_fields=["functionality_mean", "functionality_variance"])
    elif criterion_id == "design":
        project.design_mean = mean
        project.design_variance = variance
        project.save(update_fields=["design_mean", "design_variance"])
    elif criterion_id == "complexity":
        project.complexity_mean = mean
        project.complexity_variance = variance
        project.save(update_fields=["complexity_mean", "complexity_variance"])


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
