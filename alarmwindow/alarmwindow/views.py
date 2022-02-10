from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import TemplateView
from .models import Alarms, Nodes
#from .Telnet import *


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

def get_controller_and_id(request):
    request_data = request.GET.dict()
    controller = request_data['controller'] if 'controller' in request_data.keys() else 'BSC03'
    alarm_id = request_data['alarm_id']
    return controller, alarm_id


def get_alarm_text(request):
    controller_name, alarm_id = get_controller_and_id(request)
    controller_id = Nodes.objects.filter(name=controller_name).first().id
    alarm_text = Alarms.objects.filter(node_id=controller_id, id=alarm_id).first().text

    response = {
        'text': alarm_text
    }
    return JsonResponse(response)


class AlarmView(TemplateView):
    template_name = 'alarmwindow/alarms.html'

    @staticmethod
    def __get_node_id(answer):
        if 'node' in answer.keys():
            n_name = answer['node']
            n_id = Nodes.objects.only('id').get(name=n_name).id
            return n_id
        return 1

    def get(self, request: WSGIRequest, **kwargs):
        if is_ajax(request) and request.method == "GET":
            node_id = self.__get_node_id(request.GET.dict())
            alarms = Alarms.objects.filter(node_id=node_id, is_active=True).order_by('raising_time')
            return JsonResponse({"alarms": [x.toDict() for x in alarms]}, status=200)

        alarms = Alarms.objects.all()
        ctx = {'charging': [], 'alarms': alarms}
        return render(request, self.template_name, ctx)


def index(request):
    return AlarmView.as_view()
