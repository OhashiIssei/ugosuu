# Generated by Django 4.1.1 on 2023-02-23 08:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ugosite', '0002_delete_newcategory_remove_article_parent_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='chapter',
            old_name='parent_subject',
            new_name='subject',
        ),
        migrations.RenameField(
            model_name='section',
            old_name='parent_chapter',
            new_name='chapter',
        ),
        migrations.RenameField(
            model_name='subject',
            old_name='parent_category',
            new_name='category',
        ),
        migrations.RenameField(
            model_name='subsection',
            old_name='parent_section',
            new_name='section',
        ),
    ]
