kafka_servers = "kafka1:19092,kafka2:29092,kafka3:39092"  # Kafka 브로커 서버 주소

kafka_input_options = {
    "kafka.bootstrap.servers": kafka_servers,
    "subscribe": "user,post,mail",
    "startingOffsets": "latest"
}

kafka_output_avro_options = {
    "kafka.bootstrap.servers": kafka_servers,
    "topic": "output_avro"
}

kafka_output_options = {
    "kafka.bootstrap.servers": kafka_servers,
    "topic": "filtered"
}