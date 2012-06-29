from django.http import HttpResponsePermanentRedirect

from hostname_redirects.models import RedirectHost


class HostnameRedirectMiddleware(object):
    def process_request(self, request):
        server_name = request.META['SERVER_NAME']
        try:
            rh = RedirectHost.objects.select_related('site').get(hostname=server_name)
        except RedirectHost.DoesNotExist:
            return None
        new_location = '%s://%s%s' % (
            request.is_secure() and 'https' or 'http',
            rh.site.domain,
            request.get_full_path()
        )
        return HttpResponsePermanentRedirect(new_location)
