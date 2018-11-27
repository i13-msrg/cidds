import django_tables2 as tables

from simulator.models import SimulationResults


class SimulationResultsTable(tables.Table):

    selection_column = tables.CheckBoxColumn(verbose_name = 'Selection')

    class Meta:
        model = SimulationResults
        fields = ('selection_column','id', 'reference' , 'algorithm', 'status', 'image', 'created', 'modified',)
