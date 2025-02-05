from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Category, Expenses
from django.contrib import messages

@login_required(login_url='/authentication/login/')
def index(request):
    expenses = Expenses.objects.filter(owner=request.user)
    return render(request, 'expenses/index.html', {"expenses": expenses})

@login_required(login_url='/authentication/login/')
def add_expense(request):
    categories = Category.objects.all()

    if request.method == "POST":
        amount = request.POST.get('amount')
        date = request.POST.get('expense_date')
        category_name = request.POST.get('category')
        description = request.POST.get('description', '')

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/add_expense.html', {'categories': categories})

        Expenses.objects.create(
            owner=request.user,
            amount=amount,
            date=date,
            category=category_name,  # ✅ Store as a string (category name)
            description=description
        )
        messages.success(request, 'Expense saved successfully')
        return redirect('expenses')

    return render(request, 'expenses/add_expense.html', {'categories': categories})

@login_required(login_url='/authentication/login/')
def expense_edit(request, id):
    expense = get_object_or_404(Expenses, pk=id)
    categories = Category.objects.all()

    if request.method == 'POST':
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        date = request.POST.get('expense_date')
        category_name = request.POST.get('category')  # Get category name from form

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/edit-expense.html', {'expense': expense, 'categories': categories})

        # ✅ Store category as a string (not a model instance)
        expense.amount = amount
        expense.date = date
        expense.category = category_name
        expense.description = description
        expense.save()

        messages.success(request, 'Expense updated successfully')
        return redirect('expenses')

    return render(request, 'expenses/edit-expense.html', {'expense': expense, 'categories': categories})

@login_required(login_url='/authentication/login/')
def delete_expense(request, id):
    expense = get_object_or_404(Expenses, pk=id)
    expense.delete()
    messages.success(request, 'Expense removed successfully')
    return redirect('expenses')
