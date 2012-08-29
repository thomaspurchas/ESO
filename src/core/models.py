from os import path as os_path
import os

from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import pre_delete
from django.conf import settings

from file_management import delete_file_on_model_delete, generate_md5_sum

class Email(models.Model):
    email = models.CharField(max_length=50)

    def __unicode__(self):
        return self.email

# MD5 manager. Provides a method to check for any file with the same md5 sum
# as the one provided against the provided models in addition to the current model.
class Md5Manager(models.Manager):
    def unique_md5(self, md5_sum, models):
        # Currently very crude, it expects the models to have an md5_sum attribute
        if self.filter(md5_sum = md5_sum):
            return False

        for model in models:
            if model.objects.filter(md5_sum = md5_sum):
                return False

        return True

# Create your models here.
class Tag(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    tagged = models.ManyToManyField("Page", related_name="tags")

    def __unicode__(self):
        return self.title

class Site(models.Model):
    title = models.CharField(max_length=200)
    domain = models.CharField(max_length=200)

    def __unicode__(self):
        return self.title

class Page(models.Model):
    url = models.CharField(max_length=500)
    site = models.ForeignKey(Site, null=True)

    body = models.TextField(blank=True, null=True)
    head = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return self.url

    def get_absolute_url(self):
        return reverse('serve_document', args=(self.id,))

    def get_preview_url(self):
        return reverse('preview', args=(self.id,))

    def get_api_url(self):
        return reverse('api_serve_document', args=(self.id,))

    def admin_tags(self):
        result = ''
        for tag in list(self.tags.all())[:]:
            result += '%s, ' % tag.title
        #result += '%s' % list(self.tags.all())[-1].title
        return result
    admin_tags.short_description = 'Tags'
