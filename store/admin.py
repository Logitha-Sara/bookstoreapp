from django.contrib import admin
from .models import Category, Author, Book, Order, OrderItem, Profile, Wishlist

admin.site.register(OrderItem)
admin.site.register(Author)
admin.site.register(Profile)
admin.site.register(Wishlist)

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title','author','price','stock')
    prepopulated_fields = {'slug': ('title',)}

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['book']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ( 'user__username',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


