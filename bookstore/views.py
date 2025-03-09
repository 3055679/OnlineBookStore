import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import  render, get_object_or_404
from .models import Book, Cart, Order,Category,OrderItem
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator

def home(request):
    book_list=Book.objects.all()
    context={
        'book_list':book_list,
    }

    return render(request, 'bookstore/home.html', context)

def books_by_category(request, category_id=None):
    if category_id is not None:
        category = get_object_or_404(Category, id=category_id)
        books = Book.objects.filter(category=category)
    else:
        category = "All Books" 
        books = Book.objects.all() 
    categories = Category.objects.all() 
    return render(request, 'bookstore/home.html', {
        'categories': categories,
        'books': books,
        'selected_category': category
    })

def get_categories(request):
    return {'categories': Category.objects.all()}

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
    
    total_items = sum(item["quantity"] for item in cart.values())
    subtotal = sum(item["price"] * item["quantity"] for item in cart.values())

    return JsonResponse({"success": True, "total_items": total_items, "subtotal": subtotal})


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
    cart_books = Book.objects.filter(id__in=request.session.get("cart", {}).keys())
    cart_summary = request.session.get("cart_summary", {"total_items": 0, "subtotal": 0, "shipping": 5, "total": 5})
    cart_items = request.session.get("cart", {})
    
    print("🟢 Cart Data in Session:", cart_items)

    
    book_ids = [int(k) for k in cart_items.keys()]
    cart_books = Book.objects.filter(id__in=book_ids)

 
    print("🟢 Fetched Books from DB:", cart_books)

    cart_summary = request.session.get("cart_summary", {"total_items": 0, "subtotal": 0, "shipping": 5, "total": 5})

   
    print("🟢 Checkout Summary:", cart_summary)

    context = {
        "cart_books": cart_books,
        "total_items": cart_summary["total_items"],
        "subtotal": cart_summary["subtotal"],
        "shipping": cart_summary["shipping"],
        "total": cart_summary["total"],
    }
    return render(request, 'bookstore/checkout.html', context)

# 📌 View for Transaction Confirmation Page
def transaction_view(request):
    return render(request, 'bookstore/transaction.html')

@csrf_exempt
def request_return(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        if order.status == "Delivered":  
            order.status = "Return Requested"
            order.save()
            return JsonResponse({"success": True})
        return JsonResponse({"success": False, "error": "Cannot request return for this order"})
    except Order.DoesNotExist:
        return JsonResponse({"success": False, "error": "Order not found"})

# 📌 API to Handle Order Placement
@csrf_exempt
def place_order(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            cart = data.get("cart", {})  

            if not cart:
                return JsonResponse({"success": False, "error": "购物车为空"})

            
            user = request.user if request.user.is_authenticated else None
            name = data.get("name", "").strip()
            email = data.get("email", "").strip()
            phone = data.get("phone", "").strip()
            address = data.get("address", "").strip()
            division = data.get("division", "").strip()
            state = data.get("state", "").strip()
            zipcode = data.get("zipcode", "").strip()
            payment_method = data.get("payment_method", "Not specified")

            
            total_price = sum(
                Book.objects.get(id=int(book_id)).price * qty for book_id, qty in cart.items()
            )

            if not name or not email or not address:
                return JsonResponse({"success": False, "error": "姓名, 邮箱, 地址不能为空！"})

            
            order = Order.objects.create(
                user=user,
                name=name,
                email=email,
                phone=phone,
                address=address,
                division=division,
                state=state,
                zipcode=zipcode,
                total_price=total_price,
                payment_method=payment_method,
                status="Confirmed"
            )

           
            for book_id, qty in cart.items():
                book = Book.objects.get(id=int(book_id))
                OrderItem.objects.create(order=order, book=book, quantity=qty)

            print("✅ Order Created Successfully:", order)

            return JsonResponse({"success": True, "order_id": order.id})

        except Exception as e:
            print("🔴 Order creation error:", str(e))
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "message": "Invalid request"})

# 📌 API to Fetch Order Details for Transaction Page
def get_order_details(request):
    order_id = request.GET.get("order_id")
    if not order_id or order_id == "undefined":
        return JsonResponse({"error": "Invalid order ID"}, status=400)

    try:
        order = Order.objects.get(id=order_id)
        
        return JsonResponse({
            "order_id": order.id,
            "name": order.name,
            "phone": order.phone ,
            "email": order.email,
            "payment_method": order.payment_method,
            "address": f"{order.address}, {order.state}, {order.zipcode}"
        }, json_dumps_params={'indent': 2})
    except Order.DoesNotExist:
        return JsonResponse({"error": "Order not found"}, status=404)

