from pyspark.sql import SparkSession
from pyspark.sql.avro.functions import to_avro
from pyspark.sql.functions import from_json, col, struct
from pyspark.sql.types import StructType, StructField, StringType, BinaryType

from kafka_config import kafka_input_options, kafka_output_avro_options, kafka_output_options
from my_udf import parse_log_udf
from avro_schema import access_log_avro

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
parsed_df = df.select((col("value").cast("string")).alias("log")) \

# 필드 추출 및 JSON 변환
parsed_fields_df = parsed_df.withColumn("log", parse_log_udf(col("log"))) \
    .select(
    col("log.ip").alias("ip"),
    col("log.timestamp").alias("timestamp"),
    col("log.method").alias("method"),
    col("log.url").alias("url"),
    col("log.http_version").alias("http_version"),
    col("log.status").alias("status"),
    col("log.byte").alias("byte"))

# Avro로 변환하는 작업
avro_df = parsed_fields_df.select(to_avro(struct("*"), access_log_avro).alias("value"))

# Kafka에 퍼블리싱
avro_df.selectExpr("CAST(value AS BINARY)") \
    .writeStream \
    .format("kafka") \
    .options(**kafka_output_avro_options) \
    .start()

# 공격 의심 url 필터링 및 Kafka에 퍼블리싱
# filtered_df = parsed_fields_df.where((col("url") != "/admin") & (col("url") != "/.env"))
#
# filtered_avro_df = filtered_df.select(to_avro(struct("*"), access_log_avro).alias("value"))
#
# filtered_avro_df.selectExpr("CAST(value AS BINARY)") \
#     .writeStream \
#     .format("kafka") \
#     .options(**kafka_output_options) \
#     .start()

# 스트리밍 작업 시작
spark.streams.awaitAnyTermination()
