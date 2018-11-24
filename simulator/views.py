import io

from django.core.files.base import ContentFile
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views import View
import json
from django.core.files.images import ImageFile

# Create your views here.
from matplotlib.backends.backend_agg import FigureCanvasAgg

from base import Orchestrator
from django.http import HttpResponse

from simulator.models import SimulationResults


class StartSim(View):

    def get(self, request):
        nodes = request.GET.get('nodes')
        # processes = request.GET.get('processes')
        alpha = request.GET.get('alpha')
        randomness = request.GET.get('randomness')

        plot = Orchestrator.start_helper()
        buf = io.BytesIO()
        # plot.show()
        plot.savefig(buf, format="png")
        plot.show()
        response = HttpResponse(buf.getvalue(),content_type="image/png")
        # create your image as usual, e.g. pylab.plot(...)
        return response

    def post(self, request):

        data = request.POST
        nodes = int(data.get("transactions"))
        processes = int(data.get("processes"))
        alpha = float(data.get("alpha"))
        randomness = float(data.get("randomness"))
        algorithm = data.get("algorithm")
        reference =  data.get("reference")

        sim = SimulationResults(user=request.user,
                                       num_process=processes,
                                       alpha=alpha,
                                       randomness=randomness,
                                       reference=reference,
                                       algorithm=algorithm,
                                transactions=nodes
                                      )
        sim.status = "Running"
        sim.save()

        id = sim.id

        t = Orchestrator.start_helper(sim)
        figure = io.BytesIO()
        # plot.show()
        plot = t.plot()
        plot.savefig(figure, format="png")
        plot.show()


        sim = SimulationResults.objects.get(id=id)
        sim.status = "Done"

        resultImage = ImageFile(figure)
        sim.image.save(str(id)+'.png',resultImage)
        sim.tangle = t
        sim.reference = reference
        sim.save()



        table_results =  SimulationResults.objects.all()

        data = {
            'simulation': sim,
            'table': table_results
        }
        return render(request, "simulation_results.html", data)

        # response = HttpResponse(figure.getvalue(), content_type="image/png")

        # return response


class SimulationHistory(View):

    def get(self, request):
        table_results = SimulationResults.objects.all()

        data = {
            'table': table_results
        }
        return render(request, "simulation_results.html", data)

