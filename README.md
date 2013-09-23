# django-webhooks

[![Build Status](https://travis-ci.org/cbmi/django-webhooks.png?branch=master)](https://travis-ci.org/cbmi/django-webhooks)
[![Coverage Status](https://coveralls.io/repos/cbmi/django-webhooks/badge.png?branch=master)](https://coveralls.io/r/cbmi/django-webhooks?branch=master)



## Install

```bash
# Yes.. with a two on the end
pip install django-webhooks2
```

## Setup

Add `webhooks` to `INSTALLED_APPS`:

```python
INSTALLED_APPS = (
    'webhooks',
    ...
)
```

## Settings

- `WEBHOOK_TIMEOUT` - Seconds to wait until a request times out
- `WEBHOOK_THREADS` - Maximum number of threads to be used in a worker pool

## Trigger Execution

1. Events are triggered using `webhooks.trigger(event, [*args, [**kwargs]])`
2. If a handler is registered for the event, the arguments are passed into the handler to generate a JSON-serializable payload.
3. All URLs registered for this event are collected and each URL receives a POST request with the JSON payload

**Notes:**

- If no URLs are registered for the event, the payload is not generated (since it would be wasted computation)
- All requests are sent in parallel using threads
- Logging is heavily use to catch any undesirable or unexpected behaviors (such as failing requests, errors or data serialization)

## Usage

```python
import webhooks

# Define and register a handler for an event
def handler():
    return { ... }

webhooks.events.register('event', handler)

# Bind a URL to the event
webhooks.bind('event', 'http://example.com')

# Trigger the event. Any arguments after the event name
# will be passed into the handler to produce the data that
# will be POSTed to the bound URLs.
webhooks.trigger('event')
```
