from django import forms
from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'category', 'price', 'manufacturer',
            'stock_quantity', 'unit', 'barcode',
            'tax_rate', 'supplier', 'shelf_location', 'min_stock'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'manufacturer': forms.TextInput(attrs={'class': 'form-control'}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'adet, kutu, paket...'}),
            'barcode': forms.TextInput(attrs={'class': 'form-control'}),
            'tax_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'supplier': forms.TextInput(attrs={'class': 'form-control'}),
            'shelf_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'A1, B3...'}),
            'min_stock': forms.NumberInput(attrs={'class': 'form-control'}),
        }
