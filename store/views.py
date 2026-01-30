from django.shortcuts import render, get_object_or_404, redirect
from .models import Book, Category, Order, OrderItem
from .forms import AddToCartForm, CheckoutForm
from decimal import Decimal
from django.db.models import Q
import stripe
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import RegisterForm 
from django.contrib.auth.decorators import login_required
from .models import Profile
from .models import Book, Wishlist 
from .forms import UserUpdateForm, ProfileUpdateForm



stripe.api_key = settings.STRIPE_SECRET_KEY

def book_list(request):
    books = Book.objects.all()
    categories = Category.objects.all()

    q = request.GET.get('q')
    category = request.GET.get('category')
    price = request.GET.get('price')

    if q:
        books = books.filter(
            Q(title__icontains=q) |
            Q(author__name__icontains=q) |
            Q(category__name__icontains=q)
        )

    if category:
        books = books.filter(category__slug=category)

    if price == 'low':
        books = books.filter(price__lte=500)
    elif price == 'high':
        books = books.filter(price__gte=800)

    return render(request, 'store/book_list.html', {
        'books': books,
        'categories': categories
    })

def book_detail(request, slug):
    book = get_object_or_404(Book, slug=slug)
    form = AddToCartForm(request.POST or None)
    return render(request, 'store/book_detail.html', {'book': book, 'form': form})


def _get_cart(request):
    return request.session.setdefault('cart', {})

def cart_view(request):
    cart = _get_cart(request)
    items = []
    total = Decimal('0.00')
    for slug, qty in cart.items():
        try:
            book = Book.objects.get(slug=slug)
        except Book.DoesNotExist:
            continue
        cost = book.price * qty
        items.append({'book': book, 'qty': qty, 'cost': cost})
        total += cost
    return render(request, 'store/cart.html', {'items': items, 'total': total})

def update_cart(request):
    cart = _get_cart(request)
    for slug, qty in request.POST.items():
        if slug.startswith('qty_'):
            s = slug.split('qty_')[1]
            if s in cart:
                try:
                    q = int(qty)
                    if q > 0:
                        cart[s] = q
                    else:
                        del cart[s]
                except ValueError:
                    pass
    request.session.modified = True
    return redirect('store:cart')


@login_required
def checkout(request):
    cart = request.session.get('cart', {})

    if not cart:
        messages.warning(request, "Your cart is empty")
        return redirect('store:cart')

    items = []
    total = Decimal('0.00')

    for slug, qty in cart.items():
        book = get_object_or_404(Book, slug=slug)
        cost = book.price * qty
        items.append({
            'book': book,
            'qty': qty,
            'cost': cost
        })
        total += cost

    if request.method == 'POST':
        order = Order.objects.create(
            user=request.user,
            status='paid',
            total_amount=total  
        )

        for item in items:
            OrderItem.objects.create(
                order=order,
                book=item['book'],
                quantity=item['qty'],
                price=item['book'].price
            )

        request.session['cart'] = {}
        request.session.modified = True
        return redirect('store:order_success')

    return render(request, 'store/checkout.html', {
        'items': items,
        'total': total
    })


def order_success(request):
    return render(request, 'store/order_success.html')


def add_to_cart(request, slug):
    book = get_object_or_404(Book, slug=slug)
    cart = _get_cart(request)

    cart[slug] = cart.get(slug, 0) + 1

    request.session.modified = True
    return redirect('store:cart')


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            email = form.cleaned_data.get('email')

            if User.objects.filter(username=username).exists():
                form.add_error('username', "Username already taken")
            else:
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    email=email
                )
                login(request, user)
                return redirect('store:book_list')
    else:
        form = RegisterForm()

    return render(request, 'store/register.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('store:book_list')  
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "store/login.html")

@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    return render(request, 'store/profile.html', {'profile': profile})


@login_required
def add_to_wishlist(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    wishlist_items, created = Wishlist.objects.get_or_create(user=request.user, book=book)
    return redirect('store:wishlist')


@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'store/wishlist.html', {'wishlist_items': wishlist_items})

@login_required
def remove_from_wishlist(request, id):
    Wishlist.objects.filter(id=id, user=request.user).delete()
    return redirect('store:wishlist')



@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=request.user.profile
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('store:profile')

    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    return render(request, 'store/edit_profile.html',{
        'user_form': user_form,
        'profile_form': profile_form
    })
    



