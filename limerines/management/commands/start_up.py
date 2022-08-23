from django.core.management.base import BaseCommand, CommandError
from limerines.models import AdjProfHelper, EmbeddingsHelper, RhymePronHelper, TemplateHelper

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        try:
            if not AdjProfHelper.object():
                a = AdjProfHelper()
                a.construct()
                a.save()
            if not TemplateHelper.object():
                t = TemplateHelper()
                t.construct()
                t.save()
            if not RhymePronHelper.object():
                r = RhymePronHelper()
                r.save()
            if not EmbeddingsHelper.object():
                e = EmbeddingsHelper()
                e.save()
        except:
            raise CommandError('Initalization failed.')