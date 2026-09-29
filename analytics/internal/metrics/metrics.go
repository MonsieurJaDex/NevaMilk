package metrics

import (
	"context"
	"errors"
	"fmt"
	"log"
	"log/slog"
	"net/http"
	"time"

	"github.com/MonsieurJaDex/NevaMilk/m/internal/config"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

type Metrics struct {
	Recieved *prometheus.CounterVec
	Warnings *prometheus.CounterVec

	// Аналитика показателей, представляемых пределами
	AnalyticsBoundaryValue *prometheus.GaugeVec
}

func NewMetrics(reg prometheus.Registerer) *Metrics {
	f := promauto.With(reg)

	return &Metrics{
		Recieved: f.NewCounterVec(prometheus.CounterOpts{
			Name: "total_recieved",
			Help: "Общее число обработанных метрик",
		}, []string{"topic"}),
		Warnings: f.NewCounterVec(prometheus.CounterOpts{
			Name: "device_warnings",
			Help: "Полученные сообщения с предупреждениями от датчиков",
		}, []string{"category"}),
		AnalyticsBoundaryValue: f.NewGaugeVec(prometheus.GaugeOpts{
			Name: "analytics_bound_floats",
			Help: "Полученные числовые метрики с плавающей точкой, вписываемые в пределы относительно нормы",
		}, []string{"category", "device_id"}),
	}
}

type MetricsWorker struct {
	cfg *config.AppConfig
	reg *prometheus.Registry
}

func NewMetricsWorker(cfg *config.AppConfig, reg *prometheus.Registry) MetricsWorker {
	return MetricsWorker{cfg, reg}
}

func (mw *MetricsWorker) Run(ctx context.Context, path string) {
	mux := http.NewServeMux()
	mux.Handle(path, promhttp.HandlerFor(mw.reg, promhttp.HandlerOpts{}))

	// TODO: загружать адрес из env
	srv := &http.Server{
		Addr:    "0.0.0.0:" + fmt.Sprint(mw.cfg.Port),
		Handler: mux,
	}

	errChan := make(chan error, 1)

	go func() {
		log.Printf("Metrics server starting on %s%s", srv.Addr, path)
		if err := srv.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
			errChan <- err
		}
	}()

	go func() {
		<-ctx.Done()
		slog.Info("shutting down metrics server...")

		shutdownCtx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel()

		if err := srv.Shutdown(shutdownCtx); err != nil {
			slog.Error("metrics server Shutdown Failed", "error", err.Error())
		}
	}()

	go func() {
		if err := <-errChan; err != nil {
			slog.Error("metrics server critical error", "error", err.Error())
		}
	}()
}
