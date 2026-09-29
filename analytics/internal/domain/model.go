package domain

import (
	"encoding/base64"

	"github.com/google/uuid"
)

func parseBase64(encoded string) ([]byte, error) {
	b, err := base64.StdEncoding.DecodeString(encoded)
	if err != nil {
		return nil, err
	}

	return b, nil
}

type Payload[T any] struct {
	// Category - type of sensor who sent data
	Category SensorType `json:"category"`

	// Data - base64 encoded data
	Data T `json:"data"`
}

func NewPayload[T any](category string, data T) (*Payload[T], error) {
	parsedCategory, err := NewSensorType(category)
	if err != nil {
		return nil, err
	}

	return &Payload[T]{
		Category: *parsedCategory,
		Data:     data,
	}, nil
}

type MqttMessage struct {
	// DeviceId - device identifier in UUID format
	DeviceId uuid.UUID

	// Payload - base64 encoded text payload consists of message content
	Payload string
}

func NewMqttMessage(deviceId, payload string) (*MqttMessage, error) {
	id, err := uuid.Parse(deviceId)
	if err != nil {
		return nil, err
	}

	return &MqttMessage{
		DeviceId: id,
		Payload:  payload,
	}, nil
}

func (m *MqttMessage) ParsePayload() ([]byte, error) {
	return parseBase64(m.Payload)
}
