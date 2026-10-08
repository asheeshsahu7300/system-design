package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strings"
	"sync"
	"time"
)

// URLRecord stores metadata for a shortened link
type URLRecord struct {
	ShortCode   string    `json:"short_code"`
	OriginalURL string    `json:"original_url"`
	CustomAlias bool      `json:"custom_alias"`
	CreatedAt   time.Time `json:"created_at"`
	Clicks      int64     `json:"clicks"`
}

// ClickEvent stores click audit details
type ClickEvent struct {
	Timestamp time.Time `json:"timestamp"`
	Referrer  string    `json:"referrer"`
	UserAgent string    `json:"user_agent"`
	IP        string    `json:"ip"`
}

// Store provides goroutine-safe in-memory storage
type Store struct {
	sync.RWMutex
	urls      map[string]*URLRecord
	analytics map[string][]ClickEvent
}

var globalStore = &Store{
	urls:      make(map[string]*URLRecord),
	analytics: make(map[string][]ClickEvent),
}

// ShortenRequest payload
type ShortenRequest struct {
	URL         string `json:"url"`
	CustomAlias string `json:"custom_alias,omitempty"`
}

// ShortenResponse payload
type ShortenResponse struct {
	ShortCode   string `json:"short_code"`
	ShortURL    string `json:"short_url"`
	OriginalURL string `json:"original_url"`
	CreatedAt   string `json:"created_at"`
	CustomAlias bool   `json:"custom_alias"`
}

func enableCORS(w http.ResponseWriter) {
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
	w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")
}

func handleHealth(w http.ResponseWriter, r *http.Request) {
	enableCORS(w)
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"status":    "healthy",
		"service":   "url-shortener-go",
		"timestamp": time.Now().UTC(),
	})
}

func handleShorten(w http.ResponseWriter, r *http.Request) {
	enableCORS(w)
	if r.Method == http.MethodOptions {
		return
	}
	if r.Method != http.MethodPost {
		http.Error(w, "Method Not Allowed", http.StatusMethodNotAllowed)
		return
	}

	var req ShortenRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil || strings.TrimSpace(req.URL) == "" {
		http.Error(w, `{"error": "Invalid payload: 'url' is required"}`, http.StatusBadRequest)
		return
	}

	var slug string
	var isCustom bool

	globalStore.Lock()
	defer globalStore.Unlock()

	if req.CustomAlias != "" {
		slug = strings.TrimSpace(req.CustomAlias)
		if _, exists := globalStore.urls[slug]; exists {
			http.Error(w, fmt.Sprintf(`{"error": "Custom slug '%s' is already in use"}`, slug), http.StatusConflict)
			return
		}
		isCustom = true
	} else {
		// Generate random 7-character Base62 slug with collision check
		for {
			s, err := GenerateRandomSlug(7)
			if err != nil {
				http.Error(w, `{"error": "Failed to generate slug"}`, http.StatusInternalServerError)
				return
			}
			if _, exists := globalStore.urls[s]; !exists {
				slug = s
				break
			}
		}
	}

	record := &URLRecord{
		ShortCode:   slug,
		OriginalURL: req.URL,
		CustomAlias: isCustom,
		CreatedAt:   time.Now().UTC(),
		Clicks:      0,
	}

	globalStore.urls[slug] = record
	globalStore.analytics[slug] = make([]ClickEvent, 0)

	host := r.Host
	if host == "" {
		host = "localhost:8080"
	}
	proto := "http"
	if r.TLS != nil {
		proto = "https"
	}

	res := ShortenResponse{
		ShortCode:   slug,
		ShortURL:    fmt.Sprintf("%s://%s/%s", proto, host, slug),
		OriginalURL: req.URL,
		CreatedAt:   record.CreatedAt.Format(time.RFC3339),
		CustomAlias: isCustom,
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(res)
}

func handleRedirectOrAnalytics(w http.ResponseWriter, r *http.Request) {
	enableCORS(w)
	path := strings.TrimPrefix(r.URL.Path, "/")
	if path == "" {
		http.NotFound(w, r)
		return
	}

	// Route: GET /api/v1/analytics/{code}
	if strings.HasPrefix(path, "api/v1/analytics/") {
		code := strings.TrimPrefix(path, "api/v1/analytics/")
		globalStore.RLock()
		rec, exists := globalStore.urls[code]
		events := globalStore.analytics[code]
		globalStore.RUnlock()

		if !exists {
			http.Error(w, `{"error": "URL not found"}`, http.StatusNotFound)
			return
		}

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]interface{}{
			"short_code":    rec.ShortCode,
			"original_url":  rec.OriginalURL,
			"total_clicks":  rec.Clicks,
			"created_at":    rec.CreatedAt,
			"recent_clicks": events,
		})
		return
	}

	// Route: GET /api/v1/recent
	if path == "api/v1/recent" {
		globalStore.RLock()
		list := make([]*URLRecord, 0, len(globalStore.urls))
		for _, rec := range globalStore.urls {
			list = append(list, rec)
		}
		globalStore.RUnlock()

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(list)
		return
	}

	// Route: GET /{slug} -> HTTP 302 Redirect
	globalStore.RLock()
	rec, exists := globalStore.urls[path]
	globalStore.RUnlock()

	if !exists {
		http.Error(w, "Short link not found or expired", http.StatusNotFound)
		return
	}

	// Record click asynchronously in a separate goroutine
	referrer := r.Referer()
	ua := r.UserAgent()
	ip := r.RemoteAddr

	go func(code, ref, agent, remoteIP string) {
		globalStore.Lock()
		defer globalStore.Unlock()
		if r, ok := globalStore.urls[code]; ok {
			r.Clicks++
			globalStore.analytics[code] = append(globalStore.analytics[code], ClickEvent{
				Timestamp: time.Now().UTC(),
				Referrer:  ref,
				UserAgent: agent,
				IP:        remoteIP,
			})
		}
	}(path, referrer, ua, ip)

	// Send HTTP 302 Temporary Redirect
	http.Redirect(w, r, rec.OriginalURL, http.StatusFound)
}

func main() {
	mux := http.NewServeMux()
	mux.HandleFunc("/api/v1/health", handleHealth)
	mux.HandleFunc("/api/v1/shorten", handleShorten)
	mux.HandleFunc("/", handleRedirectOrAnalytics)

	port := ":8080"
	fmt.Printf("🚀 [Go Shortener] High-performance service running on http://localhost%s\n", port)
	log.Fatal(http.ListenAndServe(port, mux))
}
