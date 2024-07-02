from django.contrib import admin
from .models import Product

# admin.site.register(Product ) #display product model in admin

class ProductAdmin(admin.ModelAdmin):
    list_display=['id','name','pdetails','cat','is_active']
    list_filter=['cat','is_active']

admin.site.register(Product,ProductAdmin)