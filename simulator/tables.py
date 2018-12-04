import django_tables2 as tables
from django_tables2 import A

from simulator.models import SimulationResults


class CheckBoxColumnWithName(tables.CheckBoxColumn):
    @property
    def header(self):
        return self.verbose_name

class SimulationResultsTable(tables.Table):
    sim_selection = CheckBoxColumnWithName(verbose_name="Slection", accessor="pk", attrs={"th__input":
                                                                {
                                                                    "onclick": "toggle(this)"}},
                                      orderable=False)

    details = tables.LinkColumn('detail', text='Details', args=[A('pk')], empty_values=())
    class Meta:
        model = SimulationResults
        fields = ('sim_selection','id','details', 'reference' , 'algorithm', 'status', 'image', 'created', 'modified')

