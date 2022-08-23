from turtle import update
from django.test import TestCase
from limerines.models import AdjProfHelper, FifthVerse, FourthVerse, TemplateHelper, RhymePronHelper, Limerick, ThirdVerse, update_rankings, SecondVerse
from unittest.mock import patch, Mock


class TestAdjProfHelperModel(TestCase):

    def setUp(self):
        self.adjProfHelper = AdjProfHelper()
        self.adjProfHelper.save()

    def test_construct_method_works(self):
        self.assertEquals(len(self.adjProfHelper.adjectives_list),603)
        self.assertEquals(len(self.adjProfHelper.profession_list),53)
        self.assertEquals(len(self.adjProfHelper.adjective_profession.keys()),603)
        self.assertEquals(len(self.adjProfHelper.places_list),17739)

    def test_object_is_singleton(self):
        a2 = AdjProfHelper()
        with self.assertRaises(Exception) as context:
            a2.save()
        self.assertTrue('There can only be one AdjProfHelper instance' in str(context.exception))

    def test_calling_object_returns_singleton(self):
        a = AdjProfHelper().object()
        self.assertEquals(self.adjProfHelper, a)

class TestTemplateHelper(TestCase):

    def setUp(self):
        self.templateHelper = TemplateHelper()
        self.templateHelper.save()

    def test_construct_method_works(self):
        self.assertEquals(len(self.templateHelper.second_verse_templates),767)
        self.assertEquals(len(self.templateHelper.third_verse_templates),3574)
        self.assertEquals(len(self.templateHelper.fourth_verse_templates),60588)
        self.assertEquals(len(self.templateHelper.fifth_verse_templates),52404)

    def test_object_is_singleton(self):
        t2 = TemplateHelper()
        with self.assertRaises(Exception) as context:
            t2.save()
        self.assertTrue('There can only be one TemplateHelper instance' in str(context.exception))

    def test_calling_object_returns_singleton(self):
        t = TemplateHelper().object()
        self.assertEquals(self.templateHelper, t)


class TestRhymePronHelper(TestCase):

    def setUp(self):
        self.rhymePronHelper = RhymePronHelper()
        self.rhymePronHelper.save()
        self.adjPronHelper = AdjProfHelper()
        self.adjPronHelper.save()

    def test_object_is_singleton(self):
        r2 = RhymePronHelper()
        with self.assertRaises(Exception) as context:
            r2.save()
        self.assertTrue('There can only be one RhymePronHelper instance' in str(context.exception))

    def test_calling_object_returns_singleton(self):
        t = RhymePronHelper().object()
        self.assertEquals(self.rhymePronHelper, t)

    @patch('limerines.models.requests.get')
    def test_rhyme_api_calls(self, mock_get):
        mock_response = Mock()
        expected_dict = [ {"word":"low","freq":25,"score":300,"flags":"bc","syllables":"1"}]
        mock_response.json.return_value = expected_dict
        mock_response.status_code = 200

        mock_get.return_value = mock_response

        # Word that exists in helper
        result = self.rhymePronHelper.get_rhymes("car")
        car_rhyming = ['are', 'or', 'core', 'corps', 'ore', 'cor', 'oar', 'gar', 'for', 'more', 'your', 
        'far', 'four', 'war', 'door', 'nor', 'bar', 'score', 'shore', 'bore', 'par', 'pour', 'wore', 
        'fore', 'sore', 'jar', 'lore', 'pore', 'roar', 'scar', 'tar', 'tor', 'tore', 'boar', 'char', 'mar', 
        'chore', 'soar', 'tsar', 'yore', 'floor', 'store', 'ignore', 'star', 'ashore', 'cigar', 'drawer', 
        'guitar', 'swore', 'adore', 'afar', 'spore', 'decor', 'spar', 'before', 'bizarre', 'offshore', 'vapour', 
        'rapport', 'abhor', 'bazaar', 'explore', 'restore', 'anymore', 'prewar', 'deplore', 'evermore', 'implore', 
        'postwar', 'furthermore', 'seminar', 'antiwar', 'guarantor', 'underscore', 'reservoir', 'heretofore', 'repertoire', 
        'registrar']
        self.assertEqual(mock_get.call_count, 0)
        self.assertEqual(result, car_rhyming)

        # Word that does not exist only call once
        result = self.rhymePronHelper.get_rhymes("hello")
        self.assertEqual(result, ['low'])
        result = self.rhymePronHelper.get_rhymes("hello")
        self.assertEqual(mock_get.call_count, 1)
        self.assertEqual(result, ['low'])

    @patch('limerines.models.requests.get')
    def test_pronunciation_api_calls(self, mock_get):
        mock_response = Mock()
        expected_dict = {
            "word": "hello",
            "pron": "HH AH0 L OW1",
            "ipa": "h\u028cl\u02c8\u0259\u028a\u032f",
            "freq": 19,
            "flags": "bc"
        }
        mock_response.json.return_value = expected_dict
        mock_response.status_code = 200

        mock_get.return_value = mock_response

        # Word that exists in helper
        result = self.rhymePronHelper.get_pronunciation("car")
        car_pronunciation = 'K AA1 R'
        self.assertEqual(mock_get.call_count, 0)
        self.assertEqual(result, car_pronunciation)

        # Word that does not exist only call once
        result = self.rhymePronHelper.get_pronunciation("hello")
        self.assertEqual(result, 'HH AH0 L OW1')
        result = self.rhymePronHelper.get_pronunciation("hello")
        self.assertEqual(mock_get.call_count, 1)
        self.assertEqual(result, 'HH AH0 L OW1')

    def test_get_rhyming_name(self):
        names = self.rhymePronHelper.get_rhyming_name("year","gear")
        male_names = names[0]
        female_names = names[1]
        place_names = names[2]
        self.assertEquals(male_names,[])
        self.assertEquals(female_names,['Pier'])
        self.assertEquals(place_names,['Peer'])

        names = self.rhymePronHelper.get_rhyming_name("storm","alarm")
        male_names = names[0]
        female_names = names[1]
        place_names = names[2]
        self.assertEquals(male_names,['Norm'])
        self.assertEquals(female_names,['Storm'])
        self.assertEquals(place_names,['Benidorm','Tulkarm'])
    
    def test_proper_noun_rhyme_exists(self):
        noun_rhyme_exists = self.rhymePronHelper.proper_noun_rhyme_exists('mother',['a','caring','boy'])
        self.assertTrue(noun_rhyme_exists)
        noun_rhyme_exists = self.rhymePronHelper.proper_noun_rhyme_exists('group',['a','caring','boy'])
        self.assertFalse(noun_rhyme_exists)


