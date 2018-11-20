import io

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
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
        nodes = data.get("nodes")
        # processes = data.get("alpha")
        alpha = data.get("alpha")
        randomness = data.get("randomness")
        algorithm = data.get("algoritm")
        reference =  data.get("reference")

        t = Orchestrator.start_helper()
        figure = io.BytesIO()
        # plot.show()
        plot = t.plot()
        plot.savefig(figure, format="png")
        plot.show()

        resultImage = ImageFile(figure)

        sim_result =  SimulationResults(user= request.user)
        sim_result.image = resultImage
        sim_result.tangle = t
        sim_result.reference = reference


        response = HttpResponse(figure.getvalue(), content_type="image/png")
        # return JsonResponse(
        #     data={
        #         "test": True,
        #         "error": None
        #     },
        #     status=200,
        # )
        return response

