from django.test import TestCase
from django.test.client import RequestFactory
from django.http import HttpResponsePermanentRedirect
from django.conf import settings
from django.contrib.sites.models import Site

from hostname_redirects.models import RedirectHost
from hostname_redirects.middleware import HostnameRedirectMiddleware


class MiddlewareTests(TestCase):
    def setUp(self):
        self.middleware = HostnameRedirectMiddleware()
        self.factory = RequestFactory()
    
    def test_hostname_redirect(self):
        current_site = Site.objects.get_current()
        RedirectHost.objects.create(hostname='derp.com', site=current_site)
        req = self.factory.get('/some/path/')
        req.META['SERVER_NAME'] = current_site.domain
        ret_val = self.middleware.process_request(req)
        self.assertIsNone(ret_val)

        req.META['SERVER_NAME'] = 'derp.com'
        ret_val = self.middleware.process_request(req)
        self.assertIsInstance(ret_val, HttpResponsePermanentRedirect)
        self.assertIn(current_site.domain, ret_val['Location'])
    
    def test_fallback_redirect(self):
        settings.CATCHALL_REDIRECT_HOSTNAME = 'derp.com'
        req = self.factory.get('/some/path/')
        ret_val = self.middleware.process_request(req)
        self.assertIsInstance(ret_val, HttpResponsePermanentRedirect)
        self.assertIn('derp.com', ret_val['Location'])

        req.META['SERVER_NAME'] = 'example.com'
        ret_val = self.middleware.process_request(req)
        self.assertIsNone(ret_val)

    def test_remove_www(self):
        settings.REMOVE_WWW = True
        current_site = Site.objects.get_current()
        req = self.factory.get('/some/path/')
        req.META['SERVER_NAME'] = 'www.morederp.com'
        ret_val = self.middleware.process_request(req)
        self.assertIsInstance(ret_val, HttpResponsePermanentRedirect)
        self.assertIn('morederp.com', ret_val['Location'])
        self.assertNotIn('www.morederp.com', ret_val['Location'])

