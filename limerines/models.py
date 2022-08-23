from django.db import models
import random
import collections
import requests
import numpy as np
from nltk.corpus import names
from transformers import  GPT2Tokenizer, GPT2LMHeadModel, pipeline


from .utils import get_three_highest, get_pos_tags, \
    syllables_in_verse, get_scores, \
    check_end_of_sentence, \
    get_masked_word, count_syllables, \
    return_verses, get_ten_highest_verbs, \
    get_feminine, get_masculine, load_model

MODEL = GPT2LMHeadModel.from_pretrained('distilgpt2')
TOKENIZER = GPT2Tokenizer.from_pretrained('distilgpt2')
UNMASKER = pipeline("fill-mask",model="distilroberta-base")
FEMININE_PROFESSIONS = {'actress':'actor', 'businesswoman':'businessman', 'saleswoman':'salesman', 'waitress':'waiter', 'woman':'man', 'girl':'boy'}

class AdjProfHelper(models.Model):
    adjectives_list = models.JSONField(null=True)
    profession_list = models.JSONField(null=True)
    adjective_profession = models.JSONField(null=True)
    places_list = models.JSONField(null=True)

    def construct(self):
        self.adjectives_list = load_model('limerines/my_data/adjectives_list.pickle')
        self.profession_list = load_model('limerines/my_data/professions_list.pickle')
        self.adjective_profession = load_model('limerines/my_data/adjective_professions.pickle')
        with open('limerines/my_data/places.txt') as file:
            lines = file.readlines()
            self.places_list = [line.rstrip() for line in lines]

    @classmethod
    def object(cls):
        return cls._default_manager.all().first() # Since only one item

    def save(self, *args, **kwargs):
        if not self.pk and AdjProfHelper.objects.exists():
            raise Exception('There can only be one AdjProfHelper instance')
        if not AdjProfHelper.objects.exists():
            self.construct()
        return super(AdjProfHelper, self).save(*args, **kwargs)


class TemplateHelper(models.Model):
    second_verse_templates = models.JSONField(null=True)
    third_verse_templates = models.JSONField(null=True)
    fourth_verse_templates = models.JSONField(null=True)
    fifth_verse_templates = models.JSONField(null=True)

    def construct(self):
        self.second_verse_templates = load_model('limerines/my_data/second_verse_templates.pickle')
        self.third_verse_templates = load_model('limerines/my_data/third_verse_templates.pickle')
        self.fourth_verse_templates = load_model('limerines/my_data/fourth_verse_templates.pickle')
        self.fifth_verse_templates = load_model('limerines/my_data/fifth_verse_templates.pickle')

    @classmethod
    def object(cls):
        return cls._default_manager.all().first() # Since only one item

    def save(self, *args, **kwargs):
        if not self.pk and TemplateHelper.objects.exists():
            raise Exception('There can only be one TemplateHelper instance')
        if not TemplateHelper.objects.exists():
            self.construct()
        return super(TemplateHelper, self).save(*args, **kwargs)

class RhymePronHelper(models.Model):
    rhymes = models.JSONField(null=True)
    pronunciation = models.JSONField(null=True)

    def get_rhymes(self,word):
        if word in self.rhymes.keys():
            return self.rhymes[word]

        url = "https://rhymebrain.com/talk?function=getRhymes&word=" + word
        try:
            rhymes = requests.get(url)
            resulting_rhymes = [result["word"] for result in rhymes.json() if result["score"] == 300 and result["freq"] >= 18 and "a" not in result["flags"] and "b" in result["flags"]]
        except:
            return []

        if len(resulting_rhymes) < 10:
            resulting_rhymes = [result["word"] for result in rhymes.json() if result["score"] >= 200 and result["freq"] >= 18 and "a" not in result["flags"] and "b" in result["flags"]]
        
        self.rhymes[word] = resulting_rhymes
        self.save()
        return resulting_rhymes

    def get_pronunciation(self, word):
        if word in self.pronunciation.keys():
            return self.pronunciation[word]

        url = "https://rhymebrain.com/talk?function=getWordInfo&word=" + word
        try:
            pron = requests.get(url)
            result = pron.json()["pron"]
        except:
            return ''

        self.pronunciation[word] = result
        self.save()
        return result

    def get_rhyming_name(self, word1, word2):
        male_names = names.words('male.txt') 
        female_names = names.words('female.txt')
        places = AdjProfHelper.object().places_list
        rhymes = [rhyme.lower() for rhyme in self.get_rhymes(word1)]
        rhymes.extend([rhyme.lower() for rhyme in self.get_rhymes(word2)])
        try:
            matching_3_m = [name for name in male_names if name[-3:] == word1[-3:] or name[-3:] == word2[-3:]]
        except:
            pass
        else:
            for name in matching_3_m:
                name_rhymes = self.get_rhymes(name.lower())
                if word1 in name_rhymes or word2 in name_rhymes:
                    rhymes.append(name.lower())
        try:
            matching_3_f = [name for name in female_names if name[-3:] == word1[-3:] or name[-3:] == word2[-3:]]
        except:
            pass
        else:
            for name in matching_3_f:
                name_rhymes = self.get_rhymes(name.lower())
                if word1 in name_rhymes or word2 in name_rhymes:
                    rhymes.append(name.lower())
        try:
            matching_3_p = [place for place in places if place[-3:] == word1[-3:] or place[-3:] == word2[-3:]]
        except:
            pass
        else:
            for place in matching_3_p:
                place_rhymes = self.get_rhymes(place.lower())
                if word1 in place_rhymes or word2 in place_rhymes:
                    rhymes.append(place.lower())

        rhyming_male_names = [name for name in male_names if name.lower() in rhymes]
        rhyming_female_names = [name for name in female_names if name.lower() in rhymes]
        rhyming_places = [place for place in places if place.lower() in rhymes]

        return (rhyming_male_names, rhyming_female_names, rhyming_places)

    def proper_noun_rhyme_exists(self, word1, first_verse):
        syllables = 3
        for w in first_verse:
            syl = count_syllables(w)
            syllables += syl
        male_names = names.words('male.txt') 
        female_names = names.words('female.txt')
        places = AdjProfHelper.object().places_list

        rhymes = [rhyme.lower() for rhyme in self.get_rhymes(word1)]
        try:
            matching_3_m = [name for name in male_names if name[-3:] == word1[-3:]]
        except:
            pass
        else:
            for name in matching_3_m:
                syl = count_syllables(name)
                if syl + syllables in [8,9]:
                    name_rhymes = self.get_rhymes(name.lower())
                    if word1 in name_rhymes:
                        return True
        try:
            matching_3_f = [name for name in female_names if name[-3:] == word1[-3:]]
        except:
            pass
        else:
            for name in matching_3_f:
                syl = count_syllables(name)
                if syl + syllables in [8,9]:
                    name_rhymes = self.get_rhymes(name.lower())
                    if word1 in name_rhymes:
                        return True
        try:
            matching_3_p = [place for place in places if place[-3:] == word1[-3:]]
        except:
            pass
        else:
            for place in matching_3_p:
                syl = count_syllables(place)
                if syl + syllables in [8,9]:
                    place_rhymes = self.get_rhymes(place.lower())
                    if word1 in place_rhymes:
                        return True

        needed_syllables = [8-syllables, 9-syllables]
        if any(name.lower() in rhymes and count_syllables(name) in needed_syllables for name in male_names) or any(name.lower() in rhymes and count_syllables(name) in needed_syllables for name in female_names) or any(place.lower() in rhymes and count_syllables(place) in needed_syllables for place in places):
            return True
        return False

    @classmethod
    def object(cls):
        return cls._default_manager.all().first() # Since only one item

    def save(self, *args, **kwargs):
        if not self.pk and RhymePronHelper.objects.exists():
            raise Exception('There can only be one RhymePronHelper instance')
        if not RhymePronHelper.objects.exists():
            self.rhymes =  load_model('limerines/my_data/rhymes.pickle')
            self.pronunciation = load_model('limerines/my_data/pronunciation.pickle')
        return super(RhymePronHelper, self).save(*args, **kwargs)

