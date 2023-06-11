package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/Shopify/sarama"
	influxdb2 "github.com/influxdata/influxdb-client-go/v2"
	"github.com/influxdata/influxdb-client-go/v2/api"
	"github.com/linkedin/goavro/v2"
)

var (
	influxURL    = "http://influxdb:8086"
	influxToken  = "sample-token"
	influxBucket = "dashboard"
	influxOrg    = "log-streaming"
	//kafkaBrokers = []string{"localhost:19092", "localhost:29092", "localhost:39092"}
	kafkaBrokers    = []string{"kafka1:19092", "kafka2:29092", "kafka3:39092"}
	kafkaTopic      = "output_avro"
	consumerGroupID = "kafka-influxdb-consumer"
)

func main() {

	fmt.Printf("start consumer\n")
	// Set up InfluxDB client
	client := influxdb2.NewClientWithOptions(influxURL, influxToken, influxdb2.DefaultOptions().SetBatchSize(100))
	writeAPI := client.WriteAPI(influxOrg, influxBucket)

	// Set up Kafka consumer
	config := sarama.NewConfig()
	config.Consumer.Group.Rebalance.Strategy = sarama.BalanceStrategyRoundRobin
	config.Consumer.Offsets.Initial = sarama.OffsetOldest
	config.Version = sarama.V2_6_0_0

	consumer, err := sarama.NewConsumerGroup(kafkaBrokers, consumerGroupID, config)
	if err != nil {
		log.Fatalf("Failed to create consumer group: %s", err)
	}
	defer func(consumer sarama.ConsumerGroup) {
		err := consumer.Close()
		if err != nil {
			log.Fatalf("Failed to close consumer group: %s", err)
		}
	}(consumer)

	// Set up Avro codec
	codec, err := goavro.NewCodec(`{
		  "type": "record",
		  "name": "LogRecord",
		  "fields": [
			{"name": "ip", "type": "string"},
			{"name": "timestamp", "type": "string"},
			{"name": "method", "type": "string"},
			{"name": "url", "type": "string"},
			{"name": "http_version", "type": "string"},
			{"name": "status", "type": "string"},
			{"name": "byte", "type": "string"}
		  ]
		}`)

	if err != nil {
		log.Fatalf("Failed to create Avro codec: %s", err)
	}

	// Handle Kafka consumer errors
	go func() {
		for err := range consumer.Errors() {
			log.Printf("Kafka consumer error: %s", err)
		}
	}()

	// Handle OS signals to gracefully stop the consumer
	signals := make(chan os.Signal, 1)
	signal.Notify(signals, syscall.SIGINT, syscall.SIGTERM)

	ctx, cancel := context.WithCancel(context.Background())
	go func() {
		select {
		case <-signals:
			cancel()
		case <-ctx.Done():
		}
	}()

	// Consume messages from Kafka
	for {
		handler := &kafkaMessageHandler{codec: codec, writeAPI: writeAPI}

		if err := consumer.Consume(ctx, []string{kafkaTopic}, handler); err != nil {
			log.Printf("Kafka consumer error: %s", err)
		}

		if ctx.Err() != nil {
			break
		}
	}

	// Close InfluxDB client
	client.Close()
}

type kafkaMessageHandler struct {
	codec    *goavro.Codec
	writeAPI api.WriteAPI
}

type KafkaMessage struct {
	IP          string `json:"ip"`
	Timestamp   string `json:"timestamp"`
	Method      string `json:"method"`
	URL         string `json:"url"`
	HTTPVersion string `json:"http_version"`
	Status      string `json:"status"`
	Byte        string `json:"byte"`
}

func (h *kafkaMessageHandler) Setup(session sarama.ConsumerGroupSession) error {
	return nil
}

func (h *kafkaMessageHandler) Cleanup(session sarama.ConsumerGroupSession) error {
	return nil
}

func (h *kafkaMessageHandler) ConsumeClaim(session sarama.ConsumerGroupSession, claim sarama.ConsumerGroupClaim) error {
	for msg := range claim.Messages() {
		// Decode Avro message

		native, _, err := h.codec.NativeFromBinary(msg.Value)
		if err != nil {
			log.Printf("Failed to decode Avro message: %s", err)
			session.MarkMessage(msg, "")
			continue
		}

		// Convert to KafkaMessage struct
		message := KafkaMessage{
			IP:          native.(map[string]interface{})["ip"].(string),
			Timestamp:   native.(map[string]interface{})["timestamp"].(string),
			Method:      native.(map[string]interface{})["method"].(string),
			URL:         native.(map[string]interface{})["url"].(string),
			HTTPVersion: native.(map[string]interface{})["http_version"].(string),
			Status:      native.(map[string]interface{})["status"].(string),
			Byte:        native.(map[string]interface{})["byte"].(string),
		}

		// Store in InfluxDB
		h.storeMessageInInfluxDB(message)

		session.MarkMessage(msg, "")
	}

	return nil
}

func (h *kafkaMessageHandler) storeMessageInInfluxDB(message KafkaMessage) {
	write := fmt.Sprintf("kafka_messages ip=\"%s\", timestamp=\"%s\", method=\"%s\", url=\"%s\", http_version=\"%s\", status=\"%s\", byte=\"%s\"",
		message.IP, message.Timestamp, message.Method, message.URL, message.HTTPVersion, message.Status, message.Byte)
	point := influxdb2.NewPoint(
		"access-log",
		nil,
		map[string]interface{}{
			"ip":           message.IP,
			"timestamp":    message.Timestamp,
			"method":       message.Method,
			"url":          message.URL,
			"http_version": message.HTTPVersion,
			"status":       message.Status,
			"byte":         message.Byte,
		},
		time.Now(),
	)

	h.writeAPI.WritePoint(point)
	log.Printf("Stored Kafka message in InfluxDB: %s", write)
}
