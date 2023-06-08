import threading
import time

from kafka import KafkaProducer
from kafka_setup import setup
from faker_log_gen import create_log

post_resources = ["/posts",
                  "/posts/feed"
                  "/posts/search",
                  "/posts?category=fashion",
                  "/posts?category=sport",
                  "/posts?category=game",
                  "/posts?category=life",
                  "/posts?category=news",
                  "/admin",
                  "/.env"]

user_resources = ["/users",
                  "/users/profile?lang=kor",
                  "/users/profile?lang=en",
                  "/users/setting",
                  "/login",
                  "/reset-pw",
                  "/users/search",
                  "/users/friends"
                  "/admin",
                  "/.env"]

mail_resources = ["/mails/inbox",
                  "/mails/inbox?type=important",
                  "/mails/inbox?type=advertise",
                  "/mails/inbox?type=deleted",
                  "/mails/outbox?type=temp",
                  "/mails/outbox?type=later",
                  "/mails/outbox?type=deleted",
                  "/mails/search"
                  "/admin",
                  "/.env"]

bootstrap_server = ["127.0.0.1:19092", "127.0.0.1:29092", "127.0.0.1:39092"]
prod = KafkaProducer(bootstrap_servers=bootstrap_server)


def create_user_server_log() -> None:
    create_log(
        server_name='user',
        resources=user_resources,
        producer=prod)


def create_post_server_log() -> None:
    create_log(
        server_name='post',
        resources=post_resources,
        producer=prod)


def create_mail_server_log() -> None:
    create_log(
        server_name='mail',
        resources=mail_resources,
        producer=prod)


threads = []
for _ in range(1):
    threads.append(threading.Thread(target=create_user_server_log))
    threads.append(threading.Thread(target=create_post_server_log))
    threads.append(threading.Thread(target=create_mail_server_log))

if __name__ == '__main__':
    setup()
    start_time = time.time()

    for _ in range(1):
        threading.Thread(target=create_user_server_log).start()
        threading.Thread(target=create_post_server_log).start()
        threading.Thread(target=create_mail_server_log).start()
        time.sleep(1)

    end_time = time.time()
    execution_time = (end_time - start_time) * 1000  # 초를 밀리초로 변환
    print(f"실행 시간: {execution_time:.2f} ms")
