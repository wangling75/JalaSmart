from homeassistant.components.number import NumberEntity
from .const import DOMAIN, CONF_DEVICE_TYPE, TYPE_WIDE
from .entity import JalaBaseEntity

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    # 获取用户在配置流程中选择的设备类型
    # 如果是老配置(没有这个字段)，默认按标准版处理
    device_type = entry.data.get(CONF_DEVICE_TYPE, "standard")

    # 定义范围逻辑
    if device_type == TYPE_WIDE:
        # 宽幅版范围
        under_min, under_max = 160, 170
        over_min, over_max = 270, 280
    else:
        # 标准版范围 (默认)
        under_min, under_max = 175, 205
        over_min, over_max = 235, 265

    async_add_entities([
        # 使用动态变量设置范围
        JalaNumber(coordinator, "Under", "欠压保护", under_min, under_max, "V", "voltage"),
        JalaNumber(coordinator, "Over", "过压保护", over_min, over_max, "V", "voltage"),
        
        # 其他数值保持不变
        JalaNumber(coordinator, "Max", "额定电流", 1, 63, "A", "current"),
        JalaNumber(coordinator, "Duration", "过流关闭时间", 0, 60, "s", "duration"),
        JalaNumber(coordinator, "Limit", "月用电量限制", 0, 9999, "kWh", "limit"),
    ])

class JalaNumber(JalaBaseEntity, NumberEntity):
    def __init__(self, coordinator, key, name, min_val, max_val, unit, mode):
        super().__init__(coordinator)
        self._key = key
        self._mode = mode
        self._attr_name = name
        self._attr_unique_id = f"{coordinator.line_id}_{key}"
        self._attr_native_min_value = min_val
        self._attr_native_max_value = max_val
        self._attr_native_unit_of_measurement = unit
        self._attr_native_step = 1

    @property
    def native_value(self):
        try:
            return float(self.coordinator.data.get(self._key, 0))
        except (ValueError, TypeError):
            return 0

    async def async_set_native_value(self, value: float):
        if self._mode == "voltage":
            if self._key == "Under":
                await self.coordinator.set_voltage_protection(under=value)
            else:
                await self.coordinator.set_voltage_protection(over=value)
        elif self._mode == "current":
            await self.coordinator.set_current_protection(max_curr=value)
        elif self._mode == "duration":
            await self.coordinator.set_current_protection(duration=value)
        elif self._mode == "limit":
            await self.coordinator.set_limit(limit=value)