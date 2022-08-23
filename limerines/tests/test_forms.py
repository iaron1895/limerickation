from django.test import SimpleTestCase
from limerines.forms import LimerickForm, VoteForm, FilterForm, SaveLimerickForm

class TestLimerickForm(SimpleTestCase):

    def test_limerick_form_with_valid_data(self):
        form = LimerickForm(data={
            'adjective':'old',
            'profession':'man',
            'kind':'single'
        })

        self.assertTrue(form.is_valid())

    def test_limerick_form_with_invalid_data(self):
        form = LimerickForm(data={
            'adjective':'man',
            'profession':'old',
            'kind':'single'
        })

        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors),2)

    def test_limerick_form_with_no_data(self):
        form = LimerickForm(data={})

        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors),3)

class TestVoteForm(SimpleTestCase):

    def test_vote_form_with_valid_data(self):
        form = VoteForm(data={
            'limerick_id':1,
            'upvote':'true',
        })

        self.assertTrue(form.is_valid())

    def test_vote_form_with_invalid_data(self):
        form = VoteForm(data={
            'limerick_id':'a',
            'upvote': 'b'
        })

        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors),2)

    def test_vote_form_with_no_data(self):
        form = VoteForm(data={})

        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors),2)

class TestFilterForm(SimpleTestCase):

    def test_vote_form_with_valid_data(self):
        form = FilterForm(data={
            'adjective':'old',
            'profession':'man',
            'gender':'All',
            'type':'All',
            'sort':'user'
        })

        self.assertTrue(form.is_valid())

    def test_vote_form_with_invalid_data(self):
        form = FilterForm(data={
            'adjective':'man',
            'profession':'old',
            'gender':'true',
            'type':'model',
            'sort':'name'
        })

        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors),5)

    def test_vote_form_with_no_data(self):
        form = FilterForm(data={})

        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors),5)


class TestSaveLimerickForm(SimpleTestCase):

    def test_vote_form_with_valid_data(self):
        form = SaveLimerickForm(data={
            'verse1':'verse1',
            'verse2':'verse2',
            'verse3':'verse3',
            'verse4':'verse4',
            'verse5':'verse5',
            'overse1':'overse1',
            'overse3':'overse3',
            'overse4':'overse4',
            'overse5':'overse5',
            'adjective':'old',
            'profession':'man',
            'female':'False',
            'place':'False',
        })

        self.assertTrue(form.is_valid())

    def test_vote_form_with_no_data(self):
        form = SaveLimerickForm(data={})

        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors),11)