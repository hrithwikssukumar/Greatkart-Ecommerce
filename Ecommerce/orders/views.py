from django.shortcuts import render, redirect
from carts.models import Cart, CartItem
from .forms import OrderForm
import datetime
from .models import Order
from carts.views import _cart_id
from django.conf import settings
from django.http import JsonResponse
from django.urls import reverse
from django.shortcuts import get_object_or_404
import json
import stripe


stripe.api_key = settings.STRIPE_SECRET_KEY


def place_order(request, total=0, quantity=0):
 
    cart_id = _cart_id(request)
    current_user = request.user 
    cart_items = CartItem.objects.filter(cart__cart_id=cart_id)
    cart_count   = cart_items.count()
    
    if cart_count <= 0:
        print("No items found for the current user in the cart.")
        return redirect('productlist')

    grand_total = 0
    tax         = 0

    for cart_item in cart_items:
        total    += cart_item.product.price * cart_item.quantity
        quantity += cart_item.quantity

    tax = (2 * total) / 100
    grand_total = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            data = Order()
            data.user            = current_user
            data.first_name      = form.cleaned_data['first_name']
            data.last_name       = form.cleaned_data['last_name']
            data.email           = form.cleaned_data['email']
            data.phone_number    = form.cleaned_data['phone_number']
            data.address_line_1  = form.cleaned_data['address_line_1']
            data.address_line_2  = form.cleaned_data['address_line_2']
            data.city            = form.cleaned_data['city']
            data.state           = form.cleaned_data['state']
            data.country         = form.cleaned_data['country']
            data.order_note      = form.cleaned_data['order_note']
            data.order_total     = grand_total
            data.tax             = tax
            data.ip              = request.META.get('REMOTE_ADDR')
            data.save()

            # Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d  = datetime.date(yr, mt, dt)

            current_date = d.strftime("%Y%d%m")
            order_number = current_date + str(data.id)  # Corrected to use 'data.id'
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user,is_ordered=False,order_number=order_number)
            context ={
                'order'      : order,
                'cart_items' : cart_items,
                'total'      : total,
                'tax'        : tax,
                'grand_total':grand_total,
                'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLISHABLE_KEY,

            }

            return render(request,'orders/payments.html',context)
        else:
            print(form.errors)    
    else:
        form = OrderForm()        

    return render(request, 'cart/checkout.html', {'form': form, 'cart_items': cart_items, 'grand_total': grand_total})




def create_checkout_session(request):
    print("create_checkout_session called")

    cart_id = _cart_id(request)
    cart_items = CartItem.objects.filter(cart__cart_id=cart_id)
    
    total = 0
    for cart_item in cart_items:
        total += cart_item.product.price * cart_item.quantity

    grand_total = total 

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Order Payment',
                        },
                        'unit_amount': int(grand_total * 100),  # Convert to cents
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('checkout_success')),
            cancel_url=request.build_absolute_uri(reverse('checkout_cancel')),
        )

       

        return JsonResponse({'id': checkout_session.id})
    except Exception as e:
        print("Error:", str(e)) 
        return JsonResponse({'error': str(e)})



def checkout_success(request,order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.payment_method == 'STRIPE':
        try:
            payment = Payment.objects.get(order=order)
            payment_intent = stripe.PaymentIntent.retrieve(payment.payment_id)
            if payment_intent.status == 'succeeded':
                order.is_paid = True
                payment.payment_status = 'Succeeded'
                order.save()
                payment.save()
                order.cart.cartitem_set.all().delete()  
                messages.success(request, "Your payment was successful!")
            else:
                messages.warning(request, f"Payment not completed: {payment_intent.status}. Please try again.")
        except Exception as e:
            messages.error(request, f"Error fetching payment status: {str(e)}")


    return render(request, 'order/order_confirmation.html', {'order': order})




def checkout_cancel(request):
    return render(request, 'products/checkout_cancel.html')  



# def stripe_checkout(request):
#     stripe.api_key = settings.STRIPE_SECRET_KEY

#     # cart_items = get_user_cart_items(request.user)  # This could be a query to retrieve cart items
#     # grand_total = sum(cart_item.price * cart_item.quantity for cart_item in cart_items)

#     if request.method == 'POST':
#         checkout_session = stripe.checkout.Session.create(
#             payment_method_types=['card'],
#             line_items=[
#                 {
#                     'price_data': {
#                         'currency': 'usd',
#                         'product_data': {
#                             'name': 'Order Payment',
#                         },
#                         'unit_amount': int(grand_total * 100),  # Convert to cents
#                     },
#                     'quantity': 1,
#                 },
#             ],
#             mode='payment',
#             customer_creation='always',
#             success_url=settings.REDIRECT_DOMAIN + '/payment_successful?session_id={CHECKOUT_SESSION_ID}',
#             cancel_url=settings.REDIRECT_DOMAIN + '/payment_cancelled',
#         )
#         return JsonResponse({'id': checkout_session.id})
#     return render(request, 'order/payments.html')  


