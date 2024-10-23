class SimulationConfig:
    # Constants
    EXECUTION_MODE_LOCAL = 'local'
    EXECUTION_MODE_DOCKER = 'docker'
    EXECUTION_MODE_GNS3 = 'gns3'

    # configurable
    EXECUTION_MODE = EXECUTION_MODE_DOCKER



class PHYSICS:
    # Constants for Labeling and Verification Process
    SCANNER_READ_SPEED = 0.001  # Time in seconds to read a label
    PRINTER_PRINT_SPEED = 0.05  # Time in seconds to print a label
    NETWORK_DELAY = 0.01  # Time in seconds for network communication delay

    # Example constants for sensor detection (modify as needed)
    SENSOR_DETECTION_TIME = 0.002  # Time in seconds for part presence sensor to detect a part

    CONVEYOR_BELT_SPEED = 0.003  # Centimeter/mil-second

    PART_DISTANCE = 7

    STICKER_PLACEMENT = 10 #Time which operator prints and places sticker on part


class TAG:
    # Define tag names as constants for easier maintenance and readability
    PART_PRESENT = 'PART_PRESENT'
    CUSTOMER_PART_NUMBER = 'CUSTOMER_PART_NUMBER'
    MAHLE_PART_NUMBER = 'MPN'
    SERIAL_NUMBER = 'SN'
    READ_PN_SN = 'ReadPNSN'
    CODE_READED = 'CodeReaded'
    HMI_PREVIOUS_TEST_RESULT_CODE = 'HMI.PreviousTestResultCode'
    HMI_PREVIOUS_TEST_RESULT_MESSAGE = 'HMI.PreviousTestResultMessage'
    START_TEST = 'StartTest'
    BYPASS = 'Bypass'
    TEST_RESULT = 'TestResult'
    READ_TEST_RESULT = 'ReadTestResult'
    CONFIRMATION_BIT = 'ConfirmationBit'
    HEARTBEAT = 'HeartBeat'
    COM_ERROR = 'ComError'
    HMI_STATUSCODE = 'HMI.STATUSCODE'
    HMI_MESSAGE = 'HMI.MESSAGE'
    MACHINE_RESET = 'MachineReset'

    #TEST TAGS
    CONVEYOR_BELT_ENGINE_STATUS= 'conveyor_belt_engine_status'
    CONVEYOR_BELT_ENGINE_MODE = 'conveyor_belt_engine_mode'
    PART_DISTANCE_TO_SENSOR_VALUE = 'part_distance_to_sensor_value'
    WAITING_FOR_STICKER = 'waiting_for_sticker'

    TAG_LIST = {
        PART_PRESENT: {'id': 0, 'plc': 1, 'type': 'input', 'fault': 0.0, 'default': 0},
        CUSTOMER_PART_NUMBER: {'id': 1, 'plc': 1, 'type': 'input', 'fault': 0.0, 'default': 0},
        MAHLE_PART_NUMBER: {'id': 2, 'plc': 1, 'type': 'input', 'fault': 0.0, 'default': 0},
        SERIAL_NUMBER: {'id': 3, 'plc': 1, 'type': 'input', 'fault': 0.0, 'default': 0},
        READ_PN_SN: {'id': 4, 'plc': 1, 'type': 'output', 'fault': 0.0, 'default': 0},
        CODE_READED: {'id': 5, 'plc': 1, 'type': 'output', 'fault': 0.0, 'default': 0},
        HMI_PREVIOUS_TEST_RESULT_CODE: {'id': 6, 'plc': 1, 'type': 'output', 'fault': 0.0, 'default': 0},
        HMI_PREVIOUS_TEST_RESULT_MESSAGE: {'id': 7, 'plc': 1, 'type': 'output', 'fault': 0.0, 'default': 0},
        START_TEST: {'id': 8, 'plc': 1, 'type': 'output', 'fault': 0.0, 'default': 0},
        BYPASS: {'id': 9, 'plc': 1, 'type': 'output', 'fault': 0.0, 'default': 0},
        TEST_RESULT: {'id': 10, 'plc': 1, 'type': 'output', 'fault': 0.0, 'default': 0},
        READ_TEST_RESULT: {'id': 11, 'plc': 1, 'type': 'output', 'fault': 0.0, 'default': 0},
        CONFIRMATION_BIT: {'id': 12, 'plc': 1, 'type': 'output', 'fault': 0.0, 'default': 0},
        HEARTBEAT: {'id': 13, 'plc': 1, 'type': 'output', 'fault': 0.0, 'default': 0},
        COM_ERROR: {'id': 14, 'plc': 1, 'type': 'output', 'fault': 0.0, 'default': 0},
        HMI_STATUSCODE: {'id': 15, 'plc': 1, 'type': 'output', 'fault': 0.0, 'default': 0},
        HMI_MESSAGE: {'id': 16, 'plc': 1, 'type': 'output', 'fault': 0.0, 'default': 0},
        MACHINE_RESET: {'id': 17, 'plc': 1, 'type': 'output', 'fault': 0.0, 'default': 0},
        CONVEYOR_BELT_ENGINE_STATUS:{'id': 18, 'plc': 1, 'type': 'input', 'fault': 0.0, 'default': 1},
        CONVEYOR_BELT_ENGINE_MODE:{'id': 19, 'plc': 1, 'type': 'output', 'fault': 0.0, 'default': 2},
        PART_DISTANCE_TO_SENSOR_VALUE:{'id': 20, 'plc': 1, 'type': 'input', 'fault': 0.0, 'default': 5},
        WAITING_FOR_STICKER:{'id': 21, 'plc': 1, 'type': 'input', 'fault': 0.0, 'default': 0},

    }   



