from os import path as os_path

from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import pre_delete

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

    tagged = models.ManyToManyField("Document", related_name="tags")

    def __unicode__(self):
        return self.title

class Lecturer(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    salutation = models.CharField(max_length=10)
    username = models.CharField(max_length=10)

    def get_full_name(self):
        return u'%s %s %s' % (self.salutation, self.first_name, self.last_name)

    def __unicode__(self):
        return get_full_name()

class LecturerAliases(models.Model):
    alias = models.CharField(max_length=100)
    lecturer = models.ForeignKey(Lecturer)

class Module(models.Model):
    short_code = models.CharField(max_length=10)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def get_complete_title(self):
        return u'%s - %s' % (self.short_code, self.title)

    def __unicode__(self):
        return self.get_complete_title()

class Document(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    author = models.ForeignKey(Lecturer, null=True)
    module = models.ForeignKey(Module, null=True)

    file = models.FileField(upload_to='documents/%Y/%m/%d', max_length=200)
    md5_sum = models.CharField(max_length=64, unique=True)

    extracted_content = models.TextField(blank=True, null=True)

    objects = Md5Manager()

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('serve_document', args=(self.id,))

    def get_api_url(self):
        return reverse('api_serve_document', args=(self.id,))

    def has_pdf(self):
        if os_path.splitext(self.file.name)[1].lower() == u'.pdf':
            return True
        elif len(self.packs.filter(type='pdf')):
            return True

        return False

    def has_pngs(self):
        if len(self.packs.filter(type='pngs')):
            return True

        return False

    def generate_md5_sum(self):
        self.md5_sum = generate_md5_sum(self.file)

    def admin_tags(self):
        result = ''
        for tag in list(self.tags.all())[:]:
            result += '%s, ' % tag.title
        #result += '%s' % list(self.tags.all())[-1].title
        return result
    admin_tags.short_description = 'Tags'

class DerivedPack(models.Model):
    type = models.CharField(max_length=20)

    derived_from = models.ForeignKey(Document, related_name='packs')

    class Meta:
        unique_together = ('type', 'derived_from',)

    def __unicode__(self):
        return '%s - derived from: %s' % (self.type, self.derived_from.title)

class DerivedFile(models.Model):

    def generate_filename(instance, file_name):
        path = instance.pack.derived_from.file.name
        dir, name = os_path.split(path)
        type = instance.pack.type
        file_name = type + '-' + str(instance.order) + os_path.splitext(file_name)[1]

        path = os_path.join(dir, 'derived_files', name, type, file_name)

        return path

    file = models.FileField(upload_to=generate_filename, max_length=200)
    md5_sum = models.CharField(max_length=64, unique=True)
    order = models.IntegerField(default=0)

    extracted_content = models.TextField(blank=True, null=True)

    pack = models.ForeignKey(DerivedPack, related_name='files')

    objects = Md5Manager()

    def get_absolute_url(self):
        return reverse('serve_document', args=(self.pack.derived_from.id,
            self.pack.type, self.order))

    def get_api_url(self):
        return reverse('api_serve_document', args=(self.pack.derived_from.id,
            self.pack.type, self.order))

    def __unicode__(self):
        return '%s - %s - derived from: %s' % (
            self.pack.type, self.order, self.pack.derived_from.title)

    def admin_image(self):
        if self.file.name.endswith('.png'):
            return u'<img width=300px src="%s"/>' % self.get_absolute_url()
        return u'No image'
    admin_image.allow_tags = True
    admin_image.short_description = 'Preview'

    def generate_md5_sum(self):
        self.md5_sum = generate_md5_sum(self.file)

pre_delete.connect(delete_file_on_model_delete, sender=DerivedFile)
pre_delete.connect(delete_file_on_model_delete, sender=Document)
