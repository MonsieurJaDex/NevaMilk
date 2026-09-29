package domain

import (
	"fmt"
)

type SensorType uint8

const (
	SensorPt100          SensorType = iota // Игольчатый датчик Pt100
	SensorPt1000                           // RTD-зонд Pt1000
	SensorPH                               // pH-датчик
	SensorHumidityCap                      // Ёмкостный датчик влажности
	SensorPsychrometric                    // Психрометрический датчик
	SensorLoadCell                         // Тензодатчик
	SensorLevelCap                         // Ёмкостный сигнализатор уровня
	SensorComputerVision                   // Промышленная камера машинного зрения
	SensorTemperature                      // сенсор температуры
	SensorVibration                        // Сенсор вибраций
)

var sensorTypeNames = map[SensorType]string{
	SensorPt100:          "pt100 Needle",
	SensorPt1000:         "pt1000 RTD",
	SensorPH:             "pH Sensor",
	SensorHumidityCap:    "humidity",
	SensorPsychrometric:  "psychrometric",
	SensorLoadCell:       "load Cell",
	SensorLevelCap:       "capacitive Level",
	SensorComputerVision: "computer Vision",
	SensorTemperature:    "temperature",
	SensorVibration:      "vibration",
}

var sensorTypeByName = make(map[string]SensorType, len(sensorTypeNames))

func init() {
	for t, name := range sensorTypeNames {
		sensorTypeByName[name] = t
	}
}

func NewSensorType(s string) (*SensorType, error) {
	if t, ok := sensorTypeByName[s]; ok {
		return &t, nil
	}
	return nil, fmt.Errorf("unknown sensor type string: %q", s)
}

// String implements fmt.Stringer.
func (t SensorType) String() string {
	if name, ok := sensorTypeNames[t]; ok {
		return name
	}
	return fmt.Sprintf("SensorType(%d)", int(t))
}
