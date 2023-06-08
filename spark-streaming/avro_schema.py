access_log_avro = """
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
