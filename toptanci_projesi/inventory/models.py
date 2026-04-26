from django.db import models
from django.utils.translation import gettext_lazy as _
from datetime import date


class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Product Name"))
    category = models.CharField(max_length=255, verbose_name=_("Category"))
    price = models.FloatField(verbose_name=_("Price"))
    manufacturer = models.CharField(max_length=255, verbose_name=_("Manufacturer"))
    stock_quantity = models.IntegerField(default=0, verbose_name=_("Stock Quantity"))
    unit = models.CharField(max_length=50, default="adet", verbose_name=_("Unit"))
    barcode = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Barcode"))
    tax_rate = models.FloatField(default=20.0, verbose_name=_("Tax Rate (%)"))
    supplier = models.CharField(max_length=255, blank=True, default="", verbose_name=_("Supplier"))
    shelf_location = models.CharField(max_length=50, blank=True, default="", verbose_name=_("Shelf Location"))
    min_stock = models.IntegerField(default=0, verbose_name=_("Minimum Stock"))

    def __str__(self):
        return f"{self.name} - {self.manufacturer}"

    def is_low_stock(self):
        return self.stock_quantity <= self.min_stock


class Customer(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Customer Name"))
    shop_name = models.CharField(max_length=255, blank=True, default="", verbose_name=_("Shop Name"))
    phone = models.CharField(max_length=50, blank=True, default="", verbose_name=_("Phone"))
    email = models.EmailField(blank=True, default="", verbose_name=_("Email"))
    address = models.TextField(blank=True, default="", verbose_name=_("Address"))
    tax_number = models.CharField(max_length=50, blank=True, default="", verbose_name=_("Tax Number"))
    contact_person = models.CharField(max_length=255, blank=True, default="", verbose_name=_("Contact Person"))
    debt = models.FloatField(default=0.0, verbose_name=_("Debt (₺)"))
    debt_due_date = models.DateField(null=True, blank=True, verbose_name=_("Payment Due Date"))
    notes = models.TextField(blank=True, default="", verbose_name=_("Notes"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    @property
    def days_overdue(self):
        """Kaç gün gecikti. Negatif = daha vadesi gelmemiş."""
        if not self.debt_due_date or self.debt <= 0:
            return None
        return (date.today() - self.debt_due_date).days

    @property
    def risk_score(self):
        """Borç × gecikme günü. Sadece gecikmiş borçlar için."""
        days = self.days_overdue
        if days is None or days <= 0:
            return 0
        return round(self.debt * days, 2)

    @property
    def debt_rating(self):
        """A (en iyi) → F (en kötü) harf notu."""
        if self.debt <= 0:
            return 'A'
        if not self.debt_due_date:
            return 'B'
        days = self.days_overdue
        if days < 0:
            return 'B'
        elif days <= 30:
            return 'C'
        elif days <= 90:
            return 'D'
        else:
            return 'F'

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class StockMovement(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='movements', verbose_name=_("Product"))
    change_amount = models.IntegerField(verbose_name=_("Change Amount"))
    old_stock = models.IntegerField(verbose_name=_("Old Stock"))
    new_stock = models.IntegerField(verbose_name=_("New Stock"))
    date = models.DateTimeField(auto_now_add=True, verbose_name=_("Date"))
    note = models.CharField(max_length=255, blank=True, default="", verbose_name=_("Note"))

    def __str__(self):
        return f"{self.product.name} | {self.change_amount:+d} | {self.date.strftime('%d.%m.%Y %H:%M')}"
