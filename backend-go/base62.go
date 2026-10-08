package main

import (
	"crypto/rand"
	"errors"
	"math/big"
	"strings"
)

const Base62Alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
const Base = uint64(len(Base62Alphabet))

// EncodeBase62 encodes an unsigned 64-bit integer into a Base62 string
func EncodeBase62(num uint64) string {
	if num == 0 {
		return string(Base62Alphabet[0])
	}

	var sb strings.Builder
	var digits []byte

	for num > 0 {
		rem := num % Base
		digits = append(digits, Base62Alphabet[rem])
		num /= Base
	}

	// Reverse the slice
	for i := len(digits) - 1; i >= 0; i-- {
		sb.WriteByte(digits[i])
	}

	return sb.String()
}

// DecodeBase62 decodes a Base62 string back into uint64
func DecodeBase62(s string) (uint64, error) {
	var num uint64
	for i := 0; i < len(s); i++ {
		idx := strings.IndexByte(Base62Alphabet, s[i])
		if idx == -1 {
			return 0, errors.New("invalid base62 character: " + string(s[i]))
		}
		num = num*Base + uint64(idx)
	}
	return num, nil
}

// GenerateRandomSlug generates a cryptographically secure random 7-character Base62 string
func GenerateRandomSlug(length int) (string, error) {
	var sb strings.Builder
	alphaLen := big.NewInt(int64(len(Base62Alphabet)))

	for i := 0; i < length; i++ {
		n, err := rand.Int(rand.Reader, alphaLen)
		if err != nil {
			return "", err
		}
		sb.WriteByte(Base62Alphabet[n.Int64()])
	}

	return sb.String(), nil
}
