from django.contrib import admin
from .models import Project, Decision, Annotator

# Register your models here.
admin.site.register(Annotator)
admin.site.register(Decision)


class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "description")


admin.site.register(Project, ProjectAdmin)
