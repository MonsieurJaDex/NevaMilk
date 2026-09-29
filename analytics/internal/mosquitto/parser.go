package mosquitto

import (
	"encoding/json/v2"
	"fmt"
	"strings"

	"github.com/MonsieurJaDex/NevaMilk/m/internal/domain"
	mqtt "github.com/eclipse/paho.mqtt.golang"
	"github.com/google/uuid"
)

func parseMsg[T any](msg mqtt.Message) (*domain.Payload[T], *uuid.UUID, error) {
	strMsg := string(msg.Payload())
	parts := strings.Split(strMsg, ".")

	if len(parts) != 2 {
		return nil, nil, fmt.Errorf("invalid message format, failed to parse: %s", strMsg)
	}

	mqttMsg, err := domain.NewMqttMessage(parts[0], parts[1])
	if err != nil {
		return nil, nil, err
	}

	decodedPayload, err := mqttMsg.ParsePayload()
	if err != nil {
		return nil, nil, err
	}

	var rawPayload struct {
		// Category - type of sensor who sent data
		Category string `json:"category"`

		// Data - base64 encoded data
		Data T `json:"data"`
	}

	if err := json.Unmarshal(decodedPayload, &rawPayload); err != nil {
		return nil, nil, err
	}

	payload, err := domain.NewPayload(rawPayload.Category, rawPayload.Data)
	if err != nil {
		return nil, nil, err
	}

	uid, err := uuid.Parse(parts[0])
	if err != nil {
		return nil, nil, err
	}

	return payload, &uid, nil
}
