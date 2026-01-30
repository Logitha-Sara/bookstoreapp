from django.urls import path
from . import views

app_name = 'store'
urlpatterns = [
    path('', views.book_list, name='book_list'),
    path('category/<slug:category_slug>/', views.book_list, name='category_books'),
    path('book/<slug:slug>/', views.book_detail, name='book_detail'),
    path('add-to-cart/<slug:slug>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/update/', views.update_cart, name='update_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-success/', views.order_success, name='order_success'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/add/<int:book_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:book_id>/',views.remove_from_wishlist,name='remove_from_wishlist'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
]

