from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Source, Income
from django.contrib import messages
from django.core.paginator import Paginator
import json
from django.http import JsonResponse
from user_preferences.models import UserPreference
from .forms import ProfileUpdateForm
from django.db.models import Sum
from datetime import date, timedelta
from typing import Dict, Any, List
from django.views.decorators.csrf import csrf_exempt
from .receipt_scanner import IncomeReceiptScanner
import datetime
from django.db import transaction
from django.http import HttpResponse
import csv
import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
from django.db import models




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

@csrf_exempt
def search_incomes(request):
    if request.method == "POST":
        try:
            search_str = json.loads(request.body).get("searchText", "")
            incomes = Income.objects.filter(
                amount__istartswith=search_str, owner=request.user
            ) | Income.objects.filter(
                date__istartswith=search_str, owner=request.user
            ) | Income.objects.filter(
                description__icontains=search_str, owner=request.user
            ) | Income.objects.filter(
                source__icontains=search_str, owner=request.user
            )
            data = list(incomes.values())
            return JsonResponse(data, safe=False)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    return JsonResponse({"error": "Invalid request"}, status=400)

@login_required(login_url='/authentication/login/')
def index(request):
    sources = Source.objects.all()
    incomes = Income.objects.filter(owner=request.user)
    paginator = Paginator(incomes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    user_preference, created = UserPreference.objects.get_or_create(user=request.user, defaults={"currency": "USD"})
    currency = user_preference.currency

    context = {
        'incomes': page_obj,
        "currency": currency,
    }
    return render(request, 'userincome/index.html', context)
@login_required(login_url='/authentication/login/')
def add_income(request):
    sources = Source.objects.all()

    if request.method == "POST":
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and 'receipt' in request.FILES:
            return scan_income_receipt_api(request)
            
        amount = request.POST.get('amount')
        date = request.POST.get('income_date')
        source_name = request.POST.get('source')
        custom_source = request.POST.get('custom_source', '').strip()
        description = request.POST.get('description', '')
        transaction_type = request.POST.get('transaction_type', 'Income')

        if source_name == "Other" and custom_source:
            normalized_source = custom_source.lower()
            existing_source = Source.objects.filter(name__iexact=custom_source).first()

            if existing_source:
                source_name = existing_source.name
            else:
                source_name = custom_source.capitalize()
                Source.objects.create(name=source_name)

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'userincome/add_income.html', {'sources': sources})

        Income.objects.create(
            owner=request.user,
            amount=float(amount),
            date=date,
            source=source_name,
            description=description,
            transaction_type=transaction_type
        )
        messages.success(request, 'Income saved successfully')
        return redirect('incomes')

    return render(request, 'userincome/add_income.html', {
        'sources': sources,
        'default_date': datetime.date.today().strftime('%Y-%m-%d')
    })

@login_required(login_url='/authentication/login/')
def income_edit(request, id):
    income = get_object_or_404(Income, pk=id)
    sources = Source.objects.all()

    if request.method == 'POST':
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        date = request.POST.get('income_date')
        source_name = request.POST.get('source')
        transaction_type = request.POST.get('transaction_type', 'Income')

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'userincome/edit-income.html', {'income': income, 'sources': sources})

        income.amount = float(amount)  # Ensure amount is a float
        income.date = date
        income.source = source_name
        income.description = description
        income.transaction_type = transaction_type
        income.save()

        messages.success(request, 'Income updated successfully')
        return redirect('incomes')

    return render(request, 'userincome/edit-income.html', {'income': income, 'sources': sources})

@login_required(login_url='/authentication/login/')
def delete_income(request, id):
    income = get_object_or_404(Income, pk=id, owner=request.user)
    income.delete()
    messages.success(request, 'Income deleted successfully')
    return redirect('incomes')

