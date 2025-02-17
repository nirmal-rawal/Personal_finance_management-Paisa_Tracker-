
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Source, Income
from django.contrib import messages
from django.core.paginator import Paginator
import json
from django.http import JsonResponse
from user_preferences.models import UserPreference 
from .forms import ProfileUpdateForm 
from django.http import JsonResponse
import json
from .models import Income

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
            # Parse the search text from the request body
            search_str = json.loads(request.body).get("searchText", "")

            # Filter incomes based on the search text
            incomes = Income.objects.filter(
                amount__istartswith=search_str, owner=request.user
            ) | Income.objects.filter(
                date__istartswith=search_str, owner=request.user
            ) | Income.objects.filter(
                description__icontains=search_str, owner=request.user
            ) | Income.objects.filter(
                source__icontains=search_str, owner=request.user
            )

            # Convert the filtered incomes to a list of dictionaries
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

        # If "Other" is selected and a custom source is provided
        if source_name == "Other" and custom_source:
            # Normalize the input (convert to lowercase for comparison)
            normalized_source = custom_source.lower()

            # Check if a source with the same name (case-insensitive) exists
            existing_source = Source.objects.filter(name__iexact=custom_source).first()

            if existing_source:
                source_name = existing_source.name  # Use the existing source
            else:
                # Create a new source with consistent capitalization
                source_name = custom_source.capitalize()
                Source.objects.create(name=source_name)  

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'userincome/add_income.html', {'sources': sources})

        Income.objects.create(
            owner=request.user,
            amount=amount,
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

        income.amount = amount
        income.date = date
        income.source = source_name
        income.description = description
        income.save()

        messages.success(request, 'Income updated successfully')
        return redirect('incomes')

    return render(request, 'userincome/edit-income.html', {'income': income, 'sources': sources})

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Income

@login_required(login_url='/authentication/login/')
def delete_income(request, id):
    income = get_object_or_404(Income, pk=id, owner=request.user)
    income.delete()
    messages.success(request, 'Income deleted successfully')
    return redirect('incomes')

