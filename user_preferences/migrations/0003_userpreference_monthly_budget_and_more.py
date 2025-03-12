# Generated by Django 5.1.5 on 2025-03-12 14:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_preferences', '0002_rename_users_userpreference_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='userpreference',
            name='monthly_budget',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='userpreference',
            name='savings_goal',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
