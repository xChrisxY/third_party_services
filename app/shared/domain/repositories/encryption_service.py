from abc import ABC, abstractmethod 

class EncryptionService(ABC): 

    @abstractmethod
    async def encrypt(self, data: str) -> str: 
        pass 
    
    @abstractmethod 
    async def decrypt(self, encrypted_data: str) -> str: 
        pass