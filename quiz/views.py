from django.shortcuts import render, get_object_or_404, redirect
from .forms import QuestionFormSet
from quiz.models import Category, Quiz, Answer, UserAnswer, Question
from django.db.models import Count
from django.contrib.auth.decorators import login_required
import random
from django.contrib import messages

# Create your views here.
@login_required(login_url='login')
def index_view(request):
    categories = Category.objects.all() \
    .annotate(
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

    quizzes_with_questions = []
    for quiz in quizzes:
        if quiz.question_set.exists():  # Проверка на наличие вопросов в тесте
            quiz.unique_users_passed = UserAnswer.objects.filter(quiz=quiz).values('user__email').distinct().count()
            quizzes_with_questions.append(quiz)

    if quizzes_with_questions:
        context = {
            'title': f'Тесты по теме «{category.title}»',
            'category': category,
            'quizzes': quizzes_with_questions,
        }
        return render(request, 'quiz/category.html', context=context)
    else:
        context = {
            'title1': f'В категории «{category.title}» нету тестов',
            'category': category,
        }
        return render(request, 'quiz/no_category.html', context=context)


def quiz_view(request, category_slug, quiz_slug):
    quiz = get_object_or_404(Quiz, slug=quiz_slug, category__slug=category_slug)
    questions = quiz.question_set.all().prefetch_related('answer_set')

    if not questions.exists():
        return render(request, 'no_questions.html')

    skipped_questions = request.session.get('skipped_questions', [])

    if 'id' in request.session:
        id = request.session['id']
        question = questions.filter(id__gt=id).order_by('id').first()
        if question is None:
            if skipped_questions:
                question_id = skipped_questions[0]
                question = questions.get(id=question_id)
            else:
                del request.session['id']
                return redirect('results')
    else:
        question = questions.first()

    if request.method == 'POST':
        if 'skip' in request.POST:
            if question.id not in skipped_questions:
                skipped_questions.append(question.id)
                request.session['skipped_questions'] = skipped_questions
            else:
                messages.error(request, 'Вы уже пропустили этот вопрос.')
            request.session['id'] = question.id
            request.session.modified = True  # Добавлено здесь
            return redirect('quiz', category_slug=category_slug, quiz_slug=quiz_slug)

        answer_ids = request.POST.getlist('answer')
        if not answer_ids:
            return render(request, 'no_answer.html')

        user_answer, created = UserAnswer.objects.get_or_create(user=request.user, question=question, quiz=quiz, category=quiz.category)
        user_answer.answers.set(answer_ids)
        if not created:
            user_answer.attempt_number += 1
        user_answer.save()

        correct_answers = question.answer_set.filter(is_correct=True)
        incorrect_answers = question.answer_set.filter(is_correct=False)
        user_answers = user_answer.answers.all()
        correct_user_answers = set(user_answers).intersection(set(correct_answers))
        incorrect_user_answers = set(user_answers).intersection(set(incorrect_answers))

        points = sum(answer.score for answer in correct_user_answers)
        user_answer.score = points

        if incorrect_user_answers:
            penalty = sum(answer.score for answer in incorrect_user_answers)
            user_answer.score -= penalty

        user_answer.save()

        if question.id in skipped_questions:
            skipped_questions.remove(question.id)
            request.session['skipped_questions'] = skipped_questions

        request.session['id'] = question.id
        request.session.modified = True  # Добавлено здесь
        return redirect('quiz', category_slug=category_slug, quiz_slug=quiz_slug)

    correct_answers_count = question.answer_set.filter(is_correct=True).count()

    context = {
        'title': quiz.title,
        'question': question,
        'answers': question.answer_set.all(),
        'time_limit': quiz.time_limit,
        'is_multiple_choice': correct_answers_count > 1,
    }

    return render(request, 'quiz/quiz.html', context=context)





# def quiz_view(request, category_slug, quiz_slug):
#     quiz = get_object_or_404(Quiz, slug=quiz_slug, category__slug=category_slug)
#     questions = quiz.question_set.all().prefetch_related('answer_set')

#     if request.method == 'POST':
#         formset = QuestionFormSet(request.POST)
#         if formset.is_valid():
#             for form in formset:
#                 form.save()
                
#         user = request.user
#         time_spent = request.POST.get('time_spent', 0)
#         if time_spent.isdigit():
#             time_spent = int(time_spent)
#         else:
#             time_spent = 0

#         for question in questions:
#             answer_ids = request.POST.getlist(str(question.id))
#             user_answer, created = UserAnswer.objects.get_or_create(user=user, question=question, quiz=quiz, category=quiz.category)
#             if answer_ids:
#                 if created:
#                     user_answer.time_spent = time_spent
#                 else:
#                     user_answer.attempt_number += 1
#                 user_answer.answers.set(answer_ids)
#             else:
#                 user_answer.time_spent = time_spent
#             user_answer.save()

#         request.session['quiz_id'] = quiz.id
#         request.session['quiz_title'] = quiz.title

#         return redirect('results')

#     else:
#         formset = QuestionFormSet()

#     question_data = []
#     for question in questions:
#         question_data.append({
#             'question': question,
#             'answers': question.answer_set.all(),
#             'is_multiple_choice': question.answer_set.filter(is_correct=True).count() > 1,
#             'correct_answers_count': question.answer_set.filter(is_correct=True).count(),
#         })

#     unique_users_passed = UserAnswer.objects.filter(quiz=quiz).values('user__email').distinct().count()
    
#     context = {
#         'title': quiz.title,
#         'questions': question_data,
#         'unique_users_passed': unique_users_passed,
#         'time_limit': quiz.time_limit,
#         'formset': formset,
#     }

#     return render(request, 'quiz/quiz.html', context=context)





def results(request):
    user_answers = UserAnswer.objects.filter(user=request.user).prefetch_related('answers', 'correct_answer')
    results = []
    for user_answer in user_answers:
        result = {
            'question': user_answer.question.question,
            'user_answers': [answer.answer for answer in user_answer.answers.all()],
            'correct_answers': [answer.answer for answer in user_answer.correct_answer.all()],
            'is_correct': set(user_answer.answers.all()) == set(user_answer.correct_answer.all()),
        }
        results.append(result)

    context = {
        'results': results,
    }

    return render(request, 'quiz/result.html', context=context)




# def results(request):
#     # Получить результаты теста из базы данных
#     quiz = Quiz.objects.get(id=request.session['quiz_id'])
#     user_answers = UserAnswer.objects.filter(user=request.user, quiz=quiz)

#     results = []
#     for user_answer in user_answers:
#         question = user_answer.question
#         correct_answers = Answer.objects.filter(question=question, is_correct=True)
#         is_correct = any(answer in correct_answers for answer in user_answer.answers.all())
        
#         # Проверяем количество правильных ответов
#         if len(correct_answers) > 1:
#             if is_correct:
#                 result_text = "Один из ответов правильный"
#             else:
#                 result_text = "Вы не правильно ответили"
#         else:
#             result_text = "Вы правильно ответили на вопрос" if is_correct else "Вы не правильно ответили"

#         results.append({
#             'question': question.question,
#             'user_answers': [answer.answer for answer in user_answer.answers.all()],
#             'correct_answers': [answer.answer for answer in correct_answers],
#             'is_correct': is_correct,
#             'result_text': result_text,
#         })

#     return render(request, 'quiz/result.html', {'results': results})





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