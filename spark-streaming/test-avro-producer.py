from io import BytesIO

import avro
from avro.io import DatumWriter
from avro.schema import parse as parse_schema
from kafka import KafkaProducer

# Kafka producer 설정
kafka_bootstrap_servers = "localhost:19092,localhost:29092,localhost:39092"  # Kafka 브로커 서버 주소
kafka_topic = "your_topic_name"  # 프로듀싱할 토픽 이름

# Kafka producer 생성
producer = KafkaProducer(
    bootstrap_servers=kafka_bootstrap_servers,
    value_serializer=lambda x: x
)

# 프로듀싱할 데이터 생성
data = {
    "ip": "127.0.0.1",
    "timestamp": "2023-06-12 12:00:00",
    "method": "GET",
    "url": "http://example.com",
    "http_version": "HTTP/1.1",
    "status": "200",
    "byte": "1024"
}

# Avro 스키마 설정
log_record_avro_schema = """
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
avro_schema = parse_schema(log_record_avro_schema)

# Avro 데이터 직렬화
bytes_writer = BytesIO()
encoder = avro.io.BinaryEncoder(bytes_writer)
writer = DatumWriter(avro_schema)
writer.write(data, encoder)
bytes_data = bytes_writer.getvalue()

print(bytes_data)

# 데이터 프로듀싱
producer.send(kafka_topic, value=bytes_data)
producer.flush()

# Kafka producer 종료
producer.close()