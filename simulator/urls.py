from django.urls import path

from simulator.views import StartSim

urlpatterns = [
    path('startsim/', StartSim.as_view()),

]