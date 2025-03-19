from django.urls import path
from . import views
from .views import books_by_category
from .views import order_status,my_orders, write_review,submit_review

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
    path('category/<int:category_id>/', views.books_by_category, name='books_by_category'),
    path('category/all/', views.books_by_category, name='all_books'),
    path('get_order_details/', views.get_order_details, name='get_order_details'), 
    path('my_orders/', views.my_orders, name='my_orders'),
    path("cancel_order/<int:order_id>/", views.cancel_order, name="cancel_order"),
    path("request_return/<int:order_id>/", views.request_return, name="request_return"),
    path("save_cart_session/", views.save_cart_session, name="save_cart_session"),
    path('get-cart-summary/', views.get_cart_summary, name='get_cart_summary'),
    path("order_status/<int:order_id>/", views.order_status, name="order_status"),
    path("order_status_api/<int:order_id>/", views.order_status_api, name="order_status_api"),
    path("cancel_order/<int:order_id>/", views.cancel_order, name="cancel_order"),
    path("cancel_order_page/<int:order_id>/", views.cancel_order_page, name="cancel_order_page"),
    path("return_order_page/<int:order_id>/", views.return_order_page, name="return_order_page"),
    path("request_return/<int:order_id>/", views.request_return, name="request_return"),
    path("write_review/<int:order_id>/", views.write_review, name="write_review"),
    path("submit_review/", views.submit_review, name="submit_review"),
    
    # Footer pages
    path('contact/', views.contact, name='contact'),
    path('submit_contact/', views.submit_contact, name='submit_contact'),
    path('cookies/', views.cookies, name='cookies'),
    path('legal/', views.legal, name='legal'),
    path('privacy/', views.privacy, name='privacy'),
] 