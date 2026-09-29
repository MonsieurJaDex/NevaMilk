package mosquitto

import (
	"log/slog"
	"time"

	"github.com/MonsieurJaDex/NevaMilk/m/internal/config"
	"github.com/MonsieurJaDex/NevaMilk/m/internal/metrics"
	mqtt "github.com/eclipse/paho.mqtt.golang"
	"github.com/prometheus/client_golang/prometheus"
)

type Client struct {
	cfg     *config.AppConfig
	client  mqtt.Client
	metrics *metrics.Metrics

	analyticsCh chan mqtt.Message
	warningsCh  chan mqtt.Message
}

func NewClient(appConfig *config.AppConfig, reg prometheus.Registerer) *Client {
	c := &Client{
		cfg:         appConfig,
		analyticsCh: make(chan mqtt.Message, 100),
		warningsCh:  make(chan mqtt.Message, 100),
		metrics:     metrics.NewMetrics(reg),
	}

	opts := mqtt.NewClientOptions()

	opts.AddBroker(appConfig.MQTT.BrokerURL)
	opts.SetClientID(appConfig.MQTT.ClientID)

	opts.SetAutoReconnect(true)
	opts.SetConnectRetry(true)

	opts.SetKeepAlive(30 * time.Second)
	opts.SetCleanSession(true)
	opts.SetConnectTimeout(2 * time.Second)

	opts.SetWill("/disconnect", "Broker disconnected", opts.WillQos, false)
	opts.OnConnect = c.handleConnection
	opts.OnConnectionLost = c.handleConnectionLost

	c.client = mqtt.NewClient(opts)

	return c
}

func (c *Client) Connect() error {
	if token := c.client.Connect(); token.Wait() && token.Error() != nil {
		return token.Error()
	}

	return nil
}

func (c *Client) Disconnect() {
	c.client.Disconnect(250)
}

func (c *Client) Raw() mqtt.Client {
	return c.client
}

func (c *Client) enqueue(ch chan mqtt.Message) mqtt.MessageHandler {
	return func(_ mqtt.Client, msg mqtt.Message) {
		select {
		case ch <- msg:
		default:
			slog.Info("Queue is full, dropping value from topic", "topic", msg.Topic())
		}
	}
}
