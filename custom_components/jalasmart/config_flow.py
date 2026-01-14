"""Config flow for JalaSmart integration."""
import voluptuous as vol
from homeassistant import config_entries
from .const import (
    DOMAIN,
    CONF_DEVICE_ID,
    CONF_CONTROLLER_ID,
    CONF_LINE_ID,
    CONF_LINE_NO,
    CONF_AUTH_TOKEN,
    CONF_SCAN_INTERVAL,
    CONF_DEVICE_TYPE,
    TYPE_STANDARD,
    TYPE_WIDE,
    DEFAULT_SCAN_INTERVAL,
)

class JalaSmartConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for JalaSmart."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # 使用 Line ID 作为唯一 ID，防止重复添加
            await self.async_set_unique_id(user_input[CONF_LINE_ID])
            self._abort_if_unique_id_configured()

            # 根据设备类型生成显示标题
            if user_input[CONF_DEVICE_TYPE] == TYPE_WIDE:
                type_name = "空开" 
            else:
                type_name = "断路器"
            
            title = f"Line {user_input[CONF_LINE_NO]} ({type_name})"

            return self.async_create_entry(title=title, data=user_input)

        # 定义下拉菜单的友好显示名称
        device_types = {
            TYPE_STANDARD: "断路器 (欠压175-205 / 过压235-265)",
            TYPE_WIDE: "空开 (欠压160-170 / 过压270-280)",
        }

        # 配置表单：去掉了四个 ID 项的 default 参数
        data_schema = vol.Schema(
            {
                vol.Required(CONF_DEVICE_ID): str,
                vol.Required(CONF_CONTROLLER_ID): str,
                vol.Required(CONF_LINE_ID): str,
                vol.Required(CONF_LINE_NO): int,
                vol.Required(CONF_DEVICE_TYPE, default=TYPE_STANDARD): vol.In(device_types),
                vol.Required(CONF_AUTH_TOKEN): str,
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): int,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )