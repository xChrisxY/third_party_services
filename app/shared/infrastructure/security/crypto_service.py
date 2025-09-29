import logging
import os 
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Dict, Any

from ...domain.repositories.encryption_service import EncryptionService 
from config.settings import settings

logger = logging.getLogger(__name__)

class CrytoService(EncryptionService):
    
    def __init__(self):
        self.encryption_key = settings.encryption_key
        self.fernet = self._create_fernet(settings.encryption_key)

    def _create_fernet(self, password: str) -> Fernet: 
        try: 
            password_bytes = password.encode()
            salt = b'third_party_services_salt' 
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(), 
                length=32, 
                salt=salt, 
                iterations=100000
            )

            key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
            return Fernet(key)
            
        except Exception as e: 
            logger.error(f"Error creando instancia Fernet: {str(e)}")
            raise

    async def encrypt(self, data: str) -> str:
        try: 
            
            if not data: 
                return data 
            
            encrypted_data = self.fernet.encrypt(data.encode())
            return encrypted_data.decode()
            
        except Exception as e: 
            logger.error(f"Error encriptando datos: {str(e)}")
            raise

    async def decrypt(self, encrypted_data: str) -> str:
        try: 
            
            if not encrypted_data: 
                return encrypted_data 
            
            decrypted_data = self.fernet.decrypt(encrypted_data.encode())
            return decrypted_data.decode()
            
        except Exception as e: 
            logger.error(f"Error desencriptando datos: {str(e)}")
            raise

    async def encrypt_credentials(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        try: 
            encrypted_credentials = credentials.copy()   

            if 'api_key' in credentials and credentials['api_key']: 
                encrypted_credentials['api_key'] = await self.encrypt(credentials['api_key'])

            if 'secret_key' in credentials and credentials['secret_key']: 
                encrypted_credentials['secret_key'] = await self.encrypt(credentials['secret_key'])

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
                decrypted_credentials['api_key'] = await self.decrypt(decrypted_credentials['api_key'])

            if 'secret_key' in decrypted_credentials and decrypted_credentials['secret_key']: 
                decrypted_credentials['secret_key'] = await self.decrypt(decrypted_credentials['secret_key'])
            
            decrypted_credentials['encrypted'] = False 
            logger.info(f"Credenciales desencriptadas exitosamente")
            return decrypted_credentials
            
        except Exception as e: 
            logger.error(f"Error desencriptando datos: {str(e)}")
            raise
        