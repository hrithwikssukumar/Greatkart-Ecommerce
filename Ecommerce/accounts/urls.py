
from django.urls import path
from. import views

urlpatterns = [
    
    path('register/',views.user_register,name='register'),
    path('signin/',views.user_login,name='signin'),
    path('logout/',views.user_logout,name='logout'),
    path('dashboard/',views.user_dashboard,name='dashboard'),
    path('activate/<uidb64>/<token>/', views.activate_user, name='activate'),
    path('forgotpassword/',views.forgot_password,name='forgotpassword'),
    path('resetpassword_validate/<uidb64>/<token>/', views.resetpassword_validate, name='resetpassword_validate'),
    path('resetpassword/',views.reset_password,name='resetpassword'),


]
