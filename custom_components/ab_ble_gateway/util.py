
import logging
from uuid import UUID
_LOGGER = logging.getLogger(__name__)


def to_unformatted_mac(addr: int):
    """Return unformatted MAC address"""
    return ''.join(f'{i:02X}' for i in addr[:])


def to_mac(addr: str) -> str:
    """Return formatted MAC address"""
    return ':'.join(f'{i:02X}' for i in addr)


''' Converts the April Brother BLE Gateway Data Format into Raw HCI Packets '''
''' See  https://wiki.aprbrother.com/en/User_Guide_For_AB_BLE_Gateway_V4.html#data-format '''


def parse_ap_ble_devices_data(devices_data):
    d = devices_data
    data = bytearray(bytearray(6))  # prepend 6 bytes
    data.extend(d)
    data.append(d[7])  # append rrsid at the end
    data[2] = len(data) - 3  # set size field
    data[7 + 6] = len(data) - 14 - 1  # set adpayload_size (where the rrsid was)
    data[7:13] = data[7:13][::-1]  # reverse mac address
    # _LOGGER.error(data[7:13])
    return data


''' Converts RAW HCI Packets info BLE advertisments '''
''' This is from https://github.com/Ernst79/bleparser/blob/ecd3c596760aab3ec4bf7ba30515831024fc47d3/package/bleparser/__init__.py#L82 '''


