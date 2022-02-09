from django.db import models


class Alarms(models.Model):
    id = models.IntegerField(primary_key=True)
    type = models.CharField(max_length=7)
    raising_time = models.CharField(max_length=15)
    ceasing_time = models.CharField(max_length=15)
    managed_object = models.CharField(max_length=30)
    object_name = models.CharField(max_length=30)
    slogan = models.CharField(max_length=30)
    descr = models.CharField(max_length=60)
    text = models.CharField(max_length=300)
    is_active = models.BooleanField()
    node_id = models.IntegerField()

    def toDict(self):
        return {
            'id': self.id,
            'type': self.type,
            'raising_time': self.raising_time,
            'managed_object': self.managed_object,
            'object_name': self.object_name,
            'slogan': self.slogan,
            'descr': self.descr
        }
