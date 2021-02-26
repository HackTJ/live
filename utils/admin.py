from django.contrib import admin
from .models import LiveUser
from django.contrib.auth.admin import UserAdmin
from django.db import models

def set_active(modeladmin, request, queryset):
    queryset.update(is_active=True)

class LiveUserAdmin(UserAdmin):
    actions = [set_active]

admin.site.register(LiveUser, LiveUserAdmin)