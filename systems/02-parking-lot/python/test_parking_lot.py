import unittest
from datetime import datetime, timedelta
import threading
from models import Vehicle, VehicleType, ParkingSpot, SpotType
from strategies import HourlyPricingStrategy, VehicleBasedPricingStrategy
from parking_lot import ParkingLot, ParkingFloor


class TestParkingLot(unittest.TestCase):
    def setUp(self):
        self.lot = ParkingLot("City Center Parking", HourlyPricingStrategy(hourly_rate=10.0))
        floor1 = ParkingFloor(1)
        floor1.add_spot(ParkingSpot("F1-C1", 1, SpotType.COMPACT))
        floor1.add_spot(ParkingSpot("F1-R1", 1, SpotType.REGULAR))
        floor1.add_spot(ParkingSpot("F1-L1", 1, SpotType.LARGE))
        self.lot.add_floor(floor1)

    def test_park_and_vacate_car(self):
        car = Vehicle("KA-01-AB-1234", VehicleType.CAR)
        ticket = self.lot.park_vehicle(car)
        self.assertIsNotNone(ticket)
        self.assertEqual(ticket.vehicle.license_plate, "KA-01-AB-1234")
        self.assertEqual(ticket.spot.spot_type, SpotType.REGULAR)

        # Vacate 2 hours later
        exit_time = ticket.entry_time + timedelta(hours=2)
        fee = self.lot.vacate_vehicle(ticket.ticket_id, exit_time)
        self.assertEqual(fee, 20.0)
        self.assertFalse(ticket.spot.is_occupied)

    def test_lot_full_rejection(self):
        bus1 = Vehicle("BUS-01", VehicleType.BUS)
        bus2 = Vehicle("BUS-02", VehicleType.BUS)

        ticket1 = self.lot.park_vehicle(bus1)
        self.assertIsNotNone(ticket1)
        self.assertEqual(ticket1.spot.spot_type, SpotType.LARGE)

        # Second bus should be rejected because only 1 large spot exists
        ticket2 = self.lot.park_vehicle(bus2)
        self.assertIsNone(ticket2, "Second bus should fail to park as large spots are exhausted")

    def test_thread_safety_concurrent_parking(self):
        # Create a single spot lot
        single_spot_lot = ParkingLot("Single Spot Lot")
        floor = ParkingFloor(1)
        floor.add_spot(ParkingSpot("S1", 1, SpotType.REGULAR))
        single_spot_lot.add_floor(floor)

        successful_tickets = []
        lock = threading.Lock()

        def try_park(plate):
            car = Vehicle(plate, VehicleType.CAR)
            t = single_spot_lot.park_vehicle(car)
            if t:
                with lock:
                    successful_tickets.append(t)

        threads = [threading.Thread(target=try_park, args=(f"CAR-{i}",)) for i in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Exactly 1 vehicle should have secured the spot despite 20 race conditions
        self.assertEqual(len(successful_tickets), 1)


if __name__ == "__main__":
    unittest.main()
