# Generated by Django 5.1.5 on 2025-03-30 07:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expenses', '0014_alter_category_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expenses',
            name='transaction_type',
            field=models.CharField(choices=[('Expense', 'Expense'), ('Income', 'Income')], max_length=50),
        ),
    ]
