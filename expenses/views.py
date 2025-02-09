from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Category, Expenses
from django.contrib import messages
from django.core.paginator import Paginator
import json
from django.http import JsonResponse



def search_expenses(request):
    if request.method == "POST":
        try:
            search_str = json.loads(request.body).get("searchText", "")
            expenses = Expenses.objects.filter(
                amount__istartswith=search_str, owner=request.user
            ) | Expenses.objects.filter(
                date__istartswith=search_str, owner=request.user
            ) | Expenses.objects.filter(
                description__icontains=search_str, owner=request.user
            ) | Expenses.objects.filter(
                category__icontains=search_str, owner=request.user
            )
            
            data = list(expenses.values())
            return JsonResponse(data, safe=False)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)
        
    



@login_required(login_url='/authentication/login/')
def index(request):
    category = Category.objects.all()
    expenses = Expenses.objects.filter(owner=request.user)
    
    # Pagination
    paginator = Paginator(expenses, 4)  # Show 5 expenses per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'expenses': page_obj,  # Use paginated object
    }
    return render(request, 'expenses/index.html', context)
@login_required(login_url='/authentication/login/')
def add_expense(request):
    categories = Category.objects.all()

    if request.method == "POST":
        amount = request.POST.get('amount')
        date = request.POST.get('expense_date')
        category_name = request.POST.get('category')
        custom_category = request.POST.get('custom_category', '').strip()
        description = request.POST.get('description', '')

        # If the user selects 'Other', use the custom category input
        if category_name == "Other" and custom_category:
            category_name = custom_category  # Use the custom category
            # Save custom category to the database if not already present
            Category.objects.get_or_create(name=custom_category)

        # Validate input
        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/add_expense.html', {'categories': categories})

        # Save the expense
        Expenses.objects.create(
            owner=request.user,
            amount=amount,
            date=date,
            category=category_name,
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
        category_name = request.POST.get('category')

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/edit-expense.html', {'expense': expense, 'categories': categories})

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