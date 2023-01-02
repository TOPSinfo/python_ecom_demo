
from django.shortcuts import render,redirect,get_object_or_404
from accounts.forms import RegisterationForm ,UserProfileForm , UserForm
from accounts.models import Account , UserProfile
from django.contrib import messages
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from carts.models import Cart , CartItem
from orders.models import Order ,OrderProduct
from carts.views import _cart_id
import requests

## email verification

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

def register(request):

    if request.method == 'POST':
        form = RegisterationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            username =  email.split('@')[0]
            user = Account.objects.create(first_name=first_name, last_name=last_name, email=email,username=username ,password=password)
            user.phone_number = phone_number
            user.save()


            ## create user profile 

            user_profile = UserProfile()
            user_profile.profile_pic = 'default/profile_pic.jpg'
            user_profile.user = user
            user_profile.save()

            #activate user account

            current_site = get_current_site(request)
            mail_subjet = "Please activate your account"
            message = render_to_string('accounts/activate.html',{

                'user': user,
                'domain' : current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token' : default_token_generator.make_token(user),
            })

            to_email = email
            send_mail = EmailMessage(mail_subjet,message,to=[to_email])
            send_mail.send()

            # messages.success(request,"Registeration successful.")
            return redirect('/accounts/login/?command=verification&email=' + email)
    else:
        form = RegisterationForm

    context = {
        "form": form,
    }
    return render(request,'accounts/register.html',context)


def login(request):
    if request.method=='POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = auth.authenticate(email=email,password=password)

        if user is not None:

            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)

                    # Getting product variations
                    product_varitaions =[]
                    for item in cart_item:
                        variation = item.variations.all()
                        product_varitaions.append(list(variation))
                    
                    cart_item = CartItem.objects.filter(user=user)
                    ex_var_list =[]
                    id = []
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)
                    
                    for pr in product_varitaions:
                        if pr in ex_var_list:   
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item =CartItem.objects.get(id=item_id)
                            item.quantity +=1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()

            except:
                pass

            auth.login(request,user)
            # messages.success(request,)

            url =request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    return redirect(params['next'])
            except:
                return redirect('dashboard')
        else:
            messages.error(request,"Inavlid credentials. ")
            return redirect('login')
    return render(request,'accounts/login.html')

@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    messages.success(request,"logout successful")
    return redirect('login')



def activate(request,uidb64,token):

    try:
        uid = urlsafe_base64_decode(uidb64)
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user,token):
        user.is_active = True
        user.save()
        messages.success(request,"Congratulations your Account is now Activated")
        return redirect('login')
    
    else:
        messages.error(request,"Invalid activation link")
        return redirect('register')
    

@login_required(login_url='login')
def dashboard(request):

    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id,is_ordered=True)
    orders_count = orders.count()

    user_profile = UserProfile.objects.get(user = request.user)

    context ={
        'orders_count' : orders_count,
        'user_profile' : user_profile,
    }
    return render(request,'accounts/dashboard.html',context)

def forgotpassword(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)
            
            current_site = get_current_site(request)
            mail_subjet = "Reset Password"
            message = render_to_string('accounts/reset_password_email.html',{

                'user': user,
                'domain' : current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token' : default_token_generator.make_token(user),
            })

            to_email = email
            send_mail = EmailMessage(mail_subjet,message,to=[to_email])
            send_mail.send()

            messages.success(request,"Password reset email has been sent")

            return redirect('login')


        else:
            messages.error(request,"Account does not exist")
            return redirect('forgotpassword')

    return render(request,'accounts/forgotpassword.html')



def resetpassword_validate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user,token):
        request.session["uid"] = uid
        messages.success(request,"Please reset your password")
        return redirect('resetpassword')
    
    else:
        messages.error(request,"Link has been expired")
        return redirect('login')
        

def resetpassword(request):

    if request.method == "POST":
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,"Password successfully reset")
            return redirect('login')
        
        else:
            messages.error("Passwords don't match")
            return redirect('resetpassword')
    else:
        return render(request,'accounts/resetpassword.html')


@login_required(login_url='login')
def my_orders(request):

    orders = Order.objects.filter(user = request.user,is_ordered=True).order_by('-created_at')

    context = {
        "orders": orders,
    }


    
    return render(request,'accounts/myorders.html',context)


@login_required(login_url='login')
def edit_profile(request):
    user_profile = get_object_or_404(UserProfile,user= request.user)

    if request.method == 'POST':
        user_form = UserForm(request.POST,instance=request.user)
        profile_form = UserProfileForm(request.POST,request.FILES,instance=user_profile)
        if user_form.is_valid() and profile_form.is_valid() :
            user_form.save()
            profile_form.save()
            messages.success(request,"Your profile has been updated")
            return redirect('edit_profile')

    else:
            user_form = UserForm(instance=request.user)
            profile_form = UserProfileForm(instance=user_profile)
        
    context = {
                "user_form": user_form,
                "profile_form": profile_form,
                "user_profile": user_profile,
            }

    
    return render(request,'accounts/edit_profile.html',context)

@login_required(login_url='login')
def change_password(request):

    if request.method == 'POST':

        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        user = Account.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            success = user.check_password(current_password)

            if success:
                user.set_password(new_password)
                user.save()
                messages.success(request,'Password changed successfully')
                return redirect('change_password')
            else:
                messages.error(request,"Invalid current password")
                return redirect('change_password')

        else:
            messages.error(request,"Passwords didn't match")
            return redirect('change_password')
    context = {}
    return render(request,'accounts/change_password.html',context)



def order_detail(request,order_id):

    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)

    subtotal=0
    for i in order_detail:
        subtotal += i.product_price * i.quantity

    context = {
        "order_detail": order_detail,
        "order":order,
        "subtotal" :subtotal
    }


    return render(request,'accounts/order_detail.html',context)