class TestLimerick(TestCase):

    def setUp(self):
        self.limerick = Limerick.objects.create(
                verse1='verse1',
                verse2='verse2',
                verse3='verse3',
                verse4='verse4',
                verse5='verse5.',
                adjective='old',
                profession='man',
                female=False,
                place=False,
                perplexity=0
        )
        self.rhymePronHelper = RhymePronHelper()
        self.rhymePronHelper.save()

    def test_return_whole_sentence(self):
        result = self.limerick.return_whole_sentence()
        whole_sentence =  "verse1 verse2 verse3 verse4 verse5."
        self.assertEquals(result, whole_sentence)

    def test_get_pronunciation(self):
        self.assertEqual(self.limerick.pronunciation, None)
        self.limerick.get_pronunciation()
        self.limerick.save()
        pron = self.limerick.pronunciation
        self.assertEquals(pron['verse1'], ['V ER1 S'])
        self.assertEquals(pron['verse2'], ['V ER1 S'])
        self.assertEquals(pron['verse3'], ['V ER1 S'])
        self.assertEquals(pron['verse4'], ['V ER1 S'])
        self.assertEquals(pron['verse5'], ['V ER1 S AH0'])

    def test_update_rankings(self):
        self.limerick.rank = 1
        self.limerick.save()
        self.l2 = Limerick.objects.create(
                verse1='verse1',
                verse2='verse2',
                verse3='verse3',
                verse4='verse4',
                verse5='verse5.',
                adjective='old',
                profession='man',
                female=False,
                place=False,
                perplexity=0,
                votes=2,
                rank=2
        )
        self.assertEquals(self.limerick.rank,1)
        self.assertEquals(self.l2.rank,2)
        update_rankings()
        self.limerick.refresh_from_db()
        self.l2.refresh_from_db()
        self.assertEquals(self.limerick.rank,2)
        self.assertEquals(self.l2.rank,1)

