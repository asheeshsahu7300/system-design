package parking

import (
	"math"
	"time"
)

type VehicleType string

const (
	Motorcycle VehicleType = "MOTORCYCLE"
	Car        VehicleType = "CAR"
	Bus        VehicleType = "BUS"
)

type SpotType string

const (
	Compact SpotType = "COMPACT"
	Regular SpotType = "REGULAR"
	Large   SpotType = "LARGE"
)

type Vehicle struct {
	LicensePlate string
	Type         VehicleType
}

type ParkingSpot struct {
	SpotID     string
	FloorID    int
	Type       SpotType
	IsOccupied bool
	Vehicle    *Vehicle
}

func (s *ParkingSpot) CanFit(v *Vehicle) bool {
	if s.IsOccupied {
		return false
	}
	switch v.Type {
	case Motorcycle:
		return true
	case Car:
		return s.Type == Regular || s.Type == Large
	case Bus:
		return s.Type == Large
	default:
		return false
	}
}

type ParkingTicket struct {
	TicketID  string
	Vehicle   *Vehicle
	Spot      *ParkingSpot
	EntryTime time.Time
	ExitTime  time.Time
	FeePaid   float64
}

// PricingStrategy interface
type PricingStrategy interface {
	CalculateFee(ticket *ParkingTicket, exitTime time.Time) float64
}

type HourlyPricingStrategy struct {
	HourlyRate float64
}

func (h *HourlyPricingStrategy) CalculateFee(ticket *ParkingTicket, exitTime time.Time) float64 {
	duration := exitTime.Sub(ticket.EntryTime)
	hours := math.Ceil(duration.Hours())
	if hours < 1 {
		hours = 1
	}
	return hours * h.HourlyRate
}
