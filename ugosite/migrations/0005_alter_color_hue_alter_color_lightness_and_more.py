# Generated by Django 4.1.1 on 2022-11-24 09:23

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ugosite', '0004_color'),
    ]

    operations = [
        migrations.AlterField(
            model_name='color',
            name='hue',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(255)]),
        ),
        migrations.AlterField(
            model_name='color',
            name='lightness',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(255)]),
        ),
        migrations.AlterField(
            model_name='color',
            name='saturation',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(255)]),
        ),
    ]
