from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Category, Expenses
from django.contrib import messages
from django.core.paginator import Paginator
import json
from django.http import JsonResponse
from user_preferences.models import UserPreference
from .forms import ProfileUpdateForm, ExpenseForm
import datetime
from typing import Dict, Any, List
from .receipt_scanner import ReceiptScanner
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

# Common categories that should always be available
DEFAULT_CATEGORIES = [
    'groceries', 'dining', 'transportation', 
    'shopping', 'utilities', 'health', 'entertainment',
    'rent', 'education', 'travel'
]

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
    paginator = Paginator(expenses, 10)
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
        # Handle AJAX scan request
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and 'receipt' in request.FILES:
            return scan_receipt_api(request)
            
        # Handle form submission
        form_data = request.POST.copy()
        
        # Handle custom category if 'Other' is selected
        if form_data.get('category') == 'Other' and form_data.get('custom_category'):
            form_data['category'] = form_data['custom_category']
        
        form = ExpenseForm(form_data, request.FILES)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    expense = form.save(commit=False)
                    expense.owner = request.user
                    
                    # Ensure category exists
                    category_name = expense.category
                    if not Category.objects.filter(name=category_name).exists():
                        Category.objects.create(
                            name=category_name,
                            type='EXPENSE' if expense.transaction_type == 'Expense' else 'INCOME'
                        )
                    
                    expense.save()
                    messages.success(request, 'Expense saved successfully')
                    return redirect('expenses')
            except Exception as e:
                messages.error(request, f'Error saving expense: {str(e)}')
        else:
            # Print form errors to console for debugging
            print("Form errors:", form.errors)
            messages.error(request, 'Please correct the errors below')
    else:
        form = ExpenseForm(initial={
            'date': datetime.date.today(),
            'transaction_type': 'Expense'
        })
    
    return render(request, 'expenses/add_expense.html', {
        'categories': categories,
        'form': form,
        'default_categories': DEFAULT_CATEGORIES
    })

@csrf_exempt
@login_required
def scan_receipt_api(request):
    if request.method == 'POST' and request.FILES.get('receipt'):
        try:
            receipt_file = request.FILES['receipt']
            
            # Validate file
            if receipt_file.size > 5 * 1024 * 1024:
                return JsonResponse({'error': 'File too large (max 5MB)'}, status=400)
            
            if not receipt_file.content_type.startswith('image/'):
                return JsonResponse({'error': 'Only image files allowed'}, status=400)

            scanner = ReceiptScanner()
            result = scanner.scan_receipt(receipt_file)
            
            if result and 'error' not in result:
                return JsonResponse(result)
            
            error_msg = result.get('error', 'No receipt data found')
            return JsonResponse({'error': error_msg}, status=400)
            
        except Exception as e:
            return JsonResponse({
                'error': 'Processing failed',
                'details': str(e)
            }, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required(login_url='/authentication/login/')
def expense_edit(request, id):
    expense = get_object_or_404(Expenses, pk=id)
    categories = Category.objects.all()
    if request.method == 'POST':
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        date = request.POST.get('expense_date')
        category_name = request.POST.get('category')
        transaction_type = request.POST.get('transaction_type', 'Expenses')

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/edit-expense.html', {'expense': expense, 'categories': categories})

        expense.amount = amount
        expense.date = date
        expense.category = category_name
        expense.description = description
        expense.transaction_type = transaction_type
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
    expenses = Expenses.objects.filter(owner=request.user)
    
    finalrep: Dict[str, float] = {}
    dates_by_category: Dict[str, List[str]] = {}

    # Get unique categories
    category_list = list(set(expense.category for expense in expenses))

    # Calculate amounts per category
    for category in category_list:
        category_expenses = expenses.filter(category=category)
        dates_by_category[category] = [
            expense.date.strftime("%Y-%m-%d") 
            for expense in category_expenses
        ]
        finalrep[category] = sum(exp.amount for exp in category_expenses)

    # Get currency preference
    user_preference = UserPreference.objects.filter(user=request.user).first()
    currency = user_preference.currency if user_preference else "USD"
    
    # Calculate summary metrics
    total_amount = sum(finalrep.values())
    percentages = {
        category: (amount / total_amount) * 100 
        for category, amount in finalrep.items()
    } if total_amount > 0 else {}
    
    average_expenses = total_amount / len(category_list) if category_list else 0

    # Find max and min categories
    max_category = max(finalrep, key=lambda k: finalrep[k]) if finalrep else None
    min_category = min(finalrep, key=lambda k: finalrep[k]) if finalrep else None

    # Calculate essential vs non-essential
    essential_categories = ["rent", "groceries", "utilities", "health"]
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
        'essential_amount': essential_amount,
        'non_essential_amount': non_essential_amount,
    }, safe=False)

@login_required(login_url='/authentication/login/')
def stats_view(request):
    return render(request, 'expenses/stats.html')