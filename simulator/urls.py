from django.urls import path, include
from django.views.generic import TemplateView


from simulator.views import StartSim, SimulationHistory, Comparison, Details

urlpatterns = [
    path('initialize/', StartSim.as_view(), name='initialize'),
    path('history/', SimulationHistory.as_view(), name='history'),
    path('start/', include([
        path('cidds/', TemplateView.as_view(template_name='start_form_cidds.html'), name='startsim'),
        path('cac/', TemplateView.as_view(template_name='start_form_cac.html'), name='startcac'),
    ])),
    path('compare/', Comparison.as_view(), name='compare'),
    path('<int:sim_id>/', Details.as_view(), name='detail'),
]