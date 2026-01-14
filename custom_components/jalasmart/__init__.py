"""The JalaSmart integration."""
import asyncio
import logging
import async_timeout
import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from datetime import timedelta

from .const import (
    DOMAIN,
    BASE_URL,
    HEADERS,
    CONF_DEVICE_ID,
    CONF_CONTROLLER_ID,
    CONF_LINE_ID,
    CONF_LINE_NO,
    CONF_AUTH_TOKEN,
    CONF_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "switch", "number"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up JalaSmart from a config entry."""
    
    coordinator = JalaSmartDataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


class JalaSmartDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching JalaSmart data."""

    def __init__(self, hass, entry):
        """Initialize."""
        self.entry = entry
        self.device_id = entry.data[CONF_DEVICE_ID]
        self.line_id = entry.data[CONF_LINE_ID]
        self.controller_id = entry.data[CONF_CONTROLLER_ID]
        self.line_no = entry.data[CONF_LINE_NO]
        
        # 将Auth Token加入Header
        self.headers = HEADERS.copy()
        self.headers["Authorization"] = entry.data[CONF_AUTH_TOKEN]

        update_interval = timedelta(seconds=entry.data[CONF_SCAN_INTERVAL])
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )

    async def _async_update_data(self):
        """Fetch data from API."""
        url = f"{BASE_URL}/devices/{self.device_id}/lines/{self.line_id}"
        
        try:
            async with async_timeout.timeout(10):
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=self.headers) as response:
                        if response.status != 200:
                            raise UpdateFailed(f"Error fetching data: {response.status}")
                        data = await response.json()
                        # 返回 Data 字段下的内容
                        return data.get("Data", {})
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")

    # --- API Control Methods ---

    async def set_voltage_protection(self, under=None, over=None):
        """Set Under/Over voltage."""
        # 获取当前值作为 fallback
        current_under = self.data.get("Under")
        current_over = self.data.get("Over")
        
        payload = {
            "Under": str(int(under)) if under is not None else str(current_under),
            "Over": str(int(over)) if over is not None else str(current_over)
        }
        
        url = f"{BASE_URL}/devices/{self.device_id}/lines/{self.line_id}/Under"
        return await self._send_put_request(url, payload)

    async def set_current_protection(self, max_curr=None, duration=None):
        """Set Max current and Duration."""
        current_max = self.data.get("Max")
        current_duration = self.data.get("Duration")
        
        payload = {
            "Max": int(max_curr) if max_curr is not None else int(current_max),
            "Duration": str(int(duration)) if duration is not None else str(current_duration)
        }
        
        url = f"{BASE_URL}/devices/{self.device_id}/lines/{self.line_id}/max"
        return await self._send_put_request(url, payload)

    async def set_limit(self, limit):
        """Set monthly limit."""
        payload = {"Limit": str(int(limit))}
        url = f"{BASE_URL}/devices/{self.device_id}/lines/{self.line_id}/limit"
        return await self._send_put_request(url, payload)

    async def set_enabled(self, enabled: bool):
        """Set Lock (Enabled). 1=Lock(On), 0=Unlock(Off)."""
        # 注意：NodeRED中逻辑：Lock ON -> Enabled 1. 
        val = "1" if enabled else "0"
        payload = {"Enabled": val}
        url = f"{BASE_URL}/devices/{self.device_id}/lines/{self.line_id}/Enabled"
        return await self._send_put_request(url, payload)

    async def set_switch_status(self, is_on: bool):
        """Set Line ON/OFF."""
        status_val = 1 if is_on else 0
        payload = {
            "Lines": [{
                "LineNo": self.line_no,
                "Status": status_val
            }],
            "ControllerID": self.controller_id
        }
        url = f"{BASE_URL}/status/{self.controller_id}"
        return await self._send_put_request(url, payload)

    async def _send_put_request(self, url, payload):
        """Helper to send PUT requests."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.put(url, json=payload, headers=self.headers) as response:
                    if response.status == 200:
                        # 成功后请求一次立即刷新
                        await self.async_request_refresh()
                    else:
                        _LOGGER.error(f"Failed to set data: {response.status}")
        except Exception as e:
            _LOGGER.error(f"Error sending PUT request: {e}")