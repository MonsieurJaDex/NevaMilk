package metrics

import (
	"math"
	"sync"
)

type WelfordVariance struct {
	count int
	mean  float64
	m2    float64
}

func NewWelfordVariance() WelfordVariance {
	return WelfordVariance{
		count: 0,
		mean:  0.0,
		m2:    0.0,
	}
}

func (w *WelfordVariance) Update(x float64) {
	w.count++
	delta := x - w.mean
	w.mean += delta / float64(w.count)
	delta2 := x - w.mean
	w.m2 += delta * delta2
}

func (w *WelfordVariance) Mean() float64 {
	return w.mean
}

func (w *WelfordVariance) Count() int {
	return w.count
}

func (w *WelfordVariance) Variance() float64 {
	if w.count < 2 {
		return 0.0
	}
	return w.m2 / (float64(w.count) - 1.0)
}

func (w *WelfordVariance) Std() float64 {
	return math.Sqrt(w.Variance())
}

type WelfordRegistry struct {
	mu            sync.Mutex
	welfordsTable map[string]*WelfordVariance
}

func NewWelfordRegistry() *WelfordRegistry {
	return &WelfordRegistry{
		welfordsTable: make(map[string]*WelfordVariance),
	}
}

func (wr *WelfordRegistry) Update(key string, value float64) (float64, float64, float64) {
	wr.mu.Lock()
	defer wr.mu.Unlock()

	w, exists := wr.welfordsTable[key]
	if !exists {
		newW := NewWelfordVariance()
		w = &newW
		wr.welfordsTable[key] = w
	}

	w.Update(value)

	return w.Mean(), w.Variance(), w.Std()
}
