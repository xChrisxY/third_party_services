from typing import Dict, Any
from datetime import datetime
import uuid
import logging
import json
import asyncio

from ...domain.entities.client import Client
from ...domain.entities.client_address import ClientAddress
from ...domain.entities.client_contact import ClientContact
from ...domain.repositories.client_repository import ClientRepository
from ...domain.repositories.external_client_repository import ExternalClientRepository

logger = logging.getLogger(__name__)

class SyncClientWithFacturaUseCase:
    
    def __init__(
        self, 
        client_repository: ClientRepository, 
        external_client_repository: ExternalClientRepository
    ):
        self.client_repository = client_repository
        self.external_client_repository = external_client_repository

    async def execute(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            logger.info(f"Datos recibidos del evento cliente: {json.dumps(event_data, indent=2)}")

            client_data = self._map_to_factura_format(event_data)

            response = await self.external_client_repository.create_client(client_data)

            if response.get("status") == 'success': 
                factura_client_uid = response.get('Data', {}).get('UID')

                logger.info(f"Cliente creado con UID: {factura_client_uid}")

                await asyncio.sleep(2)
                
                client_details = await self.external_client_repository.get_client_by_id(factura_client_uid)

                client_id = await self._create_client_in_database(event_data, factura_client_uid, client_details)

                return {
                    "success": True, 
                    "client_id" : client_id, 
                    "factura_client_id" : factura_client_uid, 
                    "data": response, 
                    "message" : "Client successfully created in Factura.com and local database"
                }
            
            else:
                error_msg = response.get('message', 'Unknown error from Factura.com')
                logger.error(f"Error de Factura.com: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg
                }
            
        except Exception as e: 
            logger.error(f"Error inesperado en use case: {str(e)}")
            return {"success": False, "error": str(e)}

    def _map_to_factura_format(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mapea los datos al formato esperado por Factura.com"""
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
            
            client_dict = {
                "tenant_id": event_data.get("tenant_id", str(uuid.uuid4())),
                "external_uid": factura_uid,
                "rfc": event_data.get("rfc"),
                "business_name": event_data.get("business_name"),
                "tax_regime": event_data.get("tax_regime"),
                "tax_regime_name": self._get_tax_regime_name(event_data.get("tax_regime")),
                "tax_id_number": event_data.get("tax_id_number"),
                "address": address,
                "contact": contact,
                "cfdi_use": event_data.get("cfdi_use"),
                "cfdi_use_name": self._get_cfdi_use_name(event_data.get("cfdi_use")),
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "status": "active",
                "factura_sync": True,
                "emails": emails if emails else None
            }
            
            client_model = Client(**client_dict)
            created_client = await self.client_repository.create(client_model)
            
            if hasattr(created_client, 'inserted_id'):
                client_id = str(created_client.inserted_id)
            elif hasattr(created_client, 'id'):
                client_id = str(created_client.id)
            else:
                client_id = str(created_client)
            
            logger.info(f"Cliente creado en BD con ObjectId: {client_id}")
            return client_id
            
        except Exception as e:
            logger.error(f"Error creando cliente en BD: {str(e)}")
            raise

    def _get_tax_regime_name(self, regime_code: str) -> str:
        regime_map = {
            "601": "General de Ley Personas Morales",
            "603": "Personas Morales con Fines no Lucrativos",
            "605": "Sueldos y Salarios e Ingresos Asimilados a Salarios",
            "606": "Arrendamiento",
            "607": "Régimen de Enajenación o Adquisición de Bienes",
            "608": "Demás ingresos",
            "610": "Residentes en el Extranjero sin Establecimiento Permanente en México",
            "611": "Ingresos por Dividendos (socios y accionistas)",
            "612": "Personas Físicas con Actividades Empresariales y Profesionales",
            "614": "Ingresos por intereses",
            "615": "Régimen de los ingresos por obtención de premios",
            "616": "Sin obligaciones fiscales",
            "620": "Sociedades Cooperativas de Producción que optan por diferir sus ingresos",
            "621": "Incorporación Fiscal",
            "622": "Actividades Agrícolas, Ganaderas, Silvícolas y Pesqueras",
            "623": "Opcional para Grupos de Sociedades",
            "624": "Coordinados",
            "625": "Régimen de las Actividades Empresariales con ingresos a través de Plataformas Tecnológicas",
            "626": "Régimen Simplificado de Confianza"
        }
        return regime_map.get(regime_code, "")

    def _get_cfdi_use_name(self, cfdi_use: str) -> str:
        cfdi_use_map = {
            "G01": "Adquisición de mercancias",
            "G02": "Devoluciones, descuentos o bonificaciones",
            "G03": "Gastos en general",
            "I01": "Construcciones",
            "I02": "Mobiliario y equipo de oficina por inversiones",
            "I03": "Equipo de transporte",
            "I04": "Equipo de computo y accesorios",
            "I05": "Dados, troqueles, moldes, matrices y herramental",
            "I06": "Comunicaciones telefónicas",
            "I07": "Comunicaciones satelitales",
            "I08": "Otra maquinaria y equipo",
            "D01": "Honorarios médicos, dentales y gastos hospitalarios",
            "D02": "Gastos médicos por incapacidad o discapacidad",
            "D03": "Gastos funerales",
            "D04": "Donativos",
            "D05": "Intereses reales efectivamente pagados por créditos hipotecarios",
            "D06": "Aportaciones voluntarias al SAR",
            "D07": "Primas por seguros de gastos médicos",
            "D08": "Gastos de transportación escolar obligatoria",
            "D09": "Depósitos en cuentas para el ahorro, primas que tengan como base planes de pensiones",
            "D10": "Pagos por servicios educativos",
            "P01": "Por definir"
        }
        return cfdi_use_map.get(cfdi_use, "")