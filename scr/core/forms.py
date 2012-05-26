from django.forms import ModelForm, CharField

from core.models import DerivedFile

# The model form for file uploads
class ApiDerivedFileUploadForm(ModelForm):
    class Meta:
        model = DerivedFile
        exclude = ('md5_sum', 'pack')
