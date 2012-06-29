from django.db import models
from django.contrib.sites.models import Site


class RedirectHost(models.Model):
    hostname = models.CharField(max_length=100, unique=True)
    site = models.ForeignKey(Site)

    class Meta:
        ordering = ['hostname']

    def __unicode__(self):
        return '%s (to %s)' % (self.hostname, self.site.domain)
