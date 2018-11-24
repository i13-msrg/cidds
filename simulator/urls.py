from django.urls import path
from django.views.generic import TemplateView

from simulator.views import StartSim, SimulationHistory

urlpatterns = [
    path('initialize/', StartSim.as_view()),
    path('', TemplateView.as_view(template_name='start_form.html')),
    path('history/', SimulationHistory.as_view()),

]