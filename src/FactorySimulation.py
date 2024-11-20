import logging
import time
from ics_sim.Device import HIL
from Configs import TAG, PHYSICS, Connection

# Setup logging
logging.basicConfig(level=logging.DEBUG, filename='app.log', filemode='a', 
                    format='%(name)s - %(levelname)s - %(message)s')

class FactorySimulation(HIL):
    def __init__(self):
        super().__init__('Factory', Connection.CONNECTION, 100)
        self.init()
        self.sticker_placement_start_time = None  # Initialize the start time for sticker placement

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

        # Get the current state of the conveyor belt and part presence
        conveyor_belt_status = self._get(TAG.CONVEYOR_BELT_ENGINE_STATUS)
        part_present = self._get(TAG.PART_PRESENT)

        # Handle cases where the tag values might be None
        if conveyor_belt_status is None:
            logging.error("CONVEYOR_BELT_ENGINE_STATUS tag value is None.")
            conveyor_belt_status = 1  # Default to running

        if part_present is None:
            logging.error("PART_PRESENT tag value is None.")
            part_present = 0  # Default to no part present

        # If the conveyor belt is running and no part is present, move the part closer to the sensor
        if conveyor_belt_status:
            part_distance_to_sensor = self._get(TAG.PART_DISTANCE_TO_SENSOR_VALUE)
            if part_distance_to_sensor is None:
                logging.error("PART_DISTANCE_TO_SENSOR_VALUE tag value is None.")
                part_distance_to_sensor = PHYSICS.PART_DISTANCE  # Default starting distance

            # Update the part's position
            part_distance_to_sensor -= elapsed_time * PHYSICS.CONVEYOR_BELT_SPEED
            if part_distance_to_sensor <= 0:
                part_distance_to_sensor = 0
                self._set(TAG.PART_PRESENT, 1)  # Part has arrived at the sensor
                self._set(TAG.CONVEYOR_BELT_ENGINE_STATUS, 0)  # Stop the conveyor belt
                logging.debug("Part has arrived at the sensor. Stopping conveyor belt.")
            else:
                self._set(TAG.PART_DISTANCE_TO_SENSOR_VALUE, part_distance_to_sensor)
                logging.debug(f"Updated part distance to sensor: {part_distance_to_sensor}")

        # If the part is present and the conveyor belt is stopped, wait for PLC to process
        elif part_present:
            # Wait for PLC to process the part
            logging.debug("Part is present and conveyor belt is stopped. Waiting for PLC to process.")

        # If the part has been processed by the PLC and the conveyor belt is restarted
        else:
            if conveyor_belt_status == 0:
                # Prepare for the next part
                self._set(TAG.PART_DISTANCE_TO_SENSOR_VALUE, PHYSICS.PART_DISTANCE)
                self._set(TAG.CONVEYOR_BELT_ENGINE_STATUS, 1)  # Start the conveyor belt
                logging.debug("Conveyor belt restarted. Preparing for the next part.")

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