class Limerick(models.Model):
    verse1 = models.CharField(max_length=100)
    verse2 = models.CharField(max_length=100)
    verse3 = models.CharField(max_length=100)
    verse4 = models.CharField(max_length=100)
    verse5 = models.CharField(max_length=100)
    votes = models.IntegerField(default=0)
    model_rank = models.IntegerField(default=0)
    rank = models.IntegerField(default=0)
    adjective = models.CharField(max_length=100)
    profession = models.CharField(max_length=100)
    female = models.BooleanField()
    place = models.BooleanField()
    pronunciation = models.JSONField(null=True)
    pair = models.IntegerField(null=True)
    pair2 = models.IntegerField(null=True)
    scored_second = models.JSONField(null=True)
    scored_third = models.JSONField(null=True)
    scored_fourth = models.JSONField(null=True)
    scored_fifth = models.JSONField(null=True)
    names = models.JSONField(null=True)
    perplexity = models.FloatField(null=True)

    def __str__(self):
        return self.verse1 + '\n' + self.verse2 + '\n' + self.verse3 + '\n' + self.verse4 + '\n' + self.verse5
    
    def return_whole_sentence(self):
        return self.verse1 + " " + self.verse2 + " " + self.verse3 + " " + self.verse4 + " " + self.verse5

    def get_pronunciation(self):
        i = 1
        field_data = {}
        for verse in [self.verse1, self.verse2, self.verse3, self.verse4, self.verse5]:
            result = []
            words = verse.split()
            for word in words:
                if word.isalpha():
                    result.append(RhymePronHelper.object().get_pronunciation(word))
                else:
                    result.append(RhymePronHelper.object().get_pronunciation(word[:-1]))
            field_data['verse'+str(i)] = result
            i += 1
        self.pronunciation = field_data

    def get_perplexity(self):
        text = self.return_whole_sentence()
        tokens_tensor = TOKENIZER.encode(text, add_special_tokens=False, return_tensors="pt") 
        loss = MODEL(tokens_tensor, labels=tokens_tensor)[0]
        self.perplexity =  np.exp(loss.cpu().detach().numpy())

def update_rankings():
    ranking = 1
    limericks = Limerick.objects.all().order_by("-votes")
    for limerick in limericks:
        limerick.rank = ranking
        limerick.save()
        ranking += 1
    ranking = 1
    limericks = Limerick.objects.all().order_by("perplexity")
    for limerick in limericks:
        limerick.model_rank = ranking
        limerick.save()
        ranking += 1


