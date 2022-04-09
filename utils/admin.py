from django.contrib import admin
from .models import LiveUser
from django.contrib.auth.admin import UserAdmin
from django.db import models


def set_active(modeladmin, request, queryset):
    queryset.update(is_active=True)


set_active.short_description = "Mark selected users as active"


class LiveUserAdmin(UserAdmin):
    actions = [set_active]
    list_display = ["is_active"]


# admin.site.unregister(User)
admin.site.register(LiveUser, LiveUserAdmin)
