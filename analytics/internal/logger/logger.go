package logger

import (
	"io"
	"log/slog"
	"os"
	"strconv"
)

func NewLogger(w io.Writer, debug bool) *slog.Logger {
	if debug {
		return slog.New(slog.NewTextHandler(w, &slog.HandlerOptions{
			AddSource: true,
			Level:     slog.LevelDebug,
		}))
	}
	return slog.New(slog.NewJSONHandler(w, &slog.HandlerOptions{
		Level: slog.LevelWarn,
	}))
}

func NewBootstrapLogger(w io.Writer) *slog.Logger {
	debug, _ := strconv.ParseBool(os.Getenv("DEBUG"))
	return NewLogger(w, debug)
}
