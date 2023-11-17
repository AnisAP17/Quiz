from django.forms import ValidationError
from accounts.models import CustomUser

from django.db import models
from django.db.models import (
    Model,
    PROTECT,
    CASCADE,
    CharField,
    TextField,
    DateField,
    IntegerField,
    SlugField,
    ForeignKey,
    DateTimeField,
    ImageField,
    BooleanField,
    PositiveSmallIntegerField,
    FloatField,
)

from django.urls import reverse
from threadlocals.threadlocals import get_thread_variable


class Category(Model):
    image = ImageField(
       verbose_name='изображение',
       upload_to='quiz/%Y/',
       blank=True,
   )
    title = CharField(
        verbose_name='название',
        max_length=150,
    )
    slug = SlugField(
        verbose_name='URL',
        unique=True,
    )
    description = TextField(
        verbose_name='описание',
        blank=True,
    )
    
    npp = PositiveSmallIntegerField(
        verbose_name='сортировка',
        default=0,
        blank=True
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
        user = get_thread_variable('user')
        if user.is_staff:
            return reverse('admin_category_view', args=[self.slug])
        else:
            return reverse('category_view', args=[self.slug])


class Quiz(Model):
    author = ForeignKey(
        CustomUser,
        on_delete=PROTECT,
        verbose_name='автор',
    )
    image = ImageField(
       verbose_name='изображение',
       upload_to='quiz/%Y/',
       blank=True,
   )
    title = CharField(
        verbose_name='название',
        max_length=150,
    )
    slug = SlugField(
        verbose_name='URL',
        unique=True,  # Ensure the slug is unique
    )
    description = TextField(
        verbose_name='описание',
        blank=True,
    )
    is_public = BooleanField(
        verbose_name='отображается на странице категории',
        default=True,
    )
    category = ForeignKey(
        Category,
        on_delete=PROTECT,
        verbose_name='категория',
    )
    created = DateTimeField(
        verbose_name='создан',
        auto_now_add=True,
    )
    modified = DateTimeField(
        verbose_name='изменен',
        auto_now=True,
    )
    date = DateField(
        verbose_name='дата',
        auto_now_add=True,
    )
    users_passed = IntegerField(
        verbose_name='количество прошедших пользователей',
        default=0,
    )
    npp = PositiveSmallIntegerField(
        verbose_name='сортировка',
        default=0,
    )
    time_limit = models.IntegerField(
        default=0,
        blank=True
        )  # Время в секундах

    def __str__(self):
        return self.title
    
    def has_timer(self):
        return self.time_limit > 0

    class Meta:
        db_table = 'quiz'
        verbose_name = 'тест'
        verbose_name_plural = 'тесты'
        
       # Removed the unique_together constraint as slug is already unique
       
        ordering = (
            'npp',
       )

    def get_absolute_url(self):
        user = get_thread_variable('user')
        if user.is_staff:
            return reverse(
                'admin_quiz_view',
                kwargs={
                    'quiz_slug': self.slug,
                    'category_slug': self.category.slug,
                }
            )
        else:
            return reverse(
                'quiz_view',
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
       verbose_name='вопрос',
       max_length=150,
   )
   full_text = TextField(
       verbose_name='описание вопроса',
       blank=True,
   )
   image = ImageField(
       verbose_name='изображение',
       upload_to='quiz/%Y/',
       blank=True,
   )

   def __str__(self):
       return self.question[:50]

   class Meta:
       db_table = 'questions'
       verbose_name = 'вопрос'
       verbose_name_plural = 'вопросы'
       
       
   def clean(self):
        if Question.objects.filter(quiz=self.quiz, question=self.question).exists():
            raise ValidationError("Такой вопрос уже существует в этом тесте.")


class Answer(Model):
   answer = CharField(
       verbose_name='ответ',
       max_length=150,
   )
   is_correct = BooleanField(
       verbose_name='правильный ответ',
       default=False,
   )
   comment = CharField(
       verbose_name='комментарий к ответу',
       max_length=200,
       blank=True,
   )
   question = ForeignKey(
       Question,
       on_delete=CASCADE,
       verbose_name='вопрос',
       blank=True
   )
   score = FloatField(
       verbose_name='баллы',
        default=0   
   )

   def __str__(self):
      return self.answer

   class Meta:
      db_table = 'answers'
      verbose_name = 'ответ'
      verbose_name_plural = 'ответы'


class UserAnswer(models.Model):

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answers = models.ManyToManyField(Answer, related_name='user_answers')
    correct_answer = models.ManyToManyField(Answer, blank=True, related_name='correct_user_answers')
    time_spent = models.IntegerField(default=0)  # Время в миллисекундах
    attempt_number = models.IntegerField(default=1)  # Новое поле для отслеживания номера попытки
    score = FloatField(default=0)

    def __str__(self): 
        answers = ", ".join(str(answer) for answer in self.answers.all())
        return f'{self.user.email}: {self.quiz.title}: {self.question.question}: {answers}'


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