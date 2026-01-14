"""Constants for the JalaSmart integration."""

DOMAIN = "jalasmart"

CONF_DEVICE_ID = "device_id"
CONF_CONTROLLER_ID = "controller_id"
CONF_LINE_ID = "line_id"
CONF_LINE_NO = "line_no"
CONF_AUTH_TOKEN = "auth_token"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_DEVICE_TYPE = "device_type"  # 新增配置项

# 定义两种设备类型
TYPE_STANDARD = "standard"
TYPE_WIDE = "wide"

DEFAULT_SCAN_INTERVAL = 60
BASE_URL = "https://api.jalasmart.com/api/v2"

HEADERS = {
    "Host": "api.jalasmart.com",
    "Content-Type": "application/json",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Accept": "*/*",
    "User-Agent": "MySmart/2.6.8 (iPhone; iOS 15.2; Scale/3.00)",
    "Accept-Language": "zh-Hans-CN;q=1",
}