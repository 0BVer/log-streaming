from kafka.errors import TopicAlreadyExistsError
from kafka import KafkaAdminClient
from kafka.admin import NewTopic

bootstrap_server = ["127.0.0.1:19092", "127.0.0.1:29092", "127.0.0.1:39092"]
topics = ['user', 'post', 'mail']

admin_client = KafkaAdminClient(bootstrap_servers=bootstrap_server)


def setup():
    try:
        for topic in topics:
            # 토픽 이름, 파티션 수, 레플리케이션 팩터 설정
            num_partitions = 3
            replication_factor = 1

            # 새로운 토픽 생성을 위한 NewTopic 객체 생성
            new_topic = NewTopic(name=topic, num_partitions=num_partitions, replication_factor=replication_factor)

            # 토픽 생성 요청
            admin_client.create_topics(new_topics=[new_topic])
    except TopicAlreadyExistsError:
        pass


if __name__ == '__main__':
    setup()
