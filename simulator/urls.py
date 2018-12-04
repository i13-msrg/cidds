from django.urls import path
from django.views.generic import TemplateView

from simulator.views import StartSim, SimulationHistory, Comparison, Details

urlpatterns = [
    path('initialize/', StartSim.as_view(), name='initialize'),
    path('history/', SimulationHistory.as_view(), name='history'),
    path('start/', TemplateView.as_view(template_name='start_form.html'),
         name='startsim'),

    path('compare/', Comparison.as_view(), name='compare'),
    path('<int:sim_id>/', Details.as_view(), name='detail'),

]