class Verse():

    def __init__(self,templates,previous_verse):
        self.verse_templates = templates
        self.previous_verse = previous_verse
        self.scored_verses = []
        self.current_verse = None
        self.current_best_verses = []

    def found_a_template_match(self, tags):
        final = False
        found = False
        pos_tags = [t[1] for t in tags]
        tags_length = len(pos_tags)
        exact_matches = [t for t in self.verse_templates if t == pos_tags]
        partial_matches = [t for t in self.verse_templates if t[:tags_length] == pos_tags and len(t) > tags_length]
        if len(exact_matches) > 0:
            final = True
        if len(partial_matches) > 0:
            found = True
        return (final, found)

    def found_a_partial_template_match_2(self, tags):
        final = False
        found = False
        pos_tags = [t[1] for t in tags]
        tags_length = len(pos_tags)
        exact_matches = [t for t in self.verse_templates if t[:-2] == pos_tags and len(t) == tags_length+2]
        partial_matches = [t for t in self.verse_templates if t[:tags_length] == pos_tags and len(t) > tags_length+2]
        if len(exact_matches) > 0:
            final = True
        if len(partial_matches) > 0:
            found = True
        return (final, found)

    def get_iteration_result(self, potential_verses, syllables_needed, final_verses, candidate, rhymingVerse, exceptions = [], secondVerse = False):
        while len(potential_verses) > 0:
            all_new_verses = []
            for potential_verse, length in potential_verses:
                verse = potential_verse[length:]
                prompt = ' '.join(potential_verse)
                next_potential_words = get_three_highest(prompt, MODEL, TOKENIZER, exceptions)
                for npw in set(next_potential_words):
                    tokens = verse + [npw]
                    tags = get_pos_tags(tokens)
                    if rhymingVerse:
                        (final, found) = self.found_a_partial_template_match_2(tags)
                    else:
                        (final, found) = self.found_a_template_match(tags)
                    new_verse = potential_verse + [npw]
                    syllables = syllables_in_verse(' '.join(new_verse[length:]))
                    if final and secondVerse:
                        if syllables in syllables_needed and RhymePronHelper.object().proper_noun_rhyme_exists(new_verse[length:][-1],candidate[0][:length]) and check_end_of_sentence(' '.join(new_verse[length:]), len(new_verse[length:]), MODEL, TOKENIZER):
                            if any(fv[0] == candidate[0][:length] for fv in final_verses):
                                get_element = [i for i, fv in enumerate(final_verses) if fv[0] == candidate[0][:length]][0]
                                final_verses[get_element][1].append(new_verse[length:])

                            else:
                                final_verses.append((candidate[0][:length], [new_verse[length:]]))
                    if final and not secondVerse:
                        if syllables in syllables_needed:
                            if any(fv[0] == candidate[0][:length] for fv in final_verses):
                                get_element = [i for i, fv in enumerate(final_verses) if fv[0] == candidate[0][:length]][0]
                                final_verses[get_element][1].append(new_verse[length:])
                            else:
                                final_verses.append((candidate[0][:length], [new_verse[length:]]))
                    if found and new_verse not in all_new_verses:
                        all_new_verses.append((new_verse, length))
            potential_verses = all_new_verses.copy()
        return final_verses

    def get_next(self, multiple = False):
        if not multiple:
            self.scored_verses.pop(0)
            try:
                self.current_verse = (self.scored_verses[0][0].split(),len(self.scored_verses[0][0].split())) 
            except:
                if self.previous_verse:
                    self.previous_verse.get_next()
                    self.generate_all()
                else:
                    raise Exception("Sorry, no limericks could be generated")
        else:
            self.scored_verses = self.scored_verses[2:]
            try:
                self.current_best_verses = [(sv[0].split(), len(sv[0].split())) for sv in self.scored_verses[:2]]
            except:
                if self.previous_verse:
                    self.previous_verse.get_next(multiple)
                    self.generate_all(multiple=multiple)
                else:
                    raise Exception("Sorry, no limericks could be generated")

    def get_rhyming_results(self, final_fourth_verse, last_word, syllables_needed):
        punc = ',' if syllables_needed == 6 else '.'
        p_verse = final_fourth_verse[0]
        n_verses = final_fourth_verse[1]
        print(f'There are {len(n_verses)} verses prepared for rhyiming')
        print()
        rhyming = RhymePronHelper.object().get_rhymes(last_word)[:10]
        results = []
        for n_verse in n_verses:
            for rw in rhyming:
                eop = rw + punc
                prompt = ' '.join(p_verse + n_verse) + " <mask> " + eop
                masked_words = get_masked_word(prompt, UNMASKER)
                for mw in masked_words:
                    tokens = get_pos_tags(n_verse + [mw,rw])
                    tags = [t[1] for t in tokens]
                    if tags in self.verse_templates:
                        syllables = syllables_in_verse(' '.join(n_verse) + " " + mw + " " + rw)
                        if syllables == syllables_needed:
                            results.append(p_verse + n_verse + [mw, rw])
        return results
                


