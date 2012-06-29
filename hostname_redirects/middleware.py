from django.http import HttpResponsePermanentRedirect
from django.conf import settings
from django.contrib.sites.models import Site

from hostname_redirects.models import RedirectHost


class HostnameRedirectMiddleware(object):
    def process_request(self, request):
        server_name = request.META['SERVER_NAME']
        try:
            new_hostname = RedirectHost.objects.select_related('site') \
                .get(hostname=server_name).site.domain
        except RedirectHost.DoesNotExist:
            if getattr(settings, 'REMOVE_WWW', None) \
                    and server_name.startswith('www.'):
                new_hostname = server_name[4:]
            else:
                catchall = getattr(settings,
                    'CATCHALL_REDIRECT_HOSTNAME', None)
                # if catchall hostname is set, verify that the current
                # hostname is valid, and redirect if not
                if catchall and not Site.objects.filter(
                        domain=server_name).exists():
                    new_hostname = catchall
                else:
                    # either catchall is not set or current hostname is valid
                    return None
        new_location = '%s://%s%s' % (
            request.is_secure() and 'https' or 'http',
            new_hostname,
            request.get_full_path()
        )
        return HttpResponsePermanentRedirect(new_location)