@login_required(login_url='/authentication/login/')
def income_category_summary(request):
    incomes = Income.objects.filter(owner=request.user)  # Removed date filter
    finalrep: Dict[str, float] = {}

    # Data for Pie Chart (Income Distribution by Category)
    for income in incomes:
        source = income.source
        if source in finalrep:
            finalrep[source] += float(income.amount)
        else:
            finalrep[source] = float(income.amount)

    total_income = sum(finalrep.values())
    income_percentages = {source: (amount / total_income) * 100 for source, amount in finalrep.items()} if total_income > 0 else {}

    top_3_sources = sorted(finalrep.items(), key=lambda x: x[1], reverse=True)[:3] if finalrep else []
    top_3_sources_names = [source[0] for source in top_3_sources]
    top_3_sources_amounts = [source[1] for source in top_3_sources]
    top_3_sources_percentages = [income_percentages.get(source[0], 0) for source in top_3_sources]

    min_income_source = min(finalrep.items(), key=lambda x: x[1]) if finalrep else ("None", 0)
    min_income_source_name = min_income_source[0]
    min_income_source_amount = min_income_source[1]
    min_income_source_percentage = income_percentages.get(min_income_source_name, 0)

    monthly_income: Dict[str, float] = {}
    for income in incomes:
        month = income.date.strftime("%Y-%m")
        if month in monthly_income:
            monthly_income[month] += float(income.amount)
        else:
            monthly_income[month] = float(income.amount)

    max_peaked_month = max(monthly_income.items(), key=lambda x: x[1]) if monthly_income else ("None", 0)
    max_peaked_month_name = max_peaked_month[0]
    max_peaked_month_amount = max_peaked_month[1]
    max_peaked_month_percentage = (max_peaked_month_amount / total_income) * 100 if total_income > 0 else 0

    daily_income: Dict[str, float] = {}
    daily_income_source: Dict[str, str] = {}
    for income in incomes:
        day = income.date.strftime("%Y-%m-%d")
        if day in daily_income:
            daily_income[day] += float(income.amount)
        else:
            daily_income[day] = float(income.amount)
        daily_income_source[day] = income.source  # Store the source for each day

    last_3_months = sorted(monthly_income.keys(), reverse=True)[:3] if monthly_income else []
    if len(last_3_months) >= 2:
        latest_month_income = monthly_income[last_3_months[0]]
        previous_month_income = monthly_income[last_3_months[1]]
        growth_rate = ((latest_month_income - previous_month_income) / previous_month_income) * 100
    else:
        growth_rate = 0

    average_income = total_income / len(monthly_income) if monthly_income else 0
    average_income_percentage = (average_income / total_income) * 100 if total_income > 0 else 0

    user_preference = UserPreference.objects.filter(user=request.user).first()
    currency = user_preference.currency if user_preference else "USD"

    return JsonResponse({
        'income_source_data': finalrep,
        'income_percentages': income_percentages,
        'monthly_income_data': monthly_income,
        'daily_income_data': daily_income,
        'daily_income_source': daily_income_source,  # Include daily income source
        'currency': currency,
        'top_3_sources': {
            'names': top_3_sources_names,
            'amounts': top_3_sources_amounts,
            'percentages': top_3_sources_percentages,
        },
        'min_income_source': {
            'name': min_income_source_name,
            'amount': min_income_source_amount,
            'percentage': min_income_source_percentage,
        },
        'max_peaked_month': {
            'name': max_peaked_month_name,
            'amount': max_peaked_month_amount,
            'percentage': max_peaked_month_percentage,
        },
        'growth_rate': growth_rate,
        'average_income': {
            'amount': average_income,
            'percentage': average_income_percentage,
        },
    }, safe=False)

@csrf_exempt
@login_required
def scan_income_receipt_api(request):
    if request.method == 'POST' and request.FILES.get('receipt'):
        try:
            receipt_file = request.FILES['receipt']
            
            if receipt_file.size > 5 * 1024 * 1024:
                return JsonResponse({'error': 'File too large (max 5MB)'}, status=400)
            
            if not receipt_file.content_type.startswith('image/'):
                return JsonResponse({'error': 'Only image files allowed'}, status=400)

            scanner = IncomeReceiptScanner()
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
def income_summary(request):
    return render(request, 'userincome/income_stats.html')


def export_income_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Incomes_' + str(datetime.datetime.now().strftime('%Y-%m-%d')) + '.csv'

    writer = csv.writer(response)
    writer.writerow(['Amount', 'Description', 'Source', 'Date'])

    incomes = Income.objects.filter(owner=request.user)
    for income in incomes:
        writer.writerow([income.amount, income.description, income.source, income.date])

    return response

def export_income_pdf(request):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setTitle(f"Incomes Report - {datetime.datetime.now().strftime('%Y-%m-%d')}")

    # Set up PDF content
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 750, "Incomes Report")
    p.setFont("Helvetica", 12)
    p.drawString(100, 730, f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Table headers
    y = 700
    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, y, "Amount")
    p.drawString(180, y, "Description")
    p.drawString(330, y, "Source")
    p.drawString(430, y, "Date")
    
    # Table content
    p.setFont("Helvetica", 10)
    incomes = Income.objects.filter(owner=request.user)
    for income in incomes:
        y -= 20
        p.drawString(100, y, str(income.amount))
        p.drawString(180, y, income.description)
        p.drawString(330, y, income.source)
        p.drawString(430, y, str(income.date))

    p.showPage()
    p.save()
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=Incomes_{datetime.datetime.now().strftime("%Y-%m-%d")}.pdf'
    return response