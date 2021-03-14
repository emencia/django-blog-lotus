# Generated by Django 3.1.7 on 2021-03-14 13:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language', models.CharField(default='en', max_length=8, verbose_name='language')),
                ('title', models.CharField(default='', max_length=255, verbose_name='title')),
                ('slug', models.SlugField(max_length=255, verbose_name='slug')),
                ('description', models.TextField(blank=True, verbose_name='description')),
                ('cover', models.ImageField(blank=True, default='', max_length=255, upload_to='lotus/cover/%y/%m', verbose_name='image de couverture')),
                ('original', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='lotus.category')),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language', models.CharField(default='en', max_length=8, verbose_name='language')),
                ('title', models.CharField(default='', max_length=150, verbose_name='title')),
                ('slug', models.SlugField(max_length=255, verbose_name='slug')),
                ('content', models.TextField(blank=True, default='', verbose_name='content')),
                ('categories', models.ManyToManyField(blank=True, related_name='articles', to='lotus.Category', verbose_name='catégories')),
                ('original', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='lotus.article')),
            ],
            options={
                'verbose_name': 'Article',
                'verbose_name_plural': 'Articles',
                'ordering': ['title'],
            },
        ),
        migrations.AddConstraint(
            model_name='category',
            constraint=models.UniqueConstraint(fields=('title', 'language'), name='unique_category_title_for_lang'),
        ),
        migrations.AddConstraint(
            model_name='category',
            constraint=models.UniqueConstraint(fields=('slug', 'language'), name='unique_category_slug_for_lang'),
        ),
        migrations.AddConstraint(
            model_name='category',
            constraint=models.UniqueConstraint(fields=('original', 'language'), name='unique_category_original_for_lang'),
        ),
        migrations.AddConstraint(
            model_name='article',
            constraint=models.UniqueConstraint(fields=('title', 'language'), name='unique_article_title_for_lang'),
        ),
        migrations.AddConstraint(
            model_name='article',
            constraint=models.UniqueConstraint(fields=('slug', 'language'), name='unique_article_slug_for_lang'),
        ),
        migrations.AddConstraint(
            model_name='article',
            constraint=models.UniqueConstraint(fields=('original', 'language'), name='unique_article_original_for_lang'),
        ),
    ]
