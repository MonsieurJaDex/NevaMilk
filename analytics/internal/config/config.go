package config

import (
	"github.com/caarlos0/env/v11"
	"github.com/joho/godotenv"
)

type AppConfig struct {
	Debug bool   `env:"DEBUG,required"`
	Port  uint16 `env:"ANALYSIS_PORT,required"`
	DB    DBConfig
	MQTT  MQTTConfig
}

type DBConfig struct {
	User     string `env:"POSTGRES_USER,required"`
	Password string `env:"POSTGRES_PASSWORD,required"`
	Name     string `env:"POSTGRES_DB,required"`
}

type MQTTConfig struct {
	BrokerURL      string `env:"MQTT_BROKER_URL,required"`
	ClientID       string `env:"MQTT_CLIENT_ID,required"`
	TopicAnalytics string `env:"MQTT_TOPIC_ANALYTICS,required"`
	TopicWarnings  string `env:"MQTT_TOPIC_WARNINGS,required"`
}

func LoadConfig(path string) (*AppConfig, error) {
	_ = godotenv.Load(path)

	var cfg AppConfig

	if err := env.Parse(&cfg); err != nil {
		return nil, err
	}

	return &cfg, nil
}
