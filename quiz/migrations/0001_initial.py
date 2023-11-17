# Generated by Django 4.2.6 on 2023-11-15 04:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.CharField(max_length=150, verbose_name='ответ')),
                ('is_correct', models.BooleanField(default=False, verbose_name='правильный ответ')),
                ('comment', models.CharField(blank=True, max_length=200, verbose_name='комментарий к ответу')),
                ('score', models.FloatField(default=0, verbose_name='баллы')),
            ],
            options={
                'verbose_name': 'ответ',
                'verbose_name_plural': 'ответы',
                'db_table': 'answers',
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, upload_to='quiz/%Y/', verbose_name='изображение')),
                ('title', models.CharField(max_length=150, verbose_name='название')),
                ('slug', models.SlugField(unique=True, verbose_name='URL')),
                ('description', models.TextField(blank=True, verbose_name='описание')),
                ('npp', models.PositiveSmallIntegerField(blank=True, default=0, verbose_name='сортировка')),
            ],
            options={
                'verbose_name': 'категория',
                'verbose_name_plural': 'категории',
                'db_table': 'categories',
                'ordering': ('npp',),
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=150, verbose_name='вопрос')),
                ('full_text', models.TextField(blank=True, verbose_name='описание вопроса')),
                ('image', models.ImageField(blank=True, upload_to='quiz/%Y/', verbose_name='изображение')),
            ],
            options={
                'verbose_name': 'вопрос',
                'verbose_name_plural': 'вопросы',
                'db_table': 'questions',
            },
        ),
        migrations.CreateModel(
            name='Quiz',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, upload_to='quiz/%Y/', verbose_name='изображение')),
                ('title', models.CharField(max_length=150, verbose_name='название')),
                ('slug', models.SlugField(unique=True, verbose_name='URL')),
                ('description', models.TextField(blank=True, verbose_name='описание')),
                ('is_public', models.BooleanField(default=True, verbose_name='отображается на странице категории')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='создан')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='изменен')),
                ('date', models.DateField(auto_now_add=True, verbose_name='дата')),
                ('users_passed', models.IntegerField(default=0, verbose_name='количество прошедших пользователей')),
                ('npp', models.PositiveSmallIntegerField(default=0, verbose_name='сортировка')),
                ('time_limit', models.IntegerField(blank=True, default=0)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='автор')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='quiz.category', verbose_name='категория')),
            ],
            options={
                'verbose_name': 'тест',
                'verbose_name_plural': 'тесты',
                'db_table': 'quiz',
                'ordering': ('npp',),
            },
        ),
        migrations.CreateModel(
            name='UserAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_spent', models.IntegerField(default=0)),
                ('attempt_number', models.IntegerField(default=1)),
                ('score', models.FloatField(default=0)),
                ('answers', models.ManyToManyField(related_name='user_answers', to='quiz.answer')),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='quiz.category')),
                ('correct_answer', models.ManyToManyField(blank=True, related_name='correct_user_answers', to='quiz.answer')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.question')),
                ('quiz', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.quiz')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='question',
            name='quiz',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.quiz', verbose_name='тест'),
        ),
        migrations.AddField(
            model_name='answer',
            name='question',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='quiz.question', verbose_name='вопрос'),
        ),
    ]
