# Generated by Django 4.1.1 on 2023-02-20 10:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ugosite', '0024_remove_myfile_path_article_path_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['id']},
        ),
        migrations.AlterField(
            model_name='category',
            name='description',
            field=models.TextField(blank=True, max_length=10000),
        ),
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(default='name', max_length=200),
        ),
        migrations.AlterField(
            model_name='category',
            name='parent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='ugosite.category'),
        ),
        migrations.AlterField(
            model_name='category',
            name='type',
            field=models.CharField(choices=[('SUB', '科目'), ('CHA', '章'), ('SEC', '節'), ('SSE', '分節'), ('TER', 'テーマ'), ('OTH', 'その他')], default='OTH', max_length=200),
        ),
        migrations.AlterField(
            model_name='problem',
            name='answer',
            field=models.TextField(blank=True, max_length=10000, null=True, verbose_name='example_answer'),
        ),
        migrations.AlterField(
            model_name='problem',
            name='articles',
            field=models.ManyToManyField(to='ugosite.article'),
        ),
        migrations.AlterField(
            model_name='problem',
            name='name',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='problem',
            name='source',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='problem',
            name='text',
            field=models.TextField(max_length=1000),
        ),
        migrations.AlterField(
            model_name='question',
            name='answer',
            field=models.TextField(blank=True, max_length=10000, null=True, verbose_name='example_answer'),
        ),
        migrations.AlterField(
            model_name='question',
            name='name',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='question',
            name='source',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='question',
            name='text',
            field=models.TextField(max_length=1000),
        ),
        migrations.DeleteModel(
            name='Source',
        ),
    ]