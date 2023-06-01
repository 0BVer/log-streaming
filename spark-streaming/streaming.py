from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, udf
from pyspark.sql.types import StructType, StructField, StringType
from my_udf import parse_log_udf, serialize_avro_udf
from kafka_config import kafka_input_options, kafka_output_options, kafka_output_avro_options

spark = SparkSession.builder \
    .appName("log-processing") \
    .config("spark.sql.streaming.checkpointLocation", "../kafka/logs") \
    .getOrCreate()

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

# 필드 추출 및 JSON 변환
parsed_fields_df = parsed_df.withColumn("log", parse_log_udf(col("log"))) \
    .select(
    col("log.ip").alias("ip"),
    col("log.timestamp").alias("timestamp"),
    col("log.method").alias("method"),
    col("log.url").alias("url"),
    col("log.http_version").alias("http_version"),
    col("log.status").alias("status"),
    col("log.byte").alias("byte")) \
    .selectExpr("to_json(struct(*)) AS value")

# Avro 변환 및 Kafka에 퍼블리싱
avro_df = parsed_fields_df.withColumn("value", serialize_avro_udf(col("value")))
avro_df.select("value") \
    .writeStream \
    .format("kafka") \
    .options(**kafka_output_avro_options) \
    .start()

# 공격 의심 url 필터링 및 Kafka에 퍼블리싱
filtered_df = parsed_fields_df.where((col("url") != "/admin") & (col("url") != "/.env"))
filtered_df.selectExpr("(CAST(value AS STRING)) AS value") \
    .writeStream \
    .format("kafka") \
    .options(**kafka_output_options) \
    .start()

# 스트리밍 작업 시작
spark.streams.awaitAnyTermination()
