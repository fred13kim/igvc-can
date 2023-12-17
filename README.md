# IGVC GUI

FRED KIM IGVC GUI DOCUMENTATION

Before diving into the CAN GUI and how it works, it is important to understand what CAN is.

## CAN
This is a high level understanding of what CAN is and how it works:

        The car operates on a series of DBW Nodes.
        Each DBW Node sends a series of CAN Messages to each other.
        Each CAN Message may have a series of signals associated with data values.

The brake node for example on the vehicle may send the following messages with their respective signals:

        Message Name:
            dbwNode_Status_Brake:
                SystemStatus: ESTOP
                Counter: 32
            dbwNode_Brake_Data:
                Frequency: 1000
                Resolution: 16
                DutyCycle: 0
                Percent: 0
                Pressure: 0

Users may inspect, insert, and modify CAN messages in the `selfdrive/can/can.yml` file.
The `can.yml` file is an overarching high level human-readable structure that describes CAN messages and signals.

Each CAN message or "frame" is of the following format (directly from [CAN BUS WIKI](https://en.wikipedia.org/wiki/CAN_bus)):

|Field name 	                |Length (bits) 	|Purpose|
|---|---|---|
|Start-of-frame 	            | 1 	        |Denotes the start of frame transmission|
|Identifier 	                | 11 	        |A (unique) identifier which also represents the message priority|
|Stuff bit 	                    |1 	            |A bit of the opposite polarity to maintain synchronisation|
|Remote transmission request 	|1 	            |Must be dominant for data frames and recessive for remote request frames|
|Identifier extension bit 	    |1 	            |Must be dominant for base frame format with 11-bit identifiers|
|Reserved bit 	                |1 	            |Reserved bit. Must be dominant, but accepted as either dominant or recessive.|
|Data length code 	            |4 	            |Number of bytes of data|
|Data field 	                |(0-8 bytes)    |Data to be transmitted|
|CRC 	                        |15 	        |Cyclic redundancy check|
|CRC delimiter 	                |1 	            |Must be recessive|
|ACK slot 	                    |1 	            |Transmitter sends recessive and any receiver can assert a dominant|
|ACK delimiter 	                |1 	            |Must be recessive|
|End-of-frame 	                |7 	            |Must be recessive|
|Inter-frame spacing 	        |3 	            |Must be recessive|

This document will primarily focus on the Identifier or FRAME ID and Data Field or FRAME DATA portion of the CAN Message which composes the bulk of the frame. The former field is what identifies the CAN message being sent while the latter is composed of the signals and respective data values in part of the message being sent.

Users can refer to the [CAN BUS WIKI](https://en.wikipedia.org/wiki/CAN_bus) for specification of the other fields.

To understand further what a CAN message is and how to decode it, the context of the CAN DBC file is crucial.

## CAN DBC FILE
A CAN DBC file or CAN Database file is a text file that contains the information necessary to decode a CAN message.

At the heart of a DBC file, there are a set of decoding rules used to decode a CAN message.
In the DBC file, messages start with `BO_` while signals start with `SG_`.
From [A Simple Intro to DBC Files](https://www.csselectronics.com/pages/can-dbc-file-database-intro):
DBC MESSAGE:

    A message starts with BO_ and the ID must be unique and in decimal (not hexadecimal)
    The DBC ID adds 3 extra bits for 29 bit CAN IDs to serve as an 'extended ID' flag
    The name must be unique, 1-32 characters and may contain [A-z], digits and underscores
    The length (DLC) must be an integer between 0 and 1785
    The sender is the name of the transmitting node, or Vector__XXX if no name is available

DBC SIGNAL:

    Each message contains 1+ signals that start with SG_
    The name must be unique, 1-32 characters and may contain [A-z], digits and underscores
    The bit start counts from 0 and marks the start of the signal in the data payload
    The bit length is the signal length
    The @1 specifies that the byte order is little-endian/Intel (vs @0 for big-endian/Motorola)
    The + informs that the value type is unsigned (vs - for signed signals)
    The (scale,offset) values are used in the physical value linear equation (more below)
    The [min|max] and unit are optional meta information (they can e.g. be set to [0|0] and "")
    The receiver is the name of the receiving node (again, Vector__XXX is used as default)

Advanced parts of the DBC file in this document will not be explained. One can find in more depth on how DBC files elsewhere online.

For example the brake node may have the following segment of rules for the `dbwNode_Status_Brake` message:
```
BO_ 227 dbwNode_Status_Brake: 2 Vector__XXX
 SG_ Counter : 2|8@1+ (1,0) [0|0] "" Vector__XXX
 SG_ SystemStatus : 0|2@1+ (1,0) [0|0] "" Vector__XXX
```
For the example above, the message with ID 227 in decimal (0E3 in hex) has the name `dbwNode_Status_Brake` with a length of 2 bytes of data. This message has the following two signals:

    Counter:
        Bit start: 2
        Bit length: 8
        Little-endian (the bit-start is at the LSB (Least Significant Bit))
        Unsigned
        Scale: 1, Offset: 0
        Min: 0, Max: 0
    
    SystemStatus:
        Bit start: 0
        Bit length: 2
        Little-endian
        Unsigned
        Scale: 1, Ofset: 0
        Min: 0, Max: 0

Currently on our car, this is a raw CAN dump for a `dbwNode_Status_Brake` message:

        (1648942380.970836)  can0  0E3   [2]  78 00

The first value `1648942377.882566` is just the timestamp of the candump.
The second value `can0` is the physical CAN interface.
The third value `0E3` is the CAN FRAME ID which corresonds to `dbwNode_Status_Brake` in the dbc file.
The fourth value `[2]` is the number in bytes of data.
The fifth value `78 00` is the CAN FRAME DATA

78 00 hex:
     0 1 1 1 1 0 0 0 0 0 0 0 0 0 0 0
Bit: 7 - - - - - - 0 15- - - - - - 0

Let's decode this message:
First let's extract the signal bits:
The Counter signal starts at the 2nd bit with a length of 8, thus 0001 1110 = 30 would be the raw value
The SystemStatus starts at the 0th bit with a length of 2, thus 00 would be the raw data value which is IDLE based on the DBC

Thus,
The message is a dbwNode_Status_Brake message with
a Counter of 30 and a SystemStatus of IDLE

## THE IGVC CAN DBC FILE
[igvc_can.dbc](https://raw.githubusercontent.com/fred13kim/igvc_gui/main/gui/igvc_can.dbc)

## THE GUI PROGRAM
Due to time constraint a full physical gui using PyQtGraph to show these CAN messages has not been implemented yet. 
However, the bulk of decoding the CAN messages from a CAN dump has been implemented & all the messages are printed to stdout.

Current implementation:
https://github.com/fred13kim/igvc_gui/blob/main/gui/gui.py

Running the following program on the dump file `igvc_gui/gui/dumps/Sat Apr  2 11:32:52 PM UTC 2022` gives the following output:
i.e.
`python3 gui.py`

```
.
.
.
TIMESTAMP: 228.09912204742432s
Message: dbwNode_Status_Brake
with the following Signals:
        ('SystemStatus', 'ESTOP')
        ('Counter', 232)
TIMESTAMP: 229.09915804862976s
Message: dbwNode_Status_Brake
with the following Signals:
        ('SystemStatus', 'ESTOP')
        ('Counter', 242)
TIMESTAMP: 230.09919905662537s
Message: dbwNode_Status_Brake
with the following Signals:
        ('SystemStatus', 'ESTOP')
        ('Counter', 252)
TIMESTAMP: 231.0992729663849s
Message: dbwNode_Status_Brake
with the following Signals:
        ('SystemStatus', 'ESTOP')
        ('Counter', 6)
TIMESTAMP: 232.0993149280548s
Message: dbwNode_Status_Brake
with the following Signals:
        ('SystemStatus', 'ESTOP')
        ('Counter', 16)
TIMESTAMP: 233.0993571281433s
Message: dbwNode_Status_Brake
with the following Signals:
        ('SystemStatus', 'ESTOP')
        ('Counter', 26)
TIMESTAMP: 234.09944796562195s
Message: dbwNode_Status_Brake
with the following Signals:
        ('SystemStatus', 'ESTOP')
        ('Counter', 36)
TIMESTAMP: 235.09954404830933s
Message: dbwNode_Status_Brake
with the following Signals:
        ('SystemStatus', 'ESTOP')
        ('Counter', 46)
```
