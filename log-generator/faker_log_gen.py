import json
import time
import datetime
import numpy
import random
import tzlocal
from faker import Faker
from kafka import KafkaProducer

faker = Faker()
method = ['GET', 'POST', 'PUT', 'DELETE']
response = ["200", "201", "403", "404", "500", "301"]


def create_log(log_per_sec: int, server_name: str, resources: list, producer: KafkaProducer) -> None:
    time_now = datetime.datetime.now(tz=tzlocal.get_localzone())
    # tz = datetime.datetime.now().strftime('%z')
    dt = time_now.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    # f = open(server_name + '_access_log_' + time.strftime("%Y%m%d") + '.log', 'w')

    start_time = time.time()
    for _ in range(log_per_sec):
        ip = faker.ipv4()
        vrb = numpy.random.choice(method, p=[0.7, 0.1, 0.1, 0.1])
        uri = random.choice(resources)
        resp = numpy.random.choice(response, p=[0.8, 0.04, 0.05, 0.05, 0.02, 0.04])
        byt = int(random.gauss(5000, 50))

        log_line = '%s - - [%s] "%s %s HTTP/1.1" %s %s\n' % (ip, dt, vrb, uri, resp, byt)

        # f.write(log_line)
        # f.flush()

        json_tf = json.dumps({'log': log_line})
        producer.send(topic=server_name, value=json_tf.encode(encoding='utf-8'))
        producer.flush()

    end_time = time.time()
    execution_time = (end_time - start_time) * 1000  # 초를 밀리초로 변환
    print(f"{server_name} 생성 실행 시간: {execution_time:.2f} ms")
