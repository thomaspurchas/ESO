from django.db import models

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
    md5_sum = models.CharField(max_length=64)

    def get_absolute_url(self):
        return "/document/%i/" % self.id
