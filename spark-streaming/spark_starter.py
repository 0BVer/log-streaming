from pyspark.sql import SparkSession
from streaming_message import parse_message_to_avro
from kafka_config import user_input, user_avro_output, post_input, \
    post_avro_output, mail_input, mail_avro_output

spark = SparkSession.builder \
    .appName("log-processing") \
    .config("spark.sql.streaming.checkpointLocation", "/spark-streaming/checkpoint") \
    .getOrCreate()

parse_message_to_avro(
    spark=spark,
    kafka_input_options=user_input,
    kafka_output_options=user_avro_output
)

parse_message_to_avro(
    spark=spark,
    kafka_input_options=post_input,
    kafka_output_options=post_avro_output
)

parse_message_to_avro(
    spark=spark,
    kafka_input_options=mail_input,
    kafka_output_options=mail_avro_output
)

# 스트리밍 작업 시작
spark.streams.awaitAnyTermination()
