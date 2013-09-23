# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Webhook'
        db.create_table('webhook', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('event', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'webhooks', ['Webhook'])

        # Adding unique constraint on 'Webhook', fields ['event', 'url']
        db.create_unique('webhook', ['event', 'url'])


    def backwards(self, orm):
        # Removing unique constraint on 'Webhook', fields ['event', 'url']
        db.delete_unique('webhook', ['event', 'url'])

        # Deleting model 'Webhook'
        db.delete_table('webhook')


    models = {
        u'webhooks.webhook': {
            'Meta': {'unique_together': "(('event', 'url'),)", 'object_name': 'Webhook', 'db_table': "'webhook'"},
            'event': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['webhooks']