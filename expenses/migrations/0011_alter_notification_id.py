# Generated by Django 5.1.5 on 2025-03-26 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expenses', '0010_budget_last_alert_sent_notification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
