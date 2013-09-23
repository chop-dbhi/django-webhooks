from django.db import models
from .events import events

__all__ = ('Webhook',)

class Webhook(models.Model):
    EVENT_CHOICES = [(e, e) for e in events.keys()]
    event = models.CharField(max_length=100, choices=EVENT_CHOICES)
    url = models.CharField(max_length=200)

    class Meta(object):
        db_table = 'webhook'
        unique_together = ('event', 'url')

    def __unicode__(self):
        return u'{0} => {1}'.format(self.event, self.url)
