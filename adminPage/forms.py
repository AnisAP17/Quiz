from django import forms
from quiz.models import Category, Quiz, Question, Answer
from accounts.models import CustomUser


class PersonalInfoForm(forms.Form):
    last_name = forms.CharField(label='Фамилия', max_length=100)
    first_name = forms.CharField(label='Имя', max_length=100)
    middle_name = forms.CharField(label='Отчество', max_length=100)
    phone = forms.CharField(label='Телефон', max_length=15)
    gender = forms.ChoiceField(label='Пол', choices=[('M', 'Мужской'), ('F', 'Женский')])
    


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['image', 'title', 'slug', 'description', 'npp']

class QuizForm(forms.ModelForm):
    author = forms.ModelChoiceField(queryset=CustomUser.objects.filter(is_staff=True))
    category = forms.ModelChoiceField(queryset=Category.objects.all())
    class Meta:
        model = Quiz
        fields = ['author', 'image', 'title', 'slug', 'description', 'is_public', 'category', 'time_limit']
        widgets = {
            'category': forms.HiddenInput(),
            # другие виджеты...
        }

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['quiz', 'question', 'full_text', 'image']
        

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['answer', 'is_correct', 'score']