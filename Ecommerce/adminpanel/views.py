from django.shortcuts import render,redirect,get_object_or_404
from accounts.models import Account
from accounts.forms import RegistrationForm,EditUserForm
from django.contrib import messages
from django.db import IntegrityError
from django.http import JsonResponse
from products.models import Product
from products.forms import ProductForm
from category.models import Category
from category.forms import CategoryForm



def admin_dashboard(request):
    return render(request, 'admin/admindashboard.html')

def user_dashboard(request):
    query = request.GET.get('q')
    if query:
        user_details = Account.objects.filter(
            first_name__icontains=query) | Account.objects.filter(
            last_name__icontains=query) | Account.objects.filter(
            email__icontains=query) | Account.objects.filter(
            username__icontains=query) | Account.objects.filter(
            phone_number__icontains=query)
    else:
        user_details = Account.objects.all()

    return render(request, 'admin/userdashboard.html', {'users': user_details})


def user_add(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            if not user.username:  
                user.username = user.email.split('@')[0]
            try:
                user.save()
                messages.success(request, 'User added successfully.')
                return redirect('userdashboard')
            except IntegrityError:
                messages.error(request, 'Username already exists.')
        else:
            messages.error(request, 'Invalid form submission.')
    else:
        form = RegistrationForm()

    return render(request, 'admin/useradd.html', {'form': form})

def user_edit(request,user_id):
    user = get_object_or_404(Account, id= user_id)
    if request.method == 'POST':
        form = EditUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('admindashboard')
        else:
            form = EditUserForm(instance=user)
    else:
        form = EditUserForm(instance=user)        
    return render(request, 'admin/useredit.html', {'form': form, 'user': user})
    

def user_block(request, user_id):
    if request.method == 'POST':  
        try:
            user = get_object_or_404(Account, id=user_id)
            user.is_active = False  
            user.save()  
            return redirect('admindashboard')  
        except Account.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'User does not exist'})
    return redirect('admindashboard')



def product_dashboard(request):
    query = request.GET.get('q')
    if query:
        product_details = Product.objects.filter(
            name__icontains = query)|Product.objects.filter(
            category__name__contains = query)
    else:
        product_details = Product.objects.all()
    return render(request, 'admin/productdashboard.html',{'products':product_details})


def product_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('productdashboard')  
    else:
        form = ProductForm()
    return render(request, 'admin/productadd.html', {'form': form})

def product_edit(request,id):
    product = get_object_or_404(Product, id=id)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('productdashboard')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'admin/productedit.html', {'form': form, 'product': product})



def product_delete(request, id):  
    product = get_object_or_404(Product, id=id)
    if request.method == 'POST':
        product.delete()
        return redirect('productdashboard')
    
    return render(request, 'admin/productdelete.html', {'product': product})


def category_dashboard(request):
    query = request.GET.get('q')
    if query:
        category_details = Category.objects.filter(
            name__icontains=query) | Category.objects.filter(
            category_name__icontains=query)
    else:
        category_details = Category.objects.all()
    
    return render(request, 'admin/categorydashboard.html', {'categories': category_details})



def category_add(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('categorydashboard')  
    else:
        form = CategoryForm()

    categories = Category.objects.all()  
    return render(request, 'admin/categoryadd.html', {'categories': categories, 'form': form})

    

def category_delete(request,id):
    
    category = get_object_or_404(Category, id=id)
    if request.method == 'POST':
        category.delete()
        return redirect('categorydashboard')
    
    return render(request, 'admin/categorydelete.html', {'category': category})

    

def category_edit(request,id):

    category = get_object_or_404(Category, id=id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            return redirect('categorydashboard')
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'admin/categoryedit.html', {'form': form, 'category': category})






    







