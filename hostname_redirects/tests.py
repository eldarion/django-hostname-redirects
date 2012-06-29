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
        ret_val = self.middleware.process_request(req)
        self.assertIsNone(ret_val)

        req.META['SERVER_NAME'] = 'derp.com'
        ret_val = self.middleware.process_request(req)
        self.assertIsInstance(ret_val, HttpResponsePermanentRedirect)
        self.assertIn(current_site.domain, ret_val['Location'])