class TestSecondVerse(TestCase):

    def setUp(self):
        self.templateHelper = TemplateHelper()
        self.templateHelper.save()
        

    @patch('limerines.models.get_used_verbs')
    def test_second_verse_creation(self, mock_verbs):
        mock_verbs.return_value = ['was','had','said']
        second_verse_starting_candidates = [['an',  'old', 'man', 'who'], ['an', 'old', 'man', 'whose']]
        self.secondVerse = SecondVerse('man',second_verse_starting_candidates)
        self.assertEqual(mock_verbs.call_count, 1)
        self.assertEqual(self.secondVerse.profession,'man')
        self.assertEqual(self.secondVerse.verb_exceptions,['was','had','said'])
        self.assertEqual(self.secondVerse.second_verse_starting_candidates, second_verse_starting_candidates)
        self.assertEqual(self.secondVerse.verse_templates,self.templateHelper.second_verse_templates)
        self.assertEqual(self.secondVerse.previous_verse,None)

    @patch('limerines.models.get_used_verbs')
    @patch('limerines.models.get_ten_highest_verbs')
    @patch('limerines.models.random.sample')
    @patch('limerines.models.get_three_highest')
    def test_second_generate_beginning(self, mock_three_words, mock_random, mock_ten_verbs, mock_used_verbs):
        mock_used_verbs.return_value = ['was','had','said']
        second_verse_starting_candidates = [['an',  'old', 'man', 'who'], ['an', 'old', 'man', 'whose']]
        self.secondVerse = SecondVerse('man',second_verse_starting_candidates)
        mock_ten_verbs.return_value = ['was','had','said','called','told','spoke','could','went','wanted','did']
        mock_random.return_value = ['said','spoke','wanted']
        mock_three_words.return_value = ['name','parents','house']
        beginning_verses = self.secondVerse.generate_beginning()
        expected_beginning_verses = [(['an', 'old', 'man', 'who', 'said'], 3), (['an', 'old', 'man', 'who', 'spoke'], 3), 
        (['an', 'old', 'man', 'who', 'wanted'], 3), (['an', 'old', 'man', 'whose', 'name'], 3), 
        (['an', 'old', 'man', 'whose', 'parents'], 3), (['an', 'old', 'man', 'whose', 'house'], 3)]

        self.assertEqual(mock_ten_verbs.call_count, 1)
        self.assertEqual(mock_random.call_count, 1)
        self.assertEqual(mock_three_words.call_count, 1)
        self.assertEqual(beginning_verses, expected_beginning_verses)

    @patch('limerines.models.all_second_verses')
    @patch('limerines.models.get_scores')
    @patch('limerines.models.SecondVerse.get_iteration_result')
    @patch('limerines.models.get_used_verbs')
    def test_second_generate_all(self, mock_used_verbs, mock_iteration, mock_scores, mock_all_second_verses):
        mock_used_verbs.return_value = ['was','had','said']
        second_verse_starting_candidates = [['an',  'old', 'man', 'who'], ['an', 'old', 'man', 'whose']]
        self.secondVerse = SecondVerse('man',second_verse_starting_candidates)
        second_verse_potential = [(['an', 'old', 'man', 'who', 'lived'], 3), (['an', 'old', 'man', 'who', 'spoke'], 3), 
        (['an', 'old', 'man', 'who', 'wanted'], 3), (['an', 'old', 'man', 'whose', 'name'], 3), 
        (['an', 'old', 'man', 'whose', 'parents'], 3), (['an', 'old', 'man', 'whose', 'house'], 3)]
        mock_iteration.return_value = [['an','old','man'],[['who','lived','in','the','city','for','a','year'], 
        ['whose', 'parents', 'bought', 'the', 'car', 'from', 'a', 'friend'],['who','lived','with','a','boyfriend','for','a','year']]]
        mock_scores.return_value = [('an old man who lived in the city for a year.',10), 
        ('an old man whose parents bought the car from a friend.',5), ('an old man who lived with a boyfriend for a year.',12)]
        mock_all_second_verses.return_value = ['who lived with a boyfriend for a year.']
        self.secondVerse.generate_all(second_verse_potential)

        self.assertEqual(mock_iteration.call_count, len(second_verse_potential))
        self.assertEqual(self.secondVerse.scored_verses,[('an old man whose parents bought the car from a friend.',5),('an old man who lived in the city for a year.',10)])
        self.assertEqual(self.secondVerse.current_best_verses, [(['an','old','man','whose', 'parents', 'bought', 'the', 'car', 'from', 'a', 'friend.'],11,5),
        (['an','old','man','who','lived','in','the','city','for','a','year.'],11,10)])
        self.assertEqual(self.secondVerse.current_verse,(['an','old','man','whose', 'parents', 'bought', 'the', 'car', 'from', 'a', 'friend.'],11))

    @patch('limerines.models.get_used_verbs')
    def test_second_get_next(self,mock_used_verbs):
        mock_used_verbs.return_value = ['was','had','said']
        second_verse_starting_candidates = [['an',  'old', 'man', 'who'], ['an', 'old', 'man', 'whose']]
        self.secondVerse = SecondVerse('man',second_verse_starting_candidates)

        self.secondVerse.scored_verses = [('an old man whose parents bought the car from a friend.',5),('an old man who lived in the city for a year.',10)]
        self.secondVerse.get_next()
        self.assertEqual(self.secondVerse.scored_verses, [('an old man who lived in the city for a year.',10)])
        self.assertEqual(self.secondVerse.current_verse, (['an','old','man','who','lived','in','the','city','for','a','year.'],11))

        self.secondVerse.scored_verses = [('an old man whose parents bought the car from a friend.',5)]
        with self.assertRaises(Exception) as context:
            self.secondVerse.get_next()
        self.assertTrue('Sorry, no limericks could be generated' in str(context.exception))

        self.secondVerse.scored_verses = [('an old man whose parents bought the car from a friend.',5),('an old man who lived in the city for a year.',10),
        ('an old man who lived in the town for a year.',15), ('an old man who lived in the city for a month.',20), ('an old man who lived in the country for a year.',25),
        ('an old man whose parents bought the cat from a friend.',30), ('an old man whose parents stole the cat from a friend.',35),
        ('an old man whose parents stole the car from a friend.',40),('an old man whose parents bought the cat from a mother.',45),
        ('an old man whose parents brought the cat from a friend.',50)]
        self.secondVerse.get_next(multiple=True)
        self.assertEqual(self.secondVerse.scored_verses, [('an old man whose parents bought the cat from a friend.',30), ('an old man whose parents stole the cat from a friend.',35),
        ('an old man whose parents stole the car from a friend.',40),('an old man whose parents bought the cat from a mother.',45),
        ('an old man whose parents brought the cat from a friend.',50)])
        self.assertEqual(self.secondVerse.current_best_verses, [(['an','old','man','whose', 'parents', 'bought', 'the', 'cat', 'from', 'a', 'friend.'],11,30),
        (['an','old','man','whose', 'parents', 'stole', 'the', 'cat', 'from', 'a', 'friend.'],11,35),
        (['an','old','man','whose', 'parents', 'stole', 'the', 'car', 'from', 'a', 'friend.'],11,40),
        (['an','old','man','whose', 'parents', 'bought', 'the', 'cat', 'from', 'a', 'mother.'],11,45),
        (['an','old','man','whose', 'parents', 'brought', 'the', 'cat', 'from', 'a', 'friend.'],11,50)])

        self.secondVerse.scored_verses = [('an old man whose parents bought the car from a friend.',5),('an old man who lived in the city for a year.',10),
        ('an old man who lived in the town for a year.',15), ('an old man who lived in the city for a month.',20), ('an old man who lived in the country for a year.',25)]
        with self.assertRaises(Exception) as context:
            self.secondVerse.get_next(multiple=True)
        self.assertTrue('Sorry, no limericks could be generated' in str(context.exception))

