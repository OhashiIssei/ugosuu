# Generated by Django 4.1.1 on 2022-12-07 05:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ugosite', '0012_remove_question_articles_alter_problem_articles_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='YoutubeVideoUpdateSet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('videos', models.ManyToManyField(to='ugosite.youtubevideo')),
            ],
        ),
    ]