class SecondVerse(Verse):

    def __init__(self, profession, second_verse_starting_candidates = []):
        self.profession = profession
        self.verb_exceptions = get_used_verbs()
        self.second_verse_starting_candidates = second_verse_starting_candidates
        super().__init__(TemplateHelper.object().second_verse_templates,None)

    def generate_beginning(self):
        print(f'Exceptions for second verse are {self.verb_exceptions}')
        print()
        result = []
        who_prompt = ' '.join(self.second_verse_starting_candidates[0])
        next_potential_verbs = get_ten_highest_verbs(who_prompt, MODEL, TOKENIZER, self.verb_exceptions)
        print(f'potential verbs for second verse {next_potential_verbs}')
        print()
        next_potential_verbs = random.sample(next_potential_verbs, 3)
        self.verb_exceptions.extend(next_potential_verbs)
        print(f'potential verbs for second verse after randommised {next_potential_verbs}')
        print()
        for npv in next_potential_verbs:
            new_verse = self.second_verse_starting_candidates[0] + [npv]
            result.append((new_verse,3))
        whose_prompt = ' '.join(self.second_verse_starting_candidates[1])
        next_potential_words = get_three_highest(whose_prompt, MODEL, TOKENIZER)
        for npw in next_potential_words:
            tokens = ['whose',npw]
            tags = get_pos_tags(tokens)
            (final, found) = self.found_a_template_match(tags)
            if found:
                new_verse = self.second_verse_starting_candidates[1] + [npw]
                result.append((new_verse,3))
        return result

    def generate_all(self, second_verse_candidates):
        print(f'Second verse candidates are')
        print(second_verse_candidates)
        print()
        second_word = [v[4] for (v,l) in second_verse_candidates]
        print(f'second words from second_verse_candidates are {second_word}')
        final_second_verses = []
        for svc in second_verse_candidates:
            print(f'At potential verse {svc}')
            print()
            potential_second_verses = [svc]
            final_second_verses = self.get_iteration_result(potential_second_verses, [9], final_second_verses, svc, False, exceptions=[], secondVerse = True)
        
        if len(final_second_verses) == 0:
            svc = self.generate_beginning()
            self.generate_all(svc)
        
            """else:
            verse1 = final_second_verses[0][0]
            verses2 = final_second_verses[0][1]
            word1list = [v for v in verses2 if v[1] == second_word[0] and v[0] == 'who']
            word2list = [v for v in verses2 if v[1] == second_word[1] and v[0] == 'who']
            word3list = [v for v in verses2 if v[1] == second_word[2] and v[0] == 'who']
            word4list = [v for v in verses2 if v[1] == second_word[3] and v[0] == 'whose']
            word5list = [v for v in verses2 if v[1] == second_word[4] and v[0] == 'whose']
            word6list = [v for v in verses2 if v[1] == second_word[5] and v[0] == 'whose']
            iteration_list = [word1list, word2list, word3list, word4list, word5list, word6list]
            print("Iteration list is")
            print(iteration_list)
            texts = []
            for il in iteration_list:
                current_texts = [' '.join(verse1 + verse2)+"." for verse2 in il]
                texts.extend(current_texts)
                scored_current = sorted(get_scores(current_texts, MODEL, TOKENIZER), key=lambda x: x[1]).copy()
                scored_current = [sc for sc in scored_current if ' '.join(sc[0].split()[3:]) not in all_second_verses()]
                self.current_best_verses.extend([(sc[0].split(), len(sc[0].split()), sc[1]) for sc in scored_current[:2]])
                self.current_best_verses = sorted(self.current_best_verses, key=lambda x: x[2])
                print("Current best verses are")
                print(self.current_best_verses)

            self.scored_verses = sorted(get_scores(texts, MODEL, TOKENIZER), key=lambda x: x[1]).copy()
            self.scored_verses = [sv for sv in self.scored_verses if ' '.join(sv[0].split()[3:]) not in all_second_verses()]
            self.current_verse = (self.scored_verses[0][0].split(), len(self.scored_verses[0][0].split()))
            print(f'There are {len(self.scored_verses)} second verses')
            print()
            print(f'The current verse is {self.current_verse}')
            print()
            print(f'The current best verses are {self.current_best_verses}')"""
            
        else:
            verse1 = final_second_verses[0][0]
            verses2 = final_second_verses[0][1]
            texts = [' '.join(verse1 + verse2)+"." for verse2 in verses2]
            self.scored_verses = sorted(get_scores(texts, MODEL, TOKENIZER), key=lambda x: x[1]).copy()
            self.scored_verses = [sv for sv in self.scored_verses if ' '.join(sv[0].split()[3:]) not in all_second_verses()]
            self.current_verse = (self.scored_verses[0][0].split(), len(self.scored_verses[0][0].split()))
            self.current_best_verses = [(sv[0].split(), len(sv[0].split()), sv[1]) for sv in self.scored_verses[:5]]
            print(f'There are {len(self.scored_verses)} second verses')
            print()
            print(f'The current verse is {self.current_verse}')
            print()
            print(f'The current best verses are {self.current_best_verses}')
            print()

    def get_next(self, multiple = False):
        if not multiple:
            print(f'Getting next second verse')
            self.scored_verses.pop(0)
            try:
                self.current_verse = (self.scored_verses[0][0].split(), len(self.scored_verses[0][0].split()))
                print(f'Found a next second verse {self.current_verse}')
            except:
                raise Exception("Sorry, no limericks could be generated")
        else:
            print(f'Getting next five best second verses')
            self.scored_verses = self.scored_verses[5:]
            self.current_best_verses = [(sv[0].split(), len(sv[0].split()), sv[1]) for sv in self.scored_verses[:5]]
            if len(self.current_best_verses) == 0:
                raise Exception("Sorry, no limericks could be generated")

    def get_rhyming_results(self, final_verses, last_word):
        pass

class ThirdVerse(Verse):

    def __init__(self, secondVerse):
        self.feminine = False
        super().__init__(TemplateHelper.object().third_verse_templates, secondVerse)

    def generate_all(self, original='',multiple=False):
        done = False
        while not done:
            final_third_verses = []
            if self.previous_verse.profession in FEMININE_PROFESSIONS.keys() or self.feminine:
                self.feminine = True
                if not multiple:
                    third_verse_candidates = [(self.previous_verse.current_verse[0] + ["She"], self.previous_verse.current_verse[1])]
                else:
                    third_verse_candidates = [(cbv[0] + ["She"], cbv[1]) for cbv in self.previous_verse.current_best_verses]
            else:
                if not multiple:
                    third_verse_candidates = [(self.previous_verse.current_verse[0] + ["He"], self.previous_verse.current_verse[1])]
                else:
                    third_verse_candidates = [(cbv[0] + ["He"], cbv[1]) for cbv in self.previous_verse.current_best_verses]

            print(f'Third verse candidates are {third_verse_candidates} (there should be 5)')
            print()
            for i, tvc in enumerate(third_verse_candidates):
                print(f'At third verse candidate {i}: {tvc}')
                print()
                potential_third_verses = []
                start_prompt = ' '.join(tvc[0])
                next_potential_verbs = get_ten_highest_verbs(start_prompt, MODEL, TOKENIZER, ["was","had"])
                next_potential_verbs = random.sample(next_potential_verbs, 3)
                for npv in next_potential_verbs:
                    new_verse = tvc[0] + [npv]
                    potential_third_verses.append((new_verse, self.previous_verse.current_verse[1]))
                
                final_third_verses = self.get_iteration_result(potential_third_verses, [6], final_third_verses, tvc, False)

            if len(final_third_verses) > 0:
                done = True
            else:
                print(f'There are no third verses')
                print()
                self.previous_verse.get_next(multiple)
        texts = []
        for ftv in final_third_verses:
            verse2 = ftv[0]
            verses3 = ftv[1]
            print(f'There are {len(verses3)} third verses for second verse {verse2}')
            print()
            current_texts = [' '.join(verse2 + verse3) for verse3 in verses3]
            texts.extend(current_texts)
            scored_current = sorted(get_scores(current_texts, MODEL, TOKENIZER), key=lambda x: x[1]).copy()

            if original != '':
                originalWords = original.split()
                scored_current = [sv for sv in scored_current if sv[0].split()[-len(originalWords):] != originalWords] 

            if self.feminine:  
                scored_current = [sc for sc in scored_current if ' '.join(sc[0].split()[sc[0].split().index('She'):]) not in all_third_verses()]
            else:
                scored_current = [sc for sc in scored_current if ' '.join(sc[0].split()[sc[0].split().index('He'):]) not in all_third_verses()]

            self.current_best_verses.extend([(sc[0].split(), len(sc[0].split()), sc[1]) for sc in scored_current[:2]])
            self.current_best_verses = sorted(self.current_best_verses, key=lambda x: x[2])

        self.scored_verses = sorted(get_scores(texts, MODEL, TOKENIZER), key=lambda x: x[1]).copy()
        if self.feminine:
            self.scored_verses = [sv for sv in self.scored_verses if ' '.join(sv[0].split()[sv[0].split().index('She'):]) not in all_third_verses()]
        else:
            self.scored_verses = [sv for sv in self.scored_verses if ' '.join(sv[0].split()[sv[0].split().index('He'):]) not in all_third_verses()]
        
        if original != '':
            originalWords = original.split()
            self.scored_verses = [sv for sv in self.scored_verses if sv[0].split()[-len(originalWords):] != originalWords]
                     
        self.current_verse = (self.scored_verses[0][0].split(), len(self.scored_verses[0][0].split()))
        print(f'The current verse is {self.current_verse}')
        print()
        print(f'The current best verses after verse3 are {self.current_best_verses}')
        print()
    
    def get_rhyming_results(self, final_verses, last_word):
        pass
            

