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
            data = list(incomes.values('id', 'amount', 'date', 'description', 'source'))
            return JsonResponse(data, safe=False)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=400)

@login_required(login_url='/authentication/login/')
def index(request):
    sources = Source.objects.all()
    incomes = Income.objects.filter(owner=request.user)
    paginator = Paginator(incomes, 4)
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
        amount = request.POST.get('amount')
        date = request.POST.get('income_date')
        source_name = request.POST.get('source')
        custom_source = request.POST.get('custom_source', '').strip()
        description = request.POST.get('description', '')

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
            amount=float(amount),  # Ensure amount is a float
            date=date,
            source=source_name,
            description=description
        )
        messages.success(request, 'Income saved successfully')
        return redirect('incomes')

    return render(request, 'userincome/add_income.html', {'sources': sources})

@login_required(login_url='/authentication/login/')
def income_edit(request, id):
    income = get_object_or_404(Income, pk=id)
    sources = Source.objects.all()

    if request.method == 'POST':
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        date = request.POST.get('income_date')
        source_name = request.POST.get('source')

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'userincome/edit-income.html', {'income': income, 'sources': sources})

        income.amount = float(amount)  # Ensure amount is a float
        income.date = date
        income.source = source_name
        income.description = description
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
    todays_date = date.today()
    six_months_ago = todays_date - timedelta(days=30 * 6)
    incomes = Income.objects.filter(owner=request.user, date__gte=six_months_ago, date__lte=todays_date)

    # Data for Pie Chart (Income Distribution by Category)
    finalrep: Dict[str, float] = {}
    for income in incomes:
        source = income.source
        if source in finalrep:
            finalrep[source] += float(income.amount)
        else:
            finalrep[source] = float(income.amount)

    # Calculate total income
    total_income = sum(finalrep.values())

    # Calculate percentages for each income source
    income_percentages = {source: (amount / total_income) * 100 for source, amount in finalrep.items()} if total_income > 0 else {}

    # Get top 3 income sources
    top_3_sources = sorted(finalrep.items(), key=lambda x: x[1], reverse=True)[:3] if finalrep else []
    top_3_sources_names = [source[0] for source in top_3_sources]
    top_3_sources_amounts = [source[1] for source in top_3_sources]
    top_3_sources_percentages = [income_percentages.get(source[0], 0) for source in top_3_sources]

    # Get minimum income source
    min_income_source = min(finalrep.items(), key=lambda x: x[1]) if finalrep else ("None", 0)
    min_income_source_name = min_income_source[0]
    min_income_source_amount = min_income_source[1]
    min_income_source_percentage = income_percentages.get(min_income_source_name, 0)

    # Data for Bar Chart (Monthly Income Trends)
    monthly_income: Dict[str, float] = {}
    for income in incomes:
        month = income.date.strftime("%Y-%m")  # Group by year and month
        if month in monthly_income:
            monthly_income[month] += float(income.amount)
        else:
            monthly_income[month] = float(income.amount)

    # Get maximum peaked month
    max_peaked_month = max(monthly_income.items(), key=lambda x: x[1]) if monthly_income else ("None", 0)
    max_peaked_month_name = max_peaked_month[0]
    max_peaked_month_amount = max_peaked_month[1]
    max_peaked_month_percentage = (max_peaked_month_amount / total_income) * 100 if total_income > 0 else 0

    # Data for Line Chart (Daily Income Growth)
    daily_income: Dict[str, float] = {}
    for income in incomes:
        day = income.date.strftime("%Y-%m-%d")  # Group by day
        if day in daily_income:
            daily_income[day] += float(income.amount)
        else:
            daily_income[day] = float(income.amount)

    # Calculate growth rate over the last 3 months
    last_3_months = sorted(monthly_income.keys(), reverse=True)[:3] if monthly_income else []
    if len(last_3_months) >= 2:
        latest_month_income = monthly_income[last_3_months[0]]
        previous_month_income = monthly_income[last_3_months[1]]
        growth_rate = ((latest_month_income - previous_month_income) / previous_month_income) * 100
    else:
        growth_rate = 0

    # Calculate average income
    average_income = total_income / len(monthly_income) if monthly_income else 0
    average_income_percentage = (average_income / total_income) * 100 if total_income > 0 else 0

    # Get user's currency preference
    user_preference = UserPreference.objects.filter(user=request.user).first()
    currency = user_preference.currency if user_preference else "USD"

    return JsonResponse({
        'income_source_data': finalrep,  # For Pie Chart
        'income_percentages': income_percentages,  # Percentages for Pie Chart
        'monthly_income_data': monthly_income,  # For Bar Chart
        'daily_income_data': daily_income,  # For Line Chart
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

@login_required(login_url='/authentication/login/')
def income_summary(request):
    return render(request, 'userincome/income_stats.html')