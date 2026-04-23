from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import Product, StockMovement
from .forms import ProductForm
from django.http import HttpResponseRedirect
from django.urls import reverse


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
    old = product.stock_quantity
    product.stock_quantity += 1
    product.save()
    StockMovement.objects.create(
        product=product, change_amount=1,
        old_stock=old, new_stock=product.stock_quantity, note="Stock Increase"
    )
    return HttpResponseRedirect(reverse('product_list'))


@login_required
def product_decrease_stock(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if product.stock_quantity > 0:
        old = product.stock_quantity
        product.stock_quantity -= 1
        product.save()
        StockMovement.objects.create(
            product=product, change_amount=-1,
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
