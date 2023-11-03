from django import forms
from .models import Question, Answer

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question', 'full_text', 'image']

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['answer', 'is_correct', 'comment']

# Создайте formset для вопросов
QuestionFormSet = forms.formset_factory(QuestionForm, extra=1)