# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Tag'
        db.create_table('core_tag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('core', ['Tag'])

        # Adding M2M table for field tagged on 'Tag'
        db.create_table('core_tag_tagged', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('tag', models.ForeignKey(orm['core.tag'], null=False)),
            ('document', models.ForeignKey(orm['core.document'], null=False))
        ))
        db.create_unique('core_tag_tagged', ['tag_id', 'document_id'])


    def backwards(self, orm):
        # Deleting model 'Tag'
        db.delete_table('core_tag')

        # Removing M2M table for field tagged on 'Tag'
        db.delete_table('core_tag_tagged')


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
        },
        'core.tag': {
            'Meta': {'object_name': 'Tag'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tagged': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'tags'", 'symmetrical': 'False', 'to': "orm['core.Document']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['core']