# Generated by Django 5.2 on 2025-04-24 16:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0002_answer'),
    ]

    operations = [
        migrations.AddField(
            model_name='choice',
            name='is_correct',
            field=models.BooleanField(default=False),
        ),
    ]
