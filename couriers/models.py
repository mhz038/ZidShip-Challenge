from django.db import models
import uuid

class Shipment(models.Model):
    SHIPMENT_STATUS_CHOICES = [
        ("CREATED", "Created"),
        ("PICKED_UP", "Picked Up"),
        ("IN_TRANSIT", "In Transit"),
        ("OUT_FOR_DELIVERY", "Out For Delivery"),
        ("DELIVERED", "Delivered"),
        ("FAILED_DELIVERY", "Failed Delivery"),
        ("RETURNED", "Returned"),
        ("EXCEPTION", "Exception"),
        ("CANCELLED", "Cancelled"),
        ("UNKNOWN", "Unknown"),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    courier = models.CharField(max_length=50, db_index=True)
    waybill_id = models.CharField(max_length=100, unique=True, db_index=True)
    reference = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=SHIPMENT_STATUS_CHOICES, default="CREATED")
    courier_status = models.CharField(max_length=100, blank=True)
    
    shipment_data = models.JSONField(default=dict)
    
    raw_response = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_tracked_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self) -> str:
        return f"{self.courier} - {self.waybill_id} ({self.status})"