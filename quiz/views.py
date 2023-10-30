from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse

from quiz.models import Category, Quiz, Answer, UserAnswer
from django.db.models import Count
from django.contrib.auth.decorators import login_required
import random
from django.http import HttpResponse
from django.views import View


# Create your views here.
@login_required(login_url='login')
def index_view(request):
    categories = Category.objects.annotate(
        quiz_count=Count('quiz__id')
    ).filter(
        quiz_count__gte=1
    ).order_by('npp')

    if categories:
        context = {
            'title': 'Страница категориев',
            'categories': categories,
        }
        return render(request, 'quiz/index.html', context)
    else:
        return render(request, 'quiz/no_index.html')


def category_view(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    quizzes = Quiz.objects.filter(category=category, is_public=True).order_by('npp')

    if quizzes:
        context = {
            'title': f'Тесты по теме «{category.title}»',
            'category': category,
            'quizzes': quizzes,
        }
        return render(request, 'quiz/category.html', context=context)
    else:
        context = {
            'title1': f'В категории «{category.title}» нету тестов',
            'category': category,
            'quizzes': quizzes,
        }
        return render(request, 'quiz/no_category.html', context=context)


def quiz_view(request, category_slug, quiz_slug):
    quiz = get_object_or_404(
        Quiz,
        slug=quiz_slug,
        category__slug=category_slug,
    )
    questions = quiz.question_set.all().prefetch_related('answer_set')

    if request.method == 'POST':
        user = request.user
        for question in questions:
            user_answer = UserAnswer.objects.create(user=user, question=question)
            answer_ids = request.POST.getlist(str(question.id))
            user_answer.answers.set(answer_ids)  # Используйте .set() для ManyToMany полей

            # Определите правильные ответы для этого вопроса
            correct_answers = question.answer_set.filter(is_correct=True)
            for correct_answer in correct_answers:
                user_answer.correct_answer.add(correct_answer)  # Добавьте каждый правильный ответ в ManyToMany поле

            user_answer.save()

        return redirect('home')

    # Prepare the data for the template
    question_data = []
    for question in questions:
        question_data.append({
            'question': question,
            'answers': question.answer_set.all(),
            'is_multiple_choice': question.answer_set.filter(is_correct=True).count() > 1,
        })

    context = {
        'title': quiz.title,
        'question_data': question_data,
    }

    return render(request, 'quiz/quiz.html', context=context)



def viktorin(request):
    if request.method == 'POST':
        questions = request.session.get('questions')
        score = 0
        user_answers = []
        for question, answer in questions:
            user_answer = request.POST.get(question)
            if user_answer.lower() == answer.lower():
                score += 1
                result = 'Правильно'
            else:
                result = 'Неправильно'
            user_answers.append((question, user_answer, result))
        context = {'questions': questions, 'score': score, 'user_answers': user_answers}
    else:
        questions = [
            ('Вопрос 1', 'Ответ 1'),
            ('Вопрос 2', 'Ответ 2'),
            ('Вопрос 3', 'Ответ 3'),
            ('Вопрос 4', 'Ответ 4'),
            ('Вопрос 5', 'Ответ 5'),
            # добавьте сюда больше вопросов...
        ]
        random_questions = random.sample(questions, 5)
        request.session['questions'] = random_questions
        context = {'questions': random_questions}
    return render(request, 'quiz/viktorin.html', context)