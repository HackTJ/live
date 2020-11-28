"""hacktj_live URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import allauth

from django.contrib import admin
from django.urls import include, path

from . import views as project_views
from judge import views as judge_views
from allauth.account import views as auth_views

urlpatterns = [
    path('', project_views.index),
    path('judge', judge_views.home),
    path('judge/welcome', judge_views.welcome),
    path('judge/scoreboard', judge_views.scoreboard),
    path('judge/queue', judge_views.queue),
    path('judge/begin', judge_views.begin),
    path('judge/vote', judge_views.vote),
    path('credits', project_views.credits),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('accounts/volunteer_signup/', auth_views.signup)
]


from django.conf import settings
if settings.DEBUG:
    import debug_toolbar
    urlpatterns.append(path('__debug__/', include(debug_toolbar.urls)))

