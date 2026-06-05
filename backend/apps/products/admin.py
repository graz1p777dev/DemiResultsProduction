from django.contrib import admin

from .models import Brand, Category, Product, ProductBatch, ProductImage, ProductVariant


admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Product)
admin.site.register(ProductVariant)
admin.site.register(ProductBatch)
admin.site.register(ProductImage)
