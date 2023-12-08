from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Count
from quiz.models import Category, Question, Quiz, Answer, UserAnswer
from .forms import CategoryForm, QuizForm, QuestionForm, TextAnswerForm, DateAnswerForm, NumberAnswerForm, RangeAnswerForm
from django.utils.text import slugify
from django.forms import ValidationError, modelformset_factory

def admin_profile(request):
    quiz = Quiz.objects.count()
    categories = Category.objects.count()
    categoriess = Category.objects.all() \
    .annotate(
        quiz_count=Count('quiz')  # Измените 'id' на 'quiz'
    ).order_by('npp')
    context = {
        'quiz': quiz,
        'categories': categories,
        'categoriess': categoriess,
        'title': 'Категории тестов',
        
    }
    return render(request, 'adminPage/admin_profile.html', context)

def admin_category_view(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    quizzes = Quiz.objects.filter(category=category, is_public=True).order_by('npp')
    quizz = Quiz.objects.count()
    categories = Category.objects.count()

    quizzes_with_questions = []
    for quiz in quizzes:
        quiz.unique_users_passed = UserAnswer.objects.filter(quiz=quiz).values('user__email').distinct().count()
        quizzes_with_questions.append(quiz)

    if request.method == 'POST':
        form = QuizForm(request.POST, request.FILES)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.slug = slugify(quiz.title)
            quiz.category = category  # установить категорию
            quiz.save()
            return redirect('admin_category_view', category_slug=category_slug)
    else:
        form = QuizForm(initial={'category': category})  # установить категорию в форме

    context = {
        'title': f'Тесты по теме «{category.title}»',
        'category': category,
        'quizzes': quizzes_with_questions,
        'quiz': quizz,
        'categories': categories,
        'form': form,
    }

    if quizzes_with_questions:
        return render(request, 'adminPage/admin_category.html', context=context)
    else:
        context['title1'] = f'В категории «{category.title}» нету тестов'
        return render(request, 'adminPage/no_admin_category.html', context=context)


def admin_quiz_view(request, category_slug, quiz_slug):
    quiz = get_object_or_404(Quiz, slug=quiz_slug, category__slug=category_slug)
    questions = quiz.question_set.all().prefetch_related('answer_set')

    context = {
        'quiz': quiz,
        'questions': questions,
    }

    if questions.exists():
        return render(request, 'adminPage/admin_quiz.html', context=context)
    else:
        return render(request, 'adminPage/no_admin_quiz.html', context=context)




# Create your views here.
def admin_index(request):
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
        return render(request, 'adminPage/admin_index.html', context)
    else:
        return render(request, 'adminPage/no_admin_index.html')
    

def create_category(request):
    if request.method == "POST":
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin_profile')
    else:
        form = CategoryForm()
    quiz = Quiz.objects.count()
    categories = Category.objects.count()
    context = {
        'quiz': quiz,
        'categories': categories,
        'form': form,
    }
    return render(request, 'adminPage/create_category.html', context)

def create_quiz(request):
    quiz = Quiz.objects.all()  # Определите quiz здесь
    if request.method == 'POST':
        form = QuizForm(request.POST, request.FILES)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.slug = slugify(quiz.title)
            quiz.save()
            return redirect('admin_profile')
    else:
        form = QuizForm()
    quiz_count = Quiz.objects.count() if quiz else 0
    categories = Category.objects.count()
    context = {
        'quiz': quiz_count,
        'categories': categories,
        'form': form,
    }
    return render(request, 'adminPage/create_quiz.html', context)

def create_question(request):
    AnswerFormSet = modelformset_factory(Answer, form=AnswerForm, extra=4)
    if request.method == "POST":
        form = QuestionForm(request.POST, request.FILES)
        formset = AnswerFormSet(request.POST, request.FILES, prefix='answers')
        if form.is_valid() and formset.is_valid():
            question = form.save()
            answers = formset.save(commit=False)
            for answer in answers:
                if answer in formset.deleted_objects:
                    answer.delete()
                else:
                    answer.question = question
                    answer.save()
                    print("Saved answer:", answer)
            return redirect('admin_profile')
        else:
            print("Form errors:", form.errors)
            print("Formset errors:", formset.errors)
    else:
        form = QuestionForm()
        formset = AnswerFormSet(prefix='answers', queryset=Answer.objects.none())
    quiz = Quiz.objects.all()  # Определите quiz здесь
    quiz_count = Quiz.objects.count() if quiz else 0
    categories = Category.objects.count()
    return render(request, 'adminPage/create_question.html', {'form': form, 'formset': formset, 'categories': categories, 'quiz': quiz_count})


# def edit_question(request, quiz_slug, category_slug, question_id):
#     quiz = get_object_or_404(Quiz, slug=quiz_slug)
#     category = get_object_or_404(Category, slug=category_slug)
#     question = get_object_or_404(Question, quiz=quiz, category=category, pk=question)
#     # остальной код остается без изменений
#     AnswerFormSet = modelformset_factory(Answer, form=AnswerForm, extra=1)
#     if request.method == "POST":
#         form = QuestionForm(request.POST, request.FILES, instance=question)
#         formset = AnswerFormSet(request.POST, request.FILES, prefix='answers', queryset=Answer.objects.filter(question=question))
#         if form.is_valid() and formset.is_valid():
#             question = form.save()
#             answers = formset.save(commit=False)
#             for answer in answers:
#                 if answer in formset.deleted_objects:
#                     answer.delete()
#                 else:
#                     answer.question = question
#                     answer.save()
#             return redirect('admin_profile')
#     else:
#         form = QuestionForm(instance=question)
#         formset = AnswerFormSet(prefix='answers', queryset=Answer.objects.filter(question=question))
#     return render(request, 'adminPage/edit_question.html', {'form': form, 'formset': formset})








# def create_answer(request):
#     if request.method == "POST":
#         form = AnswerForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('answers')
#     else:
#         form = AnswerForm()
#     return render(request, 'adminPage/create_answer.html', {'form': form})


