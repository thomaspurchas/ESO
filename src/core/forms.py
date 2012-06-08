from django.forms import ModelForm, CharField

from core.models import DerivedFile, Email

class PostEmail(ModelForm):
    class Meta:
        model = Email

# The model form for file uploads
class ApiDerivedFileUploadForm(ModelForm):
    class Meta:
        model = DerivedFile
        exclude = ('md5_sum', 'pack')
