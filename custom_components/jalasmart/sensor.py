from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfElectricPotential,
    UnitOfElectricCurrent,
    UnitOfPower,
    UnitOfEnergy,
    UnitOfTemperature,
)
from .const import DOMAIN
from .entity import JalaBaseEntity # 引入刚才创建的基类

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    sensors = [
        JalaSensor(coordinator, "Voltage", "电压", UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE),
        JalaSensor(coordinator, "Current", "电流", UnitOfElectricCurrent.AMPERE, SensorDeviceClass.CURRENT),
        JalaSensor(coordinator, "Power", "功率", UnitOfPower.KILO_WATT, SensorDeviceClass.POWER),
        JalaSensor(coordinator, "Electricity", "用电量", UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, True),
        JalaSensor(coordinator, "Temp", "温度", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE),
    ]
    async_add_entities(sensors)

class JalaSensor(JalaBaseEntity, SensorEntity):
    def __init__(self, coordinator, key, name, unit, device_class, is_total=False):
        super().__init__(coordinator)
        self._key = key
        self._attr_name = name # 这里只需要写"电压"，HA会自动组合成"JalaSmart Line 41 电压"
        self._attr_unique_id = f"{coordinator.line_id}_{key}"
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING if is_total else SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        return self.coordinator.data.get(self._key)