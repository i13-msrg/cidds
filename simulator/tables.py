import django_tables2 as tables

from simulator.models import SimulationResults


class SimulationResultsTable(tables.Table):
    class Meta:
        model = SimulationResults