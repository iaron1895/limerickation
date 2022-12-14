from django.core.management.base import BaseCommand, CommandError
from limerines.models import AdjProfHelper, RhymePronHelper, TemplateHelper
from transformers import GPT2LMHeadModel, GPT2Tokenizer

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
        except:
            raise CommandError('Initalization failed.')