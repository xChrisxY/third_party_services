from typing import Dict, Any 
import uuid
import json
import logging 
import asyncio
from datetime import datetime

from ...domain.entities.client import Client 
from ...domain.entities.client_address import ClientAddress 
from ...domain.entities.client_contact import ClientContact
from ...domain.repositories.client_repository import ClientRepository 
from ...domain.repositories.external_client_repository import ExternalClientRepository

from company.domain.repositories.company_repository import CompanyRepository
from shared.responses import ErrorResponse

logger = logging.getLogger(__name__)

class InvoiceClientUseCase: 
    
    def __init__(
        self, 
        client_repository: ClientRepository, 
        external_client_repository: ExternalClientRepository, 
        company_repository: CompanyRepository
    ):
        self.client_repository = client_repository
        self.external_client_repository = external_client_repository 
        self.company_repository = company_repository
        
    async def execute(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]: 
        
        try: 
            
            company_id = invoice_data.get("company_id")
            if not company_id: 
                return {
                    "success": False, 
                    "error": "company_id es requerido para facturar"
                }

            company = await self.company_repository.get_by_id(company_id)
            if not company: 
                return {
                    "success": False, 
                    "error": f"Empresa no encontrada: {company_id}"
                }   
                
            logger.info(f"Facturando para la empresa: {company.business_name}")

            validation_result = await self._validate_input_data(invoice_data)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": f"Datos inválidos: {validation_result['error']}"
                }
            
            rfc = invoice_data.get("rfc")
            business_name = invoice_data.get("business_name")
            
            logger.info(f"Procesando facturación para RFC: {rfc}, Empresa: {business_name}")
            logger.info(f"Datos completos recibidos: {json.dumps(invoice_data, indent=2)}")

            existing_client = await self.client_repository.find_by_rfc(rfc)
            
            if existing_client: 
                factura_client_uid = existing_client.external_uid 
                internal_client_id = existing_client.id
                logger.info(f"Usando cliente existente: {internal_client_id}")
            else:
                logger.info(f"Creando nuevo cliente con RFC: {rfc}")
                client_creation_result = await self._create_client(invoice_data)
                factura_client_uid = client_creation_result["factura_uid"]
                internal_client_id = client_creation_result["internal_client_id"]
                logger.info(f"Nuevo cliente creado: {internal_client_id}")
            
            invoice_result = await self._create_invoice(
                factura_client_uid, 
                invoice_data.get("invoice_details", {})
            )

            logger.info(f"Resultado de facturación: {invoice_result}")

            return {
                "success": True, 
                "invoice_id": invoice_result.get("invoice_id"), 
                "internal_client_id": internal_client_id, 
                "factura_client_id": factura_client_uid, 
                "internal_company_id": company_id,
                "message": "Invoice processed successfully"
            }

        except Exception as e: 
            logger.error(f"Error processing invoice: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}

    async def _create_invoice(self, client_uid: str, invoice_details: Dict[str, Any]) -> Dict[str, Any]: 
        logger.info(f"Creando factura para cliente UID: {client_uid}")
        logger.info(f"Detalles de factura: {json.dumps(invoice_details, indent=2)}")
        return {"invoice_id": "inv_12345"}

    async def _create_client(self, client_data: Dict[str, Any]) -> Dict[str, Any]: 
        
        try:
            factura_payload = self._map_to_factura_format(client_data)
            logger.info(f"Datos para Factura.com: {json.dumps(factura_payload, indent=2)}")
            
            factura_response = await self.external_client_repository.create_client(factura_payload)
            logger.info(f"Respuesta de Factura.com: {json.dumps(factura_response, indent=2)}")
            
            if factura_response.get("status") != "success":
                raise Exception(f"Factura.com error: {factura_response.get('message')}")
                
            factura_uid = factura_response.get('Data', {}).get('UID')
            if not factura_uid:
                raise Exception("No se obtuvo UID de Factura.com")
            
            await asyncio.sleep(2)
            
            client_details = await self.external_client_repository.get_client_by_id(factura_uid)
            
            client_id = await self._create_client_in_database(client_data, factura_uid, client_details)
            
            return {
                "factura_uid": factura_uid, 
                "internal_client_id": client_id
            }
            
        except Exception as e:
            logger.error(f"Error creando cliente: {str(e)}")
            raise

    async def _create_client_in_database(self, event_data: Dict[str, Any], factura_uid: str, factura_response: Dict[str, Any]) -> str:
        try:
            factura_data = factura_response.get('Data', {})
            contact_data = factura_data.get('Contacto', {})
            
            address = ClientAddress(
                street=event_data.get("address", {}).get("street"),
                exterior_number=event_data.get("address", {}).get("exterior_number"),
                interior_number=event_data.get("address", {}).get("interior_number"),
                neighborhood=event_data.get("address", {}).get("neighborhood"),
                zip_code=event_data.get("address", {}).get("zip_code"),
                city=event_data.get("address", {}).get("city"),
                municipality=event_data.get("address", {}).get("municipality"),
                locality=event_data.get("address", {}).get("locality"),
                state=event_data.get("address", {}).get("state"),
                country=event_data.get("address", {}).get("country", "MEX")
            )
            
            contact = ClientContact(
                name=event_data.get("contact", {}).get("name"),
                last_names=event_data.get("contact", {}).get("last_names"),
                email=event_data.get("contact", {}).get("email"),
                email2=event_data.get("contact", {}).get("email2"),
                email3=event_data.get("contact", {}).get("email3"),
                phone=event_data.get("contact", {}).get("phone")
            )
            
            emails = []
            if event_data.get("contact", {}).get("email"):
                emails.append(event_data.get("contact", {}).get("email"))
            if event_data.get("contact", {}).get("email2"):
                emails.append(event_data.get("contact", {}).get("email2"))
            if event_data.get("contact", {}).get("email3"):
                emails.append(event_data.get("contact", {}).get("email3"))

            tax_regime_name = await self._get_tax_regime_name(event_data.get("tax_regime"))
            cfdi_use_name = await self._get_cfdi_use_name(event_data.get("cfdi_use"))
            
            client_dict = {
                "tenant_id": event_data.get("tenant_id", str(uuid.uuid4())),
                "external_uid": factura_uid,
                "company_id": event_data.get("company_id"),
                "rfc": event_data.get("rfc"),
                "business_name": event_data.get("business_name"),
                "tax_regime": event_data.get("tax_regime"),
                "tax_regime_name": tax_regime_name,
                "tax_id_number": event_data.get("tax_id_number", ""),
                "address": address,
                "contact": contact,
                "cfdi_use": event_data.get("cfdi_use"),
                "cfdi_use_name" : cfdi_use_name,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "status": "active",
                "factura_sync": True,
                "emails": emails if emails else None
            }
            
            if not client_dict["business_name"]:
                raise ValueError("business_name es requerido")
            if not client_dict["rfc"]:
                raise ValueError("rfc es requerido")
            
            client_model = Client(**client_dict)
            created_client = await self.client_repository.create(client_model)
            
            if hasattr(created_client, 'inserted_id'):
                client_id = str(created_client.inserted_id)
            elif hasattr(created_client, 'id'):
                client_id = str(created_client.id)
            else:
                client_id = str(created_client)
            
            logger.info(f"Cliente creado en BD con ID: {client_id}")
            return client_id
            
        except Exception as e:
            logger.error(f"Error creando cliente en BD: {str(e)}")
            raise

    def _map_to_factura_format(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if hasattr(event_data, 'model_dump'):
                event_data = event_data.model_dump()
            
            address = event_data.get("address", {})
            if hasattr(address, 'model_dump'):
                address = address.model_dump()
                
            contact = event_data.get("contact", {})
            if hasattr(contact, 'model_dump'):
                contact = contact.model_dump()
            
            factura_data = {
                "rfc": str(event_data.get("rfc", "")),
                "razons": str(event_data.get("business_name", "")),
                "codpos": str(address.get("zip_code", "")),
                "email": str(contact.get("email", "")),
                "usocfdi": str(event_data.get("cfdi_use", "G03")),
                "regimen": str(event_data.get("tax_regime", "603")),
                "calle": str(address.get("street", "")),
                "numero_exterior": str(address.get("exterior_number", "")),
                "numero_interior": str(address.get("interior_number", "") or ""),
                "colonia": str(address.get("neighborhood", "")),
                "ciudad": str(address.get("city", "")),
                "delegacion": str(address.get("municipality", "") or ""),
                "estado": str(address.get("state", "")),
                "pais": str(address.get("country", "MEX")),
                "numregidtrib": str(event_data.get("tax_id_number", "") or ""),
                "nombre": str(contact.get("name", "")),
                "apellidos": str(contact.get("last_names", "")),
                "telefono": str(contact.get("phone", "") or ""),
                "email2": str(contact.get("email2", "") or ""),
                "email3": str(contact.get("email3", "") or "")
            }
            
            cleaned_data = {k: v for k, v in factura_data.items() if v is not None and v != ""}
            
            logger.info(f"Datos mapeados para Factura.com: {json.dumps(cleaned_data, indent=2)}")
            return cleaned_data
            
        except Exception as e:
            logger.error(f"Error en mapeo de datos: {str(e)}")
            raise

    async def _validate_input_data(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:  
        errors = []
        
        tax_regime = invoice_data.get("tax_regime")
        if tax_regime:
            regime_validation = await self.external_client_repository.validate_tax_regime(tax_regime)
            if not regime_validation["valid"]:
                errors.append(regime_validation["error"])
            
        cfdi_use = invoice_data.get("cfdi_use")    
        if cfdi_use: 
            cfdi_validation = await self.external_client_repository.validate_cfdi_use(cfdi_use, tax_regime)
            
            if not cfdi_validation["valid"]:
                errors.append(cfdi_validation["error"])

        country = invoice_data.get("address", {}).get("country", "MEX")
        if country: 
            country_validation = await self.external_client_repository.validate_country(country)
            if not country_validation:
                errors.append(f"País no válido: {country}")

        if errors:
            return {"valid": False, "error": "; ".join(errors)}

        return {"valid": True}

    async def _get_tax_regime_name(self, regime_code: str) -> str: 
        if not regime_code:
            return ""
        
        try: 
            
            validation_result = await self.external_client_repository.validate_tax_regime(regime_code)
            if validation_result["valid"]:
                return validation_result["name"]
            else:
                logger.warning(f"Régimen {regime_code} no encontrado en catálogo: {validation_result.get('error')}")
            
        except Exception as e: 
            logger.error(f"Error obteniendo el nombre de régimen: {str(e)}")
            return ""

    async def _get_cfdi_use_name(self, cfdi_use: str) -> str: 
        if not cfdi_use: 
            return ""
        
        try: 
            validation_result = await self.external_client_repository.validate_cfdi_use(cfdi_use)
            
            if validation_result["valid"]:
                return validation_result["name"]
            else: 
                logger.error(f"Uso CFDI {cfdi_use} no encontrado en catálogo: {validation_result}")
                return ""
        except Exception as e: 
                logger.warning(f"Error obteniendo nombre de uso CFDI: {str(e)}")
                return ""