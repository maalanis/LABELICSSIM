import logging
import time
from ics_sim.Device import HIL
from Configs import TAG, PHYSICS, Connection

logging.basicConfig(level=logging.DEBUG, filename='app.log', filemode='a', 
                    format='%(name)s - %(levelname)s - %(message)s')

class FactorySimulation(HIL):
    def __init__(self):
        super().__init__('Factory', Connection.CONNECTION, 100)
        # Configure logging
    
        self.init()
        self.sticker_placement_start_time = None  # Initialize the start time for sticker placement

    def init(self):
        initial_list = []
        for tag in TAG.TAG_LIST:
            initial_value = (tag, TAG.TAG_LIST[tag]['default'])
            initial_list.append(initial_value)
            logging.debug(f"add {tag}  with value {initial_value}")
            # Log each tag and its default value as they are added
            #tag to initial list: {tag}, Default Value: {TAG.TAG_LIST[tag]['default']}")
        
        self._connector.initialize(initial_list)
        logging.info("Database initialization completed with initial values.")

    def _logic(self):
        elapsed_time = self._current_loop_time - self._last_loop_time
        #logging.debug(f"elapsed time: {elapsed_time} clt: {self._current_loop_time} llt: {self._last_loop_time}")
        # Check if the radiator part is present
        pp = self._get(TAG.PART_PRESENT)
        logging.debug(f"FS part present: {pp}")
        if pp:
            self._set(TAG.CONVEYOR_BELT_ENGINE_STATUS, 0.0)
            if self.sticker_placement_start_time is None:
                self.sticker_placement_start_time = time.time()  # Mark the start time when the part is first detected
                logging.debug("Part detected, starting sticker placement countdown.")
                self._set(TAG.WAITING_FOR_STICKER, 1)

            # Calculate the elapsed time since the sticker placement started
            time_since_sticker_started = time.time() - self.sticker_placement_start_time

            if time_since_sticker_started >= PHYSICS.STICKER_PLACEMENT:
                logging.debug("20 seconds elapsed, processing the part.")
                self._set(TAG.WAITING_FOR_STICKER, 0)
                self._set(TAG.PART_PRESENT, 0)
                self._set(TAG.CONVEYOR_BELT_ENGINE_STATUS, 1)
                self._set(TAG.PART_DISTANCE_TO_SENSOR_VALUE, 7)
                self.sticker_placement_start_time = None  # Reset the start time

        else: 
            #update part position
            part_distance_to_sensor = self._get(TAG.PART_DISTANCE_TO_SENSOR_VALUE)
            logging.debug(f"FS part distance to sensor: {part_distance_to_sensor}")
            conveyor_belt_stat = self._get(TAG.CONVEYOR_BELT_ENGINE_STATUS)
            if conveyor_belt_stat:
                part_distance_to_sensor -= elapsed_time * PHYSICS.CONVEYOR_BELT_SPEED
                part_distance_to_sensor %= PHYSICS.PART_DISTANCE
                if(part_distance_to_sensor <1):
                    self._set(TAG.PART_PRESENT, 1.0)
                    self._set(TAG.CONVEYOR_BELT_ENGINE_STATUS, 0.0)
                logging.debug(f"FS new part distance to sensor:{part_distance_to_sensor}" )
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