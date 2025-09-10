from ...domain.entities.company import Company 

class CompanyResponseDTO(Company): 
    class Config: 
        from_attributes = True 
        json_encoders = {
            'datetime': lambda v: v.isoformat() if v else None
        }