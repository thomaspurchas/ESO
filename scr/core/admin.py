from core.models import Document, Tag, DerivedFile, DerivedPack
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

class DocumentAdmin(admin.ModelAdmin):
    search_fields = ['title', 'id']
    list_filter = ['author', 'module', 'tags']
    list_display = ['title', 'id', 'admin_tags','has_pdf', 'has_pngs']
    readonly_fields = ['md5_sum', 'has_pdf', 'has_pngs']

    inlines = [
        TaggedInline,
    ]

    actions = ['regenerate_pngs', 'regenerate_pdf', 'regenerate_both']
    def regenerate_pngs(modeladmin, request, queryset):
        for doc in queryset:
            packs = doc.packs.filter(type='pngs')
            if packs:
                packs[0].delete()

            create_pngs.delay(doc.id)

    regenerate_pngs.short_description = "Re-generate PNG's"

    def regenerate_pdf(modeladmin, request, queryset):
        for doc in queryset:
            packs = doc.packs.filter(type='pdf')
            if packs:
                packs[0].delete()

            create_pdf.delay(doc.id)

    regenerate_pdf.short_description = "Re-generate PDF's"

    def regenerate_both(modeladmin, request, queryset):
        for doc in queryset:
            packs = doc.packs.filter(type__in=['pdf', 'pngs'])
            if packs:
                packs[0].delete()

            create_pdf.delay(doc.id, callback=create_pngs.subtask((doc.id,)))

    regenerate_both.short_description = "Re-generate both PDF's and PNG's"

class TagAdmin(admin.ModelAdmin):
    filter_horizontal = ['tagged']

class DerivedFileAdmin(admin.ModelAdmin):
    readonly_fields = ['md5_sum', 'pack']
    search_fields = ['pack__derived_from__title', 'pack__type']
    list_display = ['__unicode__', 'order']
    readonly_fields = ['admin_image']
    raw_id_fields = ['pack']

class DerivedPackAdmin(admin.ModelAdmin):
    readonly_fields = ['derived_from']
    search_fields = ['type', 'derived_from__title']

admin.site.register(Document, DocumentAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(DerivedFile, DerivedFileAdmin)
admin.site.register(DerivedPack, DerivedPackAdmin)
