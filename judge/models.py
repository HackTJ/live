from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

class Project(models.Model):
    # id is automatically created:
    # https://docs.djangoproject.com/en/3.0/topics/db/models/#automatic-primary-key-fields
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    description = models.CharField(max_length=255)

    mean = models.DecimalField(default=0., decimal_places=8, max_digits=12)
    variance = models.DecimalField(default=1., decimal_places=8, max_digits=12)
    numberOfVotes = models.IntegerField(default=0)
    timesSeen = models.IntegerField(default=0)
    timesSkipped = models.IntegerField(default=0)

    prioritize = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

class Annotator(models.Model):
    judge = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
    )

    updated = models.DateTimeField(blank=True, null=True)

    next = models.ForeignKey(
        Project,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="%(class)s_next"
    )
    prev = models.ForeignKey(
        Project,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="%(class)s_prev"
    )
    ignore = models.ManyToManyField(
        Project,
        related_name="%(class)s_ignore"
    )

    alpha = models.DecimalField(default=10, decimal_places=8, max_digits=12)
    beta = models.DecimalField(default=1, decimal_places=8, max_digits=12)

    read_welcome = models.BooleanField(default=False)

    def update_next(self, new_next):
        if new_next is not None:
            new_next.prioritized = False
            self.updated = datetime.utcnow()
        self.next = new_next

Project.viewed = models.ManyToManyField(
    Annotator,
    related_name="%(class)s_viewed"
)

class Decision(models.Model):
    annotator = models.ForeignKey(
        Annotator,
        on_delete=models.CASCADE,
    )
    winner = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="%(class)s_winner"
    )
    loser =  models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="%(class)s_loser"
    )
    time = models.DateTimeField(auto_now_add=True)