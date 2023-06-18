from pyspark.sql.avro.functions import to_avro
from pyspark.sql.functions import col, struct

from avro_schema import access_log_avro
from my_udf import parse_log_udf


def parse_message_to_avro(spark, kafka_input_options, kafka_output_options):
    # 스트리밍 데이터프레임 생성
    df = spark.readStream \
        .format("kafka") \
        .options(**kafka_input_options) \
        .load()

    # 로그 파싱을 위해 스키마를 적용
    parsed_df = df.select((col("value").cast("string")).alias("log"))

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
        .options(**kafka_output_options) \
        .start()
