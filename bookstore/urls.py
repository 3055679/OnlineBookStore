from django.urls import path
from . import views

app_name='bookstore'
urlpatterns=[
    path('home/', views.home, name='home'),
    path('<int:book_id>/',views.detail,name='detail'),
    path('search/', views.search, name='search'),
    path('cart/', views.cart_view, name='cart'),  # Register the cart page
    path('checkout/', views.checkout_view, name='checkout'),
    path('save_cart_summary/', views.save_cart_summary, name='save_cart_summary'),
    path('get-cart-books/', views.get_cart_books, name='get-cart-books'),
    path('place_order/', views.place_order, name='place_order'),  # New Route
    path('transaction/', views.transaction_view, name='transaction'),
    
]