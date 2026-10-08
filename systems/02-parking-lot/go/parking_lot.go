package parking

import (
	"errors"
	"fmt"
	"sync"
	"time"
)

type ParkingFloor struct {
	FloorID int
	Spots   []*ParkingSpot
}

type ParkingLot struct {
	sync.RWMutex
	Name            string
	Floors          []*ParkingFloor
	Strategy        PricingStrategy
	ActiveTickets   map[string]*ParkingTicket
	ticketCounter   int
}

func NewParkingLot(name string, strategy PricingStrategy) *ParkingLot {
	return &ParkingLot{
		Name:          name,
		Floors:        make([]*ParkingFloor, 0),
		Strategy:      strategy,
		ActiveTickets: make(map[string]*ParkingTicket),
	}
}

func (p *ParkingLot) AddFloor(floor *ParkingFloor) {
	p.Lock()
	defer p.Unlock()
	p.Floors = append(p.Floors, floor)
}

func (p *ParkingLot) ParkVehicle(v *Vehicle) (*ParkingTicket, error) {
	p.Lock()
	defer p.Unlock()

	for _, floor := range p.Floors {
		for _, spot := range floor.Spots {
			if spot.CanFit(v) {
				spot.IsOccupied = true
				spot.Vehicle = v

				p.ticketCounter++
				ticketID := fmt.Sprintf("TICK-%06d", p.ticketCounter)

				ticket := &ParkingTicket{
					TicketID:  ticketID,
					Vehicle:   v,
					Spot:      spot,
					EntryTime: time.Now().UTC(),
				}

				p.ActiveTickets[ticketID] = ticket
				return ticket, nil
			}
		}
	}

	return nil, errors.New("parking lot is full: no compatible spot available")
}

func (p *ParkingLot) VacateVehicle(ticketID string, exitTime time.Time) (float64, error) {
	p.Lock()
	defer p.Unlock()

	ticket, exists := p.ActiveTickets[ticketID]
	if !exists {
		return 0, errors.New("invalid or expired ticket ID")
	}

	fee := p.Strategy.CalculateFee(ticket, exitTime)
	ticket.Spot.IsOccupied = false
	ticket.Spot.Vehicle = nil
	ticket.ExitTime = exitTime
	ticket.FeePaid = fee

	delete(p.ActiveTickets, ticketID)
	return fee, nil
}
