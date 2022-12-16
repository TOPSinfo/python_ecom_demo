from django.urls import path
from . import views

urlpatterns = [ 
    path('',views.cart,name="carts"),
    path('add_cart/<int:product_id>/',views.add_cart,name="add_cart"),
    path('decrement_cart/<int:product_id>/<int:cart_item_id>/',views.decrement_cart,name="decrement_cart"),
    path('remove_cart/<int:product_id>/<int:cart_item_id>/',views.remove_cart,name="remove_cart"),
    path('checkout/',views.checkout,name='checkout')

]