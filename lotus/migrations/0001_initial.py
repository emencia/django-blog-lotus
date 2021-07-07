# Generated by Django 3.2.3 on 2021-07-07 00:19
# Edited to replace choices and default with some callable

import django.contrib.auth.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone

from ..choices import (
    get_language_choices, get_language_default,
    get_status_choices, get_status_default,
)


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=(settings.AUTH_USER_MODEL.lower(), models.Model),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language', models.CharField(choices=get_language_choices(), db_index=True, default=get_language_default(), max_length=8, verbose_name='language')),
                ('title', models.CharField(default='', max_length=255, verbose_name='title')),
                ('slug', models.SlugField(max_length=255, verbose_name='slug')),
                ('lead', models.TextField(blank=True, help_text='Lead paragraph, mostly used for SEO purposes in page metas.', verbose_name='lead')),
                ('description', models.TextField(blank=True, verbose_name='description')),
                ('cover', models.ImageField(blank=True, default='', max_length=255, upload_to='lotus/category/cover/%y/%m', verbose_name='cover image')),
                ('original', models.ForeignKey(blank=True, default=None, help_text='Mark this article as a translation of original article.', null=True, on_delete=django.db.models.deletion.CASCADE, to='lotus.category')),
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
                ('language', models.CharField(choices=get_language_choices(), db_index=True, default=get_language_default(), max_length=8, verbose_name='language')),
                ('status', models.SmallIntegerField(choices=get_status_choices(), db_index=True, default=get_status_default(), help_text='Publication status.', verbose_name='status')),
                ('featured', models.BooleanField(blank=True, default=False, help_text='Mark this article as featured.', verbose_name='featured')),
                ('pinned', models.BooleanField(blank=True, default=False, help_text='A pinned article is enforced at top of order results.', verbose_name='pinned')),
                ('private', models.BooleanField(blank=True, default=False, help_text='Private article is only available for authenticated users.', verbose_name='private')),
                ('publish_date', models.DateField(db_index=True, default=django.utils.timezone.now, help_text='Start date of publication.', verbose_name='publication date')),
                ('publish_time', models.TimeField(default=django.utils.timezone.now, help_text='Start time of publication.', verbose_name='publication time')),
                ('publish_end', models.DateTimeField(blank=True, db_index=True, default=None, help_text='End date of publication.', null=True, verbose_name='publication end')),
                ('last_update', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last update')),
                ('title', models.CharField(default='', max_length=150, verbose_name='title')),
                ('slug', models.SlugField(help_text="Used to build the entry's URL.", max_length=255, verbose_name='slug')),
                ('lead', models.TextField(blank=True, help_text='Lead paragraph, mostly used for SEO purposes in page metas.', verbose_name='lead')),
                ('introduction', models.TextField(blank=True, verbose_name='introduction')),
                ('content', models.TextField(blank=True, default='', verbose_name='content')),
                ('cover', models.ImageField(blank=True, default='', help_text='Article cover image.', max_length=255, upload_to='lotus/article/cover/%y/%m', verbose_name='cover image')),
                ('image', models.ImageField(blank=True, default='', help_text='Article large image.', max_length=255, upload_to='lotus/article/image/%y/%m', verbose_name='main image')),
                ('authors', models.ManyToManyField(blank=True, related_name='articles', to='lotus.Author', verbose_name='authors')),
                ('categories', models.ManyToManyField(blank=True, related_name='articles', to='lotus.Category', verbose_name='categories')),
                ('original', models.ForeignKey(blank=True, default=None, help_text='Mark this article as a translation of original article.', null=True, on_delete=django.db.models.deletion.CASCADE, to='lotus.article', verbose_name='original article')),
                ('related', models.ManyToManyField(blank=True, related_name='relations', to='lotus.Article', verbose_name='related articles')),
            ],
            options={
                'verbose_name': 'Article',
                'verbose_name_plural': 'Articles',
                'ordering': ['-publish_date', '-publish_time', '-title'],
            },
        ),
        migrations.AddConstraint(
            model_name='category',
            constraint=models.UniqueConstraint(fields=('slug', 'language'), name='lotus_unique_cat_slug_lang'),
        ),
        migrations.AddConstraint(
            model_name='category',
            constraint=models.UniqueConstraint(fields=('original', 'language'), name='lotus_unique_cat_original_lang'),
        ),
        migrations.AddConstraint(
            model_name='article',
            constraint=models.UniqueConstraint(fields=('publish_date', 'slug', 'language'), name='lotus_unique_art_pub_slug_lang'),
        ),
        migrations.AddConstraint(
            model_name='article',
            constraint=models.UniqueConstraint(fields=('original', 'language'), name='lotus_unique_art_original_lang'),
        ),
    ]
