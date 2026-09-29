package mosquitto

import (
	"context"
	"log/slog"
	"sync"

	mqtt "github.com/eclipse/paho.mqtt.golang"
)

func (c *Client) Run(ctx context.Context) {
	var wg sync.WaitGroup

	wg.Add(2)
	go func() {
		defer wg.Done()
		c.worker(ctx, c.analyticsCh, c.processAnalytics)
	}()
	go func() {
		defer wg.Done()
		c.worker(ctx, c.warningsCh, c.processWarnings)
	}()

	wg.Wait()
}

func (c *Client) worker(ctx context.Context, ch <-chan mqtt.Message, process func(mqtt.Message)) {
	for {
		select {
		case <-ctx.Done():
			return
		case msg := <-ch:
			process(msg)
		}
	}
}

func (c *Client) processAnalytics(msg mqtt.Message) {
	log := slog.With("mqtt_msg_id", msg.MessageID())

	payload, device_id, err := parseMsg[float64](msg)
	if err != nil {
		log.Error(err.Error())
		return
	}

	c.metrics.AnalyticsBoundaryValue.WithLabelValues(payload.Category.String(), device_id.String()).Set(payload.Data)

	wkey := payload.Category.String() + ":" + device_id.String()
	mean, variance, std := c.welfordReg.Update(wkey, payload.Data)

	c.metrics.AnalyticsStats.WithLabelValues(payload.Category.String(), device_id.String(), "mean").Set(mean)
	c.metrics.AnalyticsStats.WithLabelValues(payload.Category.String(), device_id.String(), "variance").Set(variance)
	c.metrics.AnalyticsStats.WithLabelValues(payload.Category.String(), device_id.String(), "std").Set(std)

	slog.Info("Analytics", "topic", msg.Topic(), "payload", msg.Payload())
}

func (c *Client) processWarnings(msg mqtt.Message) {
	log := slog.With("mqtt_msg_id", msg.MessageID())

	payload, _, err := parseMsg[string](msg)
	if err != nil {
		log.Error(err.Error())
		return
	}

	c.metrics.Warnings.WithLabelValues(payload.Category.String()).Inc()

	slog.Info("Warnings", "topic", msg.Topic(), "payload", payload.Data)
}
