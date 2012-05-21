from os import path as os_path

from django.db import models

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
class Lecturer(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    salutation = models.CharField(max_length=10)
    username = models.CharField(max_length=10)

    def get_full_name():
        return u'%s %s %s' % self.salutation, self.first_name, self.last_name

    def __unicode__():
        return get_full_name()

class LecturerAliases(models.Model):
    alias = models.CharField(max_length=100)
    lecturer = models.ForeignKey(Lecturer)

class Module(models.Model):
    short_code = models.CharField(max_length=10)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def get_complete_title():
        return u'%s - %s' % self.short_code, self.title

    def __unicode__():
        return self.get_complete_title()

class Document(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    author = models.ForeignKey(Lecturer, null=True)
    module = models.ForeignKey(Module, null=True)

    file = models.FileField(upload_to='documents/%Y/%m/%d')
    md5_sum = models.CharField(max_length=64, unique=True)

    objects = Md5Manager()

    def get_absolute_url(self):
        return "/document/%i/" % self.id

class DerivedPack(models.Model):
    type = models.CharField(max_length=20)

    derived_from = models.ForeignKey(Document, related_name='packs')

    class Meta:
        unique_together = ('type', 'derived_from',)

class DerivedFile(models.Model):

    def generate_filename(instance, file_name):
        path = instance.pack.derived_from.file.path
        dir, name = os_path.split(path)
        type = instance.pack.type

        path = os_path.join(dir, 'derived_files', name, type, file_name)

        return path

    file = models.FileField(upload_to=generate_filename)
    md5_sum = models.CharField(max_length=64, unique=True)
    order = models.IntegerField(default=0)

    pack = models.ForeignKey(DerivedPack, related_name='files')

    objects = Md5Manager()
