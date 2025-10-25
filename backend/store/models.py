from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.utils import timezone
from cloudinary.models import CloudinaryField


# =======================
#  CUSTOM USER MANAGER
# =======================
class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        if not username:
            raise ValueError("Users must have a username")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, username, password, **extra_fields)


# =======================
#  CUSTOM USER MODEL
# =======================
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.username


# =======================
#  CATEGORY
# =======================
class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    image = CloudinaryField('category_images', blank=True, null=True)

    def __str__(self):
        return self.name


# =======================
#  PRODUCT
# =======================
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    main_image = CloudinaryField('products/main', blank=True, null=True)
    image1 = CloudinaryField('products/extra', blank=True, null=True)
    image2 = CloudinaryField('products/extra', blank=True, null=True)
    image3 = CloudinaryField('products/extra', blank=True, null=True)
    image4 = CloudinaryField('products/extra', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deal_of_the_day = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_new = models.BooleanField(default=False)
    # New fields for abroad orders
    is_abroad_order = models.BooleanField(default=False)
    abroad_delivery_days = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Estimated delivery days for orders from abroad. Only applies if 'Is Abroad Order' is checked."
    )

    def __str__(self):
        return self.name
    


class ProductVariant(models.Model):
    product = models.ForeignKey(
        "Product", on_delete=models.CASCADE, related_name="variants"
    )
    color_name = models.CharField(max_length=50, blank=True, null=True)
    color_code = models.CharField(max_length=7, blank=True, null=True, help_text="e.g. #000000")
    storage_option = models.CharField(max_length=50, blank=True, null=True, help_text="e.g. 64GB, 128GB")

    image_main = CloudinaryField("variants/main", blank=True, null=True)
    image1 = CloudinaryField("variants/extra", blank=True, null=True)
    image2 = CloudinaryField("variants/extra", blank=True, null=True)
    image3 = CloudinaryField("variants/extra", blank=True, null=True)
    image4 = CloudinaryField("variants/extra", blank=True, null=True)

    stock = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        parts = [self.product.name]
        if self.color_name:
            parts.append(self.color_name)
        if self.storage_option:
            parts.append(self.storage_option)
        return " - ".join(parts)

    


# =======================
#  CART AND CART ITEM
# =======================
class Cart(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Cart"


class CartItem(models.Model):
    cart_item_id = models.AutoField(primary_key=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"



# =======================
#  PAYMENT MODELS
# =======================
class PaymentMethod(models.Model):
    payment_method_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    method_name = models.CharField(max_length=100)
    details = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.method_name



class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    payment_id = models.AutoField(primary_key=True)
    order_id = models.IntegerField()  # Order relationship can be added if needed
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Payment {self.payment_id} for Order {self.order_id}"


class PaymentDetail(models.Model):
    PAYMENT_DETAIL_STATUS_CHOICES = [
        ('success', 'Success'),
        ('failure', 'Failure'),
        ('pending', 'Pending'),
    ]
    payment_detail_id = models.AutoField(primary_key=True)
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name="details")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=PAYMENT_DETAIL_STATUS_CHOICES, default='pending')
    reference = models.CharField(max_length=200)
    details = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Detail for {self.payment}"


# =======================
#  SHIPPING ADDRESS
# =======================
class ShippingAddress(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.full_name} - {self.city}"


# =======================
#  ORDER AND ORDER ITEM
# =======================
class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('ready_for_pickup', 'Ready for Pickup'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    order_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    shipping_address = models.ForeignKey(ShippingAddress, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=ORDER_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.order_id} - {self.user.username}"



class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
