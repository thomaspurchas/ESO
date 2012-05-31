# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding unique constraint on 'Document', fields ['md5_sum']
        db.create_unique('core_document', ['md5_sum'])

        # Adding unique constraint on 'DerivedPack', fields ['type', 'derived_from']
        db.create_unique('core_derivedpack', ['type', 'derived_from_id'])

        # Adding unique constraint on 'DerivedFile', fields ['md5_sum']
        db.create_unique('core_derivedfile', ['md5_sum'])


    def backwards(self, orm):
        # Removing unique constraint on 'DerivedFile', fields ['md5_sum']
        db.delete_unique('core_derivedfile', ['md5_sum'])

        # Removing unique constraint on 'DerivedPack', fields ['type', 'derived_from']
        db.delete_unique('core_derivedpack', ['type', 'derived_from_id'])

        # Removing unique constraint on 'Document', fields ['md5_sum']
        db.delete_unique('core_document', ['md5_sum'])


    models = {
        'core.derivedfile': {
            'Meta': {'object_name': 'DerivedFile'},
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'md5_sum': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'pack': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'files'", 'to': "orm['core.DerivedPack']"})
        },
        'core.derivedpack': {
            'Meta': {'unique_together': "(('type', 'derived_from'),)", 'object_name': 'DerivedPack'},
            'derived_from': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'packs'", 'to': "orm['core.Document']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'core.document': {
            'Meta': {'object_name': 'Document'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Lecturer']", 'null': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'md5_sum': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'module': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Module']", 'null': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'core.lecturer': {
            'Meta': {'object_name': 'Lecturer'},
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'salutation': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'core.lectureraliases': {
            'Meta': {'object_name': 'LecturerAliases'},
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lecturer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Lecturer']"})
        },
        'core.module': {
            'Meta': {'object_name': 'Module'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'short_code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['core']