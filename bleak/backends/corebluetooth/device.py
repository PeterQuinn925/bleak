# -*- coding: utf-8 -*-
from Foundation import NSDictionary

from bleak.backends.device import BLEDevice


class BLEDeviceCoreBluetooth(BLEDevice):
    """
    A CoreBlutooth class representing a BLE server detected during
    a `discover` call.

    - The `details` attribute will be a CBPeripheral object.

    - The `metadata` keys are more or less part of the crossplattform interface.

    - Note: Take care not to rely on any reference to `advertisementData` and
      it's data as lower layers of the corebluetooth stack can change it. i.e.
      only valid/trusted in callback(s) or if copied.

    - AdvertisementData fields/keys that might be of interest:
      - kCBAdvDataAppleMfgData
      - kCBAdvDataChannel
      - kCBAdvDataManufacturerData
      - kCBAdvDataIsConnectable
      - kCBAdvDataChannel
      - kCBAdvDataAppleMfgData
      - kCBAdvDataTxPowerLevel
      - kCBAdvDataLocalName
      - kCBAdvDataServiceUUIDs
      - kCBAdvDataManufacturerData
    """

    def __init__(self, *args, **kwargs):
        super(BLEDeviceCoreBluetooth, self).__init__(*args, **kwargs)
        self.metadata = {}
        self._rssi = kwargs.get("rssi")

    def _update(self, advertisementData: NSDictionary):
        self._update_uuids(advertisementData)
        self._update_manufacturer(advertisementData)

    def _update_uuids(self, advertisementData: NSDictionary):
        cbuuids = advertisementData.get("kCBAdvDataServiceUUIDs", [])
        if not cbuuids:
            return
        # converting to lower case to match other platforms
        chuuids = [str(u).lower() for u in cbuuids]
        if "uuids" in self.metadata:
            for uuid in chuuids:
                if not uuid in self.metadata["uuids"]:
                    self.metadata["uuids"].append(uuid)
        else:
            self.metadata["uuids"] = chuuids

    def _update_manufacturer(self, advertisementData: NSDictionary):
        mfg_bytes = advertisementData.get("kCBAdvDataManufacturerData")
        if not mfg_bytes:
            return

        mfg_id = int.from_bytes(mfg_bytes[0:2], byteorder="little")
        mfg_val = bytes(mfg_bytes[2:])
        self.metadata["manufacturer_data"] = {mfg_id: mfg_val}

    @property
    def rssi(self):
        return self._rssi