class FourthVerse(Verse):

    def __init__(self, thirdVerse):
        super().__init__(TemplateHelper.object().fourth_verse_templates, thirdVerse)

    def generate_all(self, original='', multiple = False):
        done = False
        while not done:
            final_fourth_verses = []
            if not multiple:
                fourth_verse_candidates = [self.previous_verse.current_verse]
            else:
                fourth_verse_candidates = [(cbv[0], cbv[1]) for cbv in self.previous_verse.current_best_verses]
            
            print(f'Fourth verse candidates are {fourth_verse_candidates} (there should be 10)')
            print()
            for i, fvc in enumerate(fourth_verse_candidates):
                print(f'At potential fvc {i}: {fvc}')
                print()
                potential_fourth_verses = [fvc]
                final_fourth_verses = self.get_iteration_result(potential_fourth_verses, [1,2,3], final_fourth_verses, fvc, True)
            
            if len(final_fourth_verses) > 0:
                texts = []
                total_rhyming = []
                for ffv in final_fourth_verses:
                    verse3 = ffv[0]
                    last_word = verse3[-1]
                    rhyming_results = self.get_rhyming_results(ffv, last_word, 6)
                    total_rhyming.extend(rhyming_results)
                    if len(rhyming_results) > 0:
                        done = True
                        print(f'There are {len(rhyming_results)} verses 4 for verse {verse3} after rhyiming')
                        print()
                        current_texts = [' '.join(result) for result in rhyming_results]
                        texts.extend(current_texts)
                        scored_current = sorted(get_scores(current_texts, MODEL, TOKENIZER), key=lambda x: x[1]).copy()
                        if original != '':
                            originalWords = original.split()
                            scored_current = [sv for sv in scored_current if sv[0].split()[-len(originalWords):] != originalWords]
                        self.current_best_verses.extend([(sc[0].split(), len(sc[0].split()),sc[1]) for sc in scored_current[:1]])
                        self.current_best_verses = sorted(self.current_best_verses, key=lambda x: x[2])


                if len(total_rhyming) > 0:
                    self.scored_verses = sorted(get_scores(texts, MODEL, TOKENIZER), key=lambda x: x[1]).copy()
                    if original != '':
                        originalWords = original.split()
                        self.scored_verses = [sv for sv in self.scored_verses if sv[0].split()[-len(originalWords):] != originalWords]
                    self.current_verse = (self.scored_verses[0][0].split(),len(self.scored_verses[0][0].split()))  

                else:
                    print(f'There are no fourth verses (after rhyming)')
                    self.previous_verse.get_next(multiple)
            else:
                print(f'There are no fourth verses (before rhyming)')
                self.previous_verse.get_next(multiple)

