from core.models import Page, Tag, Email, Site
from convert.tasks import create_pngs, create_pdf

from tastypie.admin import ApiKeyInline
from tastypie.models import ApiAccess, ApiKey

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib import admin

admin.site.register(ApiKey)
admin.site.register(ApiAccess)

class UserModelAdmin(UserAdmin):
    inlines = [ApiKeyInline]

admin.site.unregister(User)
admin.site.register(User,UserModelAdmin)

class TaggedInline(admin.TabularInline):
    model = Tag.tagged.through

class PageAdmin(admin.ModelAdmin):

    inlines = [
        TaggedInline,
    ]

class TagAdmin(admin.ModelAdmin):
    filter_horizontal = ['tagged']

admin.site.register(Page, PageAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Email)
admin.site.register(Site)