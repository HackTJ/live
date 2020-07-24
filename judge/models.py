from django.db import models

class Project(models.Model):
    # id is automatically created:
    # https://docs.djangoproject.com/en/3.0/topics/db/models/#automatic-primary-key-fields
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    mean = models.DecimalField(default=0., decimal_places=8, max_digits=12)
    variance = models.DecimalField(default=1., decimal_places=8, max_digits=12)
    numberOfVotes = models.IntegerField()
    timesSeen = models.IntegerField()
    timesSkipped = models.IntegerField()
    prioritize = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
