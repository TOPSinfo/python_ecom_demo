from itertools import product 
from unicodedata import category
from django.shortcuts import render , get_object_or_404 ,redirect
from carts.models import Cart, CartItem
from category.models import Category
from .models import Product
from carts.views import _cart_id
from django.core.paginator import EmptyPage,PageNotAnInteger,Paginator
from django.http import HttpResponse
from django.db.models import Q
from .models import ReviewRating ,ProductGallery
from .forms import ReviewForm
from django.contrib import messages
from orders.models import OrderProduct

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
    
   
    try:
        ordered_products = OrderProduct.objects.filter(user=request.user,product_id=product_details.id).exists()
    except :
        ordered_products = None    

    reviews = ReviewRating.objects.filter(product_id=product_details.id,status=True)

    product_gallery = ProductGallery.objects.filter(product_id = product_details.id)

    
    
    context = {
        "product_details" : product_details,
        "in_cart" : in_cart,
        "order_products" : ordered_products,
        "reviews": reviews,
        "product_gallery": product_gallery,
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



def submit_review(request,product_id):

    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':

        try:
            review = ReviewRating.objects.get(user__id=request.user.id,product__id=product_id)

            form = ReviewForm(request.POST,instance=review)
            form.save()
            messages.success(request,"Review updated Successfully")


        except:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data["subject"]
                data.review = form.cleaned_data["review"]
                data.rating = form.cleaned_data["rating"]
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request,"Review Submitted Successfully")
                return redirect(url)
