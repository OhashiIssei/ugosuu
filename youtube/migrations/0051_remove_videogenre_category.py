# Generated by Django 4.1.1 on 2023-02-08 12:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('youtube', '0050_videogenre_category'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='videogenre',
            name='category',
        ),
    ]
