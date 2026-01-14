from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

class JalaBaseEntity(CoordinatorEntity):
    """JalaSmart 实体基类，用于定义设备信息。"""

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_has_entity_name = True # 允许使用子名称

    @property
    def device_info(self):
        """返回设备信息，用于将多个实体归类到一个设备下。"""
        return {
            "identifiers": {(DOMAIN, self.coordinator.line_id)},
            "name": f"JalaSmart Line {self.coordinator.line_no}",
            "manufacturer": "JalaSmart",
            "model": "Smart Breaker",
            "sw_version": "2.0",
            # 如果你想把所有线路归属到同一个主控制器下，可以取消下面注释
            # "via_device": (DOMAIN, self.coordinator.controller_id),
        }