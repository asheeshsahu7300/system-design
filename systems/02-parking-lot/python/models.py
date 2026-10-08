from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


class VehicleType(Enum):
    MOTORCYCLE = "MOTORCYCLE"
    CAR = "CAR"
    BUS = "BUS"


class SpotType(Enum):
    COMPACT = "COMPACT"   # Suitable for Motorcycles
    REGULAR = "REGULAR"   # Suitable for Cars & Motorcycles
    LARGE = "LARGE"       # Suitable for Buses, Trucks, Cars & Motorcycles


@dataclass
class Vehicle:
    license_plate: str
    vehicle_type: VehicleType


class ParkingSpot:
    def __init__(self, spot_id: str, floor_id: int, spot_type: SpotType):
        self.spot_id = spot_id
        self.floor_id = floor_id
        self.spot_type = spot_type
        self.is_occupied: bool = False
        self.vehicle: Optional[Vehicle] = None

    def can_fit(self, vehicle: Vehicle) -> bool:
        if self.is_occupied:
            return False
        if vehicle.vehicle_type == VehicleType.MOTORCYCLE:
            return True
        elif vehicle.vehicle_type == VehicleType.CAR:
            return self.spot_type in (SpotType.REGULAR, SpotType.LARGE)
        elif vehicle.vehicle_type == VehicleType.BUS:
            return self.spot_type == SpotType.LARGE
        return False

    def assign_vehicle(self, vehicle: Vehicle) -> bool:
        if not self.can_fit(vehicle):
            return False
        self.is_occupied = True
        self.vehicle = vehicle
        return True

    def vacate(self):
        self.is_occupied = False
        self.vehicle = None


@dataclass
class ParkingTicket:
    ticket_id: str
    vehicle: Vehicle
    spot: ParkingSpot
    entry_time: datetime
    exit_time: Optional[datetime] = None
    fee_paid: Optional[float] = None
