from django.contrib import admin
from .models import Project, Decision, Annotator

# Register your models here.
admin.site.register(Project)
admin.site.register(Annotator)
admin.site.register(Decision)