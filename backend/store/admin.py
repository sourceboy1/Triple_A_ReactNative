from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import (
    CustomUser, Category, Product, Cart, CartItem,
    PaymentMethod, Payment, PaymentDetail,
    ShippingAddress, Order, OrderItem, ProductVariant
)

# =======================
# CUSTOM USER ADMIN
# =======================
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('id', 'email', 'username', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('id',)
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'address', 'phone')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )


# =======================
# PRODUCT VARIANT INLINE
# =======================
class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = (
        "color_name",
        "color_code",
        "storage_option",
        "price",
        "stock",
        "image_main",
        "image1",
        "image2",
        "image3",
        "image4",
        "variant_image_tag",
    )
    readonly_fields = ("variant_image_tag",)

    def variant_image_tag(self, obj):
        if obj.image_main:
            return format_html('<img src="{}" style="width:60px;height:auto;" />', obj.image_main.url)
        return "-"
    variant_image_tag.short_description = "Main Variant Image"


# =======================
# PRODUCT ADMIN
# =======================
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'category', 'price', 'stock', 
        'is_deal_of_the_day', 'is_featured', 'is_new',
        'is_abroad_order', 'main_image_tag', 'image1_tag',
        'image2_tag', 'image3_tag', 'image4_tag'
    )
    list_filter = ('category', 'is_deal_of_the_day', 'is_featured', 'is_new', 'is_abroad_order')
    search_fields = ('name', 'description')
    inlines = [ProductVariantInline]

    # Thumbnails
    def main_image_tag(self, obj):
        if obj.main_image:
            return format_html('<img src="{}" style="width:50px;height:auto;" />', obj.main_image.url)
        return "-"
    main_image_tag.short_description = 'Main Image'

    def image1_tag(self, obj):
        if obj.image1:
            return format_html('<img src="{}" style="width:50px;height:auto;" />', obj.image1.url)
        return "-"
    image1_tag.short_description = 'Image 1'

    def image2_tag(self, obj):
        if obj.image2:
            return format_html('<img src="{}" style="width:50px;height:auto;" />', obj.image2.url)
        return "-"
    image2_tag.short_description = 'Image 2'

    def image3_tag(self, obj):
        if obj.image3:
            return format_html('<img src="{}" style="width:50px;height:auto;" />', obj.image3.url)
        return "-"
    image3_tag.short_description = 'Image 3'

    def image4_tag(self, obj):
        if obj.image4:
            return format_html('<img src="{}" style="width:50px;height:auto;" />', obj.image4.url)
        return "-"
    image4_tag.short_description = 'Image 4'


# =======================
# CATEGORY ADMIN
# =======================
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_id', 'name', 'description')
    search_fields = ('name',)


# =======================
# OTHER MODELS ADMIN
# =======================
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at')


class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart_item_id', 'cart', 'product', 'quantity')


class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('payment_method_id', 'user', 'method_name', 'created_at')


class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'order_id', 'payment_method', 'amount', 'status', 'payment_date')
    list_filter = ('status',)


class PaymentDetailAdmin(admin.ModelAdmin):
    list_display = ('payment_detail_id', 'payment', 'amount', 'status', 'reference')


class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'full_name', 'city', 'state', 'country')


class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'user', 'total_amount', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__username',)


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'price')


# =======================
# REGISTER MODELS
# =======================
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
admin.site.register(PaymentMethod, PaymentMethodAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(PaymentDetail, PaymentDetailAdmin)
admin.site.register(ShippingAddress, ShippingAddressAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
