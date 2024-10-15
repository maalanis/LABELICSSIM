import logging

from ics_sim.Device import HIL
from Configs import TAG, PHYSICS, Connection


class FactorySimulation(HIL):
    def __init__(self):
        super().__init__('Factory', Connection.CONNECTION, 100)
        # Configure logging
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        self.init()

    def init(self):
        initial_list = []
        for tag in TAG.TAG_LIST:
            initial_value = (tag, TAG.TAG_LIST[tag]['default'])
            initial_list.append(initial_value)
            # Log each tag and its default value as they are added
            #tag to initial list: {tag}, Default Value: {TAG.TAG_LIST[tag]['default']}")
        
        self._connector.initialize(initial_list)
        logging.info("Database initialization completed with initial values.")

    def _logic(self):
        elapsed_time = self._current_loop_time - self._last_loop_time
        logging.debug(f"elapsed time: {elapsed_time} clt: {self._current_loop_time} llt: {self._last_loop_time}")
        # Check if the radiator part is present
        if self._get(TAG.PART_PRESENT):
            logging.debug("entered part present if")
            # Simulate barcode scanning and applying label
            self._simulate_label_application()

            # Simulate data retrieval after barcode scanning
            self._simulate_barcode_scanning()

        # Periodically update physical properties
         # update part position
        else: 
            #update part position
            part_distance_to_sensor = self._get(TAG.PART_DISTANCE_TO_SENSOR_VALUE)
            logging.debug(f"part distance to sensor: {part_distance_to_sensor}")
            if self._get(TAG.CONVEYOR_BELT_ENGINE_STATUS):
                part_distance_to_sensor -= elapsed_time * PHYSICS.CONVEYOR_BELT_SPEED
                part_distance_to_sensor %= PHYSICS.PART_DISTANCE
                logging.debug(f"new part distance to sensor:{part_distance_to_sensor}" )

        self._set(TAG.PART_DISTANCE_TO_SENSOR_VALUE, part_distance_to_sensor)
        #self._update_physical_properties(elapsed_time)

    def _simulate_label_application(self):
        part_number = self._get(TAG.CUSTOMER_PART_NUMBER)
        serial_number = self._get(TAG.SERIAL_NUMBER)
        if part_number and serial_number:
            self.report(f'Label applied with PN: {part_number}, SN: {serial_number}', logging.INFO)

    def _simulate_barcode_scanning(self):
        if self._get(TAG.CODE_READED):
            part_data = self._retrieve_part_data()
            self.report(f'Barcode scanned: {part_data}', logging.INFO)

    def _retrieve_part_data(self):
        # This function would typically interact with a database or an external system
        return {
            'part_number': self._get(TAG.CUSTOMER_PART_NUMBER),
            'serial_number': self._get(TAG.SERIAL_NUMBER),
            'test_result': self._get(TAG.TEST_RESULT)
        }

    def _update_physical_properties(self, elapsed_time):
        # Example physical property update
        # Update conveyor belt status based on machine state
        conveyor_status = self._get(TAG.CONVEYOR_BELT_ENGINE_STATUS)
        if conveyor_status:
            self.report('Conveyor belt in operation', logging.INFO)



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