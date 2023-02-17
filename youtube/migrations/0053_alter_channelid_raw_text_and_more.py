# Generated by Django 4.1.1 on 2023-02-16 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('youtube', '0052_videogenre_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='channelid',
            name='raw_text',
            field=models.CharField(max_length=30, unique=True),
        ),
        migrations.AlterField(
            model_name='channelsectionid',
            name='raw_text',
            field=models.CharField(max_length=30, unique=True),
        ),
        migrations.AlterField(
            model_name='playlistid',
            name='raw_text',
            field=models.CharField(max_length=30, unique=True),
        ),
        migrations.AlterField(
            model_name='videoid',
            name='raw_text',
            field=models.CharField(max_length=30, unique=True),
        ),
    ]
