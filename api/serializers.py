from rest_framework import serializers
from .models import Product, Order

# ================= Product Serializer =================
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


# ================= Order Item Serializer (Corrected) =================
class OrderItemSerializer(serializers.Serializer):
    product = serializers.IntegerField()
    order_qty = serializers.IntegerField()

    def validate(self, data):
        # Check product exists
        try:
            product = Product.objects.get(product_id=data['product'])
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found")

        qty = data['order_qty']
        if qty <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")

        # Attach actual product object
        data['product_obj'] = product
        return data


# ================= Bulk Order Serializer =================
class BulkOrderSerializer(serializers.Serializer):
    items = OrderItemSerializer(many=True)

    def create(self, validated_data):
        orders = []
        for item in validated_data['items']:
            product = item['product_obj']
            qty     = item['order_qty']

            order = Order.objects.create(
                product=product,
                order_qty=qty,
                order_price=product.product_price
            )
            orders.append(order)

        return orders




# ================= Today Order Serializer =================
class TodayOrderSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.product_name')
    product_id = serializers.IntegerField(source='product.product_id')

    class Meta:
        model = Order
        fields = ['id', 'product_id', 'product_name', 'order_qty', 'order_price', 'order_datetime']


# ================= Daily Total Serializer =================
class DailyTotalSerializer(serializers.Serializer):
    date = serializers.DateField()
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    order_count = serializers.IntegerField()