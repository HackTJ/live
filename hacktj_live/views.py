from django.shortcuts import render


def index(request):
    return render(request, "index.html")


def credits(request):
    return render(request, "credits.html")
