from django.contrib import admin
from .models import Book, Category, Order, OrderItem  

admin.site.register(Book)
admin.site.register(Category)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0  

class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "status", "cancel_reason", "return_reason", "total_price", "created_at"]
    list_filter = ["status"]
    search_fields = ["id", "user__username", "email"]  
    inlines = [OrderItemInline]  # ✅ show details of order items

    actions = ["mark_as_confirmed", "mark_as_delivered", "mark_as_return_requested", "mark_as_cancelled"]

    def mark_as_confirmed(self, request, queryset):
        queryset.update(status="Confirmed")
    mark_as_confirmed.short_description = "Mark as Confirmed"

    def mark_as_delivered(self, request, queryset):
        queryset.update(status="Delivered")
    mark_as_delivered.short_description = "Mark as Delivered"

    def mark_as_return_requested(self, request, queryset):
        queryset.update(status="Return Requested")
    mark_as_return_requested.short_description = "Mark as Return Requested"

    def mark_as_cancelled(self, request, queryset):
        queryset.update(status="Cancelled")
    mark_as_cancelled.short_description = "Mark as Cancelled"

admin.site.register(Order, OrderAdmin)
