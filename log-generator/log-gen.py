import threading

from kafka import KafkaProducer
from kafka_setup import kafka_topic_setup
from faker_log_gen import create_log
from log_resource import user_resources, post_resources, mail_resources

bootstrap_server = ["127.0.0.1:19092", "127.0.0.1:29092", "127.0.0.1:39092"]
prod = KafkaProducer(bootstrap_servers=bootstrap_server)


def create_user_server_log() -> None:
    create_log(server_name='user', resources=user_resources, producer=prod)


def create_post_server_log() -> None:
    create_log(server_name='post', resources=post_resources, producer=prod)


def create_mail_server_log() -> None:
    create_log(server_name='mail', resources=mail_resources, producer=prod)


if __name__ == '__main__':
    kafka_topic_setup()

    print("[start generating]")
    threading.Thread(target=create_user_server_log).start()
    threading.Thread(target=create_post_server_log).start()
    threading.Thread(target=create_mail_server_log).start()
