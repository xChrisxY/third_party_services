from ...domain.entities.client import Client

class ClientResponseDTO(Client): 
    class Config: 
        from_attributes = True 
        json_encoders = {
            'datetime': lambda v: v.isoformat() if v else None
        }