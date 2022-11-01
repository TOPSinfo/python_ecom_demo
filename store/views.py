from itertools import product
from unicodedata import category
from django.shortcuts import render , get_object_or_404
from carts.models import Cart, CartItem
from category.models import Category
from .models import Product
from carts.views import _cart_id
from django.core.paginator import EmptyPage,PageNotAnInteger,Paginator
from django.http import HttpResponse
from django.db.models import Q
# Create your views here.


def store(request, category_slug=None):
    products = None
    categories = None

    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.all().filter(category= categories,is_available=True)
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        
    paginator = Paginator(products,4)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    product_count = products.count()

    context = {
        'products': paged_products,
        'product_count': product_count
    }

    return render(request, 'store/store.html',context)


def product_details(request, category_slug,product_slug):

    try:
        product_details = Product.objects.get(category__slug= category_slug,slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id = _cart_id(request),product= product_details).exists()

    except Exception as e:
        raise e
    
    context = {
        "product_details" : product_details,
        "in_cart" : in_cart
    }
    return render(request, 'store/product_details.html',context)




def search(request):

    products = Product.objects.none()

    if 'keyword' in request.GET:
        keyword =  request.GET['keyword']
        if keyword:
            print(keyword)
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
    
    print(products)
    context = {
        'products': products,
        'product_count': products.count()
    }

    return render(request, 'store/store.html',context)
