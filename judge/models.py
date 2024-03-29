from datetime import datetime
from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext_lazy


class Project(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True)
    description = models.CharField(max_length=255, blank=True)
    tags = ArrayField(models.CharField(max_length=255), default=list)
    link = models.URLField(blank=True)

    overall_mean = models.DecimalField(default=0.0, decimal_places=8, max_digits=12)
    overall_variance = models.DecimalField(default=1.0, decimal_places=8, max_digits=12)

    innovation_mean = models.DecimalField(default=0.0, decimal_places=8, max_digits=12)
    innovation_variance = models.DecimalField(
        default=1.0, decimal_places=8, max_digits=12
    )

    functionality_mean = models.DecimalField(
        default=0.0, decimal_places=8, max_digits=12
    )
    functionality_variance = models.DecimalField(
        default=1.0, decimal_places=8, max_digits=12
    )

    design_mean = models.DecimalField(default=0.0, decimal_places=8, max_digits=12)
    design_variance = models.DecimalField(default=1.0, decimal_places=8, max_digits=12)

    complexity_mean = models.DecimalField(default=0.0, decimal_places=8, max_digits=12)
    complexity_variance = models.DecimalField(
        default=1.0, decimal_places=8, max_digits=12
    )

    numberOfVotes = models.IntegerField(default=0)
    timesSeen = models.IntegerField(default=0)  # decision made and not skipped
    timesSkipped = models.IntegerField(default=0)

    prioritize = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.pk})"


class Annotator(models.Model):
    judge = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        unique=True,
        primary_key=True,
    )
    updated = models.DateTimeField(auto_now=True)
    current = models.ForeignKey(
        Project,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="%(class)s_current",
    )
    prev = models.ForeignKey(
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
            # the project has been assigned, so cancel the prioritization:
            new_current.prioritized = False
            self.current = new_current
            self.save(update_fields=["current"])
            self.ignore.add(new_current)

    def __str__(self):
        return f"{self.judge.get_username()} ({self.pk})"


class Decision(models.Model):
    # one Decision has one Annotator, but one Annotator has multiple decisions
    # (Annotator is one, Decision is many)
    annotator = models.ForeignKey(
        Annotator,
        on_delete=models.CASCADE,
        to_field="judge",
    )

    class Criterion(models.TextChoices):
        OVERALL = "overall", gettext_lazy("Overall")
        INNOVATION = "innovation", gettext_lazy("Innovation")
        FUNCTIONALITY = "functionality", gettext_lazy("Functionality")
        DESIGN = "design", gettext_lazy("Design")
        COMPLEXITY = "complexity", gettext_lazy("Technical Complexity")

    criterion = models.CharField(
        max_length=max(len(value) for value in Criterion.values),
        choices=Criterion.choices,
        default=Criterion.OVERALL,
    )
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
