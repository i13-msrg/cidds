import django_tables2 as tables

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
    class Meta:
        model = SimulationResults
        fields = ('sim_selection','id', 'reference' , 'algorithm', 'status', 'image', 'created', 'modified')

