# Generated by Django 4.1.1 on 2023-03-09 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('youtube', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlaylistItemId',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('raw_text', models.CharField(max_length=50, unique=True)),
            ],
        ),
    ]