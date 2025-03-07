from .interfaces import CourierInterface
from .http_client import HttpClient

class AramexCourier(CourierInterface):
    
    STATUS_MAPPING = {
        "1": "CREATED",
        "2": "PICKED_UP",
        "3": "IN_TRANSIT",
        "4": "OUT_FOR_DELIVERY",
        "5": "DELIVERED",
        "6": "FAILED_DELIVERY",
        "7": "RETURNED",
        "8": "EXCEPTION"
    }
    
    def __init__(self, api_key, account_number, account_pin, base_url="https://api.aramex.com/v1"):
        self.api_key = api_key
        self.account_number = account_number
        self.account_pin = account_pin
        self.base_url = base_url
        self.http_client = HttpClient(
            default_headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "API-Key": self.api_key
            }
        )
    
    def create_waybill(self, shipment_data):
        url = f"{self.base_url}/create_waybill"
        
        aramex_payload = self._transform_to_aramex_format(shipment_data)
        
        response = self.http_client.request(
            method="POST",
            url=url,
            json_data=aramex_payload
        )
        
        if response.status_code != 200:
            error_data = response.json() if response.content else {"message": "Unknown error"}
            raise Exception(f"Aramex API error: {error_data.get('message', 'Unknown error')}")
        
        result = response.json()
        
        return result
    
    def generate_label(self, waybill_id):
        url = f"{self.base_url}/{waybill_id}/label"
        
        response = self.http_client.request(
            method="GET", 
            url=url
        )
        
        if response.status_code != 200:
            error_data = response.json() if response.content else {"message": "Unknown error"}
            raise Exception(f"Failed to generate label: {error_data.get('message', 'Unknown error')}")
        
        return response.content
    
    def track_shipment(self, waybill_id):
        url = f"{self.base_url}/{waybill_id}/tracking"
        
        response = self.http_client.request(method="GET", url=url)
        
        if response.status_code != 200:
            error_data = response.json() if response.content else {"message": "Unknown error"}
            raise Exception(f"Failed to track shipment: {error_data.get('message', 'Unknown error')}")
        
        result = response.json()
        
        return result
    
    def map_status(self, courier_status):
        return self.STATUS_MAPPING.get(courier_status, "UNKNOWN")
    
    @property
    def supports_cancellation(self):
        return True
    
    def cancel_shipment(self, waybill_id):
        url = f"{self.base_url}/{waybill_id}/cancel"
        
        response = self.http_client.request(method="POST", url=url)
        
        if response.status_code != 200:
            error_data = response.json() if response.content else {"message": "Unknown error"}
            raise Exception(f"Failed to cancel shipment: {error_data.get('message', 'Unknown error')}")
        
        result = response.json()
        
        return result
    
    def _transform_to_aramex_format(self, shipment_data):
        return shipment_data