import aio_pika
import json
import asyncio
import logging
from config.settings import settings
from ...application.use_cases.sync_company_with_factura_use_case import SyncCompanyWithFacturaUseCase
from ..dependencies import get_external_company_repository
from ...infrastructure.repositories.mongodb_company_repository import MongoDBCompanyRepository

from app.client.application.use_cases.sync_client_with_factura_use_case import SyncClientWithFacturaUseCase
from app.client.infrastructure.dependencies import get_external_client_repository
from app.client.infrastructure.repositories.mongodb_client_repository import MongoDBClientRepository

from config.database import connect_to_mongo, get_database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RabbitMQConsumer:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.company_sync_use_case = None
        self.client_sync_use_case = None

    async def connect(self):
        try:
            logger.info("Conectando a MongoDB...")
            await connect_to_mongo()
            database = get_database()
            logger.info("MongoDB conectado exitosamente")

            # Configurar use case para empresas
            company_repository = MongoDBCompanyRepository(database)
            external_company_repository = get_external_company_repository()
            self.company_sync_use_case = SyncCompanyWithFacturaUseCase(
                company_repository,
                external_company_repository
            )

            # Configurar use case para clientes
            client_repository = MongoDBClientRepository(database)
            external_client_repository = get_external_client_repository()
            self.client_sync_use_case = SyncClientWithFacturaUseCase(
                client_repository,
                external_client_repository
            )

            logger.info(f"Conectando a RabbitMQ en {settings.rabbitmq_host}:{settings.rabbitmq_port}...")
            self.connection = await aio_pika.connect_robust(
                host=settings.rabbitmq_host,
                port=settings.rabbitmq_port,
                login=settings.rabbitmq_username,
                password=settings.rabbitmq_password,
                virtualhost=settings.rabbitmq_vhost
            )
            logger.info("RabbitMQ conectado exitosamente")
            
            self.channel = await self.connection.channel()
            await self.channel.set_qos(prefetch_count=1)
            logger.info("Canal de RabbitMQ creado")

        except Exception as e:
            logger.error(f"Error en la conexión: {str(e)}")
            raise

    async def setup_queues(self):
        queues = {}
        
        # Configurar cola para empresas
        logger.info(f"Creando cola: {settings.company_created_queue}")
        company_queue = await self.channel.declare_queue(
            settings.company_created_queue,
            durable=True,
            arguments={
                "x-dead-letter-exchange": "",
                "x-dead-letter-routing-key": f"{settings.company_created_queue}_dlq"
            }
        )
        
        await self.channel.declare_queue(
            f"{settings.company_created_queue}_dlq",
            durable=True
        )
        
        await company_queue.bind(
            "amq.topic",
            routing_key=settings.company_created_routing_key
        )
        queues[settings.company_created_routing_key] = company_queue

        # Configurar cola para clientes
        logger.info(f"Creando cola: {settings.client_created_queue}")
        client_queue = await self.channel.declare_queue(
            settings.client_created_queue,
            durable=True,
            arguments={
                "x-dead-letter-exchange": "",
                "x-dead-letter-routing-key": f"{settings.client_created_queue}_dlq"
            }
        )
        
        await self.channel.declare_queue(
            f"{settings.client_created_queue}_dlq",
            durable=True
        )
        
        await client_queue.bind(
            "amq.topic",
            routing_key=settings.client_created_routing_key
        )
        queues[settings.client_created_routing_key] = client_queue

        return queues

    async def on_company_message(self, message: aio_pika.IncomingMessage):
        try:
            logger.info(f"Mensaje de empresa recibido - Delivery Tag: {message.delivery_tag}")
            
            raw_body = message.body.decode()
            cleaned_body = self._clean_json_string(raw_body)
            
            event_data = json.loads(cleaned_body)
            logger.info(f"Evento de empresa recibido: {event_data.get('company_id')}")

            result = await self.company_sync_use_case.execute(event_data)

            if result["success"]:
                logger.info(f"Company synced with Factura.com: {result['factura_company_id']}")
                await message.ack()
            else:
                logger.error(f"Error syncing company: {result['error']}")
                await message.nack(requeue=False)

        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON: {str(e)}")
            await message.nack(requeue=False)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            await message.nack(requeue=False)

    async def on_client_message(self, message: aio_pika.IncomingMessage):
        try:
            logger.info(f"Mensaje de cliente recibido - Delivery Tag: {message.delivery_tag}")
            
            raw_body = message.body.decode()
            cleaned_body = self._clean_json_string(raw_body)
            
            event_data = json.loads(cleaned_body)
            logger.info(f"Evento de cliente recibido: {event_data.get('rfc')}")

            result = await self.client_sync_use_case.execute(event_data)

            if result["success"]:
                logger.info(f"Client synced with Factura.com: {result['factura_client_uid']}")
                await message.ack()
            else:
                logger.error(f"Error syncing client: {result['error']}")
                await message.nack(requeue=False)

        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON: {str(e)}")
            await message.nack(requeue=False)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            await message.nack(requeue=False)

    async def consume(self):
        try:
            await self.connect()
            queues = await self.setup_queues()

            # Suscribirse a ambas colas
            company_queue = queues[settings.company_created_routing_key]
            client_queue = queues[settings.client_created_routing_key]

            await company_queue.consume(self.on_company_message, no_ack=False)
            await client_queue.consume(self.on_client_message, no_ack=False)

            logger.info(f"Listening for {settings.company_created_routing_key} events...")
            logger.info(f"Listening for {settings.client_created_routing_key} events...")

            logger.info("Consumidor iniciado exitosamente")
            await asyncio.Future() 

        except Exception as e:
            logger.error(f"Error fatal en el consumidor: {str(e)}", exc_info=True)
        finally:
            if self.connection:
                logger.info("Cerrando conexión...")
                await self.connection.close()
                logger.info("Conexión cerrada")

    def _clean_json_string(self, json_string: str) -> str:
        import re
        cleaned = re.sub(r'("[\w+/=]+)\n([\w+/=]+")', r'\1\2', json_string)
        cleaned = re.sub(r'("[\w+/=\s]+)"', lambda m: m.group(0).replace('\n', ''), cleaned)
        return cleaned

async def main():
    try:
        logger.info("Iniciando consumidor RabbitMQ...")
        consumer = RabbitMQConsumer()
        await consumer.consume()
    except KeyboardInterrupt:
        logger.info("⏹Consumidor detenido por el usuario")
    except Exception as e:
        logger.error(f"Error inesperado en main: {str(e)}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())