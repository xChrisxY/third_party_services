from abc import ABC, abstractmethod 
from typing import Dict, Any 

class CredentialRepository(ABC): 
    
    @abstractmethod 
    async def encrypt_credentials(self, credentials: Dict[str, Any]) -> Dict[str, Any]: 
        pass 
    
    @abstractmethod 
    async def decrypt_credentials(self, encrypted_credentials: Dict[str, Any]) -> Dict[str, Any]: 
        pass