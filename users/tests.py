from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .forms import RegisterForm
from django.contrib.messages import get_messages
from django.core import mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

# Form Tests
class RegisterFormTest(TestCase):
    """Tests for the RegisterForm"""
    
    def test_register_form_valid_data(self):
        """Test that RegisterForm accepts valid data"""
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'complex_password123',
            'password2': 'complex_password123',
        }
        form = RegisterForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_register_form_password_mismatch(self):
        """Test that RegisterForm validates password match"""
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'complex_password123',
            'password2': 'different_password',
        }
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
    
    def test_register_form_email_required(self):
        """Test that RegisterForm requires email"""
        form_data = {
            'username': 'testuser',
            'email': '',
            'password1': 'complex_password123',
            'password2': 'complex_password123',
        }
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
    
    def test_register_form_username_unique(self):
        """Test that RegisterForm validates username uniqueness"""
        # Create a user first
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='password123'
        )
        
        # Try to create another user with the same username
        form_data = {
            'username': 'existinguser',
            'email': 'new@example.com',
            'password1': 'complex_password123',
            'password2': 'complex_password123',
        }
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

# View Tests
class RegisterViewTest(TestCase):
    """Tests for the register view"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.register_url = reverse('register')
    
    def test_register_view_get(self):
        """Test that register view returns 200 and uses correct template"""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')
    
    def test_register_view_post_valid(self):
        """Test that register view creates a user and redirects on valid data"""
        user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'complex_password123',
            'password2': 'complex_password123',
        }
        response = self.client.post(self.register_url, user_data)
        
        # Check redirect
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
        
        # Check user was created
        self.assertTrue(User.objects.filter(username='newuser').exists())
        
        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('Welcome newuser', str(messages[0]))
    
    def test_register_view_post_invalid(self):
        """Test that register view shows form errors on invalid data"""
        user_data = {
            'username': 'newuser',
            'email': 'invalid-email',  # Invalid email
            'password1': 'password123',
            'password2': 'password123',
        }
        response = self.client.post(self.register_url, user_data)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        
        # Check user was not created
        self.assertFalse(User.objects.filter(username='newuser').exists())
        
        # Check form errors are shown
        self.assertIn('form', response.context)
        self.assertFalse(response.context['form'].is_valid())

class LoginViewTest(TestCase):
    """Tests for the login view"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.login_url = reverse('login')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
    
    def test_login_view_get(self):
        """Test that login view returns 200 and uses correct template"""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')
    
    def test_login_view_post_valid(self):
        """Test that login view authenticates user and redirects on valid data"""
        login_data = {
            'username': 'testuser',
            'password': 'testpassword',
        }
        response = self.client.post(self.login_url, login_data)
        
        # Check redirect to home page
        self.assertEqual(response.status_code, 302)
        
        # Check user is authenticated
        self.assertTrue(response.wsgi_request.user.is_authenticated)
    
    def test_login_view_post_invalid(self):
        """Test that login view shows error on invalid credentials"""
        login_data = {
            'username': 'testuser',
            'password': 'wrongpassword',
        }
        response = self.client.post(self.login_url, login_data)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        
        # Check user is not authenticated
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        
        # Check error message
        self.assertContains(response, "Invalid username or password")

class LogoutViewTest(TestCase):
    """Tests for the logout view"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.logout_url = reverse('logout')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.client.login(username='testuser', password='testpassword')
    
    def test_logout_view(self):
        """Test that logout view logs out user and redirects"""
        # Verify user is logged in
        self.assertTrue(self.client.session.get('_auth_user_id'))
        
        # Logout
        response = self.client.get(self.logout_url)
        
        # Check redirect
        self.assertEqual(response.status_code, 302)
        
        # Check user is logged out
        self.assertFalse(self.client.session.get('_auth_user_id'))

class ForgotPasswordViewTest(TestCase):
    """Tests for the forgot password view"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.forgot_password_url = reverse('forgot_password')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
    
    def test_forgot_password_view_get(self):
        """Test that forgot password view returns 200 and uses correct template"""
        response = self.client.get(self.forgot_password_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/forgot_password.html')
    
    def test_forgot_password_view_post_valid(self):
        """Test that forgot password view sends email on valid data"""
        form_data = {
            'email': 'test@example.com',
        }
        response = self.client.post(self.forgot_password_url, form_data)
        
        # Check redirect
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('password_reset_done'))
        
        # Check email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['test@example.com'])
    
    def test_forgot_password_view_post_invalid_email(self):
        """Test that forgot password view handles invalid email"""
        form_data = {
            'email': 'nonexistent@example.com',
        }
        response = self.client.post(self.forgot_password_url, form_data)
        
        # Check redirect (should still redirect to avoid email enumeration)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('password_reset_done'))
        
        # Check no email was sent
        self.assertEqual(len(mail.outbox), 0)

