from homeassistant.components.switch import SwitchEntity
from .const import DOMAIN
from .entity import JalaBaseEntity

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Jala switches from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        JalaMainSwitch(coordinator),
        JalaLockSwitch(coordinator)
    ])

class JalaMainSwitch(JalaBaseEntity, SwitchEntity):
    """主控开关 (Line Status)."""

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "开关"
        self._attr_unique_id = f"{coordinator.line_id}_main_switch"

    @property
    def is_on(self) -> bool:
        """Return True if entity is on."""
        # 优化点：使用字符串比较或明确转换，增强兼容性
        status = self.coordinator.data.get("Status", 0)
        return str(status) == "1"

    async def async_turn_on(self, **kwargs):
        """Turn the entity on."""
        # 1. 发送物理指令
        await self.coordinator.set_switch_status(True)
        
        # 2. 乐观更新：立即修改本地缓存数据，防止 UI 弹回
        if self.coordinator.data is not None:
            self.coordinator.data["Status"] = 1
            
        # 3. 立即更新 HA 内部状态机并通知 UI 刷新
        self.async_write_ha_state()
        
        # 4. (可选) 触发 Coordinator 刷新，确保与服务器最终同步
        # 如果你的 API 反应很快，这一步可以确保数据准确
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """Turn the entity off."""
        await self.coordinator.set_switch_status(False)
        
        if self.coordinator.data is not None:
            self.coordinator.data["Status"] = 0
            
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()


class JalaLockSwitch(JalaBaseEntity, SwitchEntity):
    """锁定开关 (Enabled/Lock)."""

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "锁定控制"
        self._attr_unique_id = f"{coordinator.line_id}_lock_switch"
        self._attr_icon = "mdi:lock"

    @property
    def is_on(self) -> bool:
        """Return True if entity is on."""
        enabled = self.coordinator.data.get("Enabled", 0)
        return str(enabled) == "1"

    async def async_turn_on(self, **kwargs):
        """Turn the entity on."""
        await self.coordinator.set_enabled(True)
        
        # 同步更新本地状态
        if self.coordinator.data is not None:
            self.coordinator.data["Enabled"] = 1
            
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """Turn the entity off."""
        await self.coordinator.set_enabled(False)
        
        if self.coordinator.data is not None:
            self.coordinator.data["Enabled"] = 0
            
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()