from datetime import datetime
from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import ArrayField

num_criteria = len(settings.LIVE_JUDGE_CRITERIA)


class Project(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    link = models.URLField(blank=True)

    means = ArrayField(
        models.DecimalField(default=0.0, decimal_places=8, max_digits=12),
        # default=lambda: [0.0, ] * num_criteria,
        size=num_criteria,
    )
    variances = ArrayField(
        models.DecimalField(default=1.0, decimal_places=8, max_digits=12),
        # default=lambda: [1.0, ] * num_criteria,
        size=num_criteria,
    )
    numberOfVotes = models.IntegerField(default=0)
    timesSeen = models.IntegerField(default=0)  # decision made and not skipped
    timesSkipped = models.IntegerField(default=0)

    prioritize = models.BooleanField(default=False)
    active = models.BooleanField(default=True)


class Annotator(models.Model):
    judge = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    updated = models.DateTimeField(auto_now=True)
    current = models.OneToOneField(
        Project,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="%(class)s_current",
    )
    prev = models.OneToOneField(
        Project,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="%(class)s_prev",
    )
    ignore = models.ManyToManyField(
        Project,
        related_name="%(class)s_ignore",
    )

    viewed = models.ManyToManyField(
        Project,
        related_name="%(class)s_viewed",
    )

    alpha = models.DecimalField(default=10, decimal_places=8, max_digits=12)
    beta = models.DecimalField(default=1, decimal_places=8, max_digits=12)

    read_welcome = models.BooleanField(default=False)

    def update_current(self, new_current):
        if new_current:  # comparison was not skipped
            # the project jas been assigned, so cancel the prioritization:
            new_current.prioritized = False
            self.current = new_current
            self.ignore.add(new_current)


class Decision(models.Model):
    annotator = models.ForeignKey(
        Annotator,
        on_delete=models.CASCADE,
    )
    criterion = models.IntegerField(default=0)
    winner = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="%(class)s_winner",
    )
    loser = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="%(class)s_loser",
    )
    time = models.DateTimeField(auto_now_add=True)
