#!/usr/bin/env python3

import pyqtgraph as pg
import cantools
import can


def main():
    dbc_path = './igvc_can.dbc'
    dump_path = './dumps/Sat Apr  2 11:32:52 PM UTC 2022'
    #dump_path = './dumps/sample'
    dbc = cantools.database.load_file(dbc_path)
    messages = []
    for message in dbc.messages:
        messages.append(message.name)
    can_data = {}
    can_data = dict.fromkeys(messages,{});

    with open(dump_path) as fp:
        candump = fp.readlines()

    init_timestamp = float(candump[0].split()[0].strip('()'))

    for dump in candump:
        dump = dump.split()
        cur_timestamp = float(dump[0].strip('()'))
        frame_id = int(dump[2], 16)
        raw_data = bytearray.fromhex(''.join(dump[4:]))
        delta_timestamp = cur_timestamp - init_timestamp
        try:
            message_name = dbc.get_message_by_frame_id(frame_id).name
        except KeyError:
            continue
        message_data = dbc.decode_message(frame_id, raw_data)
        if (message_name != "dbwNode_Status_Brake"):
            continue
        print(f"TIMESTAMP: {delta_timestamp}s\nMessage: {message_name}\nwith the following Signals:")
        for signal, val in message_data.items():
            print(f"\t{signal,val}")

if __name__ == "__main__":
    main()
    #pg.exec()
