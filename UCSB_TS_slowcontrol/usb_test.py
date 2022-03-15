import usb.core
import usb.util

dev = usb.core.find(idVendor=0xFFFF, idProduct=0x5678)
if dev is None:
    raise ValueError('Device is not found')
# device is found :-)
print(dev)

