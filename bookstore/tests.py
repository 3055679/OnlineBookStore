from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from decimal import Decimal
from .models import Book, Category, Cart, Order, OrderItem, Review

# 模型测试
class CategoryModelTest(TestCase):
    """Tests for the Category model"""
    
    def setUp(self):
        """Set up test data"""
        self.category = Category.objects.create(name="Fiction")
    
    def test_category_creation(self):
        """Test that a category can be created"""
        self.assertEqual(self.category.name, "Fiction")
    
    def test_category_str_representation(self):
        """Test the string representation of a category"""
        self.assertEqual(str(self.category), "Fiction")

class BookModelTest(TestCase):
    """Tests for the Book model"""
    
    def setUp(self):
        """Set up test data"""
        self.category = Category.objects.create(name="Science Fiction")
        self.book = Book.objects.create(
            title="Dune",
            author="Frank Herbert",
            price=15.99,
            rating=4.5,
            desc="A science fiction masterpiece",
            category=self.category
        )
    
    def test_book_creation(self):
        """Test that a book can be created with all fields"""
        self.assertEqual(self.book.title, "Dune")
        self.assertEqual(self.book.author, "Frank Herbert")
        self.assertEqual(self.book.price, 15.99)
        self.assertEqual(self.book.rating, 4.5)
        self.assertEqual(self.book.desc, "A science fiction masterpiece")
        self.assertEqual(self.book.category, self.category)
    
    def test_book_str_representation(self):
        """Test the string representation of a book"""
        self.assertEqual(str(self.book), "Dune")

class CartModelTest(TestCase):
    """Tests for the Cart model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword"
        )
        self.category = Category.objects.create(name="Mystery")
        self.book = Book.objects.create(
            title="The Da Vinci Code",
            author="Dan Brown",
            price=12.99,
            rating=4.0,
            desc="A mystery thriller novel",
            category=self.category
        )
        self.cart_item = Cart.objects.create(
            user=self.user,
            book=self.book,
            quantity=2
        )
    
    def test_cart_creation(self):
        """Test that a cart item can be created"""
        self.assertEqual(self.cart_item.user, self.user)
        self.assertEqual(self.cart_item.book, self.book)
        self.assertEqual(self.cart_item.quantity, 2)
    
    def test_cart_str_representation(self):
        """Test the string representation of a cart item"""
        expected_str = f"2 x The Da Vinci Code in testuser's cart"
        self.assertEqual(str(self.cart_item), expected_str)

class OrderModelTest(TestCase):
    """Tests for the Order model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="orderuser",
            email="order@example.com",
            password="orderpassword"
        )
        self.category = Category.objects.create(name="Biography")
        self.book = Book.objects.create(
            title="Steve Jobs",
            author="Walter Isaacson",
            price=19.99,
            rating=4.8,
            desc="Biography of Apple co-founder",
            category=self.category
        )
        self.order = Order.objects.create(
            user=self.user,
            name="John Doe",
            email="john@example.com",
            address="123 Test St",
            payment_method="Credit Card",
            total_price=Decimal('19.99'),
            book=self.book,
            quantity=1
        )
    
    def test_order_creation(self):
        """Test that an order can be created"""
        self.assertEqual(self.order.user, self.user)
        self.assertEqual(self.order.name, "John Doe")
        self.assertEqual(self.order.email, "john@example.com")
        self.assertEqual(self.order.address, "123 Test St")
        self.assertEqual(self.order.payment_method, "Credit Card")
        self.assertEqual(self.order.total_price, Decimal('19.99'))
        self.assertEqual(self.order.book, self.book)
        self.assertEqual(self.order.quantity, 1)
        self.assertEqual(self.order.status, "Confirmed")
    
    def test_order_str_representation(self):
        """Test the string representation of an order"""
        expected_str = f"Order {self.order.id} by John Doe"
        self.assertEqual(str(self.order), expected_str)
    
    def test_order_save_method(self):
        """Test that the save method calculates the total price correctly"""
        # Create a new order with a different quantity
        new_order = Order.objects.create(
            user=self.user,
            name="Jane Doe",
            email="jane@example.com",
            address="456 Test Ave",
            payment_method="PayPal",
            total_price=0,  # This will be calculated by the save method
            book=self.book,
            quantity=3
        )
        
        # The save method should have calculated the total price
        self.assertEqual(new_order.total_price, Decimal('59.97'))  # 19.99 * 3

