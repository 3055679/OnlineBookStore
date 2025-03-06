import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import  render
from .models import Book, Cart, Order
from django.views.decorators.csrf import csrf_exempt


from django.core.paginator import Paginator

def home(request):
    book_list=Book.objects.all()
    context={
        'book_list':book_list,
    }

    return render(request, 'bookstore/home.html', context)

def detail(request,book_id):
    book=Book.objects.get(pk=book_id)
    context={
        'book':book,
    }
    return render(request,'bookstore/detail.html',context)

def search(request):
    book_list=Book.objects.all()

    book_name=request.GET.get('book_name')
    # if book_name != '' and book_name is not None:
    #     book_list=book_list.filter(title__icontains=book_name)

    if book_name:  # If a search query is provided
        book_list = book_list.filter(title__icontains=book_name)  # Filter books by title


    # paginator code

    paginator=Paginator(book_list,4)
    page=request.GET.get('page')
    book_list=paginator.get_page(page)

    return render(request, 'bookstore/home.html', {'book_list':book_list})


def cart_view(request):
    return render(request, 'bookstore/cart.html')


def get_cart_books(request):
    book_ids = request.GET.get('ids', '').split(',')
    books = Book.objects.filter(id__in=book_ids).values('id', 'title', 'price', 'book_image')

    for book in books:
        book['image'] = book['book_image']  # Rename field for frontend

    return JsonResponse({"books": list(books)})


# 📌 View for Cart Page
# def cart_view(request):
#     return render(request, 'bookstore/cart.html')

def add_to_cart(request, book_id):
    cart = request.session.get("cart", {})

    # Fetch book details from database
    book = Book.objects.get(id=book_id)
    book_id_str = str(book_id)  

    if book_id_str in cart:
        cart[book_id_str]["quantity"] += 1
    else:
        cart[book_id_str] = {
            "title": book.title,
            "price": float(book.price),
            "quantity": 1,
        }

    request.session["cart"] = cart
    request.session.modified = True  # Ensure session updates

    return JsonResponse({"success": True})


# 📌 View for Checkout Page
# def checkout_view(request):
#     return render(request, 'bookstore/checkout.html')

# def checkout_view(request):
#     cart = request.session.get("cart", {})  # Get cart data from session
#     total_price = sum(float(item["price"]) * int(item["quantity"]) for item in cart.values()) if cart else 0
#     total_items = sum(int(item["quantity"]) for item in cart.values()) if cart else 0

#     context = {
#         "cart": cart,
#         "subtotal": round(total_price, 2),
#         "shipping": 5,  # Example shipping cost
#         "total": round(total_price + 5, 2),
#         "total_items": total_items,
#     }
#     return render(request, 'bookstore/checkout.html', context)


def checkout_view(request):
    cart_summary = request.session.get("cart_summary", {"total_items": 0, "subtotal": 0, "shipping": 5, "total": 5})

    # Debugging Log
    print("🟢 Checkout Summary:", cart_summary)

    context = {
        "total_items": cart_summary["total_items"],
        "subtotal": cart_summary["subtotal"],
        "shipping": cart_summary["shipping"],
        "total": cart_summary["total"],
    }
    return render(request, 'bookstore/checkout.html', context)

# 📌 View for Transaction Confirmation Page
def transaction_view(request):
    return render(request, 'bookstore/transaction.html')

# 📌 API to Handle Order Placement
@csrf_exempt
def place_order(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Parse JSON data from the request

            # Debugging: Print the received data
            print("🟢 Received Order Data:", data)

            # Validate required fields
            required_fields = ["name", "email", "address", "payment_method", "total_price"]
            for field in required_fields:
                if field not in data:
                    return JsonResponse({"success": False, "error": f"Missing required field: {field}"})

            # Save order to the database
            order = Order.objects.create(
                name=data["name"],
                email=data["email"],
                phone=data.get("phone", ""),
                address=data["address"],
                division=data.get("division", ""),
                state=data.get("state", ""),
                zipcode=data.get("zipcode", ""),
                payment_method=data["payment_method"],
                account_no=data.get("account_no", "") if data["payment_method"] in ["credit", "debit"] else "",
                cvv=data.get("cvv", "") if data["payment_method"] in ["credit", "debit"] else "",
                expiry_date=data.get("expiry_date", "") if data["payment_method"] in ["credit", "debit"] else "",
                sort_code=data.get("sort_code", "") if data["payment_method"] in ["credit", "debit"] else "",
                paypal_id=data.get("paypal_id", "") if data["payment_method"] == "paypal" else "",
                total_price=data["total_price"],
            )

            # Debugging: Print the created order
            print("🟢 Order Created:", order.id)

            return JsonResponse({"success": True, "order_id": order.id})
        except Exception as e:
            # Debugging: Print the error
            print("🔴 Error Creating Order:", str(e))
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "message": "Invalid request"})

# 📌 API to Fetch Order Details for Transaction Page
def get_order_details(request):
    order_id = request.GET.get("order_id")
    try:
        order = Order.objects.get(id=order_id)

        return JsonResponse({
            "order_id": order.id,
            "name": order.name,
            "phone": order.phone,
            "email": order.email,
            "payment_method": order.payment_method,
            "account_no": order.account_no,
            "paypal_id": order.paypal_id,
            "address": f"{order.address}, {order.division}, {order.state}, {order.zipcode}",
            "total_price": float(order.total_price),
        })
    except Order.DoesNotExist:
        return JsonResponse({"error": "Order not found"}, status=404)

# def get_order_details(request):
#     order_id = request.GET.get("order_id")
#     order = Order.objects.get(id=order_id)

#     return JsonResponse({
#         "order_id": order.id,
#         "name": order.name,
#         "phone": order.phone,
#         "email": order.email,
#         "payment_method": order.payment_method,
#         "address": f"{order.address}, {order.division}, {order.state}, {order.zipcode}",
#     })


# @csrf_exempt
# def save_cart_summary(request):
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)  # Get subtotal and total from AJAX request
#             request.session["cart_summary"] = {
#                 "subtotal": data["subtotal"],
#                 "shipping": 5,  # Fixed shipping cost
#                 "total": data["total"]
#             }
#             request.session.modified = True
#             return JsonResponse({"success": True})
#         except Exception as e:
#             return JsonResponse({"success": False, "error": str(e)})

#     return JsonResponse({"success": False, "message": "Invalid request"})

@csrf_exempt
def save_cart_summary(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            # Debugging Log
            print("🟢 Received Cart Data:", data)

            request.session["cart_summary"] = {
                "total_items": int(data["total_items"]),
                "subtotal": round(float(data["subtotal"]), 2),
                "shipping": 5,
                "total": round(float(data["total"]), 2)
            }
            request.session.modified = True
            return JsonResponse({"success": True})
        except Exception as e:
            print("🔴 Error Saving Cart Data:", str(e))  # Debugging
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "message": "Invalid request"})





