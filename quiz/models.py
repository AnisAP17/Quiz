from accounts.models import CustomUser

from django.db import models
from django.db.models import (
    Model,
    PROTECT,
    CASCADE,
    CharField,
    TextField,
    SlugField,
    ForeignKey,
    DateTimeField,
    ImageField,
    BooleanField,
    PositiveSmallIntegerField,
)

from django.urls import reverse


class Category(Model):
    title = CharField(
        'название',
        max_length=150,
    )
    slug = SlugField(
        'URL',
        unique=True,
    )
    description = TextField(
        'описание',
        blank=True,
    )
    npp = PositiveSmallIntegerField(
        'сортировка',
        default=0,
    )

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'categories'
        verbose_name = 'категория'
        verbose_name_plural = 'категории'
        ordering = (
            'npp',
        )

    def get_absolute_url(self):
        return reverse(
            'category',
            kwargs={
                'category_slug': self.slug,
            }
        )


class Quiz(Model):
    author = ForeignKey(
        CustomUser,
        on_delete=PROTECT,
        verbose_name='автор',
    )
    title = CharField(
        'название',
        max_length=150,
    )
    slug = SlugField(
        'URL',
        unique=True,  # Ensure the slug is unique
    )
    description = TextField(
        'описание',
        blank=True,
    )
    is_public = BooleanField(
        'отображается на странице категории',
        default=True,
    )
    category = ForeignKey(
        Category,
        on_delete=PROTECT,
        verbose_name='категория',
    )
    created = DateTimeField(
        'создан',
        auto_now_add=True,
    )
    modified = DateTimeField(
        'изменен',
        auto_now=True,
    )
    npp = PositiveSmallIntegerField(
        'сортировка',
        default=0,
    )

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'quiz'
        verbose_name = 'тест'
        verbose_name_plural = 'тесты'
        
       # Removed the unique_together constraint as slug is already unique
       
        ordering = (
            'npp',
       )

    def get_absolute_url(self):
       return reverse(
           'quiz',
           kwargs={
               'quiz_slug': self.slug,
               'category_slug': self.category.slug,
           }
       )


class Question(Model):
   quiz = ForeignKey(
       Quiz,
       on_delete=CASCADE,
       verbose_name='тест',
   )
   question = CharField(
       'вопрос',
       max_length=150,
   )
   full_text = TextField(
       'описание вопроса',
       blank=True,
   )
   image = ImageField(
       'изображение',
       upload_to='quiz/%Y/',
       blank=True,
   )

   def __str__(self):
       return self.question[:50]

   class Meta:
       db_table = 'questions'
       verbose_name = 'вопрос'
       verbose_name_plural = 'вопросы'


class Answer(Model):
   answer = CharField(
       'ответ',
       max_length=150,
   )
   is_correct = BooleanField(
       'правильный ответ',
       default=False,
   )
   comment = CharField(
       'комментарий к ответу',
       max_length=200,
       blank=True,
   )
   question = ForeignKey(
       Question,
       on_delete=CASCADE,
       verbose_name='вопрос',
   )

   def __str__(self):
      return self.answer

   class Meta:
      db_table = 'answers'
      verbose_name = 'ответ'
      verbose_name_plural = 'ответы'


class UserAnswer(models.Model):

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answers = models.ManyToManyField(Answer, related_name='user_answers')
    correct_answer = models.ManyToManyField(Answer, blank=True, related_name='correct_user_answers')

    def __str__(self):
        answers = ", ".join(str(answer) for answer in self.answers.all())
        return f'{self.user.username}: {self.question.question}: {answers}'


    def save(self, *args, **kwargs):
        if not self.pk:
            # Это новый объект, поэтому нужно создать связи
            super(UserAnswer, self).save(*args, **kwargs)
            # Получить правильные ответы для этого вопроса
            correct_answers = Answer.objects.filter(question=self.question, is_correct=True)
            for answer in correct_answers:
                self.correct_answer.add(answer)
        else:
            super(UserAnswer, self).save(*args, **kwargs)