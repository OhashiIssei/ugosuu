# Generated by Django 4.1.1 on 2023-02-17 02:54

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('ugosite', '0023_alter_category_options_remove_myfile_created_date_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='myfile',
            name='path',
        ),
        migrations.AddField(
            model_name='article',
            name='path',
            field=models.CharField(blank=True, default='/', max_length=200),
        ),
        migrations.AlterField(
            model_name='article',
            name='created_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='article',
            name='description',
            field=models.TextField(blank=True, max_length=1000),
        ),
        migrations.AlterField(
            model_name='article',
            name='name',
            field=models.CharField(default='name', max_length=200),
        ),
        migrations.AlterField(
            model_name='article',
            name='parent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ugosite.category'),
        ),
        migrations.AlterField(
            model_name='article',
            name='type',
            field=models.CharField(choices=[('BAS', '基本'), ('STU', '研究'), ('DEV', '発展'), ('SUP', '補足'), ('PRA', '演習'), ('TER', 'テーマ'), ('CAT', 'カテゴリ'), ('NOT', 'ノート'), ('OTH', 'その他')], default='OTH', max_length=200),
        ),
        migrations.AlterField(
            model_name='article',
            name='update_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]