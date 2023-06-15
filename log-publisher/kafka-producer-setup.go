package main

import (
	"context"
	"github.com/confluentinc/confluent-kafka-go/kafka"
	"log"
	"time"
)

func kafkaTopicSetup(bootstrapServer string, topics []string) {
	admin, err := kafka.NewAdminClient(&kafka.ConfigMap{
		"bootstrap.servers":       bootstrapServer,
		"api.version.request":     "true",
		"broker.version.fallback": "0.10.0.0",
	})
	if err != nil {
		log.Fatalf("Failed to create admin client: %v", err)
	}
	defer admin.Close()

	createTopics := make([]kafka.TopicSpecification, 0)
	for _, topic := range topics {
		createTopics = append(createTopics, kafka.TopicSpecification{
			Topic:             topic,
			NumPartitions:     2,
			ReplicationFactor: 1,
		})
	}
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	results, err := admin.CreateTopics(ctx, createTopics)

	if err != nil {
		log.Fatalf("Failed to create topics: %v", err)
	}

	for _, result := range results {
		if result.Error.Code() != kafka.ErrNoError && result.Error.Code() != kafka.ErrTopicAlreadyExists {
			log.Printf("Failed to create topic '%s': %v", result.Topic, result.Error)
		} else {
			log.Printf("Topic '%s' created successfully", result.Topic)
		}
	}
}
