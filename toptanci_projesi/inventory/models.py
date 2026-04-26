from django.db import models
from django.utils.translation import gettext_lazy as _


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


class StockMovement(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='movements', verbose_name=_("Product"))
    change_amount = models.IntegerField(verbose_name=_("Change Amount"))
    old_stock = models.IntegerField(verbose_name=_("Old Stock"))
    new_stock = models.IntegerField(verbose_name=_("New Stock"))
    date = models.DateTimeField(auto_now_add=True, verbose_name=_("Date"))
    note = models.CharField(max_length=255, blank=True, default="", verbose_name=_("Note"))

    def __str__(self):
        return f"{self.product.name} | {self.change_amount:+d} | {self.date.strftime('%d.%m.%Y %H:%M')}"
