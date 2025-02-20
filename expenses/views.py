from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Category, Expenses
from django.contrib import messages
from django.core.paginator import Paginator
import json
from django.http import JsonResponse
from user_preferences.models import UserPreference
from .forms import ProfileUpdateForm
import datetime
from typing import Dict, Any, List

@login_required
def profile(request):
    return render(request, 'profile.html')

@login_required
def edit_profile(request):
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'edit_profile.html', {'form': form})

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
    paginator = Paginator(expenses, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    user_preference, created = UserPreference.objects.get_or_create(user=request.user, defaults={"currency": "USD"})
    currency = user_preference.currency
    context = {
        'expenses': page_obj,
        "currency": currency,
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

        if category_name == "Other" and custom_category:
            category_name = custom_category
            Category.objects.get_or_create(name=custom_category)

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/add_expense.html', {'categories': categories})

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

@login_required(login_url='/authentication/login/')
def expense_category_summary(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date - datetime.timedelta(days=30 * 6)
    expenses = Expenses.objects.filter(owner=request.user, date__gte=six_months_ago, date__lte=todays_date)
    finalrep: Dict[str, float] = {}
    dates_by_category: Dict[str, List[str]] = {}

    def get_category(expense: Expenses) -> str:
        return expense.category

    category_list = list(set(map(get_category, expenses)))

    def get_expense_category_amount(category: str) -> float:
        amount = 0
        filtered_by_category = expenses.filter(category=category)
        dates_by_category[category] = [expense.date.strftime("%Y-%m-%d") for expense in filtered_by_category]
        for item in filtered_by_category:
            amount += item.amount
        return amount

    for category in category_list:
        finalrep[category] = get_expense_category_amount(category)

    user_preference = UserPreference.objects.filter(user=request.user).first()
    currency = user_preference.currency if user_preference else "USD"
    total_amount = sum(finalrep.values())
    percentages = {category: (amount / total_amount) * 100 for category, amount in finalrep.items()}
    average_expenses = total_amount / len(category_list) if category_list else 0

    # Handle empty finalrep case
    max_category = max(finalrep, key=lambda k: finalrep[k]) if finalrep else None
    min_category = min(finalrep, key=lambda k: finalrep[k]) if finalrep else None

    previous_period_start = six_months_ago - datetime.timedelta(days=30 * 6)
    previous_period_expenses = Expenses.objects.filter(owner=request.user, date__gte=previous_period_start, date__lte=six_months_ago)
    previous_total_amount = sum(exp.amount for exp in previous_period_expenses)
    expense_trend = ((total_amount - previous_total_amount) / previous_total_amount) * 100 if previous_total_amount != 0 else 0
    essential_categories = ["Rent", "Groceries", "Utilities"]
    essential_amount = sum(finalrep.get(category, 0) for category in essential_categories)
    non_essential_amount = total_amount - essential_amount

    return JsonResponse({
        'expense_category_data': finalrep,
        'currency': currency,
        'percentages': percentages,
        'total_amount': total_amount,
        'dates_by_category': dates_by_category,
        'average_expenses': average_expenses,
        'max_category': max_category,
        'min_category': min_category,
        'expense_trend': expense_trend,
        'essential_amount': essential_amount,
        'non_essential_amount': non_essential_amount,
    }, safe=False)

@login_required(login_url='/authentication/login/')
def stats_view(request):
    return render(request, 'expenses/stats.html')