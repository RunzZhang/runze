import struct
import numpy as np
def int32_to_2words(value):
    print("begin")
    try:
        it = int(value)
        x = np.arange(it, it + 1, dtype='<i4')
        if len(x) == 1:
            word = x.tobytes()
            piece1, piece2 = struct.unpack('<HH', word)
        else:
            print("ERROR in float to words")
        return piece1, piece2
    except:
        return 0

def float_to_2words(value):
    fl = float(value)
    x = np.arange(fl, fl + 1, dtype='<f4')
    if len(x) == 1:
        word = x.tobytes()
        piece1, piece2 = struct.unpack('<HH', word)
    else:
        print("ERROR in float to words")
    return piece1, piece2


print(int32_to_2words(50))
print(float_to_2words(50.0))