class TestThirdVerse(TestCase):

    def setUp(self):
        self.templateHelper = TemplateHelper()
        self.templateHelper.save()
        self.secondVerse = Mock(
            profession='man',
            verse_templates=self.templateHelper.second_verse_templates,
            scored_verses= [('an old man whose parents bought the car from a friend.',5),
                ('an old man who lived in the city for a year.',10),
                ('an old man who lived in the town for a year.',15), 
                ('an old man who lived in the city for a month.',20), 
                ('an old man who lived in the country for a year.',25)],
            current_verse = (['an','old','man','whose', 'parents', 'bought', 'the', 'car', 'from', 'a', 'friend.'],11),
            current_best_verses = [(['an','old','man','whose', 'parents', 'bought', 'the', 'car', 'from', 'a', 'friend.'],11,5),
                (['an','old','man','who','lived','in','the','city','for','a','year.'],11,10),
                (['an','old','man','who','lived','in','the','town','for','a','year.'],11,15),
                (['an','old','man','who','lived','in','the','city','for','a','month.'],11,20),
                (['an','old','man','who','lived','in','the','country','for','a','year.'],11,25)]
            )

    def test_third_verse_creation(self):
        self.thirdVerse = ThirdVerse(self.secondVerse)
        self.assertEqual(self.thirdVerse.feminine, False)
        
    @patch('limerines.models.all_third_verses')
    @patch('limerines.models.get_scores')
    @patch('limerines.models.ThirdVerse.get_iteration_result')
    @patch('limerines.models.random.sample')
    @patch('limerines.models.get_ten_highest_verbs')
    def test_third_generate_all_no_original(self, mock_ten_verbs, mock_random, mock_iteration, mock_scores, mock_all_third_verses):
        self.thirdVerse = ThirdVerse(self.secondVerse)
        
        mock_ten_verbs.return_value = ['was','had','said','called','told','spoke','could','went','came','did']
        mock_random.return_value = ['said','went','came']
        mock_iteration.return_value = [[['an','old','man','who','lived','in','the','city','for','a','year.'],[['He','came','back','to','the','house'],
        ['He','said','that','if','the','court'], ['He', 'said', 'he', 'was', 'afraid']]],
        [['an','old','man','whose','parents','bought','the','car','from','a','friend.'],[['He','went','out','of','his','way'],
        ['He','went','on','a','mission'], ['He', 'said', 'that', 'the', 'money']]]]

        def get_scores_side_effect(texts, model=None, tokenizer=None):
            if texts[0].startswith('an old man who lived in the city for a year') and len(texts) == 3:
                return [('an old man who lived in the city for a year. He came back to the house',10),
                ('an old man who lived in the city for a year. He said that if the court',5),
                ('an old man who lived in the city for a year. He said he was afraid',15)]
            if texts[0].startswith('an old man whose parents bought the car from a friend') and len(texts) == 3:
                return [('an old man whose parents bought the car from a friend. He went out of his way',11),
                ('an old man whose parents bought the car from a friend. He went on a mission',6),
                ('an old man whose parents bought the car from a friend. He said that the money',16)]
            return [('an old man who lived in the city for a year. He came back to the house',10),
                ('an old man who lived in the city for a year. He said that if the court',5),
                ('an old man who lived in the city for a year. He said he was afraid',15),
                ('an old man whose parents bought the car from a friend. He went out of his way',11),
                ('an old man whose parents bought the car from a friend. He went on a mission',6),
                ('an old man whose parents bought the car from a friend. He said that the money',16)]

        mock_scores.side_effect = get_scores_side_effect
        mock_all_third_verses.return_value = ['He went out of his way']

        self.thirdVerse.generate_all()

        self.assertEqual(mock_iteration.call_count, 1)
        self.assertEqual(self.thirdVerse.scored_verses,[('an old man who lived in the city for a year. He said that if the court',5),
        ('an old man whose parents bought the car from a friend. He went on a mission',6),
        ('an old man who lived in the city for a year. He came back to the house',10),
        ('an old man who lived in the city for a year. He said he was afraid',15),
        ('an old man whose parents bought the car from a friend. He said that the money',16)])
        self.assertEqual(self.thirdVerse.current_best_verses, [(['an','old','man','who','lived','in','the','city','for','a','year.','He','said','that','if','the','court'],17,5),
        (['an','old','man','whose', 'parents', 'bought', 'the', 'car', 'from', 'a', 'friend.','He','went','on','a','mission'],16,6),
        (['an','old','man','who','lived','in','the','city','for','a','year.','He','came','back','to','the','house'],17,10),
        (['an','old','man','whose','parents','bought','the','car','from','a','friend.','He','said','that','the','money'],16,16)])
        self.assertEqual(self.thirdVerse.current_verse,(['an','old','man','who','lived','in','the','city','for','a','year.','He','said','that','if','the','court'],17))
   
    @patch('limerines.models.all_third_verses')
    @patch('limerines.models.get_scores')
    @patch('limerines.models.ThirdVerse.get_iteration_result')
    @patch('limerines.models.random.sample')
    @patch('limerines.models.get_ten_highest_verbs')
    def test_third_generate_all_original(self, mock_ten_verbs, mock_random, mock_iteration, mock_scores, mock_all_third_verses):
        self.thirdVerse = ThirdVerse(self.secondVerse)
        
        mock_ten_verbs.return_value = ['was','had','said','called','told','spoke','could','went','came','did']
        mock_random.return_value = ['said','went','came']
        mock_iteration.return_value = [[['an','old','man','who','lived','in','the','city','for','a','year.'],[['He','came','back','to','the','house'],
        ['He','said','that','if','the','court'], ['He', 'said', 'he', 'was', 'afraid']]],
        [['an','old','man','whose','parents','bought','the','car','from','a','friend.'],[['He','went','out','of','his','way'],
        ['He','went','on','a','mission'], ['He', 'said', 'that', 'the', 'money']]]]

        def get_scores_side_effect(texts, model=None, tokenizer=None):
            if texts[0].startswith('an old man who lived in the city for a year') and len(texts) == 3:
                return [('an old man who lived in the city for a year. He came back to the house',10),
                ('an old man who lived in the city for a year. He said that if the court',5),
                ('an old man who lived in the city for a year. He said he was afraid',15)]
            if texts[0].startswith('an old man whose parents bought the car from a friend') and len(texts) == 3:
                return [('an old man whose parents bought the car from a friend. He went out of his way',11),
                ('an old man whose parents bought the car from a friend. He went on a mission',6),
                ('an old man whose parents bought the car from a friend. He said that the money',16)]
            return [('an old man who lived in the city for a year. He came back to the house',10),
                ('an old man who lived in the city for a year. He said that if the court',5),
                ('an old man who lived in the city for a year. He said he was afraid',15),
                ('an old man whose parents bought the car from a friend. He went out of his way',11),
                ('an old man whose parents bought the car from a friend. He went on a mission',6),
                ('an old man whose parents bought the car from a friend. He said that the money',16)]

        mock_scores.side_effect = get_scores_side_effect
        mock_all_third_verses.return_value = ['He went out of his way']

        self.thirdVerse.generate_all(original='He came back to the house')

        self.assertEqual(mock_iteration.call_count, 1)
        self.assertEqual(self.thirdVerse.scored_verses,[('an old man who lived in the city for a year. He said that if the court',5),
        ('an old man whose parents bought the car from a friend. He went on a mission',6),
        ('an old man who lived in the city for a year. He said he was afraid',15),
        ('an old man whose parents bought the car from a friend. He said that the money',16)])
        self.assertEqual(self.thirdVerse.current_best_verses, [(['an','old','man','who','lived','in','the','city','for','a','year.','He','said','that','if','the','court'],17,5),
        (['an','old','man','whose', 'parents', 'bought', 'the', 'car', 'from', 'a', 'friend.','He','went','on','a','mission'],16,6),
        (['an','old','man','who','lived','in','the','city','for','a','year.','He','said','he','was','afraid'],16,15),
        (['an','old','man','whose','parents','bought','the','car','from','a','friend.','He','said','that','the','money'],16,16)])
        self.assertEqual(self.thirdVerse.current_verse,(['an','old','man','who','lived','in','the','city','for','a','year.','He','said','that','if','the','court'],17))
   
