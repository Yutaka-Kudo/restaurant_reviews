# Generated by Django 3.2 on 2021-05-22 04:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scrape', '0012_alter_media_data_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='media_data',
            name='url',
            field=models.URLField(blank=True, max_length=1000, null=True),
        ),
    ]
