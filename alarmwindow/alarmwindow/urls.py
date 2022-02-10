from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.AlarmView.as_view(), name='alarms'),
    path('alarms', views.AlarmView.as_view(), name='alarms'),
    path('get_alarm_text', views.get_alarm_text, name='get_alarm_text')
]
