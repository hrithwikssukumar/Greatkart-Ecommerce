
from django.urls import path
from. import views

urlpatterns = [
    
    path('',views.index,name='home'),
    path('productlist/',views.list_products,name='productlist'),
    path('category/<slug:category_slug>/',views.list_products,name='product_by_category'),
    path('category/<slug:category_slug>/<slug:product_slug>/',views.detail_product,name='product_detail'),
    path('search/', views.product_search,name ='search'),
    path('add-to-wishlist/<int:product_id>/', views.add_to_wishlist, name='add-to-wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_wishlist_item, name='remove_wishlist_item'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
   
]
