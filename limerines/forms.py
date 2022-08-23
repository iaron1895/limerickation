from django import forms
from django.db.utils import OperationalError

try:
    from .models import AdjProfHelper
    try:
        ADJECTIVE_CHOICES = AdjProfHelper.object().adjectives_list
        PROFESSION_CHOICES = AdjProfHelper.object().profession_list
    except:
        ADJECTIVE_CHOICES = []
        PROFESSION_CHOICES = []
except OperationalError:
    ADJECTIVE_CHOICES = []
    PROFESSION_CHOICES = []
    
GENDER_CHOICES = (('All','All'),('female','Female'),('male','Male'))
TYPE_CHOICES = (('All','All'),('name','Name'),('place','Place'))
KIND_CHOICES = (('single','single'),('multiple', 'multiple'))
SORT_CHOICES = (('user','user'),('model', 'model'))


class LimerickForm(forms.Form):
    adjective = forms.ChoiceField(choices = ADJECTIVE_CHOICES)
    profession = forms.ChoiceField(choices = PROFESSION_CHOICES)
    kind = forms.ChoiceField(choices = KIND_CHOICES)

class VoteForm(forms.Form):
    limerick_id = forms.IntegerField()
    upvote = forms.ChoiceField(choices = [('true','true'),('false','false')])

class FilterForm(forms.Form):
    adjective = forms.ChoiceField(choices = [('All','All')] + ADJECTIVE_CHOICES)
    profession = forms.ChoiceField(choices = [('All','All')] + PROFESSION_CHOICES)
    gender = forms.ChoiceField(choices = GENDER_CHOICES)
    type = forms.ChoiceField(choices = TYPE_CHOICES)
    sort = forms.ChoiceField(choices = SORT_CHOICES)

class SaveLimerickForm(forms.Form):
    verse1 = forms.CharField(max_length=100)
    verse2 = forms.CharField(max_length=100)
    verse3 = forms.CharField(max_length=100)
    verse4 = forms.CharField(max_length=100)
    verse5 = forms.CharField(max_length=100)
    overse1 = forms.CharField(max_length=100)
    overse3 = forms.CharField(max_length=100)
    overse4 = forms.CharField(max_length=100)
    overse5 = forms.CharField(max_length=100)
    adjective = forms.CharField(max_length=100)
    profession = forms.CharField(max_length=100)
    female = forms.BooleanField(required=False)
    place = forms.BooleanField(required=False)