from django.shortcuts import render


def scoreboard(request):
    return render(request, 'scoreboard.html')
