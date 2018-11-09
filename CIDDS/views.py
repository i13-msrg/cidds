from django.shortcuts import render

def index(request):
    context = {}
    return render(request, '../static/../templates/index.html', context=context)