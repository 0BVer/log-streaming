package main

import (
	"fmt"
	"github.com/brianvoe/gofakeit/v6"
	"log"
	"math/rand"
	"sync"
	"time"

	"github.com/confluentinc/confluent-kafka-go/kafka"
)

var (
	bootstrapServers = "127.0.0.1:19092,127.0.0.1:29092,127.0.0.1:39092"
	topics           = []string{"user", "post", "mail"}
	rateLimit        = 1000 // Desired messages per second
	numProducers     = 9
	config           = kafka.ConfigMap{
		"bootstrap.servers": bootstrapServers,
		"batch.size":        32768 * 2, // 32KB
	}
)

func createLog(serverName string, producer *kafka.Producer) {

	for {
		gofakeit.Seed(time.Now().UnixNano())

		ip := gofakeit.IPv4Address()
		method := gofakeit.HTTPMethod()
		url := gofakeit.URL()
		statusCode := gofakeit.HTTPStatusCode()
		byt := 5000 + rand.Intn(1000)

		logLine := fmt.Sprintf("%s - - [%s] \"%s %s HTTP/1.1\" %d %d\n", ip, getSeoulTime(), method, url, statusCode, byt)

		msg := &kafka.Message{
			TopicPartition: kafka.TopicPartition{Topic: &serverName, Partition: kafka.PartitionAny},
			Value:          []byte(logLine),
		}

		err := producer.Produce(msg, nil)
		if err != nil {
			log.Printf("Failed to produce message: %v\n", err)
		}

		time.Sleep(time.Second / time.Duration(rateLimit))

	}
}

func getSeoulTime() string {
	location, err := time.LoadLocation("Asia/Seoul")
	if err != nil {
		log.Fatalf("Failed to load location: %s", err)
	}
	seoulTime := time.Now().In(location).Format(time.RFC3339)
	return seoulTime
}

func main() {
	kafkaTopicSetup(bootstrapServers, topics)

	producers := make([]*kafka.Producer, numProducers)

	for i := 0; i < numProducers; i++ {
		producer, err := kafka.NewProducer(&config)
		if err != nil {
			log.Fatalf("Failed to create Kafka producer: %v\n", err)
		}
		defer producer.Close()
		producers[i] = producer
	}

	wg := sync.WaitGroup{}
	wg.Add(numProducers)

	for i := 0; i < numProducers; i++ {
		go func(topic string, producer *kafka.Producer) {
			log.Println("Starting log creation", topic, producer.String())
			defer wg.Done()
			createLog(topic, producer)
		}(topics[i%len(topics)], producers[i])
	}

	wg.Wait()

}
