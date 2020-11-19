from django.conf import settings
from judge.models import Project, Annotator
import judge.crowd_bt as crowd_bt
from numpy.random import shuffle, random, choice
from datetime import datetime

def preferred_items(annotator):
    items = []
    ignored_ids = {p.id for p in annotator.ignore}

    if ignored_ids:
        available_projects = Project.query.filter(
            (Project.active == True) and not (Project.id in ignored_ids)
        ).all()
    else:
        available_projects = Project.query.filter(Project.active == True).all()
    
    prioritized_projects = [p for p in available_projects if p.prioritized]
    items = prioritized_projects if prioritized_projects else available_projects

    annotators = Annotator.query.filter(
        (Annotator.active == True) and (Annotator.next is not None)
    ).all()

    nonbusy = {a.next.id for a in annotators if (datetime.utcnow() - a.updated).total_seconds() >= settings.TIMEOUT * 60}
    preferred = nonbusy if nonbusy else items

    less_seen = [p for p in preferred if len(p.viewed) < settings.MIN_VIEWS]

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
                annotator.alpha,
                annotator.beta,
                annotator.prev.mean,
                annotator.prev.variance,
                i.mean,
                i.variance), items)
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
        annotator.alpha,
        annotator.beta,
        winner.mean,
        winner.variance,
        loser.mean,
        loser.variance
    )
    annotator.alpha = u_alpha
    annotator.beta = u_beta
    winner.mean = u_winner_mean
    winner.variance = u_winner_variance
    loser.mean = u_loser_mean
    loser.variance = u_loser_variance