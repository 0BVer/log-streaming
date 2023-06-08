from io import BytesIO

import avro
from avro.io import DatumReader
from avro.schema import parse as parse_schema
from kafka import KafkaConsumer

from kafka_config import kafka_output_avro_options

# Kafka consumer 설정
kafka_bootstrap_servers = "localhost:19092,localhost:29092,localhost:39092"  # Kafka 브로커 서버 주소

kafka_topic = kafka_output_avro_options.get("topic")
kafka_group_id = 'temp-consumer'

# Avro 스키마 설정
avroSchema = """
{
  "type": "record",
  "name": "LogRecord",
  "fields": [
    {"name": "ip", "type": "string"},
    {"name": "timestamp", "type": "string"},
    {"name": "method", "type": "string"},
    {"name": "url", "type": "string"},
    {"name": "http_version", "type": "string"},
    {"name": "status", "type": "string"},
    {"name": "byte", "type": "string"}
  ]
}
"""
avro_schema = parse_schema(avroSchema)

# Kafka consumer 생성
consumer = KafkaConsumer(
    kafka_topic,
    bootstrap_servers=kafka_bootstrap_servers,
    group_id=kafka_group_id,
    value_deserializer=lambda x: x,
    enable_auto_commit=False  # 수동으로 오프셋 커밋 설정
)

print("[consumer start]")
# 메시지 컨슈밍 및 데이터 출력
for message in consumer:
    value = message.value
    # Avro 데이터 역직렬화
    reader = DatumReader(avro_schema)
    bytes_reader = BytesIO(value)
    decoder = avro.io.BinaryDecoder(bytes_reader)
    data = reader.read(decoder)

    # 데이터 출력
    print(data)

    # 오프셋 커밋
    consumer.commit()