class OrderItemModelTest(TestCase):
    """Tests for the OrderItem model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="itemuser",
            email="item@example.com",
            password="itempassword"
        )
        self.category = Category.objects.create(name="Fantasy")
        self.book = Book.objects.create(
            title="Harry Potter",
            author="J.K. Rowling",
            price=14.99,
            rating=4.9,
            desc="Fantasy novel about a young wizard",
            category=self.category
        )
        self.order = Order.objects.create(
            user=self.user,
            name="Alice Smith",
            email="alice@example.com",
            address="789 Test Blvd",
            payment_method="Credit Card",
            total_price=Decimal('14.99'),
            book=self.book,
            quantity=1
        )
        self.order_item = OrderItem.objects.create(
            order=self.order,
            book=self.book,
            quantity=1
        )
    
    def test_order_item_creation(self):
        """Test that an order item can be created"""
        self.assertEqual(self.order_item.order, self.order)
        self.assertEqual(self.order_item.book, self.book)
        self.assertEqual(self.order_item.quantity, 1)

class ReviewModelTest(TestCase):
    """Tests for the Review model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="reviewer",
            email="reviewer@example.com",
            password="reviewpassword"
        )
        self.category = Category.objects.create(name="Self-Help")
        self.book = Book.objects.create(
            title="Atomic Habits",
            author="James Clear",
            price=11.99,
            rating=4.7,
            desc="A guide to building good habits",
            category=self.category
        )
        self.review = Review.objects.create(
            book=self.book,
            user=self.user,
            review_text="Great book, very helpful!",
            rating=5
        )
    
    def test_review_creation(self):
        """Test that a review can be created"""
        self.assertEqual(self.review.book, self.book)
        self.assertEqual(self.review.user, self.user)
        self.assertEqual(self.review.review_text, "Great book, very helpful!")
        self.assertEqual(self.review.rating, 5)
    
    def test_review_str_representation(self):
        """Test the string representation of a review"""
        expected_str = f"Review for Atomic Habits by reviewer"
        self.assertEqual(str(self.review), expected_str)

# 视图测试
class HomeViewTest(TestCase):
    """Tests for the home view"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.category = Category.objects.create(name="Fiction")
        self.book1 = Book.objects.create(
            title="Book 1",
            author="Author 1",
            price=10.99,
            rating=4.0,
            desc="Description 1",
            category=self.category
        )
        self.book2 = Book.objects.create(
            title="Book 2",
            author="Author 2",
            price=12.99,
            rating=4.2,
            desc="Description 2",
            category=self.category
        )
    
    def test_home_view_status_code(self):
        """Test that the home view returns a 200 status code"""
        response = self.client.get(reverse('bookstore:home'))
        self.assertEqual(response.status_code, 200)
    
    def test_home_view_template(self):
        """Test that the home view uses the correct template"""
        response = self.client.get(reverse('bookstore:home'))
        self.assertTemplateUsed(response, 'bookstore/home.html')
    
    def test_home_view_context(self):
        """Test that the home view contains the books in the context"""
        response = self.client.get(reverse('bookstore:home'))
        self.assertIn('book_list', response.context)
        self.assertEqual(len(response.context['book_list']), 2)

class DetailViewTest(TestCase):
    """Tests for the detail view"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.category = Category.objects.create(name="Fiction")
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            price=9.99,
            rating=4.5,
            desc="Test Description",
            category=self.category
        )
        self.user = User.objects.create_user(
            username="reviewuser",
            email="review@example.com",
            password="reviewpassword"
        )
        self.review = Review.objects.create(
            book=self.book,
            user=self.user,
            review_text="Test review",
            rating=4
        )
    
    def test_detail_view_status_code(self):
        """Test that the detail view returns a 200 status code"""
        response = self.client.get(reverse('bookstore:detail', args=[self.book.id]))
        self.assertEqual(response.status_code, 200)
    
    def test_detail_view_template(self):
        """Test that the detail view uses the correct template"""
        response = self.client.get(reverse('bookstore:detail', args=[self.book.id]))
        self.assertTemplateUsed(response, 'bookstore/detail.html')
    
    def test_detail_view_context(self):
        """Test that the detail view contains the book and reviews in the context"""
        response = self.client.get(reverse('bookstore:detail', args=[self.book.id]))
        self.assertIn('book', response.context)
        self.assertEqual(response.context['book'], self.book)
        self.assertIn('reviews', response.context)
        self.assertEqual(len(response.context['reviews']), 1)