class TestFourthVerse(TestCase):

    def setUp(self):
        self.templateHelper = TemplateHelper()
        self.templateHelper.save()
        self.secondVerse = Mock(
            profession='man',
            verse_templates=self.templateHelper.second_verse_templates,
            scored_verses= [('an old man whose parents bought the car from a friend.',5),
                ('an old man who lived in the city for a year.',10),
                ('an old man who lived in the town for a year.',15), 
                ('an old man who lived in the city for a month.',20), 
                ('an old man who lived in the country for a year.',25)],
            current_verse = (['an','old','man','whose', 'parents', 'bought', 'the', 'car', 'from', 'a', 'friend.'],11),
            current_best_verses = [(['an','old','man','whose', 'parents', 'bought', 'the', 'car', 'from', 'a', 'friend.'],11,5),
                (['an','old','man','who','lived','in','the','city','for','a','year.'],11,10),
                (['an','old','man','who','lived','in','the','town','for','a','year.'],11,15),
                (['an','old','man','who','lived','in','the','city','for','a','month.'],11,20),
                (['an','old','man','who','lived','in','the','country','for','a','year.'],11,25)]
            )
        self.thirdVerse = Mock(
            verse_templates=self.templateHelper.third_verse_templates,
            previous_verse=self.secondVerse,
            scored_verses= [('an old man who lived in the city for a year. He said that if the court',5),
                ('an old man whose parents bought the car from a friend. He went on a mission',6),
                ('an old man who lived in the city for a year. He said he was afraid',15),
                ('an old man whose parents bought the car from a friend. He said that the money',16)],
            current_verse = (['an','old','man','who','lived','in','the','city','for','a','year.','He','said','that','if','the','court'],17),
            current_best_verses = [(['an','old','man','who','lived','in','the','city','for','a','year.','He','said','that','if','the','court'],17,5),
                (['an','old','man','whose', 'parents', 'bought', 'the', 'car', 'from', 'a', 'friend.','He','went','on','a','mission'],16,6),
                (['an','old','man','who','lived','in','the','city','for','a','year.','He','said','he','was','afraid'],16,15),
                (['an','old','man','whose','parents','bought','the','car','from','a','friend.','He','said','that','the','money'],16,16)]
            )

    @patch('limerines.models.FourthVerse.get_rhyming_results')
    @patch('limerines.models.get_scores')
    @patch('limerines.models.FourthVerse.get_iteration_result')
    def test_fourth_generate_all_no_original(self, mock_iteration, mock_scores, mock_rhyming_results):
        self.fourthVerse = FourthVerse(self.thirdVerse)

        mock_iteration.return_value = [[['an','old','man','who','lived','in','the','city','for','a','year.','He','said','that','if','the','court'], 
        [['to','go','to'],['and','he','looked'],['and','he','would']]]]

        mock_rhyming_results.return_value = [['an','old','man','who','lived','in','the','city','for','a','year.','He','said','that','if','the','court', 
        'to','go','to','seventh','grade'],
        ['an','old','man','who','lived','in','the','city','for','a','year.','He','said','that','if','the','court', 'and','he','looked','pretty','high'],
        ['an','old','man','who','lived','in','the','city','for','a','year.','He','said','that','if','the','court', 'and','he','would','always','look']]

        mock_scores.return_value = [('an old man who lived in the city for a year. He said that if the court to go to seventh grade',10),
                ('an old man who lived in the city for a year. He said that if the court and he looked pretty high',5),
                ('an old man who lived in the city for a year. He said that if the court and he would always look',15)]

        self.fourthVerse.generate_all()

        self.assertEqual(mock_iteration.call_count, 1)
        self.assertEqual(self.fourthVerse.scored_verses,[('an old man who lived in the city for a year. He said that if the court and he looked pretty high',5),
        ('an old man who lived in the city for a year. He said that if the court to go to seventh grade',10),
        ('an old man who lived in the city for a year. He said that if the court and he would always look',15)])
        self.assertEqual(self.fourthVerse.current_best_verses, [(['an','old','man','who','lived','in','the','city','for','a','year.','He','said','that','if','the','court','and','he','looked','pretty','high'],22,5)])
        self.assertEqual(self.fourthVerse.current_verse,(['an','old','man','who','lived','in','the','city','for','a','year.','He','said','that','if','the','court','and','he','looked','pretty','high'],22))
   
    @patch('limerines.models.FourthVerse.get_rhyming_results')
    @patch('limerines.models.get_scores')
    @patch('limerines.models.FourthVerse.get_iteration_result')
    def test_fourth_generate_all_original(self, mock_iteration, mock_scores, mock_rhyming_results):
        self.fourthVerse = FourthVerse(self.thirdVerse)

        mock_iteration.return_value = [[['an','old','man','who','lived','in','the','city','for','a','year.','He','said','that','if','the','court'], 
        [['to','go','to'],['and','he','looked'],['and','he','would']]]]

        mock_rhyming_results.return_value = [['an','old','man','who','lived','in','the','city','for','a','year.','He','said','that','if','the','court', 
        'to','go','to','seventh','grade'],
        ['an','old','man','who','lived','in','the','city','for','a','year.','He','said','that','if','the','court', 'and','he','looked','pretty','high'],
        ['an','old','man','who','lived','in','the','city','for','a','year.','He','said','that','if','the','court', 'and','he','would','always','look']]

        mock_scores.return_value = [('an old man who lived in the city for a year. He said that if the court to go to seventh grade',10),
                ('an old man who lived in the city for a year. He said that if the court and he looked pretty high',5),
                ('an old man who lived in the city for a year. He said that if the court and he would always look',15)]

        self.fourthVerse.generate_all(original='and he would always look')

        self.assertEqual(mock_iteration.call_count, 1)
        self.assertEqual(self.fourthVerse.scored_verses,[('an old man who lived in the city for a year. He said that if the court and he looked pretty high',5),
        ('an old man who lived in the city for a year. He said that if the court to go to seventh grade',10)])
        self.assertEqual(self.fourthVerse.current_best_verses, [(['an','old','man','who','lived','in','the','city','for','a','year.','He','said','that','if','the','court','and','he','looked','pretty','high'],22,5)])
        self.assertEqual(self.fourthVerse.current_verse,(['an','old','man','who','lived','in','the','city','for','a','year.','He','said','that','if','the','court','and','he','looked','pretty','high'],22))

