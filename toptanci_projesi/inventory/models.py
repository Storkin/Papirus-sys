from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name="Ürün Adı")
    category = models.CharField(max_length=255, verbose_name="Kategori")
    price = models.FloatField(verbose_name="Fiyat")
    manufacturer = models.CharField(max_length=255, verbose_name="Üretici")
    stock_quantity = models.IntegerField(default=0, verbose_name="Stok Miktarı")
    unit = models.CharField(max_length=50, default="adet", verbose_name="Birim")
    barcode = models.CharField(max_length=100, blank=True, default="", verbose_name="Barkod")
    tax_rate = models.FloatField(default=20.0, verbose_name="KDV Oranı (%)")
    supplier = models.CharField(max_length=255, blank=True, default="", verbose_name="Tedarikçi")
    shelf_location = models.CharField(max_length=50, blank=True, default="", verbose_name="Raf Konumu")
    min_stock = models.IntegerField(default=0, verbose_name="Minimum Stok")

    def __str__(self):
        return f"{self.name} - {self.manufacturer}"

    def is_low_stock(self):
        return self.stock_quantity <= self.min_stock


class StockMovement(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='movements', verbose_name="Ürün")
    change_amount = models.IntegerField(verbose_name="Değişim Miktarı")
    old_stock = models.IntegerField(verbose_name="Eski Stok")
    new_stock = models.IntegerField(verbose_name="Yeni Stok")
    date = models.DateTimeField(auto_now_add=True, verbose_name="Tarih")
    note = models.CharField(max_length=255, blank=True, default="", verbose_name="Not")

    def __str__(self):
        return f"{self.product.name} | {self.change_amount:+d} | {self.date.strftime('%d.%m.%Y %H:%M')}"
