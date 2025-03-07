from abc import ABC, abstractmethod

class CourierInterface(ABC):
    
    @abstractmethod
    def create_waybill(self, shipment_data):
        pass
    
    @abstractmethod
    def generate_label(self, waybill_id):
        pass
    
    @abstractmethod
    def track_shipment(self, waybill_id):
        pass
    
    @abstractmethod
    def map_status(self, courier_status):
        pass
    
    def cancel_shipment(self, waybill_id):
        raise NotImplementedError("This courier does not support cancellation.")
    
    @property
    @abstractmethod
    def supports_cancellation(self):
        pass