package mosquitto

import (
	"log/slog"

	mqtt "github.com/eclipse/paho.mqtt.golang"
)

func (c *Client) handleConnection(client mqtt.Client) {
	subs := map[string]mqtt.MessageHandler{
		c.cfg.MQTT.TopicAnalytics: c.enqueue(c.analyticsCh),
		c.cfg.MQTT.TopicWarnings:  c.enqueue(c.warningsCh),
	}

	for topic, handler := range subs {
		if token := client.Subscribe(topic, 1, handler); token.Wait() && token.Error() != nil {
			slog.Info("mqtt: subscribe %s failed: %v", topic, token.Error())
		}
	}
}

func (c *Client) handleConnectionLost(client mqtt.Client, err error) {
	slog.Error("connetion with MQTT client lost", "error", err.Error())
	client.Disconnect(250)
}
