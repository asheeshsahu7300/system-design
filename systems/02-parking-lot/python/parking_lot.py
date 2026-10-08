import threading
import uuid
from datetime import datetime
from typing import List, Optional, Dict
from models import Vehicle, ParkingSpot, ParkingTicket, SpotType
from strategies import PricingStrategy, HourlyPricingStrategy


class ParkingFloor:
    def __init__(self, floor_id: int):
        self.floor_id = floor_id
        self.spots: List[ParkingSpot] = []

    def add_spot(self, spot: ParkingSpot):
        self.spots.append(spot)

    def find_available_spot(self, vehicle: Vehicle) -> Optional[ParkingSpot]:
        for spot in self.spots:
            if spot.can_fit(vehicle):
                return spot
        return None


class ParkingLot:
    """Thread-safe multi-floor parking lot management engine."""

    def __init__(self, name: str, pricing_strategy: Optional[PricingStrategy] = None):
        self.name = name
        self.floors: List[ParkingFloor] = []
        self.pricing_strategy = pricing_strategy or HourlyPricingStrategy()
        self.active_tickets: Dict[str, ParkingTicket] = {}
        self._lock = threading.RLock()

    def add_floor(self, floor: ParkingFloor):
        with self._lock:
            self.floors.append(floor)

    def park_vehicle(self, vehicle: Vehicle) -> Optional[ParkingTicket]:
        with self._lock:
            for floor in self.floors:
                spot = floor.find_available_spot(vehicle)
                if spot and spot.assign_vehicle(vehicle):
                    ticket_id = f"TICK-{uuid.uuid4().hex[:8].upper()}"
                    ticket = ParkingTicket(
                        ticket_id=ticket_id,
                        vehicle=vehicle,
                        spot=spot,
                        entry_time=datetime.utcnow()
                    )
                    self.active_tickets[ticket_id] = ticket
                    return ticket
            return None  # Lot Full

    def vacate_vehicle(self, ticket_id: str, exit_time: Optional[datetime] = None) -> float:
        with self._lock:
            ticket = self.active_tickets.get(ticket_id)
            if not ticket:
                raise ValueError(f"Invalid or already processed ticket: {ticket_id}")

            exit_timestamp = exit_time or datetime.utcnow()
            fee = self.pricing_strategy.calculate_fee(ticket, exit_timestamp)

            # Free the spot
            ticket.spot.vacate()
            ticket.exit_time = exit_timestamp
            ticket.fee_paid = fee

            del self.active_tickets[ticket_id]
            return fee

    def get_available_spots_count(self) -> int:
        with self._lock:
            count = 0
            for floor in self.floors:
                for spot in floor.spots:
                    if not spot.is_occupied:
                        count += 1
            return count
