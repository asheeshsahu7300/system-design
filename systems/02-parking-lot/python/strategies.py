from abc import ABC, abstractmethod
import math
from datetime import datetime
from models import ParkingTicket, VehicleType


class PricingStrategy(ABC):
    @abstractmethod
    def calculate_fee(self, ticket: ParkingTicket, exit_time: datetime) -> float:
        pass


class FlatRatePricingStrategy(PricingStrategy):
    def __init__(self, flat_fee: float = 10.0):
        self.flat_fee = flat_fee

    def calculate_fee(self, ticket: ParkingTicket, exit_time: datetime) -> float:
        return self.flat_fee


class HourlyPricingStrategy(PricingStrategy):
    def __init__(self, hourly_rate: float = 5.0):
        self.hourly_rate = hourly_rate

    def calculate_fee(self, ticket: ParkingTicket, exit_time: datetime) -> float:
        duration_seconds = (exit_time - ticket.entry_time).total_seconds()
        hours = max(1, math.ceil(duration_seconds / 3600))
        return hours * self.hourly_rate


class VehicleBasedPricingStrategy(PricingStrategy):
    def __init__(self):
        self.rates = {
            VehicleType.MOTORCYCLE: 2.0,
            VehicleType.CAR: 5.0,
            VehicleType.BUS: 12.0,
        }

    def calculate_fee(self, ticket: ParkingTicket, exit_time: datetime) -> float:
        duration_seconds = (exit_time - ticket.entry_time).total_seconds()
        hours = max(1, math.ceil(duration_seconds / 3600))
        base_rate = self.rates.get(ticket.vehicle.vehicle_type, 5.0)
        return hours * base_rate
