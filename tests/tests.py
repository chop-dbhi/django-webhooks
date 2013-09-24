import os
import time
import subprocess
from django.test import TransactionTestCase
import webhooks
from webhooks.registry import AlreadyRegistered, NotRegistered

TESTS_DIR = os.path.dirname(__file__)

TEST_URL = 'http://localhost:8328'

def emitlist():
    return range(5)

class WebhookTestCase(TransactionTestCase):
    def setUp(self):
        webhooks.events.register('test', emitlist)

    def tearDown(self):
        for key in webhooks.events.keys():
            webhooks.events.pop(key)

    def test_registry(self):
        self.assertEqual(webhooks.events.get('test'), emitlist)
        self.assertRaises(AlreadyRegistered, webhooks.events.register, 'test', emitlist)

        webhooks.events.unregister('test')
        self.assertEqual(webhooks.events.get('test'), None)
        self.assertRaises(NotRegistered, webhooks.events.unregister, 'test')

    def test_bind(self):
        webhooks.bind('test', TEST_URL)
        self.assertEqual(webhooks.Webhook.objects.count(), 1)
        webhooks.unbind('test', TEST_URL)
        self.assertEqual(webhooks.Webhook.objects.count(), 0)

    def test_trigger(self):
        # No event registered
        webhooks.trigger('nada', async=False)

        # No urls bound
        webhooks.trigger('test', async=False)

    def test_bad_handler(self):
        def func():
            raise Exception
        webhooks.events.register('bad', func)
        webhooks.bind('bad', TEST_URL)
        self.assertEqual(webhooks.trigger('bad', async=False), None)

    def test_bad_serialization(self):
        def func():
            class Object(object): pass
            return Object()
        webhooks.events.register('noserialize', func)
        webhooks.bind('noserialize', TEST_URL)
        self.assertEqual(webhooks.trigger('noserialize', async=False), None)

    def test_hook(self):
        webhooks.bind('test', TEST_URL)

        # Start web server subprocess
        server = subprocess.Popen(['python', os.path.join(TESTS_DIR, 'httpd.py')],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Ensure server starts since the subprocess starts asynchronously
        time.sleep(1)

        # Unpack first result
        resp, code = webhooks.test('test', TEST_URL, async=False)[0]

        # Test payload data
        self.assertEqual(resp.read(), '{}')
        self.assertEqual(code, 200)

        # Unpack first result
        resp, code = webhooks.trigger('test', async=False)[0]

        self.assertEqual(resp.read(), '[0, 1, 2, 3, 4]')
        self.assertEqual(code, 200)

        # Kill the server
        server.terminate()

    def test_hook_async(self):
        webhooks.bind('test', TEST_URL)

        # Start web server subprocess
        server = subprocess.Popen(['python', os.path.join(TESTS_DIR, 'httpd.py')],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Ensure server starts since the subprocess starts asynchronously
        time.sleep(1)

        webhooks.test('test', TEST_URL)
        webhooks.trigger('test')

        # Ensure theads are done
        time.sleep(1)

        # Kill the server
        server.terminate()
