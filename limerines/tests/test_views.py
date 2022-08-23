from django.test import TestCase, Client
from django.urls import reverse
from limerines.models import AdjProfHelper, RhymePronHelper, Limerick
from unittest.mock import patch

class TestIndexViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.index_url = reverse('limerines:index')

    def test_indexView_GET(self):
        response = self.client.get(self.index_url)

        self.assertEquals(response.status_code,200)
        self.assertTemplateUsed(response, 'limerines/index.html')

class TestLimerickViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.all_limericks_url = reverse('limerines:limericks')
        self.adjProfHelper = AdjProfHelper()
        self.adjProfHelper.save()
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
            pronunciation={'verse1':'pronunciation1',
                'verse2':'pronunciation2',
                'verse3':'pronunciation3',
                'verse4':'pronunciation4',
                'verse5':'pronunciation5'},
            perplexity=0
        )

    def test_all_limericks_GET(self):
        response = self.client.get(self.all_limericks_url)
        
        self.assertEquals(response.status_code,200)
        self.assertTemplateUsed(response, 'limerines/limericks.html')

    @patch('limerines.views.update_rankings')
    def test_all_limericks_POST_upvote(self, mock_function):
        response = self.client.post(self.all_limericks_url, {
            'limerick_id' : self.limerick.id,
            'gender':'All',
            'adjective':'All',
            'profession':'All',
            'type':'All',
            'upvote':'true',
            'sort':'user'
        })
        self.limerick.refresh_from_db()

        self.assertEquals(mock_function.called, True)
        self.assertEquals(response.status_code,200)
        self.assertEquals(self.limerick.votes,1)

    @patch('limerines.views.update_rankings')
    def test_all_limericks_POST_downvote(self, mock_function):
        response = self.client.post(self.all_limericks_url, {
            'limerick_id' : self.limerick.id,
            'gender':'All',
            'adjective':'All',
            'profession':'All',
            'type':'All',
            'upvote':'false',
            'sort':'user'
        })
        self.limerick.refresh_from_db()

        self.assertEquals(mock_function.called, True)
        self.assertEquals(response.status_code,200)
        self.assertEquals(self.limerick.votes,-1)

    @patch('limerines.views.update_rankings')
    def test_all_limericks_POST_filter(self, mock_function):
        response = self.client.post(self.all_limericks_url, {
            'gender':'All',
            'adjective':'All',
            'profession':'All',
            'type':'All',
            'sort':'user'
        })
        self.assertEquals(mock_function.called, False)
        self.assertEquals(response.status_code,200)
        self.assertEquals(response.context['sort'], 'user')
        self.assertEquals(response.context['limericks'].number, response.context['limericks'].paginator.page(1).number)
        self.assertEquals(response.context['filter_form']['adjective'].value(), 'All')
        self.assertEquals(response.context['filter_form']['profession'].value(), 'All')
        self.assertEquals(response.context['filter_form']['gender'].value(), 'All')
        self.assertEquals(response.context['filter_form']['type'].value(), 'All')
        self.assertEquals(response.context['filter_form']['sort'].value(), 'user')

        response = self.client.post(self.all_limericks_url, {
            'gender':'male',
            'adjective':'old',
            'profession':'man',
            'type':'name',
            'sort':'model'
        })
        self.assertEquals(mock_function.called, False)
        self.assertEquals(response.status_code,200)
        self.assertEquals(response.context['sort'], 'model')
        self.assertEquals(response.context['limericks'].number, response.context['limericks'].paginator.page(1).number)
        self.assertEquals(response.context['filter_form']['adjective'].value(), 'old')
        self.assertEquals(response.context['filter_form']['profession'].value(), 'man')
        self.assertEquals(response.context['filter_form']['gender'].value(), 'male')
        self.assertEquals(response.context['filter_form']['type'].value(), 'name')
        self.assertEquals(response.context['filter_form']['sort'].value(), 'model')

class TestGenerateViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.generate_url = reverse('limerines:generate')
        self.adjProfHelper = AdjProfHelper()
        self.adjProfHelper.save()
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
            pronunciation={'verse1':'pronunciation1',
                'verse2':'pronunciation2',
                'verse3':'pronunciation3',
                'verse4':'pronunciation4',
                'verse5':'pronunciation5'},
            perplexity=0
        )
        self.edit_url = reverse('limerines:edit', args=[self.limerick.id])

    def test_generate_GET(self):
        response = self.client.get(self.generate_url)
        adjective = response.context['form']['adjective'].value()
        profession = response.context['form']['profession'].value()
        
        self.assertEquals(response.status_code,200)
        self.assertTemplateUsed(response, 'limerines/generate.html')
        self.assertEquals (adjective in [a[0] for a in self.adjProfHelper.adjectives_list], True)
        self.assertEquals(profession in self.adjProfHelper.adjective_profession[adjective], True)

    @patch('limerines.views.run_limerick_generation_single')
    def test_generate_POST_quick_limerick(self, mock_function):
        mock_function.return_value = [self.limerick]
        response = self.client.post(self.generate_url, {
            'kind' : 'single',
            'adjective':'old',
            'profession':'man'
        })

        mock_function.assert_called_with('old','man')
        self.assertRedirects(response, expected_url=reverse('limerines:edit', args=[self.limerick.id]), status_code=302, target_status_code=200)

    @patch('limerines.views.run_limerick_generation_multiple')
    def test_generate_POST_best_limerick(self, mock_function):
        mock_function.return_value = [self.limerick]
        response = self.client.post(self.generate_url, {
            'kind' : 'multiple',
            'adjective':'old',
            'profession':'man'
        })

        mock_function.assert_called_with('old','man')
        self.assertRedirects(response, expected_url=self.edit_url, status_code=302, target_status_code=200)

class TestDetailViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.adjProfHelper = AdjProfHelper()
        self.adjProfHelper.save()
        self.rhymePronHelper = RhymePronHelper()
        self.rhymePronHelper.save()
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
            pronunciation={'verse1':'pronunciation1',
                'verse2':'pronunciation2',
                'verse3':'pronunciation3',
                'verse4':'pronunciation4',
                'verse5':'pronunciation5'},
            perplexity=0
        )
        self.edit_url = reverse('limerines:edit', args=[self.limerick.id])
        self.detail_url = reverse('limerines:detail', args=[self.limerick.id])
        self.result_url = reverse('limerines:result', args=[self.limerick.id])

    def test_detail_GET(self):
        response = self.client.get(self.detail_url)
        self.assertTemplateUsed(response, 'limerines/detail.html')

    def test_edit_detail_GET(self):
        response = self.client.get(self.edit_url)
        self.assertTemplateUsed(response, 'limerines/pageNotFound.html')

        session = self.client.session
        session['limericks'] = [self.limerick.id]
        session.save()
        response = self.client.get(self.edit_url)
        self.assertTemplateUsed(response, 'limerines/detail.html')

    def test_result_detail_GET(self):
        response = self.client.get(self.result_url)
        self.assertTemplateUsed(response, 'limerines/pageNotFound.html')
        
        session = self.client.session
        session['new_limerick'] = self.limerick.id
        session.save()
        response = self.client.get(self.result_url)
        self.assertTemplateUsed(response, 'limerines/detail.html')

    @patch('limerines.views.update_rankings')
    def test_detail_POST_upvote(self, mock_function):
        response = self.client.post(self.detail_url, {
            'limerick_id' : self.limerick.id,
            'upvote':'true',
        })
        self.limerick.refresh_from_db()

        self.assertEquals(mock_function.called, True)
        self.assertEquals(response.status_code,200)
        self.assertEquals(self.limerick.votes,1)

    @patch('limerines.views.update_rankings')
    def test_result_detail_POST_upvote(self, mock_function):
        session = self.client.session
        session['new_limerick'] = self.limerick.id
        session.save()
        response = self.client.post(self.result_url, {
            'limerick_id' : self.limerick.id,
            'upvote':'true',
        })
        self.limerick.refresh_from_db()

        self.assertEquals(mock_function.called, True)
        self.assertEquals(response.status_code,200)
        self.assertEquals(self.limerick.votes,1)

    @patch('limerines.views.update_rankings')
    def test_detail_POST_downvote(self, mock_function):
        response = self.client.post(self.detail_url, {
            'limerick_id' : self.limerick.id,
            'upvote':'false',
        })
        self.limerick.refresh_from_db()

        self.assertEquals(mock_function.called, True)
        self.assertEquals(response.status_code,200)
        self.assertEquals(self.limerick.votes,-1)

    @patch('limerines.views.update_rankings')
    def test_result_detail_POST_downvote(self, mock_function):
        session = self.client.session
        session['new_limerick'] = self.limerick.id
        session.save()
        response = self.client.post(self.result_url, {
            'limerick_id' : self.limerick.id,
            'upvote':'false',
        })
        self.limerick.refresh_from_db()

        self.assertEquals(mock_function.called, True)
        self.assertEquals(response.status_code,200)
        self.assertEquals(self.limerick.votes,-1)

    @patch('limerines.views.update_rankings')
    def test_edit_detail_POST_verse1_verse5_modified(self, mock_function):
        session = self.client.session
        session['limericks'] = [self.limerick.id]
        session.save()
        response = self.client.post(self.edit_url, {
            'verse1': 'verse1mod',
            'verse2': 'verse2',
            'verse3': 'verse3',
            'verse4': 'verse4',
            'verse5': 'verse5.',
            'overse1': 'verse1,',
            'overse3': 'verse3',
            'overse4': 'verse4',
            'overse5': 'verse5.',
            'female' : 'False',
            'place' : 'False',
            'adjective' : 'old',
            'profession' : 'man'
        })

        new_limerick = Limerick.objects.last()
        self.assertEqual(new_limerick.verse1, "verse1mod")
        self.assertEqual(new_limerick.verse2, "verse2")
        self.assertEqual(new_limerick.verse3, "verse3")
        self.assertEqual(new_limerick.verse4, "verse4")
        self.assertEqual(new_limerick.verse5, "verse5.")
        self.assertEquals(mock_function.called, True)
        self.assertRedirects(response, expected_url=reverse('limerines:result', args=[new_limerick.id]), status_code=302, target_status_code=200)

        response = self.client.post(self.edit_url, {
            'verse1': 'verse1',
            'verse2': 'verse2',
            'verse3': 'verse3',
            'verse4': 'verse4',
            'verse5': 'verse5mod.',
            'overse1': 'verse1,',
            'overse3': 'verse3',
            'overse4': 'verse4',
            'overse5': 'verse5.',
            'female' : 'False',
            'place' : 'False',
            'adjective' : 'old',
            'profession' : 'man'
        })

        new_limerick = Limerick.objects.last()
        self.assertEqual(new_limerick.verse1, "verse1")
        self.assertEqual(new_limerick.verse2, "verse2")
        self.assertEqual(new_limerick.verse3, "verse3")
        self.assertEqual(new_limerick.verse4, "verse4")
        self.assertEqual(new_limerick.verse5, "verse5mod.")
        self.assertEquals(mock_function.called, True)
        self.assertRedirects(response, expected_url=reverse('limerines:result', args=[new_limerick.id]), status_code=302, target_status_code=200)


    @patch('limerines.views.generateFromFourth')
    def test_edit_detail_POST_verse4_modified(self, mock_function):
        l2 = Limerick.objects.create(
            verse1='verse1',
            verse2='verse2',
            verse3='verse3',
            verse4='verse4mod',
            verse5='verse5new.',
            adjective='old',
            profession='man',
            female=False,
            place=False,
            pronunciation={'verse1':'pronunciation1',
                'verse2':'pronunciation2',
                'verse3':'pronunciation3',
                'verse4':'pronunciation4',
                'verse5':'pronunciation5'},
            perplexity=0
        )
        mock_function.return_value = l2
        session = self.client.session
        session['limericks'] = [self.limerick.id]
        session.save()
        response = self.client.post(self.edit_url, {
            'verse1': 'verse1',
            'verse2': 'verse2',
            'verse3': 'verse3',
            'verse4': 'verse4mod',
            'verse5': 'hidden',
            'overse1': 'verse1,',
            'overse3': 'verse3',
            'overse4': 'verse4',
            'overse5': 'verse5.',
            'female' : 'False',
            'place' : 'False',
            'adjective' : 'old',
            'profession' : 'man'
        })

        text = 'verse1 verse2 verse3 verse4mod'
        mock_function.assert_called_with(text,'verse5', 'old', 'man', False, False)
        self.assertRedirects(response, expected_url=reverse('limerines:result', args=[l2.id]), status_code=302, target_status_code=200)

    @patch('limerines.views.generateFromThird')
    def test_edit_detail_POST_verse3_modified(self, mock_function):
        l2 = Limerick.objects.create(
            verse1='verse1',
            verse2='verse2',
            verse3='verse3mod',
            verse4='verse4new',
            verse5='verse5new.',
            adjective='old',
            profession='man',
            female=False,
            place=False,
            pronunciation={'verse1':'pronunciation1',
                'verse2':'pronunciation2',
                'verse3':'pronunciation3',
                'verse4':'pronunciation4',
                'verse5':'pronunciation5'},
            perplexity=0
        )
        mock_function.return_value = l2
        session = self.client.session
        session['limericks'] = [self.limerick.id]
        session.save()
        response = self.client.post(self.edit_url, {
            'verse1': 'verse1',
            'verse2': 'verse2',
            'verse3': 'verse3mod',
            'verse4': 'hidden',
            'verse5': 'hidden',
            'overse1': 'verse1',
            'overse3': 'verse3',
            'overse4': 'verse4',
            'overse5': 'verse5.',
            'female' : 'False',
            'place' : 'False',
            'adjective' : 'old',
            'profession' : 'man'
        })

        text = 'verse1 verse2 verse3mod'
        mock_function.assert_called_with(text, 'verse4','verse5', 'old', 'man', False, False)
        self.assertRedirects(response, expected_url=reverse('limerines:result', args=[l2.id]), status_code=302, target_status_code=200)

    @patch('limerines.views.generateFromSecond')
    def test_edit_detail_POST_verse2_modified(self, mock_function):
        l2 = Limerick.objects.create(
            verse1='verse1',
            verse2='verse2mod',
            verse3='verse3new',
            verse4='verse4new',
            verse5='verse5new.',
            adjective='old',
            profession='man',
            female=False,
            place=False,
            pronunciation={'verse1':'pronunciation1',
                'verse2':'pronunciation2',
                'verse3':'pronunciation3',
                'verse4':'pronunciation4',
                'verse5':'pronunciation5'},
            perplexity=0
        )
        mock_function.return_value = l2
        session = self.client.session
        session['limericks'] = [self.limerick.id]
        session.save()
        response = self.client.post(self.edit_url, {
            'verse1': 'verse1',
            'verse2': 'verse2mod',
            'verse3': 'hidden',
            'verse4': 'hidden',
            'verse5': 'hidden',
            'overse1': 'verse1',
            'overse3': 'verse3',
            'overse4': 'verse4',
            'overse5': 'verse5.',
            'female' : 'False',
            'place' : 'False',
            'adjective' : 'old',
            'profession' : 'man'
        })

        text = 'verse1 verse2mod'
        mock_function.assert_called_with(text, 'verse1', 'verse3', 'verse4','verse5', 'old', 'man', False, False)
        self.assertRedirects(response, expected_url=reverse('limerines:result', args=[l2.id]), status_code=302, target_status_code=200)
