from fastavro import parse_schema

avro_schema = parse_schema({
    "type": "record",
    "name": "Log",
    "fields": [
        {"name": "ip", "type": "string"},
        {"name": "timestamp", "type": "string"},
        {"name": "method", "type": "string"},
        {"name": "url", "type": "string"},
        {"name": "http_version", "type": "string"},
        {"name": "status", "type": "string"},
        {"name": "byte", "type": "string"}
    ]
})
