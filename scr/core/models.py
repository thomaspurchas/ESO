from django.db import models

# Create your models here.
class Document(models.model):
    title = models.CharField(max_length=200)
    description = models.TextField(required=False)
    author = models.ForeignKey(Lecturer)
    module = models.ForeighKey(Module)

    file = models.FileField(upload_to='document/%Y/%m/%d')

class Lecturer(models.model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    salutation = models.CharField(max_length=10)

class Module(models.model):
    short_code = models.CharField(max_length=10)
    title = models.CharField(max_length=200)
    description = models.TextField(required=False)