def checkout_view(request):
    request.session.modified = True
    cart_items = request.session.get("cart", {})  
    print("🟢 Session Cart Data:", cart_items) 

    if not cart_items:  # if the cart is empty, return
        return render(request, 'bookstore/checkout.html', {"cart_books": []})

    try:
        book_ids = [int(k) for k in cart_items.keys()]  
        cart_books = Book.objects.filter(id__in=book_ids)
    except ValueError:
        print("🔴 Error: Invalid book IDs in cart")
        return render(request, 'bookstore/checkout.html', {"cart_books": []})

    print("🟢 Fetched Cart Books:", cart_books)  

  
    total_items = sum(cart_items.values())
    subtotal = sum(book.price * cart_items[str(book.id)] for book in cart_books) if cart_books else 0
    shipping = 5
    total = subtotal + shipping

    context = {
        "cart_books": cart_books,
        "total_items": sum(cart_items.values()),
        "subtotal": round(subtotal,2),
        "shipping": 5,
        "total": round(total,2) if subtotal else 0,
    }

    return render(request, 'bookstore/checkout.html', context)

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

@csrf_exempt 
def save_cart_session(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body) 
            cart_data = data.get("cart", {})

            print("🟢 Received Cart from Frontend:", cart_data)

            request.session["cart"] = cart_data
            request.session.modified = True
            request.session.save()

            return JsonResponse({"success": True})
        except Exception as e:
            print("🔴 Error Saving Cart Data:", str(e))
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "message": "Invalid request"})

def get_cart_summary(request):
    cart_summary = request.session.get("cart_summary", {
        "total_items": 0,
        "subtotal": 0,
        "total": 0
    })
    return JsonResponse(cart_summary)

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by("-id").prefetch_related("items")
    
    for order in orders:
        order.items_list = order.items.all()  
    
    return render(request, "bookstore/my_orders.html", {"orders": orders})

def order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_items = OrderItem.objects.filter(order=order)
    return render(request, "bookstore/order_status.html", {
        "order": order,
        "order_items": order_items
    })

def order_status_api(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return JsonResponse({"status": order.status})

@csrf_exempt
def cancel_order(request, order_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            reason = data.get("reason", "").strip()

            order = Order.objects.get(id=order_id)

            if order.status != "Processing":
                return JsonResponse({"success": False, "error": "Only processing orders can be cancelled."})

         
            order.cancel_reason = reason
            order.status = "Cancelled"
            order.save()

            return JsonResponse({"success": True})

        except Order.DoesNotExist:
            return JsonResponse({"success": False, "error": "Order not found."})
    return JsonResponse({"success": False, "error": "Invalid request"})


def cancel_order_page(request, order_id):
    """ cancel page """
    order = get_object_or_404(Order, id=order_id)
    return render(request, "bookstore/cancel_order.html", {"order": order})

def return_order_page(request, order_id):
    """ return page """
    order = get_object_or_404(Order, id=order_id)
    return render(request, "bookstore/return_order_page.html", {"order": order})

@csrf_exempt
def request_return(request, order_id):
    if request.method == "POST":
        try:
            order = Order.objects.get(id=order_id)
            if order.status != "Delivered":
                return JsonResponse({"success": False, "error": "Only delivered orders can be returned."})

            # front end uses multipart/form-data， so request.POST and request.FILES
            reason = request.POST.get("reason", "").strip()
            comments = request.POST.get("comments", "").strip()
            photo = request.FILES.get("photo")  

            if not reason:
                return JsonResponse({"success": False, "error": "Return reason is required."})

        
            order.return_reason = reason
            order.status = "Return Requested"
            order.save()

            # order.return_comments = comments
            # order.return_photo = photo
            # order.save()

            print(f"✅ Order {order_id} Return request submitted successfully: reason={reason}, comments={comments}, photo={photo}")

            return JsonResponse({"success": True})

        except Order.DoesNotExist:
            return JsonResponse({"success": False, "error": "Order not found."})

    return JsonResponse({"success": False, "error": "Invalid request"})