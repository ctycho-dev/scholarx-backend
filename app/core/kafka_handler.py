# app/core/kafka_handler.py
import logging
import json
from confluent_kafka import Producer
from typing import Optional


class KafkaHandler(logging.Handler):
    def __init__(self, topic: str, brokers: str = "localhost:29092"):
        super().__init__()
        self.topic = topic
        self.producer: Optional[Producer] = None
        self._kafka_ok = False
        self._setup_producer(brokers)
    
    @property
    def healthy(self) -> bool:
        return bool(self._kafka_ok and self.producer)

    def _setup_producer(self, brokers: str):
        """Setup Kafka producer with error handling."""
        try:
            self.producer = Producer({
                'bootstrap.servers': brokers,
                'client.id': 'scholarx-backend',
                'compression.type': 'gzip',
                'batch.size': 16384,
                'linger.ms': 10
            })
            self._kafka_ok = True
        except Exception as e:
            self._kafka_ok = False
            # Use fallback logging to avoid infinite recursion
            print(f"Failed to initialize Kafka producer: {e}")

    def emit(self, record):
        """Emit log record to Kafka."""
        if not self._kafka_ok or not self.producer:
            return

        try:
            # Format the message
            msg = self.format(record)
            if isinstance(msg, str):
                # If formatter returns string, create structured message
                log_data = {
                    "timestamp": self.formatter.formatTime(record, self.formatter.datefmt) if self.formatter else None,
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage(),
                    "module": getattr(record, 'module', ''),
                    "function": getattr(record, 'funcName', ''),
                    "line": getattr(record, 'lineno', 0)
                }
                message = json.dumps(log_data)
            else:
                message = msg

            # Send to Kafka
            self.producer.produce(
                self.topic, 
                message.encode('utf-8'),
                callback=self._delivery_callback
            )
            self.producer.poll(0)  # Non-blocking poll
            
        except Exception:
            pass

    def _delivery_callback(self, err, msg):
        # Swallow errors silently; failover doesn't rely on async delivery reports.
        pass

    def close(self):
        """Close the handler and flush remaining messages."""
        if self._kafka_ok and self.producer:
            try:
                self.producer.flush(timeout=2.0)
            except Exception:
                pass
        super().close()

