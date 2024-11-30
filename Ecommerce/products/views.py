from django.shortcuts import render,get_object_or_404
from django.shortcuts import render,redirect,reverse
from. models import Product,Wishlist
import random
from django.core.paginator import EmptyPage,PageNotAnInteger,Paginator
from category.models import Category
from carts.models import CartItem
from carts.views import _cart_id
from django.http import HttpResponse
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required




# Create your views here.
def index(request):

    products = Product.objects.all().filter(is_available = True) 
    context = {
        'products': products,  
    }
    return render(request,'home.html',context)
    
    
@login_required(login_url ='signin')
def list_products(request,category_slug = None):

    categories = None
    products   = None
    product_count =0
    
    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category = categories, is_available = True)
        paginator = Paginator(products,1)
        page  = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
        
    else:
        products = Product.objects.all().filter(is_available = True).order_by('id')
        paginator = Paginator(products,4)
        page  = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    
    context = {
        'products': paged_products,
        'product_count' : product_count,
    }
    return render(request,'products/productslist.html',context)




@login_required(login_url ='signin')
def detail_product(request,category_slug,product_slug):

    try:
        single_product = get_object_or_404(Product, category__slug=category_slug, slug=product_slug)

        # in_wishlist = Wishlist.objects.filter(user=request.user, product=single_product).exists()

        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request),product = single_product)
        
    except Exception as e:
        raise e

    context = {
      'single_product' : single_product,
      'in_cart'        : in_cart,
    #   'in_wishlist': in_wishlist,
    }

    return render(request, 'products/productdetails.html',context )



def product_search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if 'keyword':
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count =products.count()

    context = {
      'products' : products,
      'product_count' :product_count,
     
    }       
    return render(request, 'products/productslist.html',context)

@login_required(login_url ='signin')
def wishlist_view(request):

    wishlist_items = Wishlist.objects.filter(user=request.user)
      # Assuming each user has their own wishlist
    return render(request, 'products/wishlist.html', {'wishlist_items': wishlist_items})



def add_to_wishlist(request, product_id):
    
    product = get_object_or_404(Product, id=product_id)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    
    if created:
        messages.success(request, "Product added to your wishlist.")
    else:
        messages.info(request, "Product is already in your wishlist.")
    
    return redirect('add-to-wishlist')  # Adjust 'wishlist' to your


def remove_wishlist_item(request, product_id):
    # Get the item from the wishlist if it exists
    wishlist_item = get_object_or_404(Wishlist, user=request.user, product_id=product_id)
    
    # Delete the item from the wishlist
    wishlist_item.delete()
    return render(request, 'products/wishlist.html')