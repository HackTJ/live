from django.urls import path

from . import views

app_name = "judge"
urlpatterns = [
    path("", views.index, name="index"),
    path("welcome", views.welcome, name="welcome"),
    path("begin", views.begin, name="begin"),
    path("vote", views.vote, name="vote"),
    path("scoreboard", views.scoreboard, name="scoreboard"),
    path("queue", views.queue, name="queue"),
    path("rubric", views.rubric, name="rubric"),
]
