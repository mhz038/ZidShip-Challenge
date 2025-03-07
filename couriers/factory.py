from django.conf import settings
from .aramex import AramexCourier

class CourierFactory:
    
    _registry= {
        "aramex": AramexCourier
    }
    
    @classmethod
    def register_courier(cls, name, courier_class):
        cls._registry[name] = courier_class
    
    @classmethod
    def create(cls, courier_name):
        if courier_name not in cls._registry:
            raise ValueError(f"Unknown courier: {courier_name}")
        
        courier_class = cls._registry[courier_name]
        config = settings.COURIER_CONFIGS.get(courier_name, {})

        return courier_class(**config)