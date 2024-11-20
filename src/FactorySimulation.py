import logging
import time
from ics_sim.Device import HIL
from Configs import TAG, PHYSICS, Connection

logging.basicConfig(level=logging.DEBUG, filename='app.log', filemode='a', 
                    format='%(name)s - %(levelname)s - %(message)s')

class FactorySimulation(HIL):
    def __init__(self):
        super().__init__('Factory', Connection.CONNECTION, 100)
        self.init()
        self.sticker_placement_start_time = None  # Initialize the start time for sticker placement
        self.processing_part = False  # Track whether a part is being processed

    def init(self):
        """Initialize the simulation with default tag values."""
        initial_list = []
        for tag in TAG.TAG_LIST:
            initial_value = (tag, TAG.TAG_LIST[tag]['default'])
            initial_list.append(initial_value)
            logging.debug(f"Initializing tag: {tag} with value {initial_value}")
        
        self._connector.initialize(initial_list)
        logging.info("Database initialization completed with initial values.")

    def _logic(self):
        """Main logic for simulating factory behavior."""
        elapsed_time = self._current_loop_time - self._last_loop_time
        part_present = self._get(TAG.PART_PRESENT)
        logging.debug(f"Factory Simulation - Part present: {part_present}")

        if part_present and not self.processing_part:
            # Start processing the part if it's detected and not already being processed
            self._set(TAG.CONVEYOR_BELT_ENGINE_STATUS, 0.0)  # Stop the conveyor belt
            logging.debug("Conveyor belt stopped. Part detected.")
            if self.sticker_placement_start_time is None:
                self.sticker_placement_start_time = time.time()
                self.processing_part = True
                self._set(TAG.WAITING_FOR_STICKER, 1)
                logging.debug("Started sticker placement countdown.")

        if self.processing_part:
            # Check if sticker placement has completed
            time_since_sticker_started = time.time() - self.sticker_placement_start_time
            logging.debug(f"Sticker placement time elapsed: {time_since_sticker_started:.2f}s")

            if time_since_sticker_started >= PHYSICS.STICKER_PLACEMENT:
                logging.debug("Sticker placement completed. Processing the part.")
                self._set(TAG.WAITING_FOR_STICKER, 0)
                self._set(TAG.PART_PRESENT, 0)
                self._set(TAG.CONVEYOR_BELT_ENGINE_STATUS, 1)  # Restart the conveyor belt
                self._set(TAG.PART_DISTANCE_TO_SENSOR_VALUE, PHYSICS.PART_DISTANCE)
                self.sticker_placement_start_time = None
                self.processing_part = False

        elif not part_present:
            # Update part position if no part is present
            part_distance_to_sensor = self._get(TAG.PART_DISTANCE_TO_SENSOR_VALUE)
            logging.debug(f"Part distance to sensor: {part_distance_to_sensor}")
            conveyor_belt_status = self._get(TAG.CONVEYOR_BELT_ENGINE_STATUS)

            if conveyor_belt_status:
                part_distance_to_sensor -= elapsed_time * PHYSICS.CONVEYOR_BELT_SPEED
                part_distance_to_sensor %= PHYSICS.PART_DISTANCE

                if part_distance_to_sensor < 1:
                    self._set(TAG.PART_PRESENT, 1.0)  # Detect a new part
                    self._set(TAG.CONVEYOR_BELT_ENGINE_STATUS, 0.0)  # Stop conveyor belt
                    logging.debug("New part detected. Stopping conveyor belt.")
                else:
                    self._set(TAG.PART_DISTANCE_TO_SENSOR_VALUE, part_distance_to_sensor)
                    logging.debug(f"Updated part distance to sensor: {part_distance_to_sensor}")

    def _simulate_label_application(self):
        """Simulate the label application process."""
        part_number = self._get(TAG.CUSTOMER_PART_NUMBER)
        serial_number = self._get(TAG.SERIAL_NUMBER)
        if part_number and serial_number:
            self.report(f"Label applied with PN: {part_number}, SN: {serial_number}", logging.INFO)

    def _simulate_barcode_scanning(self):
        """Simulate barcode scanning."""
        if self._get(TAG.CODE_READED):
            part_data = self._retrieve_part_data()
            self.report(f"Barcode scanned: {part_data}", logging.INFO)

    def _retrieve_part_data(self):
        """Retrieve part data for simulation."""
        return {
            'part_number': self._get(TAG.CUSTOMER_PART_NUMBER),
            'serial_number': self._get(TAG.SERIAL_NUMBER),
            'test_result': self._get(TAG.TEST_RESULT)
        }

    def _update_physical_properties(self, elapsed_time):
        """Update physical properties like conveyor belt status."""
        conveyor_status = self._get(TAG.CONVEYOR_BELT_ENGINE_STATUS)
        if conveyor_status:
            self.report("Conveyor belt in operation", logging.INFO)


