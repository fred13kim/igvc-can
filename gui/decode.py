#!/usr/bin/env python3
import can
import cantools

#  timestamp        CAN bus  frame_id num_bytes  DATA
# (1648942377.882566)  can0  1E5   [8]  18 00 00 00 00 00 00 54


dbc_path = './igvc_can.dbc'
dump_path = './dumps/Sat Apr  2 11:32:52 PM UTC 2022'
dbc = None
try:
    dbc = cantools.database.load_file(dbc_path)
except Exception as e:
    if (e != 0):
        print(e)
        exit(-1)

try:
    with open(dump_path) as fp:
        candump = fp.readlines()
except Exception as e:
    if (e != 0):
        print(e)
        exit(-1)

init_timestamp = float(candump[0].split()[0].strip('()'))
for dump in candump:
    msg = {}
    dump = dump.split()
    cur_timestamp = float(dump[0].strip('()'))
    frame_id = int(dump[2], 16)
    raw_data = bytearray.fromhex(''.join(dump[4:]))
    delta_timestamp = cur_timestamp - init_timestamp
    try:
        name = dbc.get_message_by_frame_id(frame_id).name
    except KeyError:
        continue
    data = dbc.decode_message(frame_id, raw_data)
    for key, val in data.items():
        if (key == "SystemStatus"):
            print(val)

