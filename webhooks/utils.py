import json
import logging
import urllib2
import threading
from multiprocessing.pool import ThreadPool
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from .models import Webhook
from .events import events

__all__ = ('bind', 'unbind', 'trigger', 'test')

logger = logging.getLogger('webhooks')

WEBHOOK_TIMEOUT = getattr(settings, 'WEBHOOK_TIMEOUT', None)
WEBHOOK_THREADS = getattr(settings, 'WEBHOOK_THREADS', 4)

def bind(event, url):
    return Webhook.objects.get_or_create(event=event, url=url)

def unbind(event, url):
    Webhook.objects.filter(event=event, url=url).delete()

def test(event, url, *args, **kwargs):
    "Tests a URL for the event with an empty payload"
    return _trigger(event, [url], *args, **kwargs)

def trigger(event, async=True, *args, **kwargs):
    "Triggers webhooks associated with this event."
    logextra = {'event': event, 'args': args, 'kwargs': kwargs}

    # Get all urls associated with this event
    urls = list(Webhook.objects.filter(event=event).values_list('url', flat=True))

    # If no handler is registered, log an error if webhooks are registered
    # otherwise warn since not having a handler may be unexpected.
    if event not in events:
        if urls:
            logger.error('webhooks registered for missing event',
                exc_info=True, extra=logextra)
        else:
            logger.warn('no handler registered for webhook event',
                extra=logextra)
        return

    # If no webhooks are registered for the event, nothing to do.
    if not urls:
        return

    # The handler could be None which means the payload will be empty.
    handler = events.get(event)

    return _trigger(event, urls, handler=handler, async=async, *args, **kwargs)

def _trigger(event, urls, handler=None, async=True, *args, **kwargs):
    """Internal function for triggering a webhook. If no handler is provided,
    an empty dictionary will be used as the payload. This is only used for
    testing webhooks.
    """
    logextra = {'event': event, 'args': args, 'kwargs': kwargs}

    # Generate payload for encoding
    if handler:
        try:
            payload = handler(*args, **kwargs)
        except Exception:
            logger.error("error generating payload", exc_info=True, extra=logextra)
            return
    else:
        payload = {}

    # Serialize as JSON
    try:
        data = json.dumps(payload, cls=DjangoJSONEncoder)
    except Exception:
        logger.error("error serializing payload", exc_info=True, extra=logextra)
        return

    return _send_all_requests(event, urls, data, async=async)

def _send_all_requests(event, urls, data, async=True):
    """Sends a request to each url with the supplied data. If async is true,
    each request will be spawned in a separate thread.
    """
    tasks = [(event, url, data) for url in urls]

    pool = ThreadPool(WEBHOOK_THREADS)
    result = pool.map_async(_send_request, tasks)
    # Tasks are processed asynchronously, but only if async is true
    # is the result returned. No timeout is supplied here since the
    # timeout is specified in the task itself (the web request). Since
    # those will timeout after WEBHOOK_TIMEOUT, this result should not
    # take much longer.
    if not async:
        return result.get()

def _send_request(args):
    "Sends a POST request `url` with `data` as the request body."
    event, url, data = args
    logger.debug('sending webhook request', extra={
        'event': event,
        'url': url,
        'data': 'data',
    })

    request = urllib2.Request(url, data, headers={
        'Content-Type': 'application/json',
    })

    try:
        response = urllib2.urlopen(request, timeout=WEBHOOK_TIMEOUT)
        return response.getcode()
    except urllib2.HTTPError as e:
        # TODO this may be too aggressive of a log level since it's technically
        # the client's problem that the request failed (assuming a 4xx or 5xx).
        logger.error('webhook client or server error', exc_info=True, extra={
            'event': event,
            'url': url,
            'data': data,
        })
        # HTTPError has a `code` attribute corresponding to the
        # response status code
        return e.code
    except Exception as e:
        logger.error('webhook request failed', exc_info=True, extra={
            'event': event,
            'url': url,
            'data': data,
        })
