# Generated by Django 5.1.5 on 2025-03-30 07:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expenses', '0013_alter_category_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='type',
            field=models.CharField(choices=[('EXPENSE', 'Expense'), ('INCOME', 'Income')], default='EXPENSE', max_length=50),
        ),
    ]
