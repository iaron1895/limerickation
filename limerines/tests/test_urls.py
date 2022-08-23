from django.test import SimpleTestCase
from django.urls import reverse, resolve
from limerines.views import indexView, all_limericks, generate_limerick, detail

class TestUrls(SimpleTestCase):

    def test_index_url_is_resolved(self):
        url = reverse('limerines:index')
        self.assertEquals(resolve(url).func, indexView)

    def test_limericks_is_resolved(self):
        url = reverse('limerines:limericks')
        self.assertEquals(resolve(url).func, all_limericks)

    def test_generate_url_is_resolved(self):
        url = reverse('limerines:generate')
        self.assertEquals(resolve(url).func, generate_limerick)

    def test_detail_url_is_resolved(self):
        url = reverse('limerines:detail', args=[0])
        self.assertEquals(resolve(url).func, detail)

    def test_edit_url_is_resolved(self):
        url = reverse('limerines:edit', args=[0])
        self.assertEquals(resolve(url).func, detail)

    def test_result_url_is_resolved(self):
        url = reverse('limerines:result', args=[0])
        self.assertEquals(resolve(url).func, detail)