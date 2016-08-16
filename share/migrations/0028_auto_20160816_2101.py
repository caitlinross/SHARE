# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-16 21:01
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager
import mptt.fields
import share.models.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('share', '0027_auto_20160815_2205'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.TextField()),
                ('long_name', models.TextField()),
                ('synonyms', models.TextField()),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='share.Subject')),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('_default_manager', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='ThroughSubjects',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('change', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='affected_throughsubjects', to='share.Change')),
            ],
        ),
        migrations.CreateModel(
            name='ThroughSubjectsVersion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.TextField(max_length=10)),
                ('persistent_id', models.PositiveIntegerField()),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('change', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='affected_throughsubjectsversion', to='share.Change')),
            ],
        ),
        migrations.RemoveField(
            model_name='abstractcreativework',
            name='subject',
        ),
        migrations.RemoveField(
            model_name='abstractcreativework',
            name='subject_version',
        ),
        migrations.RemoveField(
            model_name='abstractcreativeworkversion',
            name='subject',
        ),
        migrations.RemoveField(
            model_name='abstractcreativeworkversion',
            name='subject_version',
        ),
        migrations.AlterField(
            model_name='venue',
            name='name',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='venueversion',
            name='name',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='throughsubjectsversion',
            name='creative_work',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='share.AbstractCreativeWork'),
        ),
        migrations.AddField(
            model_name='throughsubjectsversion',
            name='creative_work_version',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='share.AbstractCreativeWorkVersion'),
        ),
        migrations.AddField(
            model_name='throughsubjectsversion',
            name='extra',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='share.ExtraData'),
        ),
        migrations.AddField(
            model_name='throughsubjectsversion',
            name='extra_version',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='share.ExtraDataVersion'),
        ),
        migrations.AddField(
            model_name='throughsubjectsversion',
            name='same_as',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='share.ThroughSubjects'),
        ),
        migrations.AddField(
            model_name='throughsubjectsversion',
            name='same_as_version',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='share.ThroughSubjectsVersion'),
        ),
        migrations.AddField(
            model_name='throughsubjectsversion',
            name='sources',
            field=models.ManyToManyField(related_name='source_throughsubjectsversion', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='throughsubjectsversion',
            name='subject',
            field=mptt.fields.TreeForeignKey(on_delete=django.db.models.deletion.CASCADE, to='share.Subject'),
        ),
        migrations.AddField(
            model_name='throughsubjects',
            name='creative_work',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='share.AbstractCreativeWork'),
        ),
        migrations.AddField(
            model_name='throughsubjects',
            name='creative_work_version',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='share.AbstractCreativeWorkVersion'),
        ),
        migrations.AddField(
            model_name='throughsubjects',
            name='extra',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='share.ExtraData'),
        ),
        migrations.AddField(
            model_name='throughsubjects',
            name='extra_version',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='share.ExtraDataVersion'),
        ),
        migrations.AddField(
            model_name='throughsubjects',
            name='same_as',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='share.ThroughSubjects'),
        ),
        migrations.AddField(
            model_name='throughsubjects',
            name='same_as_version',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='share.ThroughSubjectsVersion'),
        ),
        migrations.AddField(
            model_name='throughsubjects',
            name='sources',
            field=models.ManyToManyField(related_name='source_throughsubjects', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='throughsubjects',
            name='subject',
            field=mptt.fields.TreeForeignKey(on_delete=django.db.models.deletion.CASCADE, to='share.Subject'),
        ),
        migrations.AddField(
            model_name='throughsubjects',
            name='version',
            field=models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='share_throughsubjects_version', to='share.ThroughSubjectsVersion'),
        ),
        migrations.AddField(
            model_name='abstractcreativework',
            name='subjects',
            field=share.models.fields.TypedManyToManyField(related_name='subjected_abstractcreativeworkversion', through='share.ThroughSubjects', to='share.Subject'),
        ),
        migrations.AddField(
            model_name='abstractcreativeworkversion',
            name='subjects',
            field=share.models.fields.TypedManyToManyField(related_name='subjected_abstractcreativeworkversion', through='share.ThroughSubjects', to='share.Subject'),
        ),
    ]
