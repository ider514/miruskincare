# Generated by Django 3.2.4 on 2021-06-27 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_carousel'),
    ]

    operations = [
        migrations.AddField(
            model_name='carousel',
            name='button',
            field=models.CharField(default='Click here', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='carousel',
            name='url',
            field=models.CharField(default='./', max_length=100),
            preserve_default=False,
        ),
    ]
