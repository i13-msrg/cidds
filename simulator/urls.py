from django.urls import path
from django.views.generic import TemplateView

from simulator.views import StartSim, SimulationHistory, Comparison

urlpatterns = [
    path('initialize/', StartSim.as_view(), name='initialize'),
    path('', TemplateView.as_view(template_name='start_form.html'), name='startsim'),
    path('history/', SimulationHistory.as_view(), name='history'),
    path('compare/', Comparison.as_view(), name='compare'),

]