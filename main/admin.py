from ckeditor.widgets import CKEditorWidget
from .models import QuestionAnswer
from django.contrib import admin
from django import forms

class QuestionAnswerAdminForm(forms.ModelForm):
    info = forms.CharField(widget=CKEditorWidget())
    class Meta:
        model = QuestionAnswer
        fields = '__all__'
        
@admin.register(QuestionAnswer)
class ProductAdmin(admin.ModelAdmin):
    pass
