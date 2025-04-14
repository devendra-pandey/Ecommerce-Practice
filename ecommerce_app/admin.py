from django.contrib import admin
from .models import *

admin.site.register(Category)
admin.site.register(Customer)
admin.site.register(CustomerAddress)
admin.site.register(PaymentMethod)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'is_verified']
    list_editable = ['is_verified']

admin.site.register(Product, ProductAdmin)
