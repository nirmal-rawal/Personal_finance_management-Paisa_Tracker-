# Generated by Django 5.1.5 on 2025-03-17 16:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userincome', '0003_alter_income_amount_alter_income_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='income',
            name='transaction_type',
            field=models.CharField(choices=[('Income', 'Income')], default='Expenses', max_length=10),
            preserve_default=False,
        ),
    ]
