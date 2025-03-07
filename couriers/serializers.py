from rest_framework import serializers
from .models import Shipment
from .factory import CourierFactory

class CreateShipmentSerializer(serializers.Serializer):
    
    courier = serializers.CharField(max_length=50)
    reference = serializers.CharField(max_length=100, required=False, allow_blank=True)
    sender = serializers.DictField()
    recipient = serializers.DictField()
    package = serializers.DictField()
    
    def validate_courier(self, value):
        try:
            CourierFactory.create(value)
            return value
        except ValueError as e:
            raise serializers.ValidationError(str(e))

class ShipmentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Shipment
        fields = "__all__"