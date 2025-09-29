import logging
from typing import Dict, Any

from ...domain.repositories.credential_repository import CredentialRepository
from shared.domain.repositories.encryption_service import EncryptionService

logger = logging.getLogger(__name__)

class CompanyCredentialService(CredentialRepository):
    
    def __init__(self, encryption_service: EncryptionService):
        self.encryption_service = encryption_service

    async def encrypt_credentials(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        try: 
            encrypted_credentials = credentials.copy()   

            if 'api_key' in credentials and credentials['api_key']: 
                encrypted_credentials['api_key'] = await self.encryption_service.encrypt(credentials['api_key'])

            if 'secret_key' in credentials and credentials['secret_key']: 
                encrypted_credentials['secret_key'] = await self.encryption_service.encrypt(credentials['secret_key'])

            encrypted_credentials['encrypted'] = True 
            logger.info(f"Credenciales encriptadas exitosamente")
            return encrypted_credentials

        except Exception as e: 
            logger.error(f"Error desencriptando datos: {str(e)}")
            raise

    async def decrypt_credentials(self, encrypted_credentials: Dict[str, Any]) -> Dict[str, Any]:

        try: 
            
            decrypted_credentials = encrypted_credentials.copy()

            if 'api_key' in decrypted_credentials and decrypted_credentials['api_key']: 
                decrypted_credentials['api_key'] = await self.encryption_service.decrypt(decrypted_credentials['api_key'])

            if 'secret_key' in decrypted_credentials and decrypted_credentials['secret_key']: 
                decrypted_credentials['secret_key'] = await self.encryption_service.decrypt(decrypted_credentials['secret_key'])
            
            decrypted_credentials['encrypted'] = False 
            logger.info(f"Credenciales desencriptadas exitosamente")
            return decrypted_credentials
            
        except Exception as e: 
            logger.error(f"Error desencriptando datos: {str(e)}")
            raise
        