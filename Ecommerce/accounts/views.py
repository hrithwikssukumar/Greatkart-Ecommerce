from django.shortcuts import render,redirect
from.forms import RegistrationForm
from. models import Account
from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required
from carts.views import _cart_id
from carts.models import Cart,CartItem
import random
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.core.mail import EmailMessage
from django.http import HttpResponse
import requests



def user_register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Extracting cleaned data from form
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]


            user = Account.objects.create_user(
                first_name   = first_name,
                last_name    = last_name,
                email        = email,
                phone_number = phone_number,
                username     = username,
                password     = password
            )
        

            current_site = get_current_site(request)
            mail_subject = "Activate your Account"
            message      = render_to_string('accounts/verification_email.html',{

                'user'   : user,
                'domain' : current_site,
                'uid'    : urlsafe_base64_encode(force_bytes(user.pk)),
                'token'  : default_token_generator.make_token(user),
            })

            to_email   = email
            send_mail = EmailMessage(mail_subject,message,to=[to_email])
            send_mail.send()
            # messages.success(request,'Thank you for registering with us.We have sent you a verification email to your email address.Please verify it')
            return redirect('/accounts/signin/?command=verification&email=' +email)
            

        else:       
            print(form.errors)
            messages.error(request, "Something went wrong. Please check your inputs.")
    else:
    
        form = RegistrationForm()

    context = {
        'form': form
    }
    return render(request, 'accounts/register.html', context)



def activate_user(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Congratulations! Your account is activated.")
        return redirect('signin')
    else:
        messages.error(request, "Activation link is invalid.")
        return redirect('register')
 


def user_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        print(f"Trying to authenticate user: {email} with password: {password}")

        # Authenticate the user
        user = auth.authenticate(email=email, password=password)

        if user is not None:
            # Check if the user is an admin
            if user.is_admin:
                return redirect('admindashboard')

            try:
                print('entering inside try block')
                # Retrieve the cart using a custom cart ID (assuming _cart_id function exists)
                cart = Cart.objects.get(cart_id=_cart_id(request))
                # Check if any cart items exist in the cart
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists() 
                
                if is_cart_item_exists:
                    cart_items = CartItem.objects.filter(cart=cart)
                    print('cart_item')

                    # Assign each cart item to the authenticated user
                    for item in cart_items:
                        item.user = user  
                        item.save()

            except Cart.DoesNotExist:
                print('entering inside except block')
                # If no cart exists, pass silently or handle the error accordingly
                pass

            # Log in the user and redirect to the home page
            auth.login(request, user)
            messages.success(request, 'You are now logged in')
            
            url = request.META.get('HTTP_REFERER')

            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextpage = params['next']
                    return redirect(nextpage)
            except:
                return redirect('dashboard')

        else:
            # Authentication failed
            print("Authentication failed")
            messages.error(request, 'Invalid credentials')
            return redirect('signin')
    return render(request, 'accounts/signin.html')


@login_required(login_url='home')
def user_logout(request):
    
    auth.logout(request)
    messages.success(request,'You are logged out')
    return redirect('home')

@login_required(login_url='home')
def user_dashboard(request):
    return render(request,'accounts/dashboard.html')



def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            #Reset password email
            current_site = get_current_site(request)
            mail_subject = "Reset your Password"
<<<<<<< HEAD
            message      = render_to_string('accounts/reset_password_email.html',{
=======
            message      = render_to_string('reset_password_email.html',{
>>>>>>> d8d3cc2de849e562af530613781fe9fd17d134fa

                'user'   : user,
                'domain' : current_site,
                'uid'    : urlsafe_base64_encode(force_bytes(user.pk)),
                'token'  : default_token_generator.make_token(user),
            })

            to_email   = email
            send_mail = EmailMessage(mail_subject,message,to=[to_email])
            send_mail.send()
            messages.success(request,'Password reset email has been sent to your email address')
            return redirect('signin')

        else:
            messages.error(request,'Account does not exist')  
            return redirect('forgotpassword')  
    return render(request,'accounts/forgotpassword.html')   
    

def resetpassword_validate(request,uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request,'Please reset your password')
        return redirect('resetpassword' )
    else:
        messages.error(request,'This link has been expired')
        return render('signin')    

def reset_password(request):
    if request.method =='POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,'Password reset success!')
            return redirect('signin')
        else:
            messages.error(request,'Passwords do not match!') 
            return redirect('resetpassword')

    else:
        return render(request,'accounts/resetpassword.html')






