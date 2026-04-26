from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import Product, StockMovement, Customer
from .forms import ProductForm, CustomerForm
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import Subquery, OuterRef


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def dashboard(request):
    products = Product.objects.all()
    total_products = products.count()
    total_stock = sum(p.stock_quantity for p in products)
    low_stock_products = [p for p in products if p.is_low_stock()]
    context = {
        'products': products,
        'total_products': total_products,
        'total_stock': total_stock,
        'low_stock_count': len(low_stock_products),
    }
    return render(request, 'inventory/dashboard.html', context)


@login_required
def product_list(request):
    products = Product.objects.all()

    q = request.GET.get('q', '').strip()
    category = request.GET.get('category', '')
    supplier = request.GET.get('supplier', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    low_stock = request.GET.get('low_stock', '')
    sort = request.GET.get('sort', 'name')

    if q:
        products = products.filter(name__icontains=q)
    if category:
        products = products.filter(category=category)
    if supplier:
        products = products.filter(supplier=supplier)
    if min_price:
        products = products.filter(price__gte=float(min_price))
    if max_price:
        products = products.filter(price__lte=float(max_price))

    # Apply sorting before low_stock (which converts queryset to list)
    if sort == 'stock_asc':
        products = products.order_by('stock_quantity', 'name')
    elif sort == 'stock_desc':
        products = products.order_by('-stock_quantity', 'name')
    elif sort == 'category':
        products = products.order_by('category', 'name')
    elif sort == 'last_movement':
        latest_movement = StockMovement.objects.filter(
            product=OuterRef('pk')
        ).order_by('-date').values('date')[:1]
        products = products.annotate(last_move=Subquery(latest_movement)).order_by('-last_move', 'name')
    else:  # default: name
        products = products.order_by('name')

    if low_stock:
        products = [p for p in products if p.is_low_stock()]

    all_products = Product.objects.all()
    categories = all_products.values_list('category', flat=True).distinct().order_by('category')
    suppliers = all_products.values_list('supplier', flat=True).distinct().order_by('supplier')

    active_filters = {}
    if q: active_filters['Arama'] = q
    if category: active_filters['Kategori'] = category
    if supplier: active_filters['Tedarikçi'] = supplier
    if min_price: active_filters['Min Fiyat'] = f"{min_price} ₺"
    if max_price: active_filters['Max Fiyat'] = f"{max_price} ₺"
    if low_stock: active_filters['Stok'] = 'Düşük Stok'

    # Build query string without 'sort' param (used in template sort links)
    get_params = request.GET.copy()
    get_params.pop('sort', None)
    sort_params = get_params.urlencode()

    context = {
        'products': products,
        'categories': categories,
        'suppliers': suppliers,
        'active_filters': active_filters,
        'q': q,
        'selected_category': category,
        'selected_supplier': supplier,
        'min_price': min_price,
        'max_price': max_price,
        'low_stock': low_stock,
        'current_sort': sort,
        'sort_params': sort_params,
    }
    return render(request, 'inventory/product_list.html', context)
    

@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'inventory/product_form.html', {'form': form})


@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return render(request, 'inventory/product_confirm_delete.html', {'product': product})


@login_required
def product_increase_stock(request, pk):
    product = get_object_or_404(Product, pk=pk)
    try:
        amount = int(request.POST.get('amount', 1))
        if amount < 1:
            amount = 1
    except (ValueError, TypeError):
        amount = 1
    old = product.stock_quantity
    product.stock_quantity += amount
    product.save()
    StockMovement.objects.create(
        product=product, change_amount=amount,
        old_stock=old, new_stock=product.stock_quantity, note="Stock Increase"
    )
    return HttpResponseRedirect(reverse('product_list'))


@login_required
def product_decrease_stock(request, pk):
    product = get_object_or_404(Product, pk=pk)
    try:
        amount = int(request.POST.get('amount', 1))
        if amount < 1:
            amount = 1
    except (ValueError, TypeError):
        amount = 1
    if product.stock_quantity >= amount:
        old = product.stock_quantity
        product.stock_quantity -= amount
        product.save()
        StockMovement.objects.create(
            product=product, change_amount=-amount,
            old_stock=old, new_stock=product.stock_quantity, note="Stock Decrease"
        )
    return HttpResponseRedirect(reverse('product_list'))


@login_required
def stock_history(request, pk):
    product = get_object_or_404(Product, pk=pk)
    movements = product.movements.order_by('-date')
    return render(request, 'inventory/stock_history.html', {'product': product, 'movements': movements})


@login_required
def all_stock_movements(request):
    movements = StockMovement.objects.select_related('product').order_by('-date')
    return render(request, 'inventory/all_stock_movements.html', {'movements': movements})


# ─── Customer Views ────────────────────────────────────────────────────────────

@login_required
def customer_list(request):
    q = request.GET.get('q', '').strip()
    sort = request.GET.get('sort', 'name')
    customers = Customer.objects.all()

    if q:
        customers = customers.filter(name__icontains=q)

    # ORM ile sıralanabilenler
    if sort == 'name':
        customers = customers.order_by('name')
    elif sort == 'shop_name':
        customers = customers.order_by('shop_name', 'name')
    elif sort == 'debt_asc':
        customers = customers.order_by('debt', 'name')
    elif sort == 'debt_desc':
        customers = customers.order_by('-debt', 'name')
    elif sort == 'created':
        customers = customers.order_by('-created_at')
    else:
        customers = customers.order_by('name')

    # debt_rating property'e göre sıralama (Python tarafında)
    if sort == 'rating':
        rating_order = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'F': 4}
        customers = sorted(customers, key=lambda c: (rating_order.get(c.debt_rating, 9), c.name))

    get_params = request.GET.copy()
    get_params.pop('sort', None)
    sort_params = get_params.urlencode()

    return render(request, 'inventory/customer_list.html', {
        'customers': customers,
        'q': q,
        'current_sort': sort,
        'sort_params': sort_params,
    })


@login_required
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('customer_list')
    else:
        form = CustomerForm()
    return render(request, 'inventory/customer_form.html', {'form': form})


@login_required
def customer_update(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('customer_list')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'inventory/customer_form.html', {'form': form, 'customer': customer})


@login_required
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        customer.delete()
        return redirect('customer_list')
    return render(request, 'inventory/customer_confirm_delete.html', {'customer': customer})
