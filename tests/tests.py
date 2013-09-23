import os
import time
import subprocess
from django.test import TestCase
import webhooks

TESTS_DIR = os.path.dirname(__file__)

class WebhookTestCase(TestCase):
    def test_registry(self):
        def emitlist():
            return range(5)

        webhooks.events.register('test', emitlist)
        self.assertEqual(webhooks.events.get('test'), emitlist)

        webhooks.events.unregister('test')
        self.assertEqual(webhooks.events.get('test'), None)

    def test_hook(self):
        webhooks.bind('test', 'http://localhost:8328')

        # Start web server subprocess
        server = subprocess.Popen(['python', os.path.join(TESTS_DIR, 'httpd.py')],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Ensure server starts since the subprocess starts asynchronously
        time.sleep(1)

        webhooks.test('test', 'http://localhost:8328', async=False)

        # Kill the server
        server.terminate()
