from django.contrib import admin
from .models import Webhook

class WebhookAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'event', 'url')
    list_editable = ('event', 'url')
    list_filter = ('event',)

admin.site.register(Webhook, WebhookAdmin)