if __name__ == '__main__':
    factory = FactorySimulation()
    factory.start()











"""
class FactorySimulation(HIL):
    def __init__(self):
        super().__init__('Factory', Connection.CONNECTION, 100)
        self.init()

    def _logic(self):
        elapsed_time = self._current_loop_time - self._last_loop_time

        # update tank water level
        tank_water_amount = self._get(TAG.TAG_TANK_LEVEL_VALUE) * PHYSICS.TANK_LEVEL_CAPACITY
        if self._get(TAG.TAG_TANK_INPUT_VALVE_STATUS):
            tank_water_amount += PHYSICS.TANK_INPUT_FLOW_RATE * elapsed_time

        if self._get(TAG.TAG_TANK_OUTPUT_VALVE_STATUS):
            tank_water_amount -= PHYSICS.TANK_OUTPUT_FLOW_RATE * elapsed_time

        tank_water_level = tank_water_amount / PHYSICS.TANK_LEVEL_CAPACITY

        if tank_water_level > PHYSICS.TANK_MAX_LEVEL:
            tank_water_level = PHYSICS.TANK_MAX_LEVEL
            self.report('tank water overflowed', logging.WARNING)
        elif tank_water_level <= 0:
            tank_water_level = 0
            self.report('tank water is empty', logging.WARNING)

        # update tank water flow
        tank_water_flow = 0
        if self._get(TAG.TAG_TANK_OUTPUT_VALVE_STATUS) and tank_water_amount > 0:
            tank_water_flow = PHYSICS.TANK_OUTPUT_FLOW_RATE

        # update bottle water
        if self._get(TAG.TAG_BOTTLE_DISTANCE_TO_FILLER_VALUE) > 1:
            bottle_water_amount = 0
            if self._get(TAG.TAG_TANK_OUTPUT_FLOW_VALUE):
                self.report('water is wasting', logging.WARNING)
        else:
            bottle_water_amount = self._get(TAG.TAG_BOTTLE_LEVEL_VALUE) * PHYSICS.BOTTLE_LEVEL_CAPACITY
            bottle_water_amount += self._get(TAG.TAG_TANK_OUTPUT_FLOW_VALUE) * elapsed_time

        bottle_water_level = bottle_water_amount / PHYSICS.BOTTLE_LEVEL_CAPACITY

        if bottle_water_level > PHYSICS.BOTTLE_MAX_LEVEL:
            bottle_water_level = PHYSICS.BOTTLE_MAX_LEVEL
            self.report('bottle water overflowed', logging.WARNING)

        # update bottle position
        bottle_distance_to_filler = self._get(TAG.TAG_BOTTLE_DISTANCE_TO_FILLER_VALUE)
        if self._get(TAG.TAG_CONVEYOR_BELT_ENGINE_STATUS):
            bottle_distance_to_filler -= elapsed_time * PHYSICS.CONVEYOR_BELT_SPEED
            bottle_distance_to_filler %= PHYSICS.BOTTLE_DISTANCE

        # update physical properties
        self._set(TAG.TAG_TANK_LEVEL_VALUE, tank_water_level)
        self._set(TAG.TAG_TANK_OUTPUT_FLOW_VALUE, tank_water_flow)
        self._set(TAG.TAG_BOTTLE_LEVEL_VALUE, bottle_water_level)
        self._set(TAG.TAG_BOTTLE_DISTANCE_TO_FILLER_VALUE, bottle_distance_to_filler)

    def init(self):
        initial_list = []
        for tag in TAG.TAG_LIST:
            initial_list.append((tag, TAG.TAG_LIST[tag]['default']))

        self._connector.initialize(initial_list)


    @staticmethod
    def recreate_connection():
        return True


if __name__ == '__main__':
    factory = FactorySimulation()
    factory.start()
"""