from django.db import models

# Create your models here.
class TempFile(models.Model):
    file = models.FileField(upload_to='upload-temp')
    name = models.CharField(max_length=200)
    upload_time = models.DateTimeField(auto_now_add=True)
    md5_sum = models.CharField(max_length=64)
