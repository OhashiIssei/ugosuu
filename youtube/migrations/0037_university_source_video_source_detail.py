# Generated by Django 4.1.1 on 2023-01-31 05:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('youtube', '0036_video_thumbnail_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='University',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default=None, max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Source',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default=None, max_length=200)),
                ('year', models.DateField()),
                ('university', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='youtube.university')),
            ],
        ),
        migrations.AddField(
            model_name='video',
            name='source_detail',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='youtube.source'),
        ),
    ]
