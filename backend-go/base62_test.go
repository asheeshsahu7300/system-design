package main

import (
	"testing"
)

func TestEncodeDecodeBase62(t *testing.T) {
	testCases := []uint64{0, 1, 61, 62, 100, 125301, 100000000, 3521614606207}

	for _, val := range testCases {
		encoded := EncodeBase62(val)
		decoded, err := DecodeBase62(encoded)
		if err != nil {
			t.Fatalf("Failed to decode %s: %v", encoded, err)
		}
		if decoded != val {
			t.Errorf("Mismatch for %d: encoded as %s, decoded back to %d", val, encoded, decoded)
		}
	}
}

func TestRandomSlugUniqueness(t *testing.T) {
	seen := make(map[string]bool)
	for i := 0; i < 1000; i++ {
		slug, err := GenerateRandomSlug(7)
		if err != nil {
			t.Fatalf("Failed to generate slug: %v", err)
		}
		if len(slug) != 7 {
			t.Errorf("Expected length 7, got %d", len(slug))
		}
		if seen[slug] {
			t.Errorf("Collision detected for slug: %s", slug)
		}
		seen[slug] = true
	}
}
