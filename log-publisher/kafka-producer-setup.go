package main

import (
	"context"
	"github.com/confluentinc/confluent-kafka-go/kafka"
	"log"
	"time"
)

func kafkaTopicSetup(bootstrapServer string, topic string) {
	admin, err := kafka.NewAdminClient(&kafka.ConfigMap{
		"bootstrap.servers":       bootstrapServer,
		"api.version.request":     "true",
		"broker.version.fallback": "0.10.0.0",
	})
	if err != nil {
		log.Fatalf("Failed to create admin client: %v", err)
	}
	defer admin.Close()

	createTopic := kafka.TopicSpecification{
		Topic:             topic,
		NumPartitions:     3,
		ReplicationFactor: 1,
	}

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	result, err := admin.CreateTopics(ctx, []kafka.TopicSpecification{createTopic})

	if err != nil {
		log.Fatalf("Failed to create topic '%s': %v", topic, err)
	}

	if result[0].Error.Code() != kafka.ErrNoError && result[0].Error.Code() != kafka.ErrTopicAlreadyExists {
		log.Printf("Failed to create topic '%s': %v", result[0].Topic, result[0].Error)
	} else {
		log.Printf("Topic '%s' created successfully", result[0].Topic)
	}
}
