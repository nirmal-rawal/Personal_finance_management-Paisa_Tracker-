# Generated by Django 5.1.5 on 2025-02-03 09:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_preferences', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userpreference',
            old_name='users',
            new_name='user',
        ),
    ]