def parse_raw_data(data: bytearray):
    """Parse the raw data."""
    # check if packet is Extended scan result
    is_ext_packet = True if data[3] == 0x0D else False
    # check for no BR/EDR + LE General discoverable mode flags
    adpayload_start = 29 if is_ext_packet else 14
    # https://www.silabs.com/community/wireless/bluetooth/knowledge-base.entry.html/2017/02/10/bluetooth_advertisin-hGsf
    try:
        adpayload_size = data[adpayload_start - 1]
    except IndexError:
        return None, None
    # check for BTLE msg size
    msg_length = data[2] + 3
    if (
        msg_length <= adpayload_start or msg_length != len(data) or msg_length != (
            adpayload_start + adpayload_size + (0 if is_ext_packet else 1)
        )
    ):
        return None, None
    # extract RSSI byte
    rssi_index = 18 if is_ext_packet else msg_length - 1
    rssi = data[rssi_index]
    # strange positive RSSI workaround
    if rssi > 127:
        rssi = rssi - 256
    # MAC address
    mac = (data[8 if is_ext_packet else 7:14 if is_ext_packet else 13])[::-1]
    complete_local_name = ""
    shortened_local_name = ""
    service_class_uuid16 = None
    service_class_uuid128 = None
    service_data_list = []
    man_spec_data_list = []

    while adpayload_size > 1:
        adstuct_size = data[adpayload_start] + 1
        if adstuct_size > 1 and adstuct_size <= adpayload_size:
            adstruct = data[adpayload_start:adpayload_start + adstuct_size]
            # https://www.bluetooth.com/specifications/assigned-numbers/generic-access-profile/
            adstuct_type = adstruct[1]
            if adstuct_type == 0x02:
                # AD type 'Incomplete List of 16-bit Service Class UUIDs'
                service_class_uuid16 = (adstruct[2] << 8) | adstruct[3]
            elif adstuct_type == 0x03:
                # AD type 'Complete List of 16-bit Service Class UUIDs'
                service_class_uuid16 = (adstruct[2] << 8) | adstruct[3]
            elif adstuct_type == 0x06:
                # AD type '128-bit Service Class UUIDs'
                service_class_uuid128 = adstruct[2:]
            elif adstuct_type == 0x08:
                # AD type 'shortened local name'
                shortened_local_name = adstruct[2:].decode("utf-8")
            elif adstuct_type == 0x09:
                # AD type 'complete local name'
                complete_local_name = adstruct[2:].decode("utf-8")
            elif adstuct_type == 0x16 and adstuct_size > 4:
                # AD type 'Service Data - 16-bit UUID'
                service_data_list.append(adstruct)
            elif adstuct_type == 0xFF:
                # AD type 'Manufacturer Specific Data'
                man_spec_data_list.append(adstruct)
                # https://www.bluetooth.com/specifications/assigned-numbers/company-identifiers/
        adpayload_size -= adstuct_size
        adpayload_start += adstuct_size

    if complete_local_name:
        local_name = complete_local_name
    else:
        local_name = shortened_local_name

    """
    if (len(service_data_list) > 1):
homeassistant    | 2022-11-24 10:32:06.681 ERROR (MainThread) [homeassistant.util.logging] Exception in async_on_mqtt_message when handling msg on 'gw/test555': 'b'\x87\xa1v\xa61.5.12\xa3mid\xce\x00\x01\x05\x0b\xa4time\xce\x00\x01\x0b4\xa2ip\xaf192.168.178.223\xa3mac\xacC45BBE8E518C\xa4rssi\xd0\xa6\xa7devices\xdc\x00*\xc4\'\x03Y/3x:\xe7\xa3\x1e\xff\x06\x00\x01\t \x02\x06\xe6]\xe9f\xea\xc7\xc0\xac\xf2\xec\x98\x02\xd4y\x11\xe4^=\xd3\xdeM\xe4\xc4 \x00\xb8|o\xa9M8\xc3\x02\x01\x06\x14\x16\x95\xfeq \\\x04\x188M\xa9o|\xb8\t\x05\x10\x02\x00,\xc4\x1a\x036\xf0\xb1\xd1\xdfc\xa4\x11\xff\x06\x00\x01\t!*\xc8; z\xd58Lara\xc4 \x00\xa0x\x17\xa2F\xfc\xac\x02\x01\x1a\x02\n\x05\x11\x07\x13\x1a\xab\x01(\xe4?\xb8\xbfNPg1\xd8\x92\xbe\xc4\x19\x00C{\xee&\x86\xc1\xa8\x02\x01\x1a\x02\n\x08\n\xffL\x00\x10\x05 \x1c\x7f\x866\xc4\x17\x03&\xc6\x9fh\x19\xb6\xad\x02\x01\x1a\x0b\xffL\x00\t\x06\x03\xdd\xc0\xa8\xb2\x08\xc4\x17\x03+\xad\x94\x1a \x1c\xc5\x02\x01\x1a\x0b\xffL\x00\t\x06\x035\xc0\xa8\xb2\x83\xc4\x19\x00\x7f9\'\xb7]}\xb9\x02\x01\x1a\x02\n\t\n\xffL\x00\x10\x05\x01\x18\x00\x98b\xc4\x10\x03\xef\xd8\x18\xbet\xc5\xae\x07\xffL\x00\x12\x02\x00\x01\xc4\x19\x00\xac\xbc2gG"\xc5\x02\x01\x1a\x02\n\x0c\n\xffL\x00\x10\x05\x01\x14\xcb\xae\xed\xc4#\x00\xec\x81\x93\xf2F\xb8\xaf\x02\x01\x1a\x02\x08\x00\x03\x03a\xfe\x10\xff\x03\x00\x01\x10\x14\x00\x00\x02\xb4\x85\xe1`\xfbn \xc4\x1a\x00a\xd2\x7f\xa3[\xb7\xac\x02\x01\x1a\x02\n\x05\x0b\xffL\x00\x10\x06\x03\x1d\xa0\xa2\xb1X\xc4$\x00\\\x85~\xb0\t\xd3\xb9\x02\x01\x06\x03\x02\x95\xfe\x14\x16\x95\xfeq \x98\x00\t\xd3\t\xb0~\x85\\\r\x04\x10\x02\xce\x00\xc4\x1a\x00@\xbe\xca\x86u\x03\xb6\x02\x01\x1a\x02\n\x0c\x0b\xffL\x00\x10\x06\x07\x1du\x9fsH\xc4%\x03\x107\xc9!\n\xad\xa9\x1c\xff\x06\x00\x01\t!\nC\xa8\xa9\x00\x85DDESKTOP-UREG7P1\xc4\x17\x03\x18\xb1\xbe\xac\xcb\x99\xa7\x02\x01\x1a\x0b\xffL\x00\t\x06\x03\xd4\xc0\xa8\xb21\xc4\'\x03\x0f\xd4\x8f\xea\x10\xa1\xaa\x1e\xff\x06\x00\x01\x0f \x02\xbf/\x90\xf4H\x0b\x9aw\xf6i\xaf\x1bGWG\x02\x1d}\xf1e\xd1&\xa2\xc4\'\x03%\xc5\x85}\xde\xab\xaa\x1e\xff\x06\x00\x01\t \x02\xb2\x112\xe0d\xb8\x7f%\x00tc(\xc2V\xb2b\xfdbi\x93a\xc2\x84\xc4\'\x03\x04\xd5\x9f]\x1a\xd8\xa9\x1e\xff\x06\x00\x01\t \x02\x80\xae3\x9a\xbb\x03)\x18\xf3QQ(~\xf0\xe2.T\xa3\x0c\xfcBI\x10\xc4$\x00\\\x85~\xb0\t\xfc\xb6\x02\x01\x06\x03\x02\x95\xfe\x14\x16\x95\xfeq \x98\x00\xf5\xfc\t\xb0~\x85\\\r\t\x10\x02\\\x03\xc4\x1a\x00`x\x05\xce\xd8\xf2\xa3\x02\x01\x1a\x02\n\x07\x0b\xffL\x00\x10\x06\x0c\x1e\x813Kh\xc4\x1a\x00`\x166\xc4\xdf\t\xa3\x02\x01\x1a\x02\n\x08\x0b\xffL\x00\x10\x065\x19\x82\x98T(\xc4\x1a\x00o\xabh\xac\xb0:\xb1\x02\x01\x1a\x02\n\x0c\x0b\xffL\x00\x10\x06\x1d\x1a\x12\r\x84\xc8\xc4\x19\x00i\xc4\xe5j\x0c;\xad\x02\x01\x1a\x02\n\x0c\n\xffL\x00\x10\x05\x07\x1c\xfef=\xc4\'\x03\x0f\xc0\x0b\x19\xfca\xa4\x1e\xff\x06\x00\x01\x0f \x02\xa4\xc9\xaf;\x82B\xcb\xa6\x0bk;M\xf1\x04\x97\x8aD*\xc8\x90Fc7\xc4 \x00\xf8\xea\xdc<g5\xaa\x02\x01\x06\r\xff\xd5\x06\x00\x08g5\xa6dzx\xf6\x04\x06\tMyCO2\xc4\'\x03\x01\x1dK\xfc\xc5"\xa5\x1e\xff\x06\x00\x01\t \x02\xb9\xe0\x94?\xa8q\xc2\xf6\xb93B\xea\xf7\xe6\x06\xbe\x17\xe4\xd4+^)2\xc4\x1a\x00Kdk\\\x9c\xdb\xad\x02\x01\x1a\x02\n\x05\x0b\xffL\x00\x10\x06\x03\x1d\xa0\xa2\xb1X\xc4\x10\x03\xc4\xc8\t\xce\x08g\xa9\x07\xffL\x00\x12\x02\x00\x01\xc4\x1a\x00g\x887\xc8\x8a\x86\xa6\x02\x01\x1a\x02\n\x08\x0b\xffL\x00\x10\x061\x1a\xf3\xbc\xc6P\xc4\x1d\x00G\x1fJ\x9e\xca\xfa\xa1\x02\x01\x06\x08\x16\xdf\xfdA\x1f\x00\x03\xd5\x05\x16,\xfe\x00\x00\x02\n\xec\xc4\'\x03!2r\xe7\x86p\xa5\x1e\xff\x06\x00\x01\x0f \x02\xfa\xe49%\xfe8q\'FO\\\xda\x1b\x0bqgd\x14\x10\x1e\xc1\xf9\xf7\xc4\x1b\x00X \x0c\x1c\x06\xe1\xb0\x02\x01\x1a\x02\n\x08\x0c\xffL\x00\x10\x07/\x1b\xc5\x05l\xb28\xc4$\x00\\\x85~\xb0\t\xd8\xb7\x02\x01\x06\x03\x02\x95\xfe\x14\x16\x95\xfeq \x98\x00\x13\xd8\t\xb0~\x85\\\r\x04\x10\x02\xc6\x00\xc4\x19\x00L\xe4\xea\x9e\x07P\xa3\x02\x01\x1a\x02\n\x0c\n\xffL\x00\x10\x05\x07\x1c\xa0^\xe5\xc4\x10\x03\xd6\xbb\x92\x16\x86@\xb2\x07\xffL\x00\x12\x02\x00\x00\xc4\x1a\x00CL\xf5\xaeo\x06\xac\x02\x01\x1a\x02\n\x0c\x0b\xffL\x00\x10\x06\n\x19\xf2V(\x08\xc4$\x02T\'\x9e\xf4\x08\x93\xa5\x03\x03\x9f\xfe\x17\x16\x9f\xfe\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc4\x19\x00y\xaa_\x8c\x8c\x8b\xa5\x02\x01\x1a\x02\n\x0c\n\xffL\x00\x10\x05\x07\x1c\r\x1c\xdc\xc4\x19\x00P27zT\xef\xae\x02\x01\x1a\x02\n\x0c\n\xffL\x00\x10\x05\x04\x14\x00j\xef\xc4\'\x03&\xac\xda\xfe\x1e\'\xa5\x1e\xff\x06\x00\x01\x0f \x02\x9d4\xacM\x0c\xfaq\x9c^\xc3\xe6\r]\xb9\x16N\x02\x11\xdcDl\xc8\x1a\xc4$\x00\\\x85~\xb0\t\xd6\xc5\x02\x01\x06\x03\x02\x95\xfe\x14\x16\x95\xfeq \x98\x00\xe4\xd6\t\xb0~\x85\\\r\x04\x10\x02\xd0\x00''
homeassistant    | Traceback (most recent call last):
homeassistant    |   File "/config/custom_components/ab_ble_gateway/__init__.py", line 54, in async_on_mqtt_message
homeassistant    |     adv = parse_raw_data(raw_data)
homeassistant    |   File "/config/custom_components/ab_ble_gateway/util.py", line 114, in parse_raw_data
homeassistant    |     raise "Multiple Service Data Fields shouldn't happen"
homeassistant    | TypeError: exceptions must derive from BaseException

       raise "Multiple Service Data Fields shouldn't happen"
    """

    if (len(man_spec_data_list) > 1):
        raise "Multiple Manufacturer Data Fields shouldn't happen"

    service_uuids = []
    if (service_class_uuid128 != None):
        service_uuids.append(UUID(bytes=bytes(service_class_uuid128)).hex)

    if (service_class_uuid16 != None):
        service_uuids.append("0000{:04x}-0000-1000-8000-00805f9b34fb".format(service_class_uuid16))

    # https://github.com/hbldh/bleak/blob/c5cbb8485741331d03a3ac151e98f45edb560938/bleak/backends/corebluetooth/scanner.py#L82
    # https://github.com/hbldh/bleak/blob/60aa4aa23a97bda075770fec43202295602f1a9d/bleak/backends/winrt/scanner.py#L159
    service_data = {}
    if len(service_data_list) > 0:
        for service_data_elem in service_data_list:
            service_data_uuid = "0000{:04x}-0000-1000-8000-00805f9b34fb".format((service_data_elem[3] << 8) | service_data_elem[2])
            service_data[service_data_uuid

                         ] = service_data_elem[4:]
            service_uuids.append(service_data_uuid)
    # service_data = {service_uuid_string: service_data_list[0] if len(service_data_list) == 1 else None            }

    manufacturer_data = {}
    if len(man_spec_data_list) > 0:
        manufacturer_id = int.from_bytes(
            man_spec_data_list[0][2:4], byteorder="little"
        )
        manufacturer_value = bytes(man_spec_data_list[0][4:])
        manufacturer_data[manufacturer_id] = manufacturer_value

    return {
        "address": to_mac(mac),
        "rssi": rssi,
        "service_uuids": service_uuids,
        "local_name": local_name,
        "service_data": service_data,
        'manufacturer_data': manufacturer_data
    }
