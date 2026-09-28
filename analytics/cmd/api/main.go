package main

import (
	"fmt"
	"os"

	"github.com/MonsieurJaDex/NevaMilk/m/internal/config"
	"github.com/MonsieurJaDex/NevaMilk/m/internal/logger"
)

func main() {
	bootstrapLogger := logger.NewBootstrapLogger(os.Stdout)

	appConfig, err := config.LoadConfig("../.env")
	if err != nil {
		bootstrapLogger.Error("error during loading application config", "error", err.Error())
	}

	fmt.Printf("%#v\n", appConfig)
}
