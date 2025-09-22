import asyncio
import logging
from .rabbitmq_consumer import RabbitMQConsumer
from .event_handlers.company_event_handler import handle_company_created_event
from .event_handlers.client_event_handler import handle_client_created_event
from config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    try:
        consumer = RabbitMQConsumer()
        
        # Registrar handlers
        consumer.register_handler(
            settings.company_created_routing_key,
            handle_company_created_event
        )
        
        consumer.register_handler(
            settings.client_created_routing_key, 
            handle_client_created_event
        )
        
        await consumer.consume()
        
    except KeyboardInterrupt:
        logger.info("🛑 Consumer detenido por el usuario")
    except Exception as e:
        logger.error(f"💥 Error inesperado: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())