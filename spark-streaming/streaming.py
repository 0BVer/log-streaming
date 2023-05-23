import re

from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, udf
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

spark = SparkSession.builder \
    .appName("log-processing") \
    .config("spark.sql.streaming.checkpointLocation", "../kafka/logs") \
    .getOrCreate()

kafka_servers = "localhost:19092,localhost:29092,localhost:39092"  # Kafka 브로커 서버 주소
kafka_topic = "user,post,mail"

kafka_input_options = {
    "kafka.bootstrap.servers": kafka_servers,
    "subscribe": kafka_topic,
    "startingOffsets": "latest"
}

# 로그 스키마 정의
log_schema = StructType([
    StructField("log", StringType())
])

# 스트리밍 데이터프레임 생성
df = spark.readStream \
    .format("kafka") \
    .options(**kafka_input_options) \
    .load()

# 로그 파싱을 위해 스키마를 적용
parsed_df = df.select(from_json(df.value.cast("string"), log_schema).alias("parsed_log")) \
    .select("parsed_log.log")

# 필드 추출을 위한 정규표현식 패턴
field_pattern = r'^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+-\s+-\s+\[([^\]]+)\]\s+"(\w+)\s+([^"]+)\s+HTTP/(\d\.\d)"\s+(\d+)\s+(\d+)$'

# 필드 추출을 위한 UDF 정의
parse_log_udf = udf(
    lambda log: re.match(field_pattern, log).groups() if re.match(field_pattern, log) else [None] * 7,
    StructType([
        StructField("ip", StringType()),
        StructField("timestamp", StringType()),
        StructField("method", StringType()),
        StructField("url", StringType()),
        StructField("http_version", StringType()),
        StructField("status", StringType()),
        StructField("byte", StringType())
    ]))

# 필드 추출 및 JSON 변환
parsed_fields_df = parsed_df.withColumn("log", parse_log_udf(col("log"))) \
    .select(
    col("log.ip").alias("ip"),
    col("log.timestamp").alias("timestamp"),
    col("log.method").alias("method"),
    col("log.url").alias("url"),
    col("log.http_version").alias("http_version"),
    col("log.status").alias("status"),
    col("log.byte").alias("byte")
) \
    .selectExpr("to_json(struct(*)) AS value")

kafka_output_options = {
    "kafka.bootstrap.servers": kafka_servers,
    "topic": "output_topic"
}

# 파싱된 로그를 다시 Kafka에 퍼블리싱
parsed_fields_df.selectExpr("(CAST(value AS STRING)) AS value") \
    .writeStream \
    .format("kafka") \
    .options(**kafka_output_options) \
    .start()

# 스트리밍 작업 시작
spark.streams.awaitAnyTermination()
