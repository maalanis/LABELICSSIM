from ics_sim.Device import PLC, SensorConnector, ActuatorConnector
from Configs import TAG, Controllers, Connection
import logging
import time

# Setup logging
logging.basicConfig(level=logging.DEBUG, filename='app.log', filemode='a',
                    format='%(name)s - %(levelname)s - %(message)s')

# Define sticker placement time locally
STICKER_PLACEMENT = 5  # Time in seconds for sticker placement

class PLC1(PLC):
    def __init__(self):
        sensor_connector = SensorConnector(Connection.CONNECTION)
        actuator_connector = ActuatorConnector(Connection.CONNECTION)
        super().__init__(1, sensor_connector, actuator_connector, TAG.TAG_LIST, Controllers.PLCs)
        # Initialize all tags to their default states
        self._initialize_tags()
        self.sticker_start_time = None  # Add a timer for sticker printing

    def _initialize_tags(self):
        """Initialize all relevant tags to their default values."""
        self._set(TAG.PRINTING_STICKER_TAG, 0)        # Printing sticker tag default: 0 (not printing)
        self._set(TAG.BARCODE_VERIFICATION_STATUS, 0) # Barcode verification status default: 0 (not verified)
        self._set(TAG.PART_READY, 0)                  # Part ready status default: 0 (not ready)
        self._set(TAG.CONVEYOR_STATUS, 1)             # Conveyor status default: 1 (running)
        logging.debug("Initialization: Tags set to default values")

    def _logic(self):
        # Check if the part is present
        part_present = self._get(TAG.PART_PRESENT)

        if part_present:
            logging.debug("Action: Scanning barcode, retrieving part details")

            # Start the sticker printing process if it hasn't started yet
            if self.sticker_start_time is None:
                self.sticker_start_time = time.time()
                self._set(TAG.PRINTING_STICKER_TAG, 1)  # Indicate that printing is in progress
                logging.debug("Status: Sticker printing started")

            # Check if sticker printing time has elapsed
            elapsed_time = time.time() - self.sticker_start_time
            if elapsed_time >= STICKER_PLACEMENT:
                logging.debug("Sticker printing process completed")

                # Simulate barcode verification and update BARCODE_VERIFICATION_STATUS
                barcode_verification_result = self._scan_barcode(TAG.CUSTOMER_PART_NUMBER)
                if barcode_verification_result:
                    self._set(TAG.BARCODE_VERIFICATION_STATUS, 1)  # Barcode verified
                    logging.debug("Result: Barcode verified successfully")
                else:
                    self._set(TAG.BARCODE_VERIFICATION_STATUS, 0)  # Verification failed
                    logging.debug("Error: Barcode verification failed")

                # Clear PRINTING_STICKER_TAG after printing is done
                self._set(TAG.PRINTING_STICKER_TAG, 0)
                logging.debug("Status: Sticker printing cleared")
                self.sticker_start_time = None  # Reset the timer

                # Start the test process if the barcode is verified
                if self._get(TAG.BARCODE_VERIFICATION_STATUS) == 1:
                    self._set(TAG.START_TEST, 1)
                    logging.debug("Action: Starting test process for verified part")
                else:
                    self._set_hmi_message("Part can't be processed in this station")
                    logging.debug("Error: Part verification failed; cannot proceed")

        else:
            logging.debug("Status: No part detected at the sensor")
            part_position = self._get(TAG.PART_DISTANCE_TO_SENSOR_VALUE)
            logging.debug(f"Sensor reading: PLC part position: {part_position}")

            if part_position is not None and part_position < 1.5:
                self._set(TAG.CONVEYOR_STATUS, 0)  # Stop conveyor when part is in position
                self._set(TAG.PART_READY, 1)       # Set PART_READY when part is in position
                logging.debug("Status: Part is in position, conveyor stopped")
            else:
                self._set(TAG.CONVEYOR_STATUS, 1)  # Keep conveyor moving until part reaches position
                self._set(TAG.PART_READY, 0)
                logging.debug("Status: Conveyor running, part not yet in position")

    def _scan_barcode(self, tag_name):
        # Placeholder function to simulate barcode scanning
        return True  # Simulated successful scan

    def _store_part_details(self, part_number, serial_number):
        # Store the part details in the PLC for further processing
        logging.debug("Action: Storing part details in database")
        self._set(TAG.CUSTOMER_PART_NUMBER, part_number)
        self._set(TAG.SERIAL_NUMBER, serial_number)

    def _get_test_status_from_m2s(self, part_number, serial_number):
        # Simulated API call to M2S system to check part status
        return "OK"  # Simulated response from the M2S system

    def _perform_test_and_record_results(self):
        # Simulate a test and record the results
        test_result = "Pass"  # Simulated test result
        self._set(TAG.TEST_RESULT, 1 if test_result == "Pass" else 0)
        logging.debug(f"Result: Test {'passed' if test_result == 'Pass' else 'failed'}")

    def _set_hmi_message(self, message):
        # Set the HMI message based on current status or actions
        self._set(TAG.HMI_MESSAGE, message)

    def _post_logic_update(self):
        super()._post_logic_update()

if __name__ == '__main__':
    plc1 = PLC1()
    plc1.set_record_variables(True)
    plc1.start()
