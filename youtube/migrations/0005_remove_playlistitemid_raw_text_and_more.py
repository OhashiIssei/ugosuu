# Generated by Django 4.1.1 on 2023-03-09 15:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('youtube', '0004_alter_playlistitemid_raw_text'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='playlistitemid',
            name='raw_text',
        ),
        migrations.AddField(
            model_name='playlistitemid',
            name='raw_text_100',
            field=models.CharField(default=1, max_length=100, unique=True),
            preserve_default=False,
        ),
    ]
