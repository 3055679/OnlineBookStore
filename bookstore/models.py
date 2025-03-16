from django.db import models
from django.contrib.auth.models import User

from django.conf import settings

class Book(models.Model):

    def __str__(self):
        return self.title

    title = models.CharField(max_length=200)
    rating = models.FloatField()
    price=models.FloatField()
    desc=models.CharField(max_length=2000,default="decription of the book")
    book_image=models.CharField(max_length=500, default="https://images.pexels.com/photos/185764/pexels-photo-185764.jpeg?auto=compress&cs=tinysrgb&w=600")
    author=models.CharField(max_length=200,default="unknown author")

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.book.title} in {self.user.username}'s cart"
    


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField()
    division = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    zipcode = models.CharField(max_length=10, blank=True, null=True)
    payment_method = models.CharField(max_length=20)
    account_no = models.CharField(max_length=20, blank=True, null=True)
    cvv = models.CharField(max_length=5, blank=True, null=True)
    expiry_date = models.CharField(max_length=10, blank=True, null=True)
    sort_code = models.CharField(max_length=10, blank=True, null=True)
    paypal_id = models.CharField(max_length=100, blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)  # Ensure this field is NOT NULL
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} by {self.name}"
