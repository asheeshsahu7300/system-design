package parking

import (
	"fmt"
	"sync"
	"testing"
	"time"
)

func TestParkingLotBasicFlow(t *testing.T) {
	strategy := &HourlyPricingStrategy{HourlyRate: 15.0}
	lot := NewParkingLot("Downtown Hub", strategy)

	floor1 := &ParkingFloor{
		FloorID: 1,
		Spots: []*ParkingSpot{
			{SpotID: "F1-S1", FloorID: 1, Type: Regular},
			{SpotID: "F1-S2", FloorID: 1, Type: Large},
		},
	}
	lot.AddFloor(floor1)

	car := &Vehicle{LicensePlate: "GO-1234", Type: Car}
	ticket, err := lot.ParkVehicle(car)
	if err != nil {
		t.Fatalf("Unexpected error parking car: %v", err)
	}

	if ticket.Spot.SpotID != "F1-S1" {
		t.Errorf("Expected spot F1-S1, got %s", ticket.Spot.SpotID)
	}

	exitTime := ticket.EntryTime.Add(2 * time.Hour)
	fee, err := lot.VacateVehicle(ticket.TicketID, exitTime)
	if err != nil {
		t.Fatalf("Failed to vacate: %v", err)
	}
	if fee != 30.0 {
		t.Errorf("Expected fee 30.0, got %f", fee)
	}
}

func TestParkingLotHighConcurrencyRaceCondition(t *testing.T) {
	strategy := &HourlyPricingStrategy{HourlyRate: 10.0}
	lot := NewParkingLot("Concurrent Lot", strategy)

	// Create exactly 5 spots
	spots := make([]*ParkingSpot, 5)
	for i := 0; i < 5; i++ {
		spots[i] = &ParkingSpot{
			SpotID:  fmt.Sprintf("SPOT-%d", i),
			FloorID: 1,
			Type:    Regular,
		}
	}
	lot.AddFloor(&ParkingFloor{FloorID: 1, Spots: spots})

	// Run 100 concurrent vehicle arrivals competing for 5 spots
	const workers = 100
	var wg sync.WaitGroup
	var mu sync.Mutex
	successfulParks := 0

	for i := 0; i < workers; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			car := &Vehicle{
				LicensePlate: fmt.Sprintf("PLATE-%d", id),
				Type:         Car,
			}
			ticket, err := lot.ParkVehicle(car)
			if err == nil && ticket != nil {
				mu.Lock()
				successfulParks++
				mu.Unlock()
			}
		}(i)
	}

	wg.Wait()

	if successfulParks != 5 {
		t.Errorf("Expected exactly 5 cars to park successfully, got %d", successfulParks)
	}
}
