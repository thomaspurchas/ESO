# Forms for the upload app.
from core.models import Document

from django import forms

class NewUploadForm(forms.Form):
    upload_file = forms.FileField(
        label='Upload a file',
        help_text='Carefull!'
    )

class UploadDetailForm(forms.Form):
    title = forms.CharField(max_length = 200, label='Title')
    author = forms.CharField(max_length = 100, label='Author', required=False)

class ApiDocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        exclude = ('md5_sum', 'title', 'description', 'author',
            'module', 'extracted_content')
