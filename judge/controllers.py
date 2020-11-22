from django.conf import settings
from django.utils import timezone
from judge.models import Project, Annotator
import judge.crowd_bt as crowd_bt
from numpy.random import shuffle, random, choice
from datetime import datetime

def preferred_items(annotator):
    items = []
    ignored_ids = [p.id for p in annotator.ignore.all()]

    if ignored_ids:
        available_projects = Project.objects.filter(active=True).exclude(id__in=ignored_ids).all()
    else:
        available_projects = Project.objects.filter(active=True).all()
    
    prioritized_projects = [p for p in available_projects if p.prioritize]
    items = prioritized_projects if prioritized_projects else available_projects

    annotators = Annotator.objects.filter(next__isnull=False).all()
    annotators = [a for a in annotators if a.judge.is_active]

    nonbusy = list({a.next for a in annotators if (a.next in available_projects) and ((timezone.make_aware(datetime.utcnow()) - a.updated).total_seconds() >= settings.TIMEOUT * 60)})
    preferred = nonbusy if nonbusy else items

    less_seen = [p for p in preferred if p.timesSeen < settings.MIN_VIEWS]

    return less_seen if less_seen else preferred

def init_annotator(annotator):
    if annotator.next is None:
        items = preferred_items(annotator)
        if items:
            annotator.update_next(choice(items))
            annotator.save()

def choose_next(annotator):
    items = preferred_items(annotator)

    shuffle(items)
    if items:
        if random() < crowd_bt.EPSILON:
            return items[0]
        else:
            return crowd_bt.argmax(lambda i: crowd_bt.expected_information_gain(
                float(annotator.alpha),
                float(annotator.beta),
                float(annotator.prev.mean),
                float(annotator.prev.variance),
                float(i.mean),
                float(i.variance)), items)
    else:
        return None


def perform_vote(annotator, next_won):
    if next_won:
        winner = annotator.next
        loser = annotator.prev
    else:
        winner = annotator.prev
        loser = annotator.next
    u_alpha, u_beta, u_winner_mean, u_winner_variance, u_loser_mean, u_loser_variance = crowd_bt.update(
        float(annotator.alpha),
        float(annotator.beta),
        float(winner.mean),
        float(winner.variance),
        float(loser.mean),
        float(loser.variance)
    )
    annotator.alpha = u_alpha
    annotator.beta = u_beta
    winner.mean = u_winner_mean
    winner.variance = u_winner_variance
    loser.mean = u_loser_mean
    loser.variance = u_loser_variance