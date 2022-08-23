from django import template
from ..utils import load_model, syllables_in_verse
from ..models import Limerick, AdjProfHelper
import random

register = template.Library()

@register.simple_tag
def get_adjective_professions():
    return AdjProfHelper.object().adjective_profession
    
@register.simple_tag
def get_pair_id(limerick):
    if not limerick.pair:
        return None
    return Limerick.objects.get(pk=limerick.pair)

@register.simple_tag
def get_pair_2_id(limerick):
    if not limerick.pair2:
        return None
    return Limerick.objects.get(pk=limerick.pair2)

@register.simple_tag
def pron_order(limerick):
    result = []
    i = 1
    for verse in [limerick.verse1, limerick.verse2, limerick.verse3, limerick.verse4, limerick.verse5]:
        words = verse.split()
        pron = limerick.pronunciation["verse"+str(i)]
        list_zip = zip(words, pron)
        result.append(list(list_zip))
        i += 1
    return result

@register.simple_tag
def get_place(limerick):
    if not limerick.place:
        return False
    return True

@register.simple_tag
def get_second_verses(limerick):
    result = []
    if limerick.scored_second:
        for verse in limerick.scored_second[:25]:
            words = verse.split()
            sentence = ' '.join(words[3:])
            result.append(sentence)
    return result

@register.simple_tag
def get_third_verses(limerick):
    result = []
    if limerick.scored_third:
        for verse in limerick.scored_third[:25]:
            words = verse.split()
            index_start = [i for i,e in enumerate(words) if '.' in e][0]
            sentence = ' '.join(words[index_start+1:])
            result.append(sentence)
    return result

@register.simple_tag
def get_fourth_verses(limerick):
    result = []
    if limerick.scored_fourth:
        for verse in limerick.scored_fourth[:25]:
            words = verse.split()
            index_start = [i for i,e in enumerate(words) if '.' in e][0]
            third_fourth = words[index_start+1:]
            index_fourth = len(limerick.verse3.split())
            sentence = ' '.join(third_fourth[index_fourth:])
            result.append(sentence)
    return result

@register.simple_tag
def get_fifth_verses(limerick):
    result = []
    if limerick.scored_fifth:
        for verse in limerick.scored_fifth[:25]:
            words = verse.split()
            index_start = [i for i,e in enumerate(words) if '.' in e][0]
            third_fourth_fifth = words[index_start+1:]
            index_fourth = len(limerick.verse3.split())
            fourth_fifth = third_fourth_fifth[index_fourth:]
            index_fifth = len(limerick.verse4.split())
            sentence = ' '.join(fourth_fifth[index_fifth:])
            result.append(sentence+'.')
    return result

@register.simple_tag
def get_first_verses(limerick):
    result = []
    if limerick.names:
        verse1 = limerick.verse1.split()
        words = verse1[:-1]
        for name in limerick.names:
            new_verse = ' '.join(words) + " " + name
            syl = syllables_in_verse(new_verse)
            if syl == 8:
                verse_words = new_verse.split()
                verse_words.insert(1,'once')
                new_verse = ' '.join(verse_words)
            result.append(new_verse)
    return result

@register.simple_tag
def get_previous(limerick, url, limericks, sort, filtered_limericks):
    if filtered_limericks:
        if limerick.id != filtered_limericks[0]:
            index = filtered_limericks.index(limerick.id)
            return Limerick.objects.get(pk = filtered_limericks[index-1])
        else:
            return None
    if 'edit' not in url:
        if sort == 'user':
            prev_limerick = (Limerick.objects.filter(rank__lt=limerick.rank).exclude(id=limerick.id).order_by('-rank','pk').first())
        else:
            prev_limerick = (Limerick.objects.filter(model_rank__lt=limerick.model_rank).exclude(id=limerick.id).order_by('-model_rank','pk').first())
        return prev_limerick
    elif 'result' not in url:
        if limericks:
            index = limericks.index(limerick.id)
            if index == 0:
                return None
            else:
                return (Limerick.objects.get(id=limericks[index-1]))
    return None

@register.simple_tag
def get_next(limerick, url, limericks, sort, filtered_limericks):
    if filtered_limericks:
        if limerick.id != filtered_limericks[-1]:
            index = filtered_limericks.index(limerick.id)
            return Limerick.objects.get(pk = filtered_limericks[index+1])
        else:
            return None
    if 'edit' not in url:
        if sort == 'user':
            next_limerick = (Limerick.objects.filter(rank__gt=limerick.rank).exclude(id=limerick.id).order_by('rank').first())
        else:
            next_limerick = (Limerick.objects.filter(model_rank__gt=limerick.model_rank).exclude(id=limerick.id).order_by('model_rank').first())
        return next_limerick
    elif 'result' not in url:
        if limericks:
            index = limericks.index(limerick.id)
            if index == len(limericks)-1:
                return None
            else:
                return (Limerick.objects.get(id=limericks[index+1]))
    return None

@register.simple_tag
def get_all_limericks():
    result = []
    limericks = Limerick.objects.all()
    for l in limericks:
        result.append([l.verse1, l.verse2, l.verse3, l.verse4, l.verse5])
    return result

@register.simple_tag
def random_from_limerick_list(limericks):
    if limericks:
        return random.choice(limericks)