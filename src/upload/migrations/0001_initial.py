# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TempFile'
        db.create_table('upload_tempfile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('upload_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('md5_sum', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal('upload', ['TempFile'])


    def backwards(self, orm):
        # Deleting model 'TempFile'
        db.delete_table('upload_tempfile')


    models = {
        'upload.tempfile': {
            'Meta': {'object_name': 'TempFile'},
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'md5_sum': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'upload_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['upload']