class FifthVerse(Verse):

    def __init__(self, fourthVerse):
        super().__init__(TemplateHelper.object().fifth_verse_templates, fourthVerse)

    def generate_all(self, original = '', multiple = False):
        done = False
        while not done:
            final_fifth_verses = []
            if not multiple:
                last_word = self.previous_verse.current_verse[0][-1]+','
                fifth_verse_candidates = [(self.previous_verse.current_verse[0][:-1]+[last_word],self.previous_verse.current_verse[1])]
            else:
                fifth_verse_candidates = [(cbv[0], cbv[1]) for cbv in self.previous_verse.current_best_verses]
                fifth_verse_candidates = []
                for cbv in self.previous_verse.current_best_verses:
                    last_word = cbv[0][-1]+','
                    fifth_verse_candidates.append((cbv[0][:-1]+[last_word],cbv[1]))

            for i, fvc in enumerate(fifth_verse_candidates):
                print(f'At potential fifth verse {i}: {fvc}')
                print()
                potential_fifth_verses = [fvc]
                final_fifth_verses = self.get_iteration_result(potential_fifth_verses, [1,2,3,4,5], final_fifth_verses, fvc, True)
            
            if len(final_fifth_verses) > 0:
                texts = []
                total_rhyming = []
                for ffv in final_fifth_verses:
                    verse4 = ffv[0]
                    index_rhyme = [i for i,e in enumerate(verse4) if '.' in e]
                    last_word = verse4[index_rhyme[0]][:-1]
                    rhyming_results = self.get_rhyming_results(ffv, last_word, 9)
                    total_rhyming.extend(rhyming_results)
                    if len(rhyming_results) > 0:
                        done = True
                        print(f'There are {len(rhyming_results)} verses 5 for verse {verse4} after rhyiming')
                        print()
                        current_texts = [' '.join(result) for result in rhyming_results]
                        texts.extend(current_texts)
                        scored_current = sorted(get_scores(current_texts, MODEL, TOKENIZER), key=lambda x: x[1]).copy()
                        if original != '':
                            originalWords = original.split()
                            scored_current = [sv for sv in scored_current if sv[0].split()[-len(originalWords):] != originalWords]
                        print(f'for final fifth verse {ffv[0]} the best one verses are')
                        print()
                        print([(sc[0].split(), len(sc[0].split())) for sc in scored_current[:1]])
                        print()
                        self.current_best_verses.extend([(sc[0].split(), len(sc[0].split()),sc[1]) for sc in scored_current[:1]])
                        self.current_best_verses = sorted(self.current_best_verses, key=lambda x: x[2])
                
                if len(total_rhyming) > 0:
                    self.scored_verses = sorted(get_scores(texts, MODEL, TOKENIZER), key=lambda x: x[1]).copy()
                    if original != '':
                        originalWords = original.split()
                        self.scored_verses = [sv for sv in self.scored_verses if sv[0].split()[-len(originalWords):] != originalWords]
                    self.current_verse = (self.scored_verses[0][0].split(),len(self.scored_verses[0][0].split()))
                else:
                    print(f'There are no fifth verses (after rhyming)')
                    self.previous_verse.get_next(multiple)
            else:
                print(f'There are no fifth verses (before rhyming)')
                self.previous_verse.get_next(multiple)
    
    def return_limerick(self, multiple=False):
        if not multiple:
            return self.current_verse 
        else:
            print("All fifth best verses are")
            print(self.current_best_verses)
            print("But the best five are")
            print(self.current_best_verses[:5])
            return [(cbv[0], cbv[1]) for cbv in self.current_best_verses[:5]]

    def get_next(self):
        pass


def convert_limerick(verse1, result, kind, feminine, limerick, name):
    additional_options = []
    syllables = syllables_in_verse(' '.join(verse1))
    if syllables in [8,9]:
        if result[kind] == '':
            if syllables == 8:
                verse1.insert(1,'once')
            if kind == 'm':
                print("Getting masculine for limerick")
                print(limerick)
                remaining_verses = return_verses(get_masculine(limerick))
            elif kind == 'f':
                remaining_verses = return_verses(get_feminine(limerick))
            else:
                if feminine:
                    remaining_verses = return_verses(get_feminine(limerick))
                else:
                    remaining_verses = return_verses(get_masculine(limerick))
            remaining_verses.insert(0,' '.join(verse1))
            result[kind] = remaining_verses
        additional_options.append(name)
    return (result, additional_options)
                

def finalise_limerick(final_limerick, feminine):
    result = {'m':'','f':'','p':''}
    potential = {'m':[],'f':[],'p':[]}
    index_rhyme = [i for i,e in enumerate(final_limerick) if '.' in e][0]
    (male_rhymes, female_rhymes, place_rhymes) = RhymePronHelper.object().get_rhyming_name(final_limerick[index_rhyme][:-1], final_limerick[-1])
    print(f'Male rhymes are {male_rhymes}')
    print(f'Female rhymes are {female_rhymes}')
    print(f'Place rhymes are {place_rhymes}')
    for name in male_rhymes:
        if feminine and final_limerick[2] in FEMININE_PROFESSIONS.keys():
            new_profession = FEMININE_PROFESSIONS[final_limerick[2]]
            verse1 = ['There', 'was'] + final_limerick[:2] + [new_profession] + ['named', name]
        else:
            verse1 = ['There', 'was'] + final_limerick[:3] + ['named', name]
        (result, additional_m) = convert_limerick(verse1, result, 'm', feminine, final_limerick, name)
        potential['m'].extend(additional_m)
    
    for name in female_rhymes:
        if not feminine and final_limerick[2] in FEMININE_PROFESSIONS.values():
            new_profession = [k for k, v in FEMININE_PROFESSIONS.items() if v == final_limerick[2]][0]
            verse1 = ['There', 'was'] + final_limerick[:2] + [new_profession] + ['named', name]
        else:
            verse1 = ['There', 'was'] + final_limerick[:3] + ['named', name]

        (result, additional_f) = convert_limerick(verse1, result, 'f', feminine, final_limerick, name)
        potential['f'].extend(set(additional_f))

    for place in place_rhymes:
        verse1 = ['There', 'was'] + final_limerick[:3] + ['from', place]
        (result, additional_p) = convert_limerick(verse1, result, 'p', feminine, final_limerick, place)
        potential['p'].extend(additional_p)

    potential['m'] = list(set(potential['m']))
    potential['f'] = list(set(potential['f']))
    potential['p'] = list(set(potential['p']))
    return (result, potential)

def getStartingVerse(adjective, profession):
    preposition = "a" if adjective[0] not in ['a','e','i','o'] else "an"
    second_verse_starting_candidates = [[preposition,  adjective, profession, 'who'], [preposition,  adjective, profession, 'whose']]
    secondVerse = SecondVerse(profession, second_verse_starting_candidates)
    second_verse_candidates = secondVerse.generate_beginning()
    secondVerse.generate_all(second_verse_candidates)
    return secondVerse

def computeLimericks(secondVerse, multiple = False):
    thirdVerse = ThirdVerse(secondVerse)
    thirdVerse.generate_all(multiple=multiple)
    fourthVerse = FourthVerse(thirdVerse)
    fourthVerse.generate_all(multiple=multiple)
    fifthVerse = FifthVerse(fourthVerse)
    fifthVerse.generate_all(multiple=multiple)
    limerick = fifthVerse.return_limerick(multiple)
    if not multiple:
        limerick = limerick[0]
        (limericks, potential) = finalise_limerick(limerick, thirdVerse.feminine)
        if not limericks:
            secondVerse.get_next()
            computeLimericks(secondVerse)
        else:
            return (limericks, thirdVerse, fourthVerse, fifthVerse, potential)
    else:
        results = []
        limericks = [l[0] for l in limerick]
        if not limericks:
            secondVerse.get_next()
            computeLimericks(secondVerse)
        for l in limericks:
            (result, potential) = finalise_limerick(l, thirdVerse.feminine)
            results.append((result, potential))
        return (results, thirdVerse.feminine)


