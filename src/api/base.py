from tastypie.resources import ModelResource, ALL_WITH_RELATIONS
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.authentication import DigestAuthentication
from django.contrib.auth.models import User
from django.db import models
from tastypie.models import create_api_key
