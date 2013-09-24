import logging
from django.conf import settings
from django.utils.importlib import import_module

__all__ = ('events', 'register', 'unregister')

logger = logging.getLogger('webhooks')

class AlreadyRegistered(Exception):
    pass

class NotRegistered(Exception):
    pass

class Events(dict):
    def register(self, event, handler):
        if event in self:
            raise AlreadyRegistered('handler {0} already registered for event {1}'.format(handler, event))
        self[event] = handler

    def unregister(self, event):
        if event not in self:
            raise NotRegistered('event {0} not registered'.format(event))
        del self[event]

events = Events()
register = events.register
unregister = events.unregister

# Autodiscover apps for webhook handlers. Modules can import webhooks and
# and do webhooks.register.
for app in settings.INSTALLED_APPS:
    module_path = '{0}.{1}'.format(app, 'webhooks')
    try:
        import_module(module_path)
    except Exception as e:
        logger.debug('failed to import module', extra={
            'module_path': module_path,
            'error': repr(e),
        })
