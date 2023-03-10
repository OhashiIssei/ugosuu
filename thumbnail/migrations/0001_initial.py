# Generated by Django 4.1.1 on 2023-02-23 08:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('youtube', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ThumbnailUpdateSet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('videos', models.ManyToManyField(to='youtube.video')),
            ],
        ),
        migrations.CreateModel(
            name='ThumbnailContent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tex_text', models.TextField(null=True)),
                ('youtube_video', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='youtube.video')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Thumbnail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tex_text', models.TextField(null=True)),
                ('youtube_video', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='youtube.video')),
            ],
        ),
    ]