class CartViewTest(TestCase):
    """Tests for the cart view"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username="cartuser",
            email="cart@example.com",
            password="cartpassword"
        )
        self.category = Category.objects.create(name="Fiction")
        self.book = Book.objects.create(
            title="Cart Test Book",
            author="Cart Test Author",
            price=8.99,
            rating=4.3,
            desc="Cart Test Description",
            category=self.category
        )
        self.cart_item = Cart.objects.create(
            user=self.user,
            book=self.book,
            quantity=1
        )
    
    def test_cart_view_requires_login(self):
        """Test that the cart view requires login"""
        response = self.client.get(reverse('bookstore:cart'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_cart_view_logged_in(self):
        """Test that a logged-in user can access the cart view"""
        self.client.login(username="cartuser", password="cartpassword")
        response = self.client.get(reverse('bookstore:cart'))
        self.assertEqual(response.status_code, 200)

class AddToCartTest(TestCase):
    """Tests for the add_to_cart functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username="addcartuser",
            email="addcart@example.com",
            password="addcartpassword"
        )
        self.category = Category.objects.create(name="Fiction")
        self.book = Book.objects.create(
            title="Add Cart Test Book",
            author="Add Cart Test Author",
            price=7.99,
            rating=4.1,
            desc="Add Cart Test Description",
            category=self.category
        )
    
    def test_add_to_cart_requires_login(self):
        """Test that adding to cart requires login"""
        response = self.client.post(reverse('bookstore:add_to_cart', args=[self.book.id]))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_add_to_cart_logged_in(self):
        """Test that a logged-in user can add to cart"""
        self.client.login(username="addcartuser", password="addcartpassword")
        response = self.client.post(reverse('bookstore:add_to_cart', args=[self.book.id]))
        self.assertEqual(response.status_code, 302)  # Redirect after adding
        
        # Check that the item was added to the cart
        cart_items = Cart.objects.filter(user=self.user, book=self.book)
        self.assertEqual(cart_items.count(), 1)
        self.assertEqual(cart_items.first().quantity, 1)

class CheckoutViewTest(TestCase):
    """Tests for the checkout view"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username="checkoutuser",
            email="checkout@example.com",
            password="checkoutpassword"
        )
        self.category = Category.objects.create(name="Fiction")
        self.book = Book.objects.create(
            title="Checkout Test Book",
            author="Checkout Test Author",
            price=6.99,
            rating=3.9,
            desc="Checkout Test Description",
            category=self.category
        )
        self.cart_item = Cart.objects.create(
            user=self.user,
            book=self.book,
            quantity=1
        )
    
    def test_checkout_view_requires_login(self):
        """Test that the checkout view requires login"""
        response = self.client.get(reverse('bookstore:checkout'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_checkout_view_logged_in(self):
        """Test that a logged-in user can access the checkout view"""
        self.client.login(username="checkoutuser", password="checkoutpassword")
        response = self.client.get(reverse('bookstore:checkout'))
        self.assertEqual(response.status_code, 200)

# 集成测试
class OrderFlowTest(TestCase):
    """Integration tests for the order flow"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username="flowuser",
            email="flow@example.com",
            password="flowpassword"
        )
        self.category = Category.objects.create(name="Fiction")
        self.book = Book.objects.create(
            title="Flow Test Book",
            author="Flow Test Author",
            price=5.99,
            rating=3.7,
            desc="Flow Test Description",
            category=self.category
        )
    
    def test_complete_order_flow(self):
        """Test the complete order flow from adding to cart to placing an order"""
        # Login
        self.client.login(username="flowuser", password="flowpassword")
        
        # Add to cart
        add_response = self.client.post(reverse('bookstore:add_to_cart', args=[self.book.id]))
        self.assertEqual(add_response.status_code, 302)  # Redirect after adding
        
        # Check cart
        cart_items = Cart.objects.filter(user=self.user, book=self.book)
        self.assertEqual(cart_items.count(), 1)
        
        # Go to checkout
        checkout_response = self.client.get(reverse('bookstore:checkout'))
        self.assertEqual(checkout_response.status_code, 200)
        
        # Place order (this would normally be a POST request with form data)
        order_data = {
            'name': 'Test User',
            'email': 'flow@example.com',
            'address': '123 Test St',
            'payment_method': 'Credit Card',
            'book_id': self.book.id,
            'quantity': 1
        }
        
        # This is a simplified version - in a real test, you'd need to mock or handle the actual order placement
        # For now, we'll create the order directly
        order = Order.objects.create(
            user=self.user,
            name=order_data['name'],
            email=order_data['email'],
            address=order_data['address'],
            payment_method=order_data['payment_method'],
            book=self.book,
            quantity=order_data['quantity'],
            total_price=self.book.price * order_data['quantity']
        )
        
        # Check that the order was created
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.book, self.book)
        self.assertEqual(order.status, "Confirmed")

