# Generated by Django 4.1.1 on 2022-11-28 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ugosite', '0005_alter_color_hue_alter_color_lightness_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='youtubevideo',
            name='new_data',
            field=models.JSONField(blank=True, help_text='補正後のデータです。', null=True),
        ),
    ]
