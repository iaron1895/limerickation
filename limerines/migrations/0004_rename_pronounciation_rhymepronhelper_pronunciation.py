# Generated by Django 4.1 on 2022-08-11 17:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('limerines', '0003_rhymepronhelper'),
    ]

    operations = [
        migrations.RenameField(
            model_name='rhymepronhelper',
            old_name='pronounciation',
            new_name='pronunciation',
        ),
    ]
