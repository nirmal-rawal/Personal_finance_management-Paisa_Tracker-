from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Category, Expenses, Notification
from django.contrib import messages
from django.core.paginator import Paginator
import json
from django.http import JsonResponse, HttpResponse
from user_preferences.models import UserPreference
from .forms import ProfileUpdateForm, ExpenseForm
import datetime
from typing import Dict, Any, List
from .receipt_scanner import ReceiptScanner
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.template import Template, Context
import csv

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO



# Common categories that should always be available
DEFAULT_CATEGORIES = [
    'groceries', 'dining', 'transportation', 
    'shopping', 'utilities', 'health', 'entertainment',
    'rent', 'education', 'travel'
]

@login_required
def profile(request):
    return render(request, 'profile.html')

def test_filter(request):
    template = Template("""
        {% load custom_filters %}
        {{ 50|div:200 }}%
    """)
    context = Context({})
    return render(request, 'test.html', {'result': template.render(context)})

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
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and 'receipt' in request.FILES:
            return scan_receipt_api(request)
            
        form_data = request.POST.copy()
        
        if form_data.get('category') == 'Other' and form_data.get('custom_category'):
            form_data['category'] = form_data['custom_category']
        
        form = ExpenseForm(form_data, request.FILES)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    expense = form.save(commit=False)
                    expense.owner = request.user
                    
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
    expense = get_object_or_404(Expenses, pk=id, owner=request.user)
    categories = Category.objects.filter(type='EXPENSE')
    user_preference = UserPreference.objects.get(user=request.user)
    
    if request.method == 'POST':
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        date = request.POST.get('expense_date')
        
        # Handle custom category
        category_name = request.POST.get('category')
        custom_category = request.POST.get('custom_category', '').strip()
        
        if category_name == 'Other' and custom_category:
            category_name = custom_category
        
        transaction_type = request.POST.get('transaction_type', 'Expense')

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/edit-expense.html', {
                'expense': expense,
                'categories': categories,
                'currency': user_preference.currency
            })

        expense.amount = amount
        expense.date = date
        expense.category = category_name
        expense.description = description
        expense.transaction_type = transaction_type
        
        # Create new category if it doesn't exist
        if not Category.objects.filter(name=category_name).exists():
            Category.objects.create(
                name=category_name,
                type='EXPENSE'
            )
        
        expense.save()
        messages.success(request, 'Expense updated successfully')
        return redirect('expenses')
        
    return render(request, 'expenses/edit-expense.html', {
        'expense': expense,
        'categories': categories,
        'currency': user_preference.currency
    })

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

    category_list = list(set(expense.category for expense in expenses))

    for category in category_list:
        category_expenses = expenses.filter(category=category)
        dates_by_category[category] = [
            expense.date.strftime("%Y-%m-%d") 
            for expense in category_expenses
        ]
        finalrep[category] = sum(exp.amount for exp in category_expenses)

    user_preference = UserPreference.objects.filter(user=request.user).first()
    currency = user_preference.currency if user_preference else "USD"
    
    total_amount = sum(finalrep.values())
    percentages = {
        category: (amount / total_amount) * 100 
        for category, amount in finalrep.items()
    } if total_amount > 0 else {}
    
    average_expenses = total_amount / len(category_list) if category_list else 0

    max_category = max(finalrep, key=lambda k: finalrep[k]) if finalrep else None
    min_category = min(finalrep, key=lambda k: finalrep[k]) if finalrep else None

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

@login_required
def notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    paginator = Paginator(notifications, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'expenses/notifications.html', {'notifications': page_obj})

@login_required
def mark_notification_as_read(request, id):
    notification = get_object_or_404(Notification, pk=id, user=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'success': True})


@login_required
def mark_all_notifications_read(request):
    if request.method == 'POST':
        try:
            # Mark all unread notifications as read for the current user
            updated_count = Notification.objects.filter(
                user=request.user,
                is_read=False
            ).update(is_read=True)
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Marked {updated_count} notifications as read'
                })
            messages.success(request, f'Marked {updated_count} notifications as read')
            return redirect('notifications')
        except Exception as e:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                }, status=500)
            messages.error(request, f'Error marking notifications as read: {str(e)}')
            return redirect('notifications')
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': False,
            'error': 'Invalid request method'
        }, status=405)
    return redirect('notifications')

@login_required
def get_unread_notifications(request):
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    recent_notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')[:5]
    
    notifications_data = [{
        'id': n.id,
        'message': n.message,
        'type': n.notification_type,
        'created_at': n.created_at.strftime("%b %d, %Y %H:%M"),
        'is_read': n.is_read,
        'url': n.related_url or '#'
    } for n in recent_notifications]
    
    return JsonResponse({
        'unread_count': unread_count,
        'notifications': notifications_data
    })

@login_required(login_url='/authentication/login/')
def stats_view(request):
    return render(request, 'expenses/stats.html')

def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Expenses_' + str(datetime.datetime.now().strftime('%Y-%m-%d')) + '.csv'

    writer = csv.writer(response)
    writer.writerow(['Amount', 'Description', 'Category', 'Date'])

    expenses = Expenses.objects.filter(owner=request.user)
    for expense in expenses:
        writer.writerow([expense.amount, expense.description, expense.category, expense.date])

    return response

def export_pdf(request):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setTitle(f"Expenses Report - {datetime.datetime.now().strftime('%Y-%m-%d')}")

    # Set up PDF content
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 750, "Expenses Report")
    p.setFont("Helvetica", 12)
    p.drawString(100, 730, f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Table headers
    y = 700
    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, y, "Amount")
    p.drawString(180, y, "Description")
    p.drawString(330, y, "Category")
    p.drawString(430, y, "Date")
    
    # Table content
    p.setFont("Helvetica", 10)
    expenses = Expenses.objects.filter(owner=request.user)
    for expense in expenses:
        y -= 20
        p.drawString(100, y, str(expense.amount))
        p.drawString(180, y, expense.description)
        p.drawString(330, y, expense.category)
        p.drawString(430, y, str(expense.date))

    p.showPage()
    p.save()
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=Expenses_{datetime.datetime.now().strftime("%Y-%m-%d")}.pdf'
    return response