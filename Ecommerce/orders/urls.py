from django.urls import path
from . import views

urlpatterns = [

     path('placeorder/', views.place_order, name='placeorder'),
     path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),    
     path('checkout-success/', views.checkout_success, name='checkout_success'),
     path('checkout-cancel/', views.checkout_cancel, name='checkout_cancel'),
     
       
]