# Generated by Django 4.1 on 2022-08-05 12:39

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Limerick',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('verse1', models.CharField(max_length=100)),
                ('verse2', models.CharField(max_length=100)),
                ('verse3', models.CharField(max_length=100)),
                ('verse4', models.CharField(max_length=100)),
                ('verse5', models.CharField(max_length=100)),
                ('votes', models.IntegerField(default=0)),
                ('model_rank', models.IntegerField(default=0)),
                ('rank', models.IntegerField(default=0)),
                ('adjective', models.CharField(max_length=100)),
                ('profession', models.CharField(max_length=100)),
                ('female', models.BooleanField()),
                ('place', models.BooleanField()),
                ('pronounciation', models.JSONField(null=True)),
                ('pair', models.IntegerField(null=True)),
                ('pair2', models.IntegerField(null=True)),
                ('scored_second', models.JSONField(null=True)),
                ('scored_third', models.JSONField(null=True)),
                ('scored_fourth', models.JSONField(null=True)),
                ('scored_fifth', models.JSONField(null=True)),
                ('names', models.JSONField(null=True)),
                ('perplexity', models.FloatField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='AdjProfHelper',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('adjectives_list', models.JSONField(null=True)),
                ('profession_list', models.JSONField(null=True)),
                ('adjective_profession', models.JSONField(null=True)),
                ('places_list', models.JSONField(null=True)),
            ],
        ),
    ]
