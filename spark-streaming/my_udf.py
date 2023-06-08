import re

from pyspark.sql.functions import udf
from pyspark.sql.types import StructType, StructField, StringType

# 필드 추출을 위한 정규표현식 패턴
field_pattern = r'^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+-\s+-\s+\[([^\]]+)\]\s+"(\w+)\s+([^"]+)\s+HTTP/(\d\.\d)"\s+(\d+)\s+(\d+)$'

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
