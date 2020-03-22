from homeassistant.helpers.entity import Entity
from serial import Serial

import time

__version__ = '1'


def setup_platform(hass, config, add_devices, discovery_info=None):
    cybleSensor = CybleSensor()
    add_devices([cybleSensor, CybleSensorHourly(cybleSensor)])


class CybleSensor(Entity):

    def __init__(self):
        self._count = None
        self._serial = Serial("/dev/watermeterusb", 9600)

    def __del__(self):
        self._serial.close()

    @property
    def name(self):
        return 'Cyble Sensor V2'

    @property
    def state(self):
        return self._count

    @property
    def unit_of_measurement(self):
        return "L"

    @property
    def icon(self):
        return "mdi:water"

    def update(self):
        while (self._serial.inWaiting() > 0):
            data = str(self._serial.readline()).split(':')
            if len(data) == 19:
                ID = data[1]
                I = data[3]
                M1 = data[6]
                M2 = data[9]
                M3 = data[12]
                M4 = data[15]
                M5 = data[18].strip("\\r\\n'")
                self._count = int(M1)


class CybleSensorHourly(Entity):

    def __init__(self, cybleSensor):
        self._count = None
        self._sensor = cybleSensor
        self._last_update = time.time()
        self._previousCount = self._sensor.state

    @property
    def name(self):
        return 'Cyble Sensor V2 (hourly)'

    @property
    def state(self):
        return self._count

    @property
    def unit_of_measurement(self):
        return "L/h"

    @property
    def icon(self):
        return "mdi:water"

    def _getHour(self, timestamp):
        return time.gmtime(timestamp).tm_hour

    def update(self):
        if (self._getHour(time.time()) != self._getHour(self._last_update)):
            currentCount = self._sensor.state
            if self._previousCount:
                self._count = currentCount - self._previousCount
            self._previousCount = currentCount
            self._last_update = time.time()
