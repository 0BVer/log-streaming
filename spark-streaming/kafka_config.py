# kafka_servers = "localhost:19092,localhost:29092,localhost:39092"  # Kafka 브로커 서버 주소
kafka_servers = "kafka1:19092,kafka2:29092,kafka3:39092"  # Kafka 브로커 서버 주소

user_input = {
    "kafka.bootstrap.servers": kafka_servers,
    "subscribe": "user",
    "startingOffsets": "latest",
    "group.id": "user-parsing-streaming"
}

post_input = {
    "kafka.bootstrap.servers": kafka_servers,
    "subscribe": "post",
    "startingOffsets": "latest",
    "group.id": "post-parsing-streaming"
}

mail_input = {
    "kafka.bootstrap.servers": kafka_servers,
    "subscribe": "mail",
    "startingOffsets": "latest",
    "group.id": "mail-parsing-streaming"
}

user_avro_output = {
    "kafka.bootstrap.servers": kafka_servers,
    "topic": "user_avro",
}

post_avro_output = {
    "kafka.bootstrap.servers": kafka_servers,
    "topic": "post_avro",
}

mail_avro_output = {
    "kafka.bootstrap.servers": kafka_servers,
    "topic": "mail_avro",
}
