from ics_sim.Device import PLC, SensorConnector, ActuatorConnector
from Configs import TAG, Controllers, Connection
import logging


# Setup logging
logging.basicConfig(level=logging.DEBUG, filename='app.log', filemode='w', 
                    format='%(name)s - %(levelname)s - %(message)s')
class PLC1(PLC):
    def __init__(self):
        sensor_connector = SensorConnector(Connection.CONNECTION)
        actuator_connector = ActuatorConnector(Connection.CONNECTION)
        super().__init__(1, sensor_connector, actuator_connector, TAG.TAG_LIST, Controllers.PLCs)

    import logging

    def _logic(self):
        logging.debug("Starting logic processing.")

        # Check if the part is present
        part_present = self._get(TAG.PART_PRESENT)
        #logging.debug(f"Queried PartPresent: {part_present}")

        #if sensor reads a part
        if part_present:
            self._set_hmi_message("Scan Barcode")
            logging.debug("Set HMI message to 'Scan Barcode'.")

            part_number = self._scan_barcode(TAG.CUSTOMER_PART_NUMBER)
            serial_number = self._scan_barcode(TAG.SERIAL_NUMBER)
            logging.debug(f"Scanned part number: {part_number}, serial number: {serial_number}")

            self._store_part_details(part_number, serial_number)
            logging.debug(f"Stored part details for part number: {part_number}, serial number: {serial_number}")

            # Simulate interaction with M2S system to retrieve status
            test_status = self._get_test_status_from_m2s(part_number, serial_number)
            logging.debug(f"Retrieved test status from M2S: {test_status}")

            # Handle part status and set machine for the next step
            if test_status == "OK":
                self._set(TAG.START_TEST, 1)
                self._set_hmi_message("Ready to start Cycle")
                logging.debug("Part OK: Starting test cycle.")
            else:
                self._set_hmi_message("Part can't be processed in this station")
                logging.debug("Part status not OK: Cannot process at this station.")

            # Perform the test and record the results
            self._perform_test_and_record_results()
            logging.debug("Performed test and recorded results.")

        #no part in the sensor
        else:
            
            part_position = self._get(TAG.PART_DISTANCE_TO_SENSOR_VALUE)
            #if part hasn't reached keep conveyor belt on
            if (part_position > 1):
                logging.debug("no part yet")
                self._set(TAG.CONVEYOR_BELT_ENGINE_STATUS, 1)
            #stop conveyor belt
            else:
                logging.debug("part reached")
                self._set(TAG.CONVEYOR_BELT_ENGINE_STATUS, 0)
                self.f_set(TAG.PART_PRESENT, 1);

    def _scan_barcode(self, tag_name):
        # Placeholder function to simulate barcode scanning
        return 1234567890  # Simulated part number or serial number

    def _store_part_details(self, part_number, serial_number):
        # Store the part details in the PLC for further processing
        self._set(TAG.CUSTOMER_PART_NUMBER, part_number)
        self._set(TAG.SERIAL_NUMBER, serial_number)

    def _get_test_status_from_m2s(self, part_number, serial_number):
        # Simulated API call to M2S system to check part status
        return "OK"  # Simulated response from the M2S system

    def _perform_test_and_record_results(self):
        # Simulate a test and record the results
        test_result = "Pass"  # Simulated test result
        if test_result == "Pass":
            self._set(TAG.TEST_RESULT, 1)  # Simulate storing a passing test result
        else:
            self._set(TAG.TEST_RESULT, 0)  # Simulate storing a failing test result

    def _set_hmi_message(self, message):
        # Set the HMI message based on current status or actions
        self._set(TAG.HMI_MESSAGE, message)

    def _post_logic_update(self):
        super()._post_logic_update()

if __name__ == '__main__':
    plc1 = PLC1()
    plc1.set_record_variables(True)
    plc1.start()
