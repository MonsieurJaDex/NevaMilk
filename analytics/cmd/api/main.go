package main

import (
	"context"
	"log/slog"
	"os"
	"os/signal"
	"syscall"

	"github.com/MonsieurJaDex/NevaMilk/m/internal/config"
	"github.com/MonsieurJaDex/NevaMilk/m/internal/logger"
	"github.com/MonsieurJaDex/NevaMilk/m/internal/mosquitto"
)

func main() {
	bootstrapLogger := logger.NewBootstrapLogger(os.Stdout)

	appConfig, err := config.LoadConfig("../.env")
	if err != nil {
		bootstrapLogger.Error("error during loading application config", "error", err.Error())
		os.Exit(1)
	}

	bootstrapLogger = nil

	appLogger := logger.NewLogger(os.Stdout, appConfig.Debug)
	slog.SetDefault(appLogger)

	client := mosquitto.NewClient(appConfig)
	if err := client.Connect(); err != nil {
		slog.Error("failed to connect to MQTT", "error", err.Error())
		os.Exit(1)
	}
	defer client.Disconnect()

	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()

	client.Run(ctx)

	<-ctx.Done()
}
