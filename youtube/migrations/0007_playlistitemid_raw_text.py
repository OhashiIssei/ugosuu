# Generated by Django 4.1.1 on 2023-03-09 15:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('youtube', '0006_alter_playlistitemid_raw_text_100'),
    ]

    operations = [
        migrations.AddField(
            model_name='playlistitemid',
            name='raw_text',
            field=models.CharField(default=1, max_length=100, unique=True),
            preserve_default=False,
        ),
    ]
