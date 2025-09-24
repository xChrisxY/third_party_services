from ...domain.entities.client import Client

class ClientResponseDTO(Client): 
    class Config: 
        from_attributes = True 
        populate_by_name = True
        json_encoders = {
            'datetime': lambda v: v.isoformat() if v else None
        }