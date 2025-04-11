[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
#  April Brother (AB) BLE Gateway V4 Component
This component allows forwarding BLE data from the AB BLE Gateway V4 to the new [bluetooth component](https://www.home-assistant.io/integrations/bluetooth/) released in Home Assistant [2022.8](https://www.home-assistant.io/blog/2022/08/03/release-20228/#first-class-bluetooth-support). 


![AB BLE Gateway V4](gateway41.jpg)


AB BLE Gateway V4 is an ESP32- and NRF52832-based BLE to network gateway and bridge. It reads BLE advertisement data such as iBeacon, Eddystone or customized format data and sends to LAN/internet server (via MQTT, HTTP or Websockets). It's widely distributed through AliExpress, Amazon, Taobao etc. For more information, see the [April Brother Wiki](https://wiki.aprbrother.com/en/AB_BLE_Gateway_V4.html). 

Please note that this component only supports forwarding via MQTT.


## Component Setup Instructions
The component should automatically discover any devices on the network (the gateway advertises itself via SSDP).

### MQTT Configuration Requirements
1. Make sure to have setup the [MQTT component](https://www.home-assistant.io/integrations/mqtt/) before adding this integration.
2. The gateway MUST be configured to use MQTT (connection type 3).
3. The gateway MQTT settings MUST match the Home Assistant MQTT configuration (same broker, port, username, and password).
4. During setup, you will need to provide:
   - MQTT Topic - the topic the gateway publishes BLE advertisements to
   - MQTT ID Prefix - the client ID prefix used by the gateway
   - Optionally: Username and Password if your MQTT broker requires authentication

The component supports authenticated login and automatically checks that the MQTT settings match.


## More Details
For more details, please check out the post on my personal website: [
December 9, 2022 - Forwarding Bluetooth with the AB BLE Gateway](https://christian.kuendig.info/posts/2022-12-hass-ab_ble/).