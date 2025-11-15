from django.urls import path
from . import views

urlpatterns=[ 
    path('',views.home,name='home'),
    path('view_item/',views.view_item,name='PRODUCTS'),
    path('Add_item/', views.Add_item,name='AddItem'),
    path('contact/',views.contact,name='contact'),
    path('update_item/<int:id>', views.update_item,name='Update'),
    path('delete/<int:id>', views.delete_book,name='Delete'),
    path('register/', views.register,name='register'),
    path('login/',views.login_user,name='loginpage'),
    path('logout/',views.logout_user,name='logoutpage'),
    path('add_to_cart/<int:product_id>',views.add_to_cart,name='add_to_cart'),
    path('view_cart/',views.view_cart,name='view_cart'),
    path('remove_from_cart/<int:product_id>',views.remove_from_cart,name='remove_from_cart'),


    path('place_order/', views.place_order, name='place_order'),
    path('buy/<int:product_id>/', views.buy_now, name='buy_now'),
    path('buyy/',views.buy_now1, name='buy_now1'),
    path('success/', views.payment_success,name='success'),
    path('cancel/', views.payment_cancel,name='cancel'),
    path('orders/', views.order_history, name='order_history'),





]