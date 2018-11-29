# Generated by Django 2.1.2 on 2018-11-29 16:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SimulationResults',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted', models.DateTimeField(editable=False, null=True)),
                ('num_process', models.IntegerField(default=1)),
                ('transactions', models.IntegerField(default=10)),
                ('alpha', models.FloatField(default=1)),
                ('randomness', models.FloatField(default=1)),
                ('algorithm', models.CharField(blank=True, help_text='A short description of the simulation', max_length=10)),
                ('reference', models.TextField(blank=True, help_text='A short description of the simulation')),
                ('tangle', models.TextField(blank=True, help_text='The tangle result from the simulation')),
                ('status', models.CharField(blank=True, help_text='Status of the simulation', max_length=20)),
                ('image', models.ImageField(blank=True, null=True, upload_to='result_images')),
                ('created', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(null=True)),
                ('user', models.ForeignKey(editable=False, help_text='User who created the simulation', null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Created by user')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