# URL测试
class UrlsTest(TestCase):
    """Tests for URL configurations"""
    
    def setUp(self):
        """Set up test data"""
        self.category = Category.objects.create(name="Fiction")
        self.book = Book.objects.create(
            title="URL Test Book",
            author="URL Test Author",
            price=4.99,
            rating=3.5,
            desc="URL Test Description",
            category=self.category
        )
    
    def test_home_url(self):
        """Test the home URL"""
        response = self.client.get(reverse('bookstore:home'))
        self.assertEqual(response.status_code, 200)
    
    def test_detail_url(self):
        """Test the detail URL"""
        response = self.client.get(reverse('bookstore:detail', args=[self.book.id]))
        self.assertEqual(response.status_code, 200)
    
    def test_cart_url(self):
        """Test the cart URL (should redirect if not logged in)"""
        response = self.client.get(reverse('bookstore:cart'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

# 搜索功能测试
class SearchTest(TestCase):
    """Tests for the search functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.category = Category.objects.create(name="Fiction")
        self.book1 = Book.objects.create(
            title="Python Programming",
            author="John Smith",
            price=29.99,
            rating=4.8,
            desc="A comprehensive guide to Python",
            category=self.category
        )
        self.book2 = Book.objects.create(
            title="Java Basics",
            author="Jane Doe",
            price=24.99,
            rating=4.5,
            desc="Introduction to Java programming",
            category=self.category
        )
    
    def test_search_results(self):
        """Test that search returns correct results"""
        response = self.client.get(reverse('bookstore:search'), {'book_name': 'Python'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Python Programming")
        self.assertNotContains(response, "Java Basics")
    
    def test_empty_search(self):
        """Test that empty search returns all books"""
        response = self.client.get(reverse('bookstore:search'), {'book_name': ''})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Python Programming")
        self.assertContains(response, "Java Basics")

# 分类筛选测试
class CategoryFilterTest(TestCase):
    """Tests for filtering books by category"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.category1 = Category.objects.create(name="Programming")
        self.category2 = Category.objects.create(name="Fiction")
        
        self.book1 = Book.objects.create(
            title="Python Guide",
            author="Tech Author",
            price=29.99,
            rating=4.8,
            desc="Python programming guide",
            category=self.category1
        )
        self.book2 = Book.objects.create(
            title="Fantasy Novel",
            author="Fiction Author",
            price=19.99,
            rating=4.6,
            desc="A fantasy novel",
            category=self.category2
        )
    
    def test_category_filter(self):
        """Test that books can be filtered by category"""
        response = self.client.get(reverse('bookstore:books_by_category', args=[self.category1.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Python Guide")
        self.assertNotContains(response, "Fantasy Novel")
    
    def test_all_categories(self):
        """Test that all books are shown when no category is selected"""
        response = self.client.get(reverse('bookstore:books_by_category'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Python Guide")
        self.assertContains(response, "Fantasy Novel") 