class ResetPasswordViewTest(TestCase):
    """Tests for the reset password view"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = default_token_generator.make_token(self.user)
        self.reset_url = reverse('reset_password', args=[self.uid, self.token])
    
    def test_reset_password_view_get(self):
        """Test that reset password view returns 200 and uses correct template"""
        response = self.client.get(self.reset_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/reset_password.html')
    
    def test_reset_password_view_post_valid(self):
        """Test that reset password view changes password on valid data"""
        form_data = {
            'new_password1': 'newpassword123',
            'new_password2': 'newpassword123',
        }
        response = self.client.post(self.reset_url, form_data)
        
        # Check redirect
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
        
        # Check password was changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword123'))
    
    def test_reset_password_view_post_invalid(self):
        """Test that reset password view shows errors on invalid data"""
        form_data = {
            'new_password1': 'newpassword123',
            'new_password2': 'differentpassword',
        }
        response = self.client.post(self.reset_url, form_data)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        
        # Check password was not changed
        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password('newpassword123'))
        
        # Check form errors are shown
        self.assertContains(response, "The two password fields didn't match")
    
    def test_reset_password_view_invalid_token(self):
        """Test that reset password view handles invalid token"""
        invalid_url = reverse('reset_password', args=[self.uid, 'invalid-token'])
        response = self.client.get(invalid_url)
        
        # Check redirect to invalid token page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('password_reset_invalid'))

# Integration Tests
class UserAuthFlowTest(TestCase):
    """Integration tests for the user authentication flow"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
    
    def test_register_login_logout_flow(self):
        """Test the complete user registration, login, and logout flow"""
        # Register a new user
        user_data = {
            'username': 'flowuser',
            'email': 'flow@example.com',
            'password1': 'complex_password123',
            'password2': 'complex_password123',
        }
        register_response = self.client.post(self.register_url, user_data)
        self.assertEqual(register_response.status_code, 302)
        self.assertRedirects(register_response, self.login_url)
        
        # Login with the new user
        login_data = {
            'username': 'flowuser',
            'password': 'complex_password123',
        }
        login_response = self.client.post(self.login_url, login_data)
        self.assertEqual(login_response.status_code, 302)
        self.assertTrue(login_response.wsgi_request.user.is_authenticated)
        
        # Logout
        logout_response = self.client.get(self.logout_url)
        self.assertEqual(logout_response.status_code, 302)
        
        # Verify logged out
        home_response = self.client.get(reverse('bookstore:home'))
        self.assertFalse(home_response.wsgi_request.user.is_authenticated)
    
    def test_password_reset_flow(self):
        """Test the complete password reset flow"""
        # Create a user
        user = User.objects.create_user(
            username='resetuser',
            email='reset@example.com',
            password='oldpassword123'
        )
        
        # Request password reset
        forgot_response = self.client.post(
            reverse('forgot_password'),
            {'email': 'reset@example.com'}
        )
        self.assertEqual(forgot_response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        
        # Extract reset URL from email
        email_body = mail.outbox[0].body
        reset_url = [line for line in email_body.split('\n') if 'reset_password' in line][0].strip()
        
        # Visit reset URL
        response = self.client.get(reset_url)
        self.assertEqual(response.status_code, 200)
        
        # Reset password
        form_data = {
            'new_password1': 'newpassword123',
            'new_password2': 'newpassword123',
        }
        reset_response = self.client.post(reset_url, form_data)
        self.assertEqual(reset_response.status_code, 302)
        
        # Try logging in with new password
        login_data = {
            'username': 'resetuser',
            'password': 'newpassword123',
        }
        login_response = self.client.post(self.login_url, login_data)
        self.assertEqual(login_response.status_code, 302)
        self.assertTrue(login_response.wsgi_request.user.is_authenticated)
