from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
from django.utils import timezone
from .models import Shipment
from .serializers import ShipmentSerializer, CreateShipmentSerializer
from .factory import CourierFactory
import logging

logger = logging.getLogger(__name__)

class ShipmentViewSet(viewsets.ModelViewSet):
    
    queryset = Shipment.objects.all()
    serializer_class = ShipmentSerializer
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CreateShipmentSerializer
        return self.serializer_class
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        courier_name = data.pop('courier')
        
        try:
            courier = CourierFactory.create(courier_name)
            courier_response = courier.create_waybill(data)
            
            shipment = Shipment(
                courier=courier_name,
                waybill_id=courier_response['waybill_id'],
                reference=courier_response.get('reference', ''),
                status=courier_response.get('status', 'CREATED'),
                courier_status=courier_response.get('courier_status', ''),
                shipment_data=data,
                raw_response=courier_response.get('raw_response', {})
            )
            shipment.save()
            
            response_serializer = ShipmentSerializer(shipment)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error creating shipment: {str(e)}")
            return Response(
                {"error": f"Failed to create shipment: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def label(self, request, pk=None):
        shipment = self.get_object()
        
        try:
            courier = CourierFactory.create(shipment.courier)
            label_data = courier.generate_label(shipment.waybill_id)
            
            response = HttpResponse(label_data, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{shipment.waybill_id}.pdf"'
            return response
            
        except Exception as e:
            logger.error(f"Error generating label: {str(e)}")
            return Response(
                {"error": f"Failed to generate label: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def track(self, request, pk=None):
        shipment = self.get_object()
        
        try:
            courier = CourierFactory.create(shipment.courier)
            tracking_info = courier.track_shipment(shipment.waybill_id)
            
            shipment.status = tracking_info.get('status', shipment.status)
            shipment.courier_status = tracking_info.get('courier_status', shipment.courier_status)
            shipment.raw_response = tracking_info.get('raw_response', {})
            shipment.last_tracked_at = timezone.now()
            shipment.save()
            
            return Response(tracking_info)
            
        except Exception as e:
            logger.error(f"Error tracking shipment: {str(e)}")
            return Response(
                {"error": f"Failed to track shipment: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        shipment = self.get_object()
        
        try:
            courier = CourierFactory.create(shipment.courier)
            
            if not courier.supports_cancellation:
                return Response(
                    {"error": "This courier does not support cancellation"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            cancel_result = courier.cancel_shipment(shipment.waybill_id)
            
            if cancel_result.get('cancelled', False):
                shipment.status = "CANCELLED"
                shipment.save()
            
            return Response(cancel_result)
            
        except Exception as e:
            logger.error(f"Error cancelling shipment: {str(e)}")
            return Response(
                {"error": f"Failed to cancel shipment: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )