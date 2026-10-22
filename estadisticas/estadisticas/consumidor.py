# estadisticas/consumidor.py — punto de entrada del consumidor de Kafka: `python -m estadisticas.consumidor`
# (compose.prod.yaml, módulo 85)
#
# El código está en infrastructure/consumer/consumidor_kafka.py (módulo 89). Este archivo solo existe para que el
# comando no cambie.
from estadisticas.infrastructure.consumer.consumidor_kafka import main

if __name__ == "__main__":
    main()