class Controllers:
    PLC_CONFIG = {
        SimulationConfig.EXECUTION_MODE_DOCKER: {
            1: {
                'name': 'PLC1',
                'ip': '192.168.0.11',
                'port': 502,
                'protocol': 'ModbusWriteRequest-TCP'
             },

        },
        SimulationConfig.EXECUTION_MODE_GNS3: {
            1: {
                'name': 'PLC1',
                'ip': '192.168.0.11',
                'port': 502,
                'protocol': 'ModbusWriteRequest-TCP'
            },

        },
        SimulationConfig.EXECUTION_MODE_LOCAL: {
            1: {
                'name': 'PLC1',
                'ip': '127.0.0.1',
                'port': 5502,
                'protocol': 'ModbusWriteRequest-TCP'
             },

        }
    }

    PLCs = PLC_CONFIG[SimulationConfig.EXECUTION_MODE]


class Connection:
    SQLITE_CONNECTION = {
        'type': 'sqlite',
        'path': 'storage/PhysicalSimulation1.sqlite',
        'name': 'fp_table',
    }
    MEMCACHE_DOCKER_CONNECTION = {
        'type': 'memcache',
        'path': '192.168.1.31:11211',
        'name': 'fp_table',
    }
    MEMCACHE_LOCAL_CONNECTION = {
        'type': 'memcache',
        'path': '127.0.0.1:11211',
        'name': 'fp_table',
    }
    File_CONNECTION = {
        'type': 'file',
        'path': 'storage/sensors_actuators.json',
        'name': 'fake_name',
    }

    CONNECTION_CONFIG = {
        SimulationConfig.EXECUTION_MODE_GNS3: MEMCACHE_DOCKER_CONNECTION,
        SimulationConfig.EXECUTION_MODE_DOCKER: SQLITE_CONNECTION, #todo : return back to sqlite connection
        SimulationConfig.EXECUTION_MODE_LOCAL: SQLITE_CONNECTION
    }
    CONNECTION = CONNECTION_CONFIG[SimulationConfig.EXECUTION_MODE]

