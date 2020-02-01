import django_tables2 as tables
from django.utils.html import format_html
from django_tables2 import A

from simulator.models import SimulationResults


class CheckBoxColumnWithName(tables.CheckBoxColumn):
    @property
    def header(self):
        return self.verbose_name

class InteractiveLink(tables.Column):
    url = '<a href="http://localhost:8080/?id={id}">Interactive</a>'

    def render(self, record):
        return format_html(self.url, id=record.simulator.id,
                           title=record.title)

class SimulationResultsTable(tables.Table):
    sim_selection = CheckBoxColumnWithName(verbose_name="Selection", accessor="pk", attrs={"th__input":
                                                                {
                                                                    "onclick": "toggle(this)"}},
                                      orderable=False)
    interactive = InteractiveLink()

    details = tables.LinkColumn('detail', text='Details', args=[A('pk')], empty_values=())
    class Meta:
        model = SimulationResults
        fields = ('sim_selection','id','details', 'reference', 'algorithm', 'status', 'image', 'created', 'modified')

