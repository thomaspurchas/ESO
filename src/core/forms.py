from django.forms import ModelForm, CharField

from core.models import Email

class PostEmail(ModelForm):
    class Meta:
        model = Email
