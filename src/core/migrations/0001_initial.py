# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Lecturer'
        db.create_table('core_lecturer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('salutation', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=10)),
        ))
        db.send_create_signal('core', ['Lecturer'])

        # Adding model 'LecturerAliases'
        db.create_table('core_lectureraliases', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('alias', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('lecturer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Lecturer'])),
        ))
        db.send_create_signal('core', ['LecturerAliases'])

        # Adding model 'Module'
        db.create_table('core_module', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('short_code', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('core', ['Module'])

        # Adding model 'Document'
        db.create_table('core_document', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Lecturer'], null=True)),
            ('module', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Module'], null=True)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('md5_sum', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal('core', ['Document'])


    def backwards(self, orm):
        # Deleting model 'Lecturer'
        db.delete_table('core_lecturer')

        # Deleting model 'LecturerAliases'
        db.delete_table('core_lectureraliases')

        # Deleting model 'Module'
        db.delete_table('core_module')

        # Deleting model 'Document'
        db.delete_table('core_document')


    models = {
        'core.document': {
            'Meta': {'object_name': 'Document'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Lecturer']", 'null': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'md5_sum': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
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