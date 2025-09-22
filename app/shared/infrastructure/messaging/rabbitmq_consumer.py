import aio_pika
import json
import asyncio
import logging
from config.settings import settings
from config.database import connect_to_mongo, get_database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RabbitMQConsumer:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.event_handlers = {}

    def register_handler(self, routing_key: str, handler_func):
        """Registra un handler para un tipo específico de evento"""
        self.event_handlers[routing_key] = handler_func
        logger.info(f"Handler registrado para: {routing_key}")

    async def connect(self):
        max_retries = 5
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Conectando a servicios... (Intento {attempt + 1}/{max_retries})")
                
                # Conectar a MongoDB
                await connect_to_mongo()
                logger.info("✅ MongoDB conectado")
                
                # Conectar a RabbitMQ
                logger.info(f"Conectando a RabbitMQ en {settings.rabbitmq_host}:{settings.rabbitmq_port}...")
                self.connection = await aio_pika.connect_robust(
                    host=settings.rabbitmq_host,
                    port=settings.rabbitmq_port,
                    login=settings.rabbitmq_username,
                    password=settings.rabbitmq_password,
                    virtualhost=settings.rabbitmq_vhost
                )
                logger.info("✅ RabbitMQ conectado")
                
                self.channel = await self.connection.channel()
                await self.channel.set_qos(prefetch_count=1)
                return

            except Exception as e:
                logger.error(f"Error en conexión (Intento {attempt + 1}): {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                else:
                    raise

    async def setup_queue(self, queue_name: str, routing_key: str):
        """Configura una cola específica"""
        try:
            logger.info(f"Configurando cola: {queue_name} para routing key: {routing_key}")
            
            queue = await self.channel.declare_queue(
                queue_name,
                durable=True,
                arguments={
                    "x-dead-letter-exchange": "",
                    "x-dead-letter-routing-key": f"{queue_name}_dlq"
                }
            )
            
            # Crear DLQ
            await self.channel.declare_queue(f"{queue_name}_dlq", durable=True)
            
            await queue.bind("amq.topic", routing_key=routing_key)
            logger.info(f"✅ Cola {queue_name} configurada para {routing_key}")
            return queue
            
        except Exception as e:
            logger.error(f"Error configurando cola {queue_name}: {str(e)}")
            raise

    async def on_message(self, message: aio_pika.IncomingMessage):
        """Maneja todos los mensajes entrantes"""
        try:
            async with message.process():
                routing_key = message.routing_key
                logger.info(f"📨 Mensaje recibido - Routing Key: {routing_key}")
                
                raw_body = message.body.decode()
                cleaned_body = self._clean_json_string(raw_body)
                event_data = json.loads(cleaned_body)
                
                # Buscar handler específico usando el routing_key original
                handler = self.event_handlers.get(routing_key)
                if handler:
                    logger.info(f"Ejecutando handler para: {routing_key}")
                    result = await handler(event_data)
                    
                    if result.get("success"):
                        logger.info(f"✅ Evento procesado: {routing_key}")
                    else:
                        logger.error(f"❌ Error en handler: {result.get('error')}")
                else:
                    logger.warning(f"⚠️  No hay handler para: {routing_key}")
                    logger.warning(f"Handlers disponibles: {list(self.event_handlers.keys())}")
                        
        except Exception as e:
            logger.error(f"💥 Error procesando mensaje: {str(e)}")

    async def consume(self):
        """Inicia el consumo de mensajes"""
        try:
            await self.connect()
            
            # Configurar todas las colas usando los routing keys registrados
            for routing_key in self.event_handlers.keys():
                # Usar los nombres de cola de settings o generar uno consistente
                if routing_key == settings.company_created_routing_key:
                    queue_name = settings.company_created_queue
                elif routing_key == settings.client_created_routing_key:
                    queue_name = settings.client_created_queue
                else:
                    # Para otros routing keys, generar un nombre basado en el routing key
                    queue_name = f"{routing_key.replace('.', '_')}_queue"
                
                queue = await self.setup_queue(queue_name, routing_key)
                await queue.consume(self.on_message)
                logger.info(f"👂 Escuchando: {routing_key} -> Cola: {queue_name}")

            logger.info("🎉 Consumer iniciado exitosamente")
            await asyncio.Future()  # Ejecutar indefinidamente
            
        except Exception as e:
            logger.error(f"💥 Error fatal: {str(e)}")
        finally:
            if self.connection:
                await self.connection.close()

    def _clean_json_string(self, json_string: str) -> str:
        import re
        cleaned = re.sub(r'("[\w+/=]+)\n([\w+/=]+")', r'\1\2', json_string)
        return cleaned