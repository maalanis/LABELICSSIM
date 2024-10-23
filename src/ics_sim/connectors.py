import os
import logging
import sqlite3
import memcache
from abc import abstractmethod, ABC
from os.path import splitext

from pyModbusTCP.client import ModbusClient

from ics_sim.helper import debug, error, validate_type
import json

from ics_sim.protocol import ClientModbus

# Setup logging configuration
#logging.basicConfig(level=logging.DEBUG,
                    #filename='app.log',  # Specify your log file's path here
                    #filemode='a',  # 'w' will overwrite the log file each run; 'a' will append to the end of the log file
                    #format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
class Connector(ABC):

    """Base class."""
    def __init__(self, connection):
        #  TODO: Check the input
        self._name = connection['name']
        self._path = connection['path']
        self._connection = connection

    @abstractmethod
    def initialize(self, values, clear_old=False):
        pass

    @abstractmethod
    def set(self, key, value):
        pass

    @abstractmethod
    def get(self, key):
        pass


class SQLiteConnector(Connector):
    def __init__(self, connection):
        Connector.__init__(self, connection)
        self._key = 'name'
        self._value = 'value'
        #logging.debug(f"Initializing SQLiteConnector with database path: {self._path}")

        
    def initialize(self, values, clear_old=True):
        logging.debug("Initializing database schema...")
        if clear_old and os.path.isfile(self._path):
            os.remove(self._path)
            #logging.debug("Existing database file removed.")
            
            

        schema = """
        CREATE TABLE IF NOT EXISTS {} (
            {} TEXT NOT NULL,
            {} REAL,
            PRIMARY KEY({})
        );
        """.format(self._name, self._key, self._value, self._key)

        try:
            with sqlite3.connect(self._path) as conn:
                conn.executescript(schema)
                logging.debug("Database schema created.")
                if values:
                    init_template = "INSERT INTO {}({},{}) VALUES (?, ?);".format(self._name, self._key, self._value)
                    cursor = conn.cursor()
                    cursor.executemany(init_template, values)
                    conn.commit()
        except sqlite3.Error as e:
            error(f'Error initializing database: {e}')
            # Consider adding more sophisticated error handling here.
            # Maybe a retry mechanism, alerting, or a fallback to a default state.

    def set(self, key, value):
        #logging.debug(f"CONNECTORS Setting value for {key}...")
        set_query = 'UPDATE {} SET {} = ? WHERE {} = ?'.format(
            self._name,
            self._value,
            self._key)
        with sqlite3.connect(self._path) as conn:
            try:
                cursor = conn.cursor()
                cursor.execute(set_query, [value, key])
                conn.commit()
                #logging.debug(f"CONNECTORS Set value for {key} successfuly")
                return value

            except sqlite3.Error as e:
                logging.debug(f"Error Setting value for {key}")
                error(f'_set in ICSSIM connection {e.args[0]} for setting tag {key}')

    
    def get(self, key):
        get_query = """SELECT {} FROM {} WHERE {} = ?""".format(
            self._value,
            self._name,
            self._key)
        with sqlite3.connect(self._path) as conn:
            try:
                cursor = conn.cursor()
                #logging.debug(f"cursor: {cursor}")
                cursor.execute(get_query, [key])
                record = cursor.fetchone()
                return record[0]
               
            except sqlite3.Error as e:
                logging.error(f"_get in ICSSIM connection {e.args[0]} for getting tag {key}")
                
        
class MemcacheConnector(Connector):
    def __init__(self, connection):
        Connector.__init__(self, connection)
        self._key = 'name'
        self._value = 'value'
        self.memcached_client = memcache.Client([self._path], debug=0)


    def initialize(self, values, clear_old=False):
        if clear_old:
            os.system('/etc/init.d/memcached restart')

        for key, value in values:
            self.memcached_client.set(key, value)

    def set(self, key, value):
        self.memcached_client.set(key, value)

    def get(self, key):
        return self.memcached_client.get(key)

    def __del__(self):
        self.memcached_client.disconnect_all()


class HardwareConnector(Connector, ABC):
    def __init__(self, connection):
        Connector.__init__(self, connection)
        path = self._path
        self.__IP = path.split(':')[0]
        self.__port = path.split(':')[1]
        self.__clientModbus = ClientModbus(self.__IP, self.__port)

    def get(self, key):
        self.__clientModbus.receive(key)

    def set(self, key, value):
        self.__clientModbus.send(key, value)


class FileConnector(Connector):
    def __init__(self, connection):
        Connector.__init__(self, connection)

    def initialize(self, values, clear_old=True):
        if not os.path.isfile(self._path):
            f = open(self._path, "x")
            obj = json.dumps(values)
            f.write(obj)
            f.close()

    def set(self, key, value):
        f = open(self._path, 'w')
        data = json.load(f)
        data[key] = value
        obj = json.dumps(data)
        f.write(obj)
        f.close()

    def get(self, key):
        f = open(self._path)
        data = json.load(f)
        f.close()
        return data[key]


class ConnectorFactory:
    @staticmethod
    def build(connection):
        validate_type(connection, 'connection', dict)

        connection_keys = connection.keys()
        if (not connection_keys) or (len(connection_keys) != 3):
            raise KeyError('Connection must contain 3 keys.')
        else:
            for key in connection_keys:
                if (key != 'path') and (key != 'name') and (key != 'type'):
                    raise KeyError('%s is an invalid key.' % key)

        if connection['type'] == 'sqlite':
            sub_path, extension = splitext(connection['path'])
            if extension == '.sqlite':
                return SQLiteConnector(connection)
            else:
                raise ValueError('%s is not acceptable extension for type sqlite.' % extension)

        elif connection['type'] == 'file':
            return FileConnector(connection)

        elif connection['type'] == 'hardware':
            return HardwareConnector(connection)

        elif connection['type'] == 'memcache':
            return MemcacheConnector(connection)

        else:
            raise ValueError('Connection type is not supported')

