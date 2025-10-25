from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    CustomUser, Category, Product, Cart, CartItem,
    PaymentMethod, Payment, PaymentDetail,
    ShippingAddress, Order, OrderItem,ProductVariant
)

# =======================
#  USER SERIALIZER
# =======================
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'address', 'phone']


# =======================
#  REGISTER SERIALIZER
# =======================
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=6)

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'address', 'phone', 'password']

    def validate_email(self, value):
        if CustomUser.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email is already taken.")
        return value

    def validate_username(self, value):
        if CustomUser.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Username is already taken.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user


# =======================
#  CATEGORY / PRODUCT / CART / ORDER SERIALIZERS (unchanged)
# =======================
from rest_framework import serializers
from .models import Product, ProductVariant

class ProductVariantSerializer(serializers.ModelSerializer):
    variant_id = serializers.IntegerField(source="id", read_only=True)
    color_hex = serializers.SerializerMethodField()   # maps color_code -> color_hex
    storage = serializers.SerializerMethodField()     # maps storage_option -> storage

    main_image = serializers.SerializerMethodField()
    image1 = serializers.SerializerMethodField()
    image2 = serializers.SerializerMethodField()
    image3 = serializers.SerializerMethodField()
    image4 = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariant
        fields = [
            "variant_id",
            "color_name",
            "color_hex",
            "storage",
            "price",
            "stock",
            "main_image",
            "image1",
            "image2",
            "image3",
            "image4",
        ]

    def _get_url(self, field):
        return field.url if field and hasattr(field, "url") else None

    def get_color_hex(self, obj):
        return obj.color_code if getattr(obj, "color_code", None) else None

    def get_storage(self, obj):
        return obj.storage_option if getattr(obj, "storage_option", None) else None

    def get_main_image(self, obj):
        return self._get_url(obj.image_main)

    def get_image1(self, obj):
        return self._get_url(obj.image1)

    def get_image2(self, obj):
        return self._get_url(obj.image2)

    def get_image3(self, obj):
        return self._get_url(obj.image3)

    def get_image4(self, obj):
        return self._get_url(obj.image4)


class ProductSerializer(serializers.ModelSerializer):
    main_image = serializers.SerializerMethodField()
    image1 = serializers.SerializerMethodField()
    image2 = serializers.SerializerMethodField()
    image3 = serializers.SerializerMethodField()
    image4 = serializers.SerializerMethodField()

    variants = ProductVariantSerializer(many=True, read_only=True)
    available_colors = serializers.SerializerMethodField()
    available_storages = serializers.SerializerMethodField()
    availability_map = serializers.SerializerMethodField()
    storage_map = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id", "category", "name", "description", "price", "original_price",
            "stock", "main_image", "image1", "image2", "image3", "image4",
            "is_deal_of_the_day", "is_featured", "is_new",
            "is_abroad_order", "abroad_delivery_days",
            "variants",
            "available_colors", "available_storages", "availability_map", "storage_map",
        ]

    def _get_url(self, field):
        return field.url if field and hasattr(field, "url") else None

    def get_main_image(self, obj):
        return self._get_url(obj.main_image)

    def get_image1(self, obj):
        return self._get_url(obj.image1)

    def get_image2(self, obj):
        return self._get_url(obj.image2)

    def get_image3(self, obj):
        return self._get_url(obj.image3)

    def get_image4(self, obj):
        return self._get_url(obj.image4)

    def get_available_colors(self, obj):
        colors = []
        seen = set()
        for v in obj.variants.all():
            key = (v.color_name, v.color_code)
            if key in seen:
                continue
            seen.add(key)
            colors.append({
                "color_name": v.color_name,
                "color_hex": v.color_code,
            })
        return colors

    def get_available_storages(self, obj):
        storages = []
        seen = set()
        for v in obj.variants.all():
            s = v.storage_option
            if s and s not in seen:
                seen.add(s)
                storages.append(s)
        return storages

    def get_availability_map(self, obj):
        result = {}
        for v in obj.variants.all():
            key = v.color_code or v.color_name or f"color_{v.id}"
            if key not in result:
                result[key] = []
            if v.storage_option and v.storage_option not in result[key]:
                result[key].append(v.storage_option)
        return result

    def get_storage_map(self, obj):
        result = {}
        for v in obj.variants.all():
            s = v.storage_option or "default"
            key = v.color_code or v.color_name or f"color_{v.id}"
            if s not in result:
                result[s] = []
            if key not in result[s]:
                result[s].append(key)
        return result


class CategorySerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["category_id", "name", "description", "image", "products"]

    def get_image(self, obj):
        return obj.image.url if obj.image and hasattr(obj.image, "url") else None




class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = '__all__'


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'created_at']


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = '__all__'


User = get_user_model()

class LoginSerializer(serializers.Serializer):
    email_or_username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        identifier = data.get('email_or_username')
        password = data.get('password')

        if not identifier or not password:
            raise serializers.ValidationError({'non_field_errors': ['Email/username and password are required']})

        # try email, then username
        user = User.objects.filter(email__iexact=identifier).first()
        if not user:
            user = User.objects.filter(username__iexact=identifier).first()

        if not user or not user.check_password(password):
            raise serializers.ValidationError({'non_field_errors': ['Incorrect email/username or password']})

        if not user.is_active:
            raise serializers.ValidationError({'non_field_errors': ['User account is disabled']})

        data['user'] = user
        return data
