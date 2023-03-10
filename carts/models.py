from email.policy import default
from tokenize import blank_re
from django.db import models
from accounts.models import Account
from store.models import Product, Variation

# Create your models here.


class Cart(models.Model):

    cart_id = models.CharField(max_length=255,blank = True)
    date_added = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return self.cart_id


class CartItem(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation,blank=True)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)
    user = models.ForeignKey(Account,on_delete=models.CASCADE,null=True)


    def subtotal(self):
        return self.product.price * self.quantity
        
    def __unicode__(self):
        return self.product