import io
import json
import os
import unittest
from unittest.mock import patch

from groundedops.providers import ProviderError, generate


class FakeResponse:
    def __init__(self, obj):
        self.data = io.BytesIO(json.dumps(obj).encode())

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, size=-1):
        return self.data.read(size)


class ProvidersTests(unittest.TestCase):
    def test_ollama_request(self):
        with patch('groundedops.providers.urlopen', return_value=FakeResponse({'response': 'grounded [1]'})) as call:
            result = generate('ollama', 'Prompt')
        self.assertEqual(result, 'grounded [1]')
        request = call.call_args.args[0]
        self.assertEqual(request.full_url, 'http://127.0.0.1:11434/api/generate')
        self.assertFalse(json.loads(request.data)['stream'])

    def test_gemini_requires_key(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ProviderError):
                generate('gemini', 'Prompt')

    def test_gemini_request(self):
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'local-test-key'}):
            with patch('groundedops.providers.urlopen', return_value=FakeResponse({'candidates': [{'content': {'parts': [{'text': 'Response [1]'}]}}]})) as call:
                result = generate('gemini', 'Prompt')
        self.assertEqual(result, 'Response [1]')
        request = call.call_args.args[0]
        self.assertEqual(request.get_header('X-goog-api-key'), 'local-test-key')
        self.assertIn('generateContent', request.full_url)
        self.assertIn('/gemini-3.5-flash-lite:generateContent', request.full_url)

    def test_gemini_model_can_be_overridden(self):
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'local-test-key', 'GEMINI_MODEL': 'gemini-custom'}):
            with patch('groundedops.providers.urlopen', return_value=FakeResponse({'candidates': [{'content': {'parts': [{'text': 'OK'}]}}]})) as call:
                self.assertEqual(generate('gemini', 'Prompt'), 'OK')
        self.assertIn('/gemini-custom:generateContent', call.call_args.args[0].full_url)

    def test_empty_provider_response(self):
        with patch('groundedops.providers.urlopen', return_value=FakeResponse({})):
            with self.assertRaises(ProviderError):
                generate('ollama', 'Prompt')

    def test_unknown_provider(self):
        with self.assertRaises(ProviderError):
            generate('unknown', 'Prompt')

    def test_bad_model_name(self):
        with patch.dict(os.environ, {'OLLAMA_MODEL': '../../bad model'}):
            with self.assertRaises(ProviderError):
                generate('ollama', 'Prompt')


if __name__ == '__main__':
    unittest.main()
