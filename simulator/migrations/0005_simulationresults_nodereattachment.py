# Generated by Django 2.1.2 on 2019-12-28 23:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('simulator', '0004_auto_20191006_1748'),
    ]

    operations = [
        migrations.AddField(
            model_name='simulationresults',
            name='nodeReattachment',
            field=models.BooleanField(blank=True, default=True, null=True),
        ),
    ]
