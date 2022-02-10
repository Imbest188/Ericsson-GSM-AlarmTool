from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import TemplateView
from .models import Alarms
from . import Telnet


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


class AlarmView(TemplateView):
    template_name = 'alarmwindow/alarms.html'

    def get(self, request: WSGIRequest, **kwargs):
        if is_ajax(request) and request.method == "GET":
            node_id = request.GET.dict()
            n_id = node_id['id'] if 'id' in node_id.keys() else 1
            alarms = Alarms.objects.filter(node_id=n_id, is_active=True).order_by('raising_time')
            return JsonResponse({"alarms": [x.toDict() for x in alarms]}, status=200)
        alarms = Alarms.objects.all()
        ctx = {'charging': [], 'alarms': alarms}
        return render(request, self.template_name, ctx)


def index(request):
    return AlarmView.as_view()
