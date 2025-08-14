from django.db import models
from ckeditor.fields import RichTextField


class QuestionAnswer(models.Model):
    TYPE = (
        # ('Chat','Chat'),
        ('EDO ijro','EDO ijro'),
        ('E-huquqshunos','E-huquqshunos'),
        ('Mahalla Ijro','Mahalla Ijro'),
        ('Elektron kluch','Elektron kluch'),
        # ('Shartnomalar va toʻlovlar','Shartnomalar va toʻlovlar'),
        ('Eng koʻp beriladigan savollar','Eng koʻp beriladigan savollar'),
    )
    question = models.CharField("savol", max_length=510)
    answer =  RichTextField(
        config_name='default',
        default='',
        blank=True,
         null=True,
        verbose_name='javob'
    )
    type = models.CharField(max_length=55, choices=TYPE)
    img = models.CharField(max_length=255, null=True, blank=True)
    video = models.CharField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        return self.question