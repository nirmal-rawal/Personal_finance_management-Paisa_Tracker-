import csv
from django.core.management.base import BaseCommand
from expenses.models import Expenses, Category
from userincome.models import Income, Source
from django.contrib.auth.models import User
from datetime import datetime

class Command(BaseCommand):
    help = 'Import data from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username of the user to associate with the data')

    def handle(self, *args, **kwargs):
        username = kwargs['username']
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User with username "{username}" does not exist'))
            return

        with open('updated_personal_transactions.csv', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                date = datetime.strptime(row['Date'], '%m/%d/%Y').date()
                description = row['Description']
                amount = float(row['Amount'])
                transaction_type = row['Transaction Type']
                category = row['Category']

                if transaction_type == 'Income':
                    source, _ = Source.objects.get_or_create(name=category)
                    if not Income.objects.filter(
                        owner=user,
                        amount=amount,
                        date=date,
                        description=description,
                        source=source.name,
                        transaction_type=transaction_type
                    ).exists():
                        Income.objects.create(
                            owner=user,
                            amount=amount,
                            date=date,
                            description=description,
                            source=source.name,
                            transaction_type=transaction_type
                        )
                        self.stdout.write(self.style.SUCCESS(f'Income record added: {description} on {date}'))
                else:
                    category_obj, _ = Category.objects.get_or_create(name=category)
                    if not Expenses.objects.filter(
                        owner=user,
                        amount=amount,
                        date=date,
                        description=description,
                        category=category_obj.name,
                        transaction_type=transaction_type
                    ).exists():
                        Expenses.objects.create(
                            owner=user,
                            amount=amount,
                            date=date,
                            description=description,
                            category=category_obj.name,
                            transaction_type=transaction_type
                        )
                        self.stdout.write(self.style.SUCCESS(f'Expense record added: {description} on {date}'))

        self.stdout.write(self.style.SUCCESS('Data import process completed'))