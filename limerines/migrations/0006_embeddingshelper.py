# Generated by Django 4.1 on 2022-08-18 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('limerines', '0005_rename_pronounciation_limerick_pronunciation'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmbeddingsHelper',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('word_score', models.JSONField(null=True)),
            ],
        ),
    ]