class TestFifthVerse(TestCase):

    def setUp(self):
        self.templateHelper = TemplateHelper()
        self.templateHelper.save()
        self.secondVerse = Mock(
            profession='man',
            verse_templates=self.templateHelper.second_verse_templates,
            scored_verses= [('an old man whose parents bought the car from a friend.',5),
                ('an old man who lived in the city for a year.',10),
                ('an old man who lived in the town for a year.',15), 
                ('an old man who lived in the city for a month.',20), 
                ('an old man who lived in the country for a year.',25)],
            current_verse = (['an','old','man','whose', 'parents', 'bought', 'the', 'car', 'from', 'a', 'friend.'],11),
            current_best_verses = [(['an','old','man','whose', 'parents', 'bought', 'the', 'car', 'from', 'a', 'friend.'],11,5),
                (['an','old','man','who','lived','in','the','city','for','a','year.'],11,10),
                (['an','old','man','who','lived','in','the','town','for','a','year.'],11,15),
                (['an','old','man','who','lived','in','the','city','for','a','month.'],11,20),
                (['an','old','man','who','lived','in','the','country','for','a','year.'],11,25)]
            )
        self.thirdVerse = Mock(
            verse_templates=self.templateHelper.third_verse_templates,
            previous_verse=self.secondVerse,
            scored_verses= [('an old man who lived in the city for a year. He said that if the court',5),
                ('an old man whose parents bought the car from a friend. He went on a mission',6),
                ('an old man who lived in the city for a year. He said he was afraid',15),
                ('an old man whose parents bought the car from a friend. He said that the money',16)],
            current_verse = (['an','old','man','who','lived','in','the','city','for','a','year.','He','said','that','if','the','court'],17),
            current_best_verses = [(['an','old','man','who','lived','in','the','city','for','a','year.','He','said','that','if','the','court'],17,5),
                (['an','old','man','whose', 'parents', 'bought', 'the', 'car', 'from', 'a', 'friend.','He','went','on','a','mission'],16,6),
                (['an','old','man','who','lived','in','the','city','for','a','year.','He','said','he','was','afraid'],16,15),
                (['an','old','man','whose','parents','bought','the','car','from','a','friend.','He','said','that','the','money'],16,16)]
            )
        self.fourthVerse = Mock(
            verse_templates=self.templateHelper.fourth_verse_templates,
            previous_verse=self.thirdVerse,
            scored_verses= [('an old man who lived in the city for a year. He said that if the court and he looked pretty high',5),
                ('an old man who lived in the city for a year. He said that if the court to go to seventh grade',10),
                ('an old man who lived in the city for a year. He said that if the court and he would always look',15)],
            current_verse = (['an','old','man','who','lived','in','the','city','for','a','year.','He','said','that','if','the','court','and','he','looked','pretty','high'],22),
            current_best_verses = [(['an','old','man','who','lived','in','the','city','for','a','year.','He','said','that','if','the','court','and','he','looked','pretty','high'],22,5)]
            )

    @patch('limerines.models.FifthVerse.get_rhyming_results')
    @patch('limerines.models.get_scores')
    @patch('limerines.models.FifthVerse.get_iteration_result')
    def test_fifth_generate_all_no_original(self, mock_iteration, mock_scores, mock_rhyming_results):
        self.fifthVerse = FifthVerse(self.fourthVerse)

        mock_iteration.return_value = [[['an','old','man','who','lived','in','the','city','for','a','year.','He','said','that','if','the','court','and','he','looked','pretty','high'], 
        [['and','I','think','he','would'],['but','he','looked','like','a'],['a','good','friend','and','a']]]]

        mock_rhyming_results.return_value = [['an','old','man','who','lived','in','the','city','for','a','year.','He','said','that','if','the','court', 
        'and','he','looked','pretty','high','and','I','think','he','would','probably','climb'],
        ['an','old','man','who','lived','in','the','city','for','a','year.','He','said','that','if','the','court', 'and','he','looked','pretty','high',
        'but','he','looked','like','a','nursery','rhyme'],
        ['an','old','man','who','lived','in','the','city','for','a','year.','He','said','that','if','the','court', 'and','he','looked','pretty','high',
        'a','good','friend','and','a','wonderful','son']]

        mock_scores.return_value = [('an old man who lived in the city for a year. He said that if the court and he looked pretty high, and I think he would probably climb',10),
                ('an old man who lived in the city for a year. He said that if the court and he looked pretty high, but he looked like a nursery rhyme',5),
                ('an old man who lived in the city for a year. He said that if the court and he looked pretty high, a good friend and a wonderful son',15)]

        self.fifthVerse.generate_all()

        self.assertEqual(mock_iteration.call_count, 1)
        self.assertEqual(self.fifthVerse.scored_verses,[('an old man who lived in the city for a year. He said that if the court and he looked pretty high, but he looked like a nursery rhyme',5),
        ('an old man who lived in the city for a year. He said that if the court and he looked pretty high, and I think he would probably climb',10),
        ('an old man who lived in the city for a year. He said that if the court and he looked pretty high, a good friend and a wonderful son',15)])
        self.assertEqual(self.fifthVerse.current_best_verses, [(['an','old','man','who','lived','in','the','city','for','a','year.','He','said','that','if','the','court','and','he','looked','pretty','high,'
        ,'but','he','looked','like','a','nursery','rhyme'],29,5)])
        self.assertEqual(self.fifthVerse.current_verse,(['an','old','man','who','lived','in','the','city','for','a','year.','He','said','that','if','the','court','and','he','looked','pretty','high,'
        ,'but','he','looked','like','a','nursery','rhyme'],29))
    