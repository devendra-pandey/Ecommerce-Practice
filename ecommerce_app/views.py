from django.shortcuts import render

from .models import Product, Cart, CartItem
from django.shortcuts import render, redirect, get_object_or_404
from .models import Order, OrderItem, PaymentMethod, CustomerAddress
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Product
from .decorators import vendor_or_admin_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegisterForm ,ProductForm
from .models import CustomerAddress



def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically login after registration
            messages.success(request, "Registration successful.")
            return redirect('product_list')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('product_list')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
@vendor_or_admin_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.is_verified = False  # Mark unverified by default
            product.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})


@login_required
def verify_product(request, pk):
    customer = request.user.customer
    if not customer.is_admin():
        return HttpResponseForbidden("Only admin can verify products.")
    
    product = get_object_or_404(Product, pk=pk)
    product.is_verified = True
    product.save()
    return redirect('unverified_products')


@login_required
def unverified_products(request):
    customer = request.user.customer
    if not customer.is_admin():
        return HttpResponseForbidden("Only admin can view this page.")

    products = Product.objects.filter(is_verified=False)
    return render(request, 'unverified_products.html', {'products': products})


# product_list view (only show verified to customers)
@login_required
def product_list(request):
    products = Product.objects.all()

    if request.user.is_authenticated:
        role = request.user.customer.role
        if role == 'CUSTOMER':
            products = products.filter(is_verified=True)
    else:
        # not logged in? show only verified products
        products = products.filter(is_verified=True)

    query = request.GET.get('q')
    if query:
        products = products.filter(name__icontains=query)

    return render(request, 'products.html', {'products': products})

@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'product_detail.html', {'product': product})


def dashboard(request):
    return render(request, 'dashboard.html')



def get_cart(request):
    customer = request.user.customer  # assumes user is authenticated and linked to Customer
    cart, _ = Cart.objects.get_or_create(customer=customer)
    return cart


@login_required
def cart_view(request):
    cart = get_cart(request)
    return render(request, 'cart.html', {'cart': cart})

@login_required
def add_to_cart(request, product_id):
    cart = get_cart(request)
    product = get_object_or_404(Product, id=product_id)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        item.quantity += 1
    item.save()
    return redirect('cart')

@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    item.delete()
    return redirect('cart')

@login_required
def update_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    quantity = int(request.POST.get('quantity', 1))
    item.quantity = max(1, quantity)
    item.save()
    return redirect('cart')


@login_required
def place_order(request):
    customer = request.user.customer
    cart = get_cart(request)

    if cart.items.count() == 0:
        messages.warning(request, "Cart is empty.")
        return redirect('cart')

    addresses = CustomerAddress.objects.filter(customer=customer)
    payment_methods = PaymentMethod.objects.all()

    if request.method == 'POST':
        address_id = request.POST['address']
        payment_method_id = request.POST['payment_method']

        address = get_object_or_404(CustomerAddress, pk=address_id)
        payment_method = get_object_or_404(PaymentMethod, pk=payment_method_id)

        order = Order.objects.create(
            customer=customer,
            cart=cart,
            address=address,
            payment_method=payment_method
        )

        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            item.product.decrease_stock(item.quantity)

        cart.items.all().delete()

        messages.success(request, "Order placed successfully.")
        return redirect('product_list')

    return render(request, 'place_order.html', {
        'addresses': addresses,
        'payment_methods': payment_methods
    })


@login_required
def order_history(request):
    customer = request.user.customer
    orders = Order.objects.filter(customer=customer).order_by('-placed_at')
    return render(request, 'order_history.html', {'orders': orders})




@login_required
def add_address(request):
    if request.method == 'POST':
        address_line = request.POST['address_line']
        city = request.POST['city']
        state = request.POST['state']
        country = request.POST['country']
        postal_code = request.POST['postal_code']

        CustomerAddress.objects.create(
            customer=request.user.customer,
            address_line=address_line,
            city=city,
            state=state,
            country=country,
            postal_code=postal_code
        )
        messages.success(request, "Address added successfully!")
        return redirect('my_addresses')

    return render(request, 'add_address.html')

@login_required
def my_addresses(request):
    addresses = CustomerAddress.objects.filter(customer=request.user.customer)
    return render(request, 'my_address.html', {'addresses': addresses})
