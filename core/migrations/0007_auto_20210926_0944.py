# Generated by Django 2.2.14 on 2021-09-26 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20210907_0342'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carousel',
            name='button',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='carousel',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='carousel',
            name='url',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