def createLimerick(lim, kind, feminine, female, adjective, profession, place, options_second, options_third, options_fourth, options_fifth, names):
    if kind == 'm' and feminine:
        options_second = [' '.join(get_masculine(o.split())) for o in options_second]
        options_third = [' '.join(get_masculine(o.split())) for o in options_third]
        options_fourth = [' '.join(get_masculine(o.split())) for o in options_fourth]
        options_fifth = [' '.join(get_masculine(o.split())) for o in options_fifth]
    if kind == 'f' and not feminine:
        options_second = [' '.join(get_feminine(o.split())) for o in options_second]
        options_third = [' '.join(get_feminine(o.split())) for o in options_third]
        options_fourth = [' '.join(get_feminine(o.split())) for o in options_fourth]
        options_fifth = [' '.join(get_feminine(o.split())) for o in options_fifth]
    limerick =  Limerick(verse1 = lim[0], verse2 = lim[1], verse3 = lim[2][0].upper() + lim[2][1:], verse4 = lim[3], verse5 = lim[4],
    female = female, adjective = adjective, profession = profession, place = place, scored_second = options_second, 
    scored_third = options_third, scored_fourth = options_fourth, scored_fifth = options_fifth, names = names)
    limerick.get_pronunciation()
    limerick.get_perplexity()
    limerick.save()
    return limerick
    

def run_limerick_generation_single(adjective, profession):
    print("starting generation")
    secondVerse = getStartingVerse(adjective, profession)
    (limericks, thirdVerse, fourthVerse, fifthVerse, potential) = computeLimericks(secondVerse)
    male_id = 0; female_id = 0; place_id = 0
    options_second = [v[0] for v in secondVerse.scored_verses][:25]
    options_third= [v[0] for v in thirdVerse.scored_verses][:25]
    options_fourth = [v[0] for v in fourthVerse.scored_verses][:25]
    options_fifth = [v[0] for v in fifthVerse.scored_verses][:25]
    results = []
    if limericks['m'] != '':
        print("There is a male limerick")
        male_limerick = createLimerick(limericks['m'], 'm', thirdVerse.feminine, False, adjective, profession, False, options_second, options_third, options_fourth, options_fifth, potential['m'])
        male_id = male_limerick.pk
        results.append(male_limerick)
    if limericks['f'] != '':
        print("There is a female limerick")
        female_limerick = createLimerick(limericks['f'], 'f', thirdVerse.feminine, True, adjective, profession, False, options_second, options_third, options_fourth, options_fifth, potential['f'])
        female_id = female_limerick.id
        if male_id != 0:
            female_limerick.pair = male_id
            female_limerick.save()
            male_limerick.pair = female_id
            male_limerick.save()
        results.append(female_limerick)
    if limericks['p'] != '':
        print("there is a place limerick")
        female = True if profession in FEMININE_PROFESSIONS.keys() else False
        place_limerick = createLimerick(limericks['p'], 'p', thirdVerse.feminine, female, adjective, profession, True, options_second, options_third, options_fourth, options_fifth, potential['p'])
        place_id = place_limerick.id
        if male_id != 0:
            place_limerick.pair = male_id
            place_limerick.save()
            male_limerick.pair2 = place_id
            male_limerick.save()
        if female_id != 0:
            place_limerick.pair2 = female_id
            place_limerick.save()
            female_limerick.pair2 = place_id
            female_limerick.save()
        results.append(place_limerick)
    print(f'Results to return is {results}')
    update_rankings()
    return results


def generateFromFourth(fourthVerseText, fifthOriginal, adjective, profession, female, place):
    fourthVerse = FourthVerse(None)
    fourthVerse.current_verse = (fourthVerseText.split(), len(fourthVerseText.split()))
    fourthVerse.scored_verses = [(fourthVerseText, 1)]
    fifthVerse = FifthVerse(fourthVerse)
    fifthVerse.generate_all(fifthOriginal)
    limerick = fifthVerse.return_limerick()[0]
    verses = split_limerick(limerick)
    result = Limerick(verse1 = verses[0], verse2 = verses[1], verse3 = verses[2], verse4 = verses[3], verse5 = verses[4],
    adjective = adjective, profession = profession, female = female, place = place)
    result.get_pronunciation()
    result.get_perplexity()
    result.save()
    update_rankings()
    return result


def generateFromThird(thirdVerseText, fourthOriginal, fifthOriginal, adjective, profession, female, place):
    thirdVerse = ThirdVerse(None)
    thirdVerse.feminine = female
    thirdVerse.current_verse = (thirdVerseText.split(), len(thirdVerseText.split()))
    fourthVerse = FourthVerse(thirdVerse)
    fourthVerse.generate_all(fourthOriginal)
    fifthVerse = FifthVerse(fourthVerse)
    fifthVerse.generate_all(fifthOriginal)
    limerick = fifthVerse.return_limerick()[0]
    verses = split_limerick(limerick)
    print(verses)
    result = Limerick(verse1 = verses[0], verse2 = verses[1], verse3 = verses[2], verse4 = verses[3], verse5 = verses[4],
    adjective = adjective, profession = profession, female = female, place = place)
    result.get_pronunciation()
    result.get_perplexity()
    result.save()
    update_rankings()
    return result

