from django.db import models

# Create your models here.
class Lecturer(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    salutation = models.CharField(max_length=10)
    username = models.CharField(max_length=10)

class LecturerAliases(models.Model):
    alias = models.CharField(max_length=100)
    lecturer = models.ForeignKey(Lecturer)

class Module(models.Model):
    short_code = models.CharField(max_length=10)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

class Document(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    author = models.ForeignKey(Lecturer, null=True)
    module = models.ForeignKey(Module, null=True)

    file = models.FileField(upload_to='document/%Y/%m/%d')
