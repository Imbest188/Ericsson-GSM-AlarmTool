from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import TemplateView
from .Telnet.EricssonTelnet import EricssonTelnet
from .Telnet.EricssonNode import EricssonBsc
from .Telnet.AlarmParser import AlarmParser


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


class AlarmView(TemplateView):
    template_name = 'alarmwindow/alarms.html'
    #telnet = EricssonBsc('172.25.157.99', 'administrator', 'Administrator1@')#('10.104.133.3', 'administrator', 'Administrator1@')#('172.25.157.99', 'administrator', 'Administrator1@')#'10.140.3.7', 'ts_user', 'apg43l2@')

    def get(self, request, **kwargs):
        alarms = AlarmParser.parse_node_output(self.telnet.get('allip;'))
        #print([x.date_time for x in alarms])

        #print([x.text for x in alarms if x.type == 'str'])
        alarms.sort(key=lambda x: x.date_time, reverse=False)

        for alarm in alarms:
            if 'RBL' in alarm.managed_object:
                alarm.object_name = self.telnet.getRblOwner(alarm.managed_object)

        ctx = {'charging': [], 'alarms': alarms}
        if is_ajax(request) and request.method == "GET":
            return JsonResponse({"alarms": [x.toDict() for x in alarms]}, status=200)
        return render(request, self.template_name, ctx)


def index(request):
    return AlarmView.as_view()
