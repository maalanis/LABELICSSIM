import random
import time

from pyModbusTCP.server import ModbusServer

from Configs import TAG
from HMI1 import HMI1
from FactorySimulation import FactorySimulation
from PLC1 import PLC1


import memcache
from Configs import Connection, TAG

from ics_sim.protocol import ProtocolFactory
from ics_sim.connectors import FileConnector, ConnectorFactory

factory = FactorySimulation()
factory.start()



plc1 = PLC1()
# plc1.set_record_variables(True)
plc1.start()




hmi1 = HMI1()
hmi1.start()

"""

connector = ConnectorFactory.build(Connection.File_CONNECTION)
"""






