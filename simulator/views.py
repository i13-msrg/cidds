import io

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views import View
import json

# Create your views here.
from matplotlib.backends.backend_agg import FigureCanvasAgg

from base import Orchestrator
from django.http import HttpResponse


class StartSim(View):

    def get(self, request):
        nodes = request.GET.get('nodes')
        processes = request.GET.get('processes')
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

        data = json.loads(request.body.decode('utf-8'))
        nodes = data.get("noeds")
        processes = data.get("alpha")
        alpha = data.get("alpha")
        randomness = data.get("randomness")
        algorithm = data.get("algoritm")


        return JsonResponse(
            data={
                "test": True,
                "error": None
            },
            status=200,
        )

