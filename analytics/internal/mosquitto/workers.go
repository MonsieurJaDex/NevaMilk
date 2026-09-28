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
	slog.Info("Analytics", "topic", msg.Topic(), "payload", msg.Payload())
}

func (c *Client) processWarnings(msg mqtt.Message) {
	slog.Info("Warnings", "topic", msg.Topic(), "payload", msg.Payload())
}
