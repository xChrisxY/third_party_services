import aio_pika
import json
import asyncio
import logging
from config.settings import settings
from ...application.use_cases.sync_company_with_factura_use_case import SyncCompanyWithFacturaUseCase
from ...infrastructure.services.factura_client import FacturaClient
from ...infrastructure.repositories.mongodb_company_repository import MongoDBCompanyRepository
from config.database import connect_to_mongo, get_database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RabbitMQConsumer:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.sync_use_case = None

    async def connect(self):
        try:
            logger.info("Conectando a MongoDB...")
            await connect_to_mongo()
            database = get_database()
            logger.info("MongoDB conectado exitosamente")

            company_repository = MongoDBCompanyRepository(database)
            factura_client = FacturaClient()

            self.sync_use_case = SyncCompanyWithFacturaUseCase(
                company_repository,
                factura_client
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

    async def setup_queue(self):
        try:
            logger.info(f"Creando cola: {settings.company_created_queue}")
            queue = await self.channel.declare_queue(
                settings.company_created_queue,
                durable=True,
                arguments={
                    "x-dead-letter-exchange": "",
                    "x-dead-letter-routing-key": f"{settings.company_created_queue}_dlq"
                }
            )
            logger.info(f"Cola principal creada: {settings.company_created_queue}")

            logger.info(f"Creando DLQ: {settings.company_created_queue}_dlq")
            await self.channel.declare_queue(
                f"{settings.company_created_queue}_dlq",
                durable=True
            )
            logger.info(f"DLQ creada: {settings.company_created_queue}_dlq")

            logger.info(f"Enlazando cola al exchange con routing key: {settings.company_created_routing_key}")
            await queue.bind(
                "amq.topic",
                routing_key=settings.company_created_routing_key
            )
            logger.info("Cola enlazada exitosamente")

            return queue

        except Exception as e:
            logger.error(f"Error configurando la cola: {str(e)}")
            raise

    async def on_message(self, message: aio_pika.IncomingMessage):
        try:
            logger.info(f"Mensaje recibido - Delivery Tag: {message.delivery_tag}")
            
            raw_body = message.body.decode()
            cleaned_body = self._clean_json_string(raw_body)
            
            event_data = json.loads(cleaned_body)
            logger.info(f"Evento recibido: {event_data.get('company_id')}")

            result = await self.sync_use_case.execute(event_data)

            if result["success"]:
                logger.info(f"Company synced with Factura.com: {result['factura_company_id']}")
                await message.ack()
                logger.info(f"Mensaje confirmado: {message.delivery_tag}")
            else:
                logger.error(f"Error syncing company: {result['error']}")
                await message.nack(requeue=False)
                logger.warning(f"Mensaje rechazado: {message.delivery_tag}")

        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON: {str(e)}")
            logger.error(f"Contenido del mensaje: {message.body.decode()}")
            await message.nack(requeue=False)
            logger.warning(f"Mensaje rechazado por JSON inválido: {message.delivery_tag}")

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            await message.nack(requeue=False)
            logger.warning(f"Mensaje rechazado por error inesperado: {message.delivery_tag}")

    async def consume(self):
        try:
            await self.connect()
            queue = await self.setup_queue()

            logger.info(f"Listening for {settings.company_created_routing_key} events...")
            logger.info(f"Queue: {settings.company_created_queue}")

            await queue.consume(self.on_message, no_ack=False)
            logger.info("Consumidor iniciado exitosamente")

            logger.info("Consumidor en ejecución...")
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