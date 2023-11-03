from django.contrib import admin
from django.contrib.admin import (
    ModelAdmin,
    TabularInline,
    register
)
from quiz.models import UserAnswer


from .models import (
    Category,
    Quiz,
    Question,
    Answer,
)

# Register your models here.

class AnswerTabularInline(TabularInline):
    model = Answer
    min_num = 2
    extra = 0


@register(Category)
class CategoryModelAdmin(ModelAdmin):
    prepopulated_fields = {
        'slug': ('title',)
    }


@register(Quiz)
class QuizModelAdmin( ModelAdmin):
    prepopulated_fields = {
        'slug': ('title',)
    }


@register(Question)
class QuestionModelAdmin(ModelAdmin):
    inlines = (
        AnswerTabularInline,
    )



@register(UserAnswer)
class UserAnswerModelAdmin(ModelAdmin):
    list_display = ('user', 'get_category', 'get_quiz', 'get_question', 'get_answers', 'get_correct', 'get_attempt', 'get_score')
    
    def get_score(self, obj):
        return obj.score
    
    get_score.short_description = 'Score'

    def get_question(self, obj):
        return obj.question.question

    get_question.short_description = 'Question'
    
    def get_category(self, obj):
        return obj.category.title
    
    get_category.short_description = 'Category'
    
    def get_quiz(self, obj):
        return obj.quiz.title

    get_quiz.short_description = 'Quiz'
    
    def get_answers(self, obj):
        return ", ".join([str(answer) for answer in obj.answers.all()])

    get_answers.short_description = 'User Answers'
    
    def get_time_spent(self, obj):
        return obj.time_spent
    
    get_time_spent.short_description = 'Time Spent'
    
    def get_attempt(self, obj):
        return obj.attempt_number
    
    get_attempt.short_description = 'Attempt Number'

    def get_correct(self, obj):
        return ", ".join([str(answer) for answer in obj.correct_answer.all()])

    get_correct.short_description = 'Correct Answer'