def generateFromSecond(secondVerseText, firstOriginal, thirdOriginal, fourthOriginal, fifthOriginal, adjective, profession, female, place):
    secondVerse = SecondVerse(profession)
    secondVerse.current_verse = (secondVerseText.split(), len(secondVerseText.split()))
    thirdVerse = ThirdVerse(secondVerse)
    thirdVerse.feminine = female
    thirdVerse.generate_all(thirdOriginal)
    fourthVerse = FourthVerse(thirdVerse)
    fourthVerse.generate_all(fourthOriginal)
    fifthVerse = FifthVerse(fourthVerse)
    fifthVerse.generate_all(fifthOriginal)
    limerick = fifthVerse.return_limerick()[0]
    index_rhyme = [i for i,e in enumerate(limerick) if '.' in e][0]
    (male_rhymes, female_rhymes, place_rhymes) = RhymePronHelper.object().get_rhyming_name(limerick[index_rhyme][:-1], limerick[-1])
    if female:
        rhymes = female_rhymes.copy()
    else:
        rhymes = male_rhymes.copy()
    rhymes.extend(place_rhymes)
    firstOriginalWords = firstOriginal.split()[:-1]
    for name in rhymes:
        verse = ' '.join(firstOriginalWords) + " " + name
        syllables = syllables_in_verse(verse)
        if syllables in [8, 9] and firstOriginalWords[1] != 'once':
            firstOriginalWords.append(name)
            if syllables == 8:
                firstOriginalWords.insert(1, 'once')
            if name in place_rhymes and firstOriginalWords[-2] != 'from':
                place = True
                firstOriginalWords[-2] = 'from'
            if name in female_rhymes or name in male_rhymes and firstOriginalWords[-2] != 'named':
                place = False
                firstOriginalWords[-2] = 'named'
            break
        if syllables in [9, 10] and firstOriginalWords[1] == 'once':
            firstOriginalWords.append(name)
            if syllables == 10:
                firstOriginalWords.pop(1)
            if name in place_rhymes and firstOriginalWords[-2] != 'from':
                place = True
                firstOriginalWords[-2] = 'from'
            if name in female_rhymes or name in male_rhymes and firstOriginalWords[-2] != 'named':
                place = False
                firstOriginalWords[-2] = 'named'
            break
    verses = split_limerick(limerick)
    result = Limerick(verse1 = ' '.join(firstOriginalWords), verse2 = verses[1], verse3 = verses[2], verse4 = verses[3], verse5 = verses[4],
    adjective = adjective, profession = profession, female = female, place = place)
    result.get_pronunciation()
    result.get_perplexity()
    result.save()
    update_rankings()
    return result


def split_limerick(limerick):
    verse1 = []; verse2 = []; verse3 = []; verse4 = []
    v1 = ''; v2 = ''; v3 = ''; v4 = ''; v5 = ''
    for i, word in enumerate(limerick):
        verse1.append(word)
        if syllables_in_verse(' '.join(verse1)) == 9:
            v1 = ' '.join(verse1)
            limerick = limerick[i+1:].copy()
            break
    for i, word in enumerate(limerick):
        if word[-1] == '.':
            verse2.append(word[:-1])
        else:
            verse2.append(word)
        if syllables_in_verse(' '.join(verse2)) == 9:
            v2 = ' '.join(verse2)+'.'
            limerick = limerick[i+1:].copy()
            break
    for i, word in enumerate(limerick):
        verse3.append(word)
        if syllables_in_verse(' '.join(verse3)) == 6:
            v3 = ' '.join(verse3)
            limerick = limerick[i+1:].copy()
            break
    for i, word in enumerate(limerick):
        if word[-1] == ',':
            verse4.append(word[:-1])
        else:
            verse4.append(word)
        if syllables_in_verse(' '.join(verse4)) == 6:
            v4 = ' '.join(verse4)+','
            v5 = ' '.join(limerick[i+1:])+'.'
            break
    return [v1,v2,v3,v4,v5]

def get_used_verbs():
    verbs = []
    total_limericks = Limerick.objects.all().count()
    for l in Limerick.objects.all():
        verbs.append(l.verse2.split()[1])
    verb_counter=collections.Counter(verbs)
    result = [e for e in verb_counter if verb_counter[e] >= 0.1*total_limericks]
    return result

def all_second_verses():
    return [l.verse2 for l in Limerick.objects.all()]

def all_third_verses():
    return [l.verse3 for l in Limerick.objects.all()]

def run_limerick_generation_multiple(adjective, profession):
    results = []
    secondVerse = getStartingVerse(adjective, profession)
    resulting_limericks = computeLimericks(secondVerse, True)
    print("Result from multiple generation")
    print(resulting_limericks)
    for (limericks, potential) in resulting_limericks[0]:
        male_id = 0; female_id = 0; place_id = 0
        if limericks['m'] != '':
            male_limerick = createLimerick(limericks['m'], 'm', True, False, adjective, profession, False, options_second=[], options_third=[], options_fourth=[], options_fifth=[], names=potential['m'])
            male_id = male_limerick.pk
            results.append(male_limerick)
        if limericks['f'] != '':
            female_limerick = createLimerick(limericks['f'], 'f', False, True, adjective, profession, False, options_second=[], options_third=[], options_fourth=[], options_fifth=[], names=potential['f'])
            female_id = female_limerick.id
            if male_id != 0:
                female_limerick.pair = male_id
                female_limerick.save()
                male_limerick.pair = female_id
                male_limerick.save()
            results.append(female_limerick)
        if limericks['p'] != '':
            female = True if profession in FEMININE_PROFESSIONS.keys() else False
            place_limerick = createLimerick(limericks['p'], 'p', resulting_limericks[1], female, adjective, profession, True, options_second=[], options_third=[], options_fourth=[], options_fifth=[], names=potential['p'])
            place_id = place_limerick.id
            if male_id != 0:
                place_limerick.pair = male_id
                place_limerick.save()
                male_limerick.pair2 = place_id
                male_limerick.save()
            if female_id != 0:
                place_limerick.pair2 = female_id
                place_limerick.save()
                female_limerick.pair2 = place_id
                female_limerick.save()
            results.append(place_limerick)
            print(f'New limerick ids: {male_id}, {female_id}, {place_id}')
    update_rankings()
    return results


