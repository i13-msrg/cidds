import io
from pprint import pprint

from django.contrib import messages
from django.core.files.base import ContentFile
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views import View
import json
from django.core.files.images import ImageFile

# Create your views here.
from django_tables2 import RequestConfig
from matplotlib.backends.backend_agg import FigureCanvasAgg

from base import Orchestrator
from django.http import HttpResponse

from simulator.models import SimulationResults
from simulator.tables import SimulationResultsTable


class StartSim(View):

    def get(self, request):
        if request.user.is_anonymous:
            user_notif = 'Please login. If you dont have a login yet, please request access!'
            data = {
                'message': user_notif

            }
            return render(request, "default.html", data)

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

        if request.user.is_anonymous:
            user_notif = 'Please login. If you dont have a login yet, please request access!'
            data = {
                'message': user_notif

            }
            return render(request, "default.html", data)

        data = request.POST
        nodes = int(data.get("transactions"))
        processes = int(data.get("processes"))
        alpha = float(data.get("alpha"))
        randomness = float(data.get("randomness"))
        algorithm = data.get("algorithm")
        reference = data.get("reference")
        pprint(data)
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
        sim.unapproved_tips = len(t.tips())
        sim.time_units = t.time
        sim.save()

        table_results = SimulationResultsTable(SimulationResults.objects.all())
        RequestConfig(request).configure(table_results)
        pprint("***************************************************************" )

        pprint(table_results )
        data = {
            'Title': 'Simulation History',
            'table': table_results,
            'messages': messages
        }
        return render(request, "simulation_results.html", data)

        # response = HttpResponse(figure.getvalue(), content_type="image/png")

        # return response


class SimulationHistory(View):

    def get(self, request):
        if request.user.is_anonymous:
            user_notif = 'Please login. If you dont have a login yet, please request access!'
            data = {
                'message': user_notif

            }
            return render(request, "default.html", data)

        pprint("***************************************************************" )
        pprint("simulation history")

        table_results = SimulationResultsTable(SimulationResults.objects.all())
        RequestConfig(request).configure(table_results)
        pprint(table_results)


        data = {
            'Title': 'Simulation History',
            'table': table_results,
            'messages': messages

        }

        pprint(data)

        return render(request, "simulation_results.html", data)



class Comparison(View):

    def post(self, request):
        data = request.POST
        pks = data.getlist("sim_selection")
        selected_objects = SimulationResults.objects.filter(pk__in=pks)

        data = {
            'first_sim': selected_objects[0],
            'second_sim': selected_objects[1]

        }

        return render(request, "compare.html", data)

class Details(View):

    def get(self, request, sim_id):
        # id = int(request.GET.get('sim_id'))
        selected_object = SimulationResults.objects.get(id=sim_id)

        data = {
            'sim': selected_object,

        }

        return render(request, "details.html", data)