Project: Mezzo
Function Area:
Title: Communication Protocol Specifications
Doc. Id:
Issue: 1.2.3
Date: 18/09/2020
Mezzo FW Compliance: 1.2.3.34

# Revision History
# Version Date Updated by Changes
### 1.0.0 27/03/2019 F. Digiugno First Edition
### 1.0.1 08/10/2019 A. Carello Align doc with the latests areas
### 1.0.2 11/10/2019 J. Casamonti Changed slow meters alarms spare1 to Generic fault
### 1.0.3 29/10/2019 A. CarelloAdd `0x1B`  value to ESC character at Par 2.2  
Add missing x16+x12+ x5+1 polynomial at Par 2.3
### 1.0.4 18/11/2019 A. Carello Add endianness example at Par 2
### 1.0.5 19/11/2019 A. Carello Add UDP port at Par 2
### 1.0.6 19/11/2019 L. Fibucchi Remove unused fields
### 1.1.0 20/11/2019 J. Casamonti Added new source selection blocks and deprecate old ones.
### 1.1.1 11/12/2019 L. Fibucchi Added Fault Code field
### 1.1.2 23/12/2019 L. Arena Added Dante Integration fields
### 1.1.3 24/12/2019 L. Fibucchi Changed Order of fast meters source selection 3/4
### 1.1.4 08/01/2020 L. Arena Updated source fields to new specifics
### 1.1.5 10/01/2020 L. Arena Added More Dante Integration fields
### 1.1.6 14/01/2020 J. Casamonti Updated slow meters pilot tone detection
### 1.1.7 19/02/2020 L. Fibucchi Added GPO fields
### 1.1.8 06/03/2020 L. Fibucchi Release adjustments
### 1.1.9 25/02/2020 L. Arena Added Zone Block fields
### 1.1.10 03/04/2020 L. Fibucchi Added auto pwoer down field
### 1.1.1 107/04/2020 L. Fibucchi Removed attack time and release time from clip limiter
### 1.1.12 07/04/2020 L. Fibucchi Release candidate
### 1.1.13 23/04/2020 L. Fibucchi Removed unused flag from pilotT one fields
### 1.1.15 26/05/2020 L. Fibucchi Added load default parameters command
### 1.1.17 16/06/2020 L. Fibucchi Added GPI scaled value and GPI config
### 1.1.19 16/06/2020 L. Fibucchi Added Minijack anti-pop, mute flags, fault flags and GPO state
### 1.1.21 18/06/2020 L. Fibucchi Added High Over T emperature field
### 1.1.22 15/07/2020 A. Carello Remove bureaucratic section
### 1.2.0 02/07/2020 L. Fibucchi Released version 1.2.0
### 1.2.2 21/07/2020 L. Fibucchi Removed unused fields in W ays Diagnostic
### 1.2.3 18/09/2020 L. Fibucchi Added OEM empty spare area

# Bibliography
PWS00: , T elnet commands specifications, 2017
## 1. Purpose of this document
The purpose of this document is to depict communication protocol used to communicate with Mezzo MCU.
### 1.1 Definitions
# Equipment  or amplifier  is the Mezzo
Remote controller  is the software, running on a PC or on another device, that is enabled to communicate with Equipment

## 2. Protocol description
The protocol is structured as master/slave where the remote control program running on a PC is the master and the amplifier is slave.
Communication will take place on a LAN Ethernet infrastructure, and uses UDP packet. All packets must be sent to UDP port 8002  
All data bigger than 1 byte are represented in little endian  if not otherwise specified, please see the example below that explain the endianness.  
2.1. Packet structure
The protocol is asymmetrical: the request end response frame are slightly dif ferent..
2.1.1. Request frame
All packets sent from PC to a device will be further defined request. A generic request packet is composed by the following fields:.
Head TAG PBus command ... CRC16 Tail
1 byte 4 bytes variable ... 2 bytes 1 byte
where:
- Head  is a fixed value, corresponding to the ASCII code STX (0x02) .
- TAG is a binary tag to be echoed back into reply , used by software to associate the reply with the issued command.
- PBus  command is a single encapsulation of a PBus operation. In a Pbus frame can be encapsulated more PBus command, this feature is called Multicommand.
The PBus command will be explained in section Errore: sorgente del riferimento non trovata.
- CRC16  is a 2 bytes value, computed as the rule presented in the paragraph ##. It is computed only on the grey part of the frame.
- Tail is a fixed value, corresponding to ASCII code ETX (0x03) .
Since some packets could contain binary data, an escaping strategy has been adopted, refer to the paragraph ## for more information. The escaping is adopted for the
whole frame except Head and T ail. As a consequence CRC16 is computed before escaping.
A request packet can be as long as 2000 byte (plain bytes not escaped), as a consequence 1992 bytes are available for pbus commands.
2.1.2. Response frame
All packets received from the PC (sent by a device), will be further defined replies. A reply has always the same T AG of the command that generated it and has the
following structure:
Head Magic ProtocolID TAG PBus command ... CRC16 Tail
Number Reply ...
1 byte 3 bytes 2 bytes 4 bytes variable ... 2 bytes 1 byte
where:
- Head  is a fixed value, corresponding to the ASCII code STX (0x02) .
- Magic  Number is 3 byte field that must be populated with ‘M’, ‘Z’, ‘O’ (0x4D, 0x5A, 0x4F).
- Protocol ID  is an identification of protocol frame such as version etc. Mezzo uses protocol identified by 0x0001 .
- TAG is a binary tag echoed back from the last issued command.
- PBus command reply  is a single encapsulation of a PBus operation reply . In multicommand contest every PBus command encapsulated in a single protocol frame
needs a PBus command reply encapsulated in a reply .
- CRC16  is a 2 bytes value, computed as the rule presented in the paragraph Errore: sorgente del riferimento non trovata. It is computed only on the grey part of the
frame.

- Tail is a fixed value, corresponding to ASCII code ETX (0x03) .
2.2. Escaping strategy
Since the protocol is binary some byte in the frame could assume the same value of STX or ETX , so an escaping strategy will take place.
In order to avoid the transmission of the special bytes STX, ETX and ESC  an escaping strategy has been adopted.
In case a special byte is found within the packet, an ESC (0x1B)  character is issued in the output buf fer followed by the special byte incremented by 0x40  (i.e. STX
becomes ESC followed by 0x42 , since 0x42 is the sum of STX [0x02] and 0x40).
The escaping strategy involves all fields of packets (request or response), excluding Head  and Tail.
Below a code snippet shows an example of the escaping and un-escaping routines:
### 2.3 CRC16 computation
Each packet contains a CRC16. The checksum value is computed before applying the escaping strategy . The CRC algorithm is the CRC16-CCITT that uses x16+x12+
x5+1 polynomial
A code snippet used to compute CRC16 is provided below:
  const uint16_t crc16tab[256] = {  
    0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50a5, 0x60c6, 0x70e7,  
    0x8108, 0x9129, 0xa14a, 0xb16b, 0xc18c, 0xd1ad, 0xe1ce, 0xf1ef,  
    0x1231, 0x0210, 0x3273, 0x2252, 0x52b5, 0x4294, 0x72f7, 0x62d6,  
    0x9339, 0x8318, 0xb37b, 0xa35a, 0xd3bd, 0xc39c, 0xf3ff, 0xe3de,  
    0x2462, 0x3443, 0x0420, 0x1401, 0x64e6, 0x74c7, 0x44a4, 0x5485,  
    0xa56a, 0xb54b, 0x8528, 0x9509, 0xe5ee, 0xf5cf, 0xc5ac, 0xd58d,  
    0x3653, 0x2672, 0x1611, 0x0630, 0x76d7, 0x66f6, 0x5695, 0x46b4,  
    0xb75b, 0xa77a, 0x9719, 0x8738, 0xf7df, 0xe7fe, 0xd79d, 0xc7bc,  
    0x48c4, 0x58e5, 0x6886, 0x78a7, 0x0840, 0x1861, 0x2802, 0x3823,  
    0xc9cc, 0xd9ed, 0xe98e, 0xf9af, 0x8948, 0x9969, 0xa90a, 0xb92b,  
    0x5af5, 0x4ad4, 0x7ab7, 0x6a96, 0x1a71, 0x0a50, 0x3a33, 0x2a12,  
    0xdbfd, 0xcbdc, 0xfbbf, 0xeb9e, 0x9b79, 0x8b58, 0xbb3b, 0xab1a,  
    0x6ca6, 0x7c87, 0x4ce4, 0x5cc5, 0x2c22, 0x3c03, 0x0c60, 0x1c41,  
    0xedae, 0xfd8f, 0xcdec, 0xddcd, 0xad2a, 0xbd0b, 0x8d68, 0x9d49,  
    0x7e97, 0x6eb6, 0x5ed5, 0x4ef4, 0x3e13, 0x2e32, 0x1e51, 0x0e70,  
    0xff9f, 0xefbe, 0xdfdd, 0xcffc, 0xbf1b, 0xaf3a, 0x9f59, 0x8f78,  
    0x9188, 0x81a9, 0xb1ca, 0xa1eb, 0xd10c, 0xc12d, 0xf14e, 0xe16f,  
    0x1080, 0x00a1, 0x30c2, 0x20e3, 0x5004, 0x4025, 0x7046, 0x6067,  
    0x83b9, 0x9398, 0xa3fb, 0xb3da, 0xc33d, 0xd31c, 0xe37f, 0xf35e,  
    0x02b1, 0x1290, 0x22f3, 0x32d2, 0x4235, 0x5214, 0x6277, 0x7256,  
    0xb5ea, 0xa5cb, 0x95a8, 0x8589, 0xf56e, 0xe54f, 0xd52c, 0xc50d,  
    0x34e2, 0x24c3, 0x14a0, 0x0481, 0x7466, 0x6447, 0x5424, 0x4405,  
    0xa7db, 0xb7fa, 0x8799, 0x97b8, 0xe75f, 0xf77e, 0xc71d, 0xd73c,  
    0x26d3, 0x36f2, 0x0691, 0x16b0, 0x6657, 0x7676, 0x4615, 0x5634,  
    0xd94c, 0xc96d, 0xf90e, 0xe92f, 0x99c8, 0x89e9, 0xb98a, 0xa9ab,  
    0x5844, 0x4865, 0x7806, 0x6827, 0x18c0, 0x08e1, 0x3882, 0x28a3,  
    0xcb7d, 0xdb5c, 0xeb3f, 0xfb1e, 0x8bf9, 0x9bd8, 0xabbb, 0xbb9a,  
    0x4a75, 0x5a54, 0x6a37, 0x7a16, 0x0af1, 0x1ad0, 0x2ab3, 0x3a92,  
    0xfd2e, 0xed0f, 0xdd6c, 0xcd4d, 0xbdaa, 0xad8b, 0x9de8, 0x8dc9,  
    0x7c26, 0x6c07, 0x5c64, 0x4c45, 0x3ca2, 0x2c83, 0x1ce0, 0x0cc1,  
    0xef1f, 0xff3e, 0xcf5d, 0xdf7c, 0xaf9b, 0xbfba, 0x8fd9, 0x9ff8,  
    0x6e17, 0x7e36, 0x4e55, 0x5e74, 0x2e93, 0x3eb2, 0x0ed1, 0x1ef0  
  }; 
  uint16_t crc16(uint16_t crc, const void *buffer, size_t len)  
  { 
    const unsigned char *buf = (const unsigned char *)buffer;  
    while(len--)  
      crc = (crc16tab[((crc) >> 8) ^ ((unsigned char)(*buf++))] ^ ((crc) << 8))  
    return crc;  
  } 
    

A code snippet used to compute the crc table is provided below:
    /* the CRC polynomial. */  
    #define   P    0x1021  
    /* number of bits in CRC: don't change it. */  
    #define W 16  
    /* this the number of bits per char: don't change it. */  
    #define B 8  
    void initcrctab(void)  
    { 
          int  b, v, i;  
          for( b = 0; b <= (1<< B)-1; ++b )  
          {  
                for( v = b<<(W-B), i = B; --i >= 0; )  
                      v = v&0x8000 ? (v<<1)^P : v<<1;  
                crc16tab[b] = v;  
          }  
    } 
    

## 3. PBus Commands
Pbus follows the memory mapped paradigm. That is to say that all values that can be read o write from Remote Control Program are grouped together in a logical basis.
All values that af fect a specific feature and have similar needs about access (read only or read/write, etc.) are grouped in a pbus area.
# An application that run PBus protocol must defines an address space containing a number of areas that can be addressed by pbus command according to access
constrains defined for the single areas.
The addresses are 32 bit wide.
The PBus command represent a generic operation. The operation is defined at least by an address (to refer into a defined area in the address space) and a length (to
know the extent of the operation).
The PBus command encapsulated in both request and reply frame have the same structure:
OPCODE ADDR32 SIZE32 DATA
1 byte 4 bytes 4 bytes variable
- OPCODE  is command (operation) code.
- ADDR32  is address field as previously described. It represent “where” to apply command.
- SIZE32  is the length (extent) of the operation.
- DATA is an optional field depending on the operation. It contain the data stream involved in the operation.
PBus requests with LEN 0 are forbidden; The LEN 0 is reserved in replies to indicate a NAK . For example suppose the equipment defines an area from 0x01030000 to
0x01030100; a PBus command can request an operation at address 0x01030050 and length 10; for that request a reply will take place. Instead if the request is at
address 0x010300F0 and length is 100 the reply will be a NAK (in other words a pbus command reply with len 0).
In general a request defines an area (address + len) where an operation must be performed. This request area must be inclusive in a defined area, otherwise a NAK
reply will be generated
3.1. Pbus Read Command ‘R’ (0x52)
PBus command for the read operation is:
# Field Offset Size Description
OPCODE 0 1 ‘R’ (0x52)
ADDR32 1 4 Address where to start reading.
SIZE32 5 4 Length of data involved in the read
Reply for read command is:
# Field Offset Size Description
OPCODE 0 1 ‘R’ (0x52)
ADDR32 1 4 The address where reading has take place. Is the same value of issue command
SIZE32 5 4 Size of data stream involved in the read operation
DATA 9SIZE32 Data stream read back at address ADDR32 with length SIZE32.
Note: if the operation cannot be performed reply will have SIZE32 0 and no DA TA field. This is NAK condition.
Replies with SIZE32 dif ferent from issue command are not allowed.
Example of read command:
STX 2143A3FF R 00030100 00000004 CRC16 ETX
Example of reply:
STX 4D5A4F 0001 2143A3FF R 00030100 00000004 76E31003 CRC16 ETX
Example of NAK reply:
STX 4D5A4F 0001 2143A3FF R 00030100 00000000 CRC16 ETX

3.2. Pbus W rite Command ‘W’ (0x57)
PBus command for the write operation is:
# Field Offset Size Description
OPCODE 0 1 ‘W’ (0x57)
ADDR32 1 4 Address where to start writing.
SIZE32 5 4 Length of data involved in the write
DATA 9 SIZE32 Data stream to be wrote at address ADDR32 with length SIZE32.
Reply for write command is:
# Field Offset Size Description
OPCODE 0 1 ‘W’ (0x57)
ADDR32 1 4 The address where writing has take place. Is the same value of issue command
SIZE32 5 4 Size of data stream involved in the write operation
Note: if the operation cannot be performed reply will have SIZE32 0. This is NAK condition.
Replies with SIZE32 dif ferent from issued command are not allowed.
Example of write command:
STX 23D47F30 W B4022A00 00000001 3F CRC16 ETX
Example of reply:
STX 4D5A4F 0001 23D47F30 W B4022A00 00000001 CRC16 ETX
Example of NAK reply:
STX 4D5A4F 0001 23D47F30 W B4022A00 00000000 CRC16 ETX
3.3. Pbus Erase Command ‘E’ (0x45)
PBus command for the erase operation is:
# Field Offset Size Description
OPCODE 0 1 ‘E’ (0x45)
ADDR32 1 4 Address where to start erasing.
SIZE32 5 4 Length of data to be erased.
Reply for write command is:
# Field Offset Size Description
OPCODE 0 1 ‘E’ (0x45)
ADDR32 1 4 The address where writing has take place. Is the same value of issue command
SIZE32 5 4 Size of data stream involved in the write operation
Note: if the operation cannot be performed reply will have SIZE32 0. This is NAK condition.
Replies with SIZE32 dif ferent from issued command are not allowed.
Example of erase command:
STX 930045F4 E 300F A030 00000120 CRC16 ETX
Example of reply:
STX 4D5A4F 0001 930045F4 E 300F A030 00000120 CRC16 ETX
Example of NAK reply:
STX 4D5A4F 0001 930045F4 E 300F A030 00000000 CRC16 ETX

3.4. Pbus Crc Command ‘C’ (0x43)
PBus command for the crc operation is:
# Field Offset Size Description
OPCODE 0 1 ‘C’ (0x43)
ADDR32 1 4 Address where to start CRC computing.
SIZE32 5 4 Length of data involved in computation of CRC
Reply for write command is:
# Field OffsetSize Description
OPCODE 0 1 ‘C’ (0x43)
ADDR32 1 4 The address where writing has take place. Is the same value of issue command
SIZE32 5 4 Size of data stream involved in the write operation
# DATA
(CRC16)9 2CRC16 computed on data at address ADDR32 and length SIZE32. It is expressed in
little endian.
Note: if the operation cannot be performed reply will have SIZE32 0. This is NAK condition.
Replies with SIZE32 dif ferent from issued command are not allowed.
Example of crc command:
STX A2349AB4 C 00AF1000 00000400 CRC16 ETX
Example of reply:
STX 4D5A4F 0001 A2349AB4 C 00AF1000 00000400 C13A CRC16 ETX
Example of NAK reply:
STX 4D5A4F 0001 A2349AB4 C 00AF1000 00000000 CRC16 ETX
3.5. Protocol Frame Examples
For the subsequent examples suppose that equipment defines 3 only areas in his PBus address space:
UnusedArea 1 (r--c) 
0x00001000 ~ 0x00002000Area 2 (rw--) 
0x00002000 ~ 0x00002010UnusedArea 3 (rwec) 
0x00002300 ~ 0x00003000Unused
Area 1 and Area 2 are adjoined, and all areas have dif ferent access right, that is to say that is forbidden to write in Area 1, or erase Area 2. Area 3 has full access rights.
The forthcoming examples shows some erroneous cases.
3.5.1. Example: operation not permitted
request
STX 764234A3 W 00001010 00000004 01234567 CRC16 ETX
This request involves Area 1 (address 0x00001010) and generates a NAK reply because the write operation cannot be performed on Area 1; only read and crc operation
are permitted for this area.
3.5.2. Example: operation across two areas
STX 5467A4CF R 00002000 00000400 CRC16 ETX
The operation requested begins in Area 2 (0x00002000) but would finish in Area 3 (from 0x00002300 on).
UnusedArea 1 (r--c) 
0x00001000 ~ 0x00002000Area 2 (rw--) 
0x00002000 ~ 0x00002010UnusedArea 3 (rwec) 
0x00002300 ~ 0x00003000Unused
# Read operation requested  
0x00002000 ~ 0x000023FF
This is not allowed and generates a NAK reply . No matter if the request operation is permitted for all areas involved. Only one area can be involved in an operation.

3.5.3. Example: another operation across two areas
Request:
STX AA3426C3 R 00001FF0 00000200 CRC16 ETX
The operation requested begins in Area 1 (0x00001FF0) but would finish in Area 2 (from 0x00002000 to 0x0000200F).
UnusedArea 1 (r--c) 
0x00001000 ~ 0x00002000Area 2 (rw--) 
0x00002000 ~ 0x00002010UnusedArea 3 (rwec) 
0x00002300 ~ 0x00003000Unused
# Read operation requested  
0x00002000 ~ 0x000023FF
This is not allowed and generates a NAK reply . No matter if the request operation involve contiguous areas. Only one area can be involved in an operation.
3.5.4. Example: operation on unallocated address space
Request:
STX 34453D3C C 00004000 00000180 CRC16 ETX
The address 0x04004000 is unallocated space. No areas are defined there, so this request generates a NAK reply .
3.5.5. Example: unknown operation
Request:
STX C1B8C3B0 Q 00001000 00000004 12A467A5 CRC16 ETX
The OPCODE is none of known operation (‘R’, ‘W’, ‘E’ or ‘C’). It could be not possible to parse that frame (for example, we cannot know if data field is present or not, we
know only for known opcode). W e must consider it as a corrupted frame and no replies will be generated.
3.5.6. Example: malformed frame
Request:
STX DA7A3498 C 00001 100 00000004 12A467A5 CRC16 ETX
The PBus command for this opcode doesn’t admit presence of DA TA field1. This frame cannot be validate. W e must consider it as a corrupted frame and no replies will
be generated.
3.5.7. Example: another malformed frame
Request:
STX 62378A34 W 00001A00 00000010 010203 CRC16 ETX
The request involves Area 2 that support write operation, but DA TA field is shorter than expected2. Only 3 bytes are present instead of 16 bytes declared in SIZE32 field.
We must consider it as a corrupted frame and no replies will be generated.
3.5.8. Example: CRC16 error
Request:
STX 78932A34 E 00002400 00000140 xxxx ETX
Crc computed on this frame doesn’t match the value in CRC16 field. W e must consider it as a corrupted frame and no replies will be generated.
## 1. Parser cannot make any assumption on the presence of DA TA field during parsing since there is no special character to bound a PBus command. It must assume
that no DA TA is present so first byte of DA TA field will be treat as OPCODE of a subsequent PBus command. Length control will invalidate this frame.
## 2. Parser must assume that SIZE32 bytes are present in DA TA field. Length control will invalidate this frame.

3.6. Protocol frame example with multicommand
The forthcoming examples shows some frame with multicommand with more emphasis on erroneous cases. Consider the preceding address space mapping.
3.6.1. Example: correct multicommand
# Request
STX DF3452B2 PBus command 1 PBus command 2 PBus command 3 CRC16 ETX
R00001020 00000002 W00002000 00000002 37A2 E00002400 00000100
This request involves all defined areas. All command are correct and the reply will be:
STX 4D5A4F 0001 DF3452B2 PBus cmd reply 1 PBus cmd reply 2 PBus cmd reply 3 CRC16 ETX
R00001020 00000002 4455 W00002000 00000002 E00002400 00000100
The commands are executed sequentially from left to right (from command 1 to command n). Note that is possible to request more operation on the same area (same
addresses) in a single multicommand.
3.6.2. Example: multicommand with error
# Request
STX 7643D4F4 PBus command 1 PBus command 2 PBus command 3 CRC16 ETX
C00001 100 00000100 C00002000 00000010 E00002400 00000100
# Reply
STX 4D5A4F 0001 7643D4F4 PBus cmd reply 1 PBus cmd reply 2 PBus cmd reply 3 CRC16 ETX
C00001 100 00000100 CD4F C00002000 00000010 E00002400 00000100
PBus command 2 request to perform a crc operation on Area 2 that do not support crc. Only PBus command reply 2 will be a NAK.
In general only failed command1 will populate the reply with NAK, no matter of the position in multicommand or outcome of other commands (if any) in multicommand.
3.6.3. Example: another multicommand with error
Request:
STX 9483A3AA PBus command 1 PBus command 2 PBus command 3 CRC16 ETX
R00002008 00000010 E00002300 00000008 W00003400 00000006 A3DE341556FF
# Reply
STX 4D5A4F 0001 9483A3AA PBus cmd reply 1 PBus cmd reply 2 PBus cmd reply 3 CRC16 ETX
R00002008 00000000 E00002300 00000008 W 00003400 00000000
PBus command 1 fails due to a read operation that exceed area 2 limits. Pbus command 3 wants to write to unallocated addresses.

3.6.4. Example: further multicommand with error
Request:
STX 345344AF PBus command 1 PBus command 2 PBus command 3 PBus command 4 CRC16 ETX
R0000101A 00000010 E00002300 00000008 A00003400 00000006 A3DE C04002500 00000D00
↑ ↑ ↑
This multicommand request cannot be parsed. PBus command 3 must be consider corrupted due to the reasons below:
## 3. The failure is intended to be such as a NAK replies can be generated, instead of a corrupted frame request.
- OPCODE  ‘A’ is unknown.
- SIZE32  and size of DA TA field doesn’t match1
Anyone of the points above by itself may suf fice to invalidate PBus command 3. Since it is not be feasible to parse PBus command 3, also any subsequent PBus
commands cannot be parsed.
No reply is generated for this request.
3.6.5. Example: false positive
The case presented below is one that should be considered wrong, because the request is malformed or corrupted, but it cannot be possible to establish the wrongness
of request. And an operation is performed by mistake.
Request:
STX AA2435E4 PBus command 1 PBus command 2 CRC16 ETX
W 00002300 0000000C 142A36 C 00001F00 00000100
↑ ↑ 9 bytes
This request should be considered as corrupted, but due to the circumstance it will be considered as correct frame composed by a single PBus command.
Indeed in PBus command 1 is asked a write operation on Area 3, 10 bytes length but DA TA field contains only 3 bytes. The subsequent PBus command 2 takes 9 bytes
(1 byte for OPCODE, 4 for ADDR32, and 4 for SIZE32). Parse cannot help but consider PBus command 2 as part of DA TA field of PBus command 1, no matter if PBus
command 2 is formerly and syntactically correct or not. Only its length is important.
## 4. In this case parser would consider DA TA field of PBus command 3 to be 6 bytes, so it assumes that the first bytes of PBus command 4 to belong DA TA field of
PBus command 3. Syntax verification and length control will invalidate this frame.
In this case a write operation will be performed and the reply will be:
STX 4D5A4F 0001 AA2435E4 W 00002300 0000000C CRC16 ETX
Since every PBus command issued should generate a PBus command reply , the Remote Control Program should establish an error condition, but a mistaken operation
is already performed.

# Mezzo
# This is the Mezzo Protocol
# BlockId Start Address End Address Description
Info 0x00000000 0x00000510This area contains general informations related to the
device.
Network 0x00001000 0x0000130cThis area contains network informations related to the
device. It is divided in the following areas:
# Source
selection0x00002000 0x00002554This area contains informations related to the amplifiers
sources.
Matrix 0x00003000 0x00003068 This area contains informations related to the Matrix.
User 0x00004000 0x00004280This area contains informations related to the User
block.
# Speaker
Layout0x00005000 0x000062f4This area contains informations related to the output
routing.
Ways 0x00007000 0x00007950This area contains informations related to the amplifiers
ways.
Dante routing 0x00008500 0x00008518This area contains informations related to Dante
Routing.
# GPI
configuration0x00009000 0x00009004 This area contains informations related to GPI.
# GPO
configuration0x00009e00 0x00009e0c This area contains informations related to GPO.
Power config 0x0000a000 0x0000a00cThis area contains informations related to Standby and
Power Configuration.
Readings 0x0000b000 0x0000bbd0This area contains informations related to amplifier
readings like meters.
AutoSetup 0x0000c000 0x0000ef04 This area contains informations related to the autosetup.
Zone Block 0x0000f000 0x0000f340This area contains informations related to the amplifiers
zones.
# Dante
Settings0x00010000 0x000120b1This area contains UXT chip informations about status
and settings. It includes as well available commands.
# OEM Spare
Area0x00013000 0x00013100 Empty Spare Area dedicated to OEM.
Blink 0x00100000 0x00100001 The blink command
# System
Reboot0x00100001 0x00100002 The system reboot command
# Load Default
Parameters0x00100002 0x00100003 Equivalent to an hardware Hard Reset
# Firmware
Area0x00700000 0x00800000This area contains the firmware. The max size for
firmware is 1048576
# Firmware
Start0x00900000 0x00900006This area contains the new firmware information, use
this to verify the firmware before flash it
# Firmware
Flash Erase0x00900010 0x0090001 1 This will start the upgrade firmware

# Info
This area contains general informations related to the device. It is divided in the following two(2) areas:
# BlockId Start Address End Address Description
Read only area data struct 0x00000000 0x0000007a Readonly informations
Read write client area 0x000000f4 0x00000510 Readonly informations
# Read only area data struct
# Readonly informations
Offset Name Type DimR \
# WDescription
0x00000000  
(0)Model char[20] 20 RString NULL terminated
representing the Model ID
0x00000014  
(20)SerialNumber char[16] 16 Rtring NULL terminated representing
the serial number
0x00000024  
(36)ManufacturerID char[20] 20 RString NULL terminated
representing the manufacturer
identifier
0x00000038  
(56)ManufacturerModel char[20] 20 RString NULL terminated
representing the manufacturer
model identifier
0x0000004c  
(76)ManufacturerSerialNumber char[20] 20 RString NULL terminated
representing the manufacturer
serial number
0x00000060  
(96)FWInfo char[20] 20 RString NULL terminated
representing the firmware version
0x00000074  
(116)MAC Address uint8[6] 6 RActual (running) MAC address
expressed in big endian. For
example if MAC address is
00:1D:C1:AA:BB:CC, bytes are:  
offset bytes
0x00 0x00
0x01 0x1D
0x02 0xC1
0x03 0xAA
0x04 0xBB
0x05 0xCC
# Read write client area
# Readonly informations
# BlockId Start Address End Address Description
NickName 0x000000f4 0x00000144 NickName
HiddenClientSpare 0x0000050c 0x00000510 Spare area for client usage

# NickName
# NickName
Offset Name Type Dim R \ W Description
0x000000f4  
(244)NickName char[20] 80 R\WString NULL terminated representing the device
Nick name (set from the client)
# HiddenClientSpare
# Spare area for client usage
Offset Name Type Dim R \ W Description
# Network
This area contains network informations related to the device. It is divided in the following areas:
# BlockId Start Address End Address Description
NetworkSettings 0x00001000 0x0000100d Network Settings
NetworkInformations 0x00001300 0x0000130c Read only area containing network informations
# NetworkSettings
# Network Settings
# BlockId Start Address End Address Description
Network configuration data struct 0x00001000 0x0000100d Network configurations

# Network configuration data struct
# Network configurations
Offset Name Type Dim R \ W Description
0x00001000  
(4096)AddressMode uint8 1 R\WIf 1 set the equipment to use a static IP address.
# In the case Ip address and netmask are set by
the appropriate fiend.  
If equal to 0, the equipment is set to dynamic
address, using DHCP (or lAuto-IP)
0x00001001  
(4097)IPAddress uint8[4] 4 R\WIs the IP address. This field is used only if
address mode is 0 (static IP).  
Is expressed in big endian.  
offset bytes
0x00 0xC0 (192)
0x01 0xA8 (168)
0x02 0x37 ( 55)
0x03 0x6C (108)
0x00001005  
(4101)NetMask uint8[4] 4 R\WIs the NetMask address. This field is used only if
address mode is 0 (static IP).  
Is expressed in big endian.  
offset bytes
0x00 0xC0 (192)
0x01 0xA8 (168)
0x02 0x37 ( 55)
0x03 0x6C (108)
0x00001009  
(4105)DefaultGW uint8[4] 4 R\WIs the default gateway address. This field is
used only if address mode is 0 (static IP).  
Is expressed in big endian.
# NetworkInformations
# Read only area containing network informations
Offset Name Type Dim R \ W Description
0x00001300  
(4864)IPAddress uint8[4] 4 RIs the IP address.  
Is expressed in big endian.
0x00001304  
(4868)NetMask uint8[4] 4 RIs the NetMask address.  
Is expressed in big endian.
0x00001308  
(4872)DefaultGW uint8[4] 4 RIs the default gateway address.  
Is expressed in big endian.
# Source selection
This area contains informations related to the amplifiers sources.
# BlockId Start Address End Address Description
# Amplifier input
references0x00002000 0x00002010
Old Sources 0x00002100 0x000021a8
Sources 0x00002200 0x000022c4
Minijack Anti-Pop
Configuration0x00002500 0x00002554This area contains the configurations related
to Minijack Anti-Pop.

# Amplifier input references
Offset Name Type Dim R \ W Description
0x00002000  
(8192)Analog Ref Float 4 R\W Analog source reference in linear
0x00002004  
(8196)Analog Delay Float 4 R\W Analog delay in s
0x00002008  
(8200)Digital Ref Float 4 R\W Digital source reference in linear
0x0000200c  
(8204)Digital Delay Float 4 R\W Digital delay in s
# Old Sources
Deprecated since version 1.1.1
# BlockId Start Address End Address Description
Priority1 T ype 0x00002100 0x00002108
Priority1 Channel 0x00002108 0x000021 10
Priority2 T ype 0x000021 10 0x000021 18
Priority2 Channel 0x000021 18 0x00002120
BackupStrategyEnable 0x00002120 0x00002124
PilotT oneEnable 0x00002124 0x00002128
Backup threshold mode 0x00002128 0x00002138
User digital threshold 0x00002138 0x00002148
User analog threshold 0x00002148 0x00002158
Pilot tone freq 0x00002158 0x00002168
Pilot tone high threshold 0x00002168 0x00002178
Pilot tone low threshold 0x00002178 0x00002188
External trigger 0x00002188 0x00002198
External input 0x00002198 0x000021a8
Priority1 T ype
Deprecated since version 1.1.0
Offset Name Type Dim R \ W Description
0x00002100  
(8448)Priority1
# Type CH
1Uint16 2 R\WEnum representing the first priority for the selected
source. For the allowed values for this field refer to …
(TODO)
0x00002102  
(8450)Priority1
# Type CH
2Uint16 2 R\WEnum representing the first priority for the selected
source. For the allowed values for this field refer to …
(TODO)
0x00002104  
(8452)Priority1
# Type CH
3Uint16 2 R\WEnum representing the first priority for the selected
source. For the allowed values for this field refer to …
(TODO)
0x00002106  
(8454)Priority1
# Type CH
4Uint16 2 R\WEnum representing the first priority for the selected
source. For the allowed values for this field refer to …
(TODO)

Priority1 Channel
Deprecated since version 1.1.0
Offset Name Type Dim R \ W Description
0x00002108  
(8456)Priority1
# Channel
CH 1Uint16 2 R\WEnum representing the first priority for the selected
source. For the allowed values for this field refer to
…(TODO)
0x0000210a  
(8458)Priority1
# Channel
CH 2Uint16 2 R\WEnum representing the first priority for the selected
source. For the allowed values for this field refer to
…(TODO)
0x0000210c  
(8460)Priority1
# Channel
CH 3Uint16 2 R\WEnum representing the first priority for the selected
source. For the allowed values for this field refer to
…(TODO)
0x0000210e  
(8462)Priority1
# Channel
CH 4Uint16 2 R\WEnum representing the first priority for the selected
source. For the allowed values for this field refer to
…(TODO)
Priority2 T ype
Deprecated since version 1.1.0
Offset Name Type Dim R \ W Description
0x000021 10 
(8464)Priority2
# Type CH
1Uint16 2 R\WEnum representing the first priority for the selected
source. For the allowed values for this field refer to …
(TODO)
0x000021 12 
(8466)Priority2
# Type CH
2Uint16 2 R\WEnum representing the first priority for the selected
source. For the allowed values for this field refer to …
(TODO)
0x000021 14 
(8468)Priority2
# Type CH
3Uint16 2 R\WEnum representing the first priority for the selected
source. For the allowed values for this field refer to …
(TODO)
0x000021 16 
(8470)Priority2
# Type CH
4Uint16 2 R\WEnum representing the first priority for the selected
source. For the allowed values for this field refer to …
(TODO)
Priority2 Channel
Deprecated since version 1.1.0
Offset Name Type Dim R \ W Description
0x000021 18 
(8472)Priority2
# Channel
CH 1Uint16 2 R\WEnum representing the first priority for the selected
source. For the allowed values for this field refer to
…(TODO)
0x000021 1a 
(8474)Priority2
# Channel
CH 2Uint16 2 R\WEnum representing the first priority for the selected
source. For the allowed values for this field refer to
…(TODO)
0x000021 1c 
(8476)Priority2
# Channel
CH 3Uint16 2 R\WEnum representing the first priority for the selected
source. For the allowed values for this field refer to
…(TODO)
0x000021 1e 
(8478)Priority2
# Channel
CH 4Uint16 2 R\WEnum representing the first priority for the selected
source. For the allowed values for this field refer to
…(TODO)

# BackupStrategyEnable
Deprecated since version 1.1.0
Offset Name Type Dim R \ W Description
0x00002120  
(8480)BackupStrategyEnable
CH 1uint8 1 R\Wif set to 0 backup strategy is disabled, if
set to 1 is enabled
0x00002121  
(8481)BackupStrategyEnable
CH 2uint8 1 R\Wif set to 0 backup strategy is disabled, if
set to 1 is enabled
0x00002122  
(8482)BackupStrategyEnable
CH 3uint8 1 R\Wif set to 0 backup strategy is disabled, if
set to 1 is enabled
0x00002123  
(8483)BackupStrategyEnable
CH 4uint8 1 R\Wif set to 0 backup strategy is disabled, if
set to 1 is enabled
# PilotT oneEnable
Deprecated since version 1.1.0
Offset Name Type Dim R \ W Description
0x00002124  
(8484)PilotT oneEnable
CH 1uint8 1 R\Wif set to 0 pilot tone is disabled, if set to 1 is
enabled
0x00002125  
(8485)PilotT oneEnable
CH 2uint8 1 R\Wif set to 0 pilot tone is disabled, if set to 1 is
enabled
0x00002126  
(8486)PilotT oneEnable
CH 3uint8 1 R\Wif set to 0 pilot tone is disabled, if set to 1 is
enabled
0x00002127  
(8487)PilotT oneEnable
CH 4uint8 1 R\Wif set to 0 pilot tone is disabled, if set to 1 is
enabled
# Backup threshold mode
Deprecated since version 1.1.0
Offset Name Type Dim R \ W Description
0x00002128  
(8488)Backup
threshold
mode CH 1Uint32 4 R\WEnum representing the backup threshold mode
to be used. For the allowed values for this field
refer to …(T ODO)
0x0000212c  
(8492)Backup
threshold
mode CH 2Uint32 4 R\WEnum representing the backup threshold mode
to be used. For the allowed values for this field
refer to …(T ODO)
0x00002130  
(8496)Backup
threshold
mode CH 3Uint32 4 R\WEnum representing the backup threshold mode
to be used. For the allowed values for this field
refer to …(T ODO)
0x00002134  
(8500)Backup
threshold
mode CH 4Uint32 4 R\WEnum representing the backup threshold mode
to be used. For the allowed values for this field
refer to …(T ODO)

# User digital threshold
Deprecated since version 1.1.0
Offset Name Type Dim R \ W Description
0x00002138  
(8504)User digital threshold
CH 1Float 4 R\WUser defined threshold for digital signal
in linear
0x0000213c  
(8508)User digital threshold
CH 2Float 4 R\WUser defined threshold for digital signal
in linear
0x00002140  
(8512)User digital threshold
CH 3Float 4 R\WUser defined threshold for digital signal
in linear
0x00002144  
(8516)User digital threshold
CH 4Float 4 R\WUser defined threshold for digital signal
in linear
# User analog threshold
Deprecated since version 1.1.0
Offset Name Type Dim R \ W Description
0x00002148  
(8520)User analog threshold
CH 1Float 4 R\WUser defined threshold for analog signal
in linear
0x0000214c  
(8524)User analog threshold
CH 2Float 4 R\WUser defined threshold for analog signal
in linear
0x00002150  
(8528)User analog threshold
CH 3Float 4 R\WUser defined threshold for analog signal
in linear
0x00002154  
(8532)User analog threshold
CH 4Float 4 R\WUser defined threshold for analog signal
in linear
# Pilot tone freq
Deprecated since version 1.1.0
Offset Name Type Dim R \ W Description
0x00002158  
(8536)Pilot tone freq CH 1 Float 4 R\W Pilot tone frequency in Hz
0x0000215c  
(8540)Pilot tone freq CH 2 Float 4 R\W Pilot tone frequency in Hz
0x00002160  
(8544)Pilot tone freq CH 3 Float 4 R\W Pilot tone frequency in Hz
0x00002164  
(8548)Pilot tone freq CH 4 Float 4 R\W Pilot tone frequency in Hz

# Pilot tone high threshold
Deprecated since version 1.1.0
Offset Name Type Dim R \ W Description
0x00002168  
(8552)Pilot tone high threshold CH 1 Float 4 R\W Pilot tone high threshold in Hz
0x0000216c  
(8556)Pilot tone high threshold CH 2 Float 4 R\W Pilot tone high threshold in Hz
0x00002170  
(8560)Pilot tone high threshold CH 3 Float 4 R\W Pilot tone high threshold in Hz
0x00002174  
(8564)Pilot tone high threshold CH 4 Float 4 R\W Pilot tone high threshold in Hz
# Pilot tone low threshold
Deprecated since version 1.1.0
Offset Name Type Dim R \ W Description
0x00002178  
(8568)Pilot tone low threshold CH 1 Float 4 R\W Pilot tone low threshold
0x0000217c  
(8572)Pilot tone low threshold CH 2 Float 4 R\W Pilot tone low threshold
0x00002180  
(8576)Pilot tone low threshold CH 3 Float 4 R\W Pilot tone low threshold
0x00002184  
(8580)Pilot tone low threshold CH 4 Float 4 R\W Pilot tone low threshold
# External trigger
Deprecated since version 1.1.0
Offset Name Type Dim R \ W Description
0x00002188  
(8584)External trigger
CH 1Uint32 4 R\WEnum representing the External trigger to
activate
0x0000218c  
(8588)External trigger
CH 2Uint32 4 R\WEnum representing the External trigger to
activate
0x00002190  
(8592)External trigger
CH 3Uint32 4 R\WEnum representing the External trigger to
activate
0x00002194  
(8596)External trigger
CH 4Uint32 4 R\WEnum representing the External trigger to
activate

# External input
Deprecated since version 1.1.0
Offset Name Type Dim R \ W Description
0x00002198  
(8600)External
input CH
1Uint32 4 R\WEnum representing the GPI input to be used to select
the source. For the GPI Input configuration see
# TODO
0x0000219c  
(8604)External
input CH
2Uint32 4 R\WEnum representing the GPI input to be used to select
the source. For the GPI Input configuration see
# TODO
0x000021a0  
(8608)External
input CH
3Uint32 4 R\WEnum representing the GPI input to be used to select
the source. For the GPI Input configuration see
# TODO
0x000021a4  
(8612)External
input CH
4Uint32 4 R\WEnum representing the GPI input to be used to select
the source. For the GPI Input configuration see
# TODO

# Sources
# BlockId Start Address End Address Description
Source Id CH 1 0x00002200 0x00002204Enum representing the source absolute ids for
the channel 1. Allowd values [-1 -> 31]
Source Id CH 2 0x00002204 0x00002208Enum representing the source absolute ids for
the channel 2. Allowd values [-1 -> 31]
Source Id CH 3 0x00002208 0x0000220cEnum representing the source absolute ids for
the channel 3. Allowd values [-1 -> 31]
Source Id CH 4 0x0000220c 0x00002210Enum representing the source absolute ids for
the channel 4. Allowd values [-1 -> 31]
# Priority Source index
CH 10x00002210 0x00002214Enum representing the source index for the
priority of channel 1 . Allowed values [0 -> 3]
# Priority Source index
CH 20x00002214 0x00002218Enum representing the source index for the
priority of channel 2 . Allowed values [0 -> 3]
# Priority Source index
CH 30x00002218 0x0000221cEnum representing the source index for the
priority of channel 3 . Allowed values [0 -> 3]
# Priority Source index
CH 40x0000221c 0x00002220Enum representing the source index for the
priority of channel 4 . Allowed values [0 -> 3]
Default priority index 0x00002220 0x00002224Enum representing the default priority index of
the selected channel. Allowed values [0 -> 3]
# Manual physical
source selection0x00002224 0x00002228if set to 0 manual source selection is disabled, if
set to -1 channel is muted, otherwise value is
BackupStrategyEnable 0x00002228 0x0000222cif set to 0 backup strategy is disabled, if set to 1
is enabled
# Backup threshold
mode0x0000222c 0x00002230Enum representing the backup threshold mode
to be used. If 0 it is the regular backup strategy .
If 1 is backup strategy with backup threshold.
Backup threshold 0x00002230 0x00002270 Thresholds for signal
PilotT oneEnable 0x00002270 0x00002274if set to 0 pilot tone is disabled, if set to 1 is
enabled
Pilot tone freq 0x00002274 0x00002284 Pilot tone frequency in Hz
# Pilot tone high
threshold0x00002284 0x00002294 Pilot tone high threshold in Hz
# Pilot tone low
threshold0x00002294 0x000022a4 Pilot tone low threshold
Pilot tone GPO enable 0x000022a4 0x000022b4Enable the ability to trigger the GPO in absence
of pilot tone
Source Id CH 1
Enum representing the source absolute ids for the channel 1. Allowd values [-1 -> 31]
Offset Name Type Dim R \ W Description
0x00002200  
(8704)Source 1
Id CH 1Int8 1 R\WEnum representing the source absolute id for the
source 1 of channel 1. Allowd values [-1 -> 31]
0x00002201  
(8705)Source 2
Id CH 1Int8 1 R\WEnum representing the source absolute id for the
source 2 of channel 1. Allowd values [-1 -> 31]
0x00002202  
(8706)Source 3
Id CH 1Int8 1 R\WEnum representing the source absolute id for the
source 3 of channel 1. Allowd values [-1 -> 31]
0x00002203  
(8707)Source 4
Id CH 1Int8 1 R\WEnum representing the source absolute id for the
source 4 of channel 1. Allowd values [-1 -> 31]

Source Id CH 2
Enum representing the source absolute ids for the channel 2. Allowd values [-1 -> 31]
Offset Name Type Dim R \ W Description
0x00002204  
(8708)Source 1
Id CH 2Int8 1 R\WEnum representing the source absolute id for the
source 1 of channel 2. Allowd values [-1 -> 31]
0x00002205  
(8709)Source 2
Id CH 2Int8 1 R\WEnum representing the source absolute id for the
source 2 of channel 2. Allowd values [-1 -> 31]
0x00002206  
(8710)Source 3
Id CH 2Int8 1 R\WEnum representing the source absolute id for the
source 3 of channel 2. Allowd values [-1 -> 31]
0x00002207  
(8711)Source 4
Id CH 2Int8 1 R\WEnum representing the source absolute id for the
source 4 of channel 2. Allowd values [-1 -> 31]
Source Id CH 3
Enum representing the source absolute ids for the channel 3. Allowd values [-1 -> 31]
Offset Name Type Dim R \ W Description
0x00002208  
(8712)Source 1
Id CH 3Int8 1 R\WEnum representing the source absolute id for the
source 1 of channel 3. Allowd values [-1 -> 31]
0x00002209  
(8713)Source 2
Id CH 3Int8 1 R\WEnum representing the source absolute id for the
source 2 of channel 3. Allowd values [-1 -> 31]
0x0000220a  
(8714)Source 3
Id CH 3Int8 1 R\WEnum representing the source absolute id for the
source 3 of channel 3. Allowd values [-1 -> 31]
0x0000220b  
(8715)Source 4
Id CH 3Int8 1 R\WEnum representing the source absolute id for the
source 4 of channel 3. Allowd values [-1 -> 31]
Source Id CH 4
Enum representing the source absolute ids for the channel 4. Allowd values [-1 -> 31]
Offset Name Type Dim R \ W Description
0x0000220c  
(8716)Source 1
Id CH 4Int8 1 R\WEnum representing the source absolute id for the
source 1 of channel 4. Allowd values [-1 -> 31]
0x0000220d  
(8717)Source 2
Id CH 4Int8 1 R\WEnum representing the source absolute id for the
source 2 of channel 4. Allowd values [-1 -> 31]
0x0000220e  
(8718)Source 3
Id CH 4Int8 1 R\WEnum representing the source absolute id for the
source 3 of channel 4. Allowd values [-1 -> 31]
0x0000220f  
(8719)Source 4
Id CH 4Int8 1 R\WEnum representing the source absolute id for the
source 4 of channel 4. Allowd values [-1 -> 31]

Priority Source index CH 1
Enum representing the source index for the priority of channel 1 . Allowed values [0 -> 3]
Offset Name Type Dim R \ W Description
0x00002210  
(8720)Priority 1 source
index CH 1Uint8 1 R\WEnum representing the source index for the
priority 1 of channel 1. Allowed values [0 -> 3]
0x0000221 1 
(8721)Priority 2 source
index CH 1Uint8 1 R\WEnum representing the source index for the
priority 2 of channel 1. Allowed values [0 -> 3]
0x00002212  
(8722)Priority 3 source
index CH 1Uint8 1 R\WEnum representing the source index for the
priority 3 of channel 1. Allowed values [0 -> 3]
0x00002213  
(8723)Priority 4 source
index CH 1Uint8 1 R\WEnum representing the source index for the
priority 4 of channel 1. Allowed values [0 -> 3]
Priority Source index CH 2
Enum representing the source index for the priority of channel 2 . Allowed values [0 -> 3]
Offset Name Type Dim R \ W Description
0x00002214  
(8724)Priority 1 source
index CH 2Uint8 1 R\WEnum representing the source index for the
priority 1 of channel 2. Allowed values [0 -> 3]
0x00002215  
(8725)Priority 2 source
index CH 2Uint8 1 R\WEnum representing the source index for the
priority 2 of channel 2. Allowed values [0 -> 3]
0x00002216  
(8726)Priority 3 source
index CH 2Uint8 1 R\WEnum representing the source index for the
priority 3 of channel 2. Allowed values [0 -> 3]
0x00002217  
(8727)Priority 4 source
index CH 2Uint8 1 R\WEnum representing the source index for the
priority 4 of channel 2. Allowed values [0 -> 3]
Priority Source index CH 3
Enum representing the source index for the priority of channel 3 . Allowed values [0 -> 3]
Offset Name Type Dim R \ W Description
0x00002218  
(8728)Priority 1 source
index CH 3Uint8 1 R\WEnum representing the source index for the
priority 1 of channel 3. Allowed values [0 -> 3]
0x00002219  
(8729)Priority 2 source
index CH 3Uint8 1 R\WEnum representing the source index for the
priority 2 of channel 3. Allowed values [0 -> 3]
0x0000221a  
(8730)Priority 3 source
index CH 3Uint8 1 R\WEnum representing the source index for the
priority 3 of channel 3. Allowed values [0 -> 3]
0x0000221b  
(8731)Priority 4 source
index CH 3Uint8 1 R\WEnum representing the source index for the
priority 4 of channel 3. Allowed values [0 -> 3]

Priority Source index CH 4
Enum representing the source index for the priority of channel 4 . Allowed values [0 -> 3]
Offset Name Type Dim R \ W Description
0x0000221c  
(8732)Priority 1 source
index CH 4Uint8 1 R\WEnum representing the source index for the
priority 1 of channel 4. Allowed values [0 -> 3]
0x0000221d  
(8733)Priority 2 source
index CH 4Uint8 1 R\WEnum representing the source index for the
priority 2 of channel 4. Allowed values [0 -> 3]
0x0000221e  
(8734)Priority 3 source
index CH 4Uint8 1 R\WEnum representing the source index for the
priority 3 of channel 4. Allowed values [0 -> 3]
0x0000221f  
(8735)Priority 4 source
index CH 4Uint8 1 R\WEnum representing the source index for the
priority 4 of channel 4. Allowed values [0 -> 3]
# Default priority index
Enum representing the default priority index of the selected channel. Allowed values [0 -> 3]
Offset Name Type Dim R \ W Description
0x00002220  
(8736)Default priority
index CH 1Uint8 1 R\WEnum representing the default priority index of
channel 1. Allowed values [0 -> 3]
0x00002221  
(8737)Default priority
index CH 2Uint8 1 R\WEnum representing the default priority index of
channel 2. Allowed values [0 -> 3]
0x00002222  
(8738)Default priority
index CH 3Uint8 1 R\WEnum representing the default priority index of
channel 3. Allowed values [0 -> 3]
0x00002223  
(8739)Default priority
index CH 4Uint8 1 R\WEnum representing the default priority index of
channel 4. Allowed values [0 -> 3]
# Manual physical source selection
if set to 0 manual source selection is disabled, if set to -1 channel is muted, otherwise value is
Offset Name Type Dim R \ W Description
0x00002224  
(8740)ManualSourceSelection
CH 1int8 1 R\Wif set to 0 manual source selection is
disabled, if set to -1 channel is muted,
otherwise value is
0x00002225  
(8741)ManualSourceSelection
CH 2int8 1 R\Wif set to 0 manual source selection is
disabled, if set to -1 channel is muted,
otherwise value is
0x00002226  
(8742)ManualSourceSelection
CH 3int8 1 R\Wif set to 0 manual source selection is
disabled, if set to -1 channel is muted,
otherwise value is
0x00002227  
(8743)ManualSourceSelection
CH 4int8 1 R\Wif set to 0 manual source selection is
disabled, if set to -1 channel is muted,
otherwise value is

# BackupStrategyEnable
if set to 0 backup strategy is disabled, if set to 1 is enabled
Offset Name Type Dim R \ W Description
0x00002228  
(8744)BackupStrategyEnable
CH 1uint8 1 R\Wif set to 0 backup strategy is disabled, if
set to 1 is enabled
0x00002229  
(8745)BackupStrategyEnable
CH 2uint8 1 R\Wif set to 0 backup strategy is disabled, if
set to 1 is enabled
0x0000222a  
(8746)BackupStrategyEnable
CH 3uint8 1 R\Wif set to 0 backup strategy is disabled, if
set to 1 is enabled
0x0000222b  
(8747)BackupStrategyEnable
CH 4uint8 1 R\Wif set to 0 backup strategy is disabled, if
set to 1 is enabled
# Backup threshold mode
Enum representing the backup threshold mode to be used. If 0 it is the regular backup strategy . If 1 is backup strategy with backup threshold.
Offset Name Type Dim R \ W Description
0x0000222c  
(8748)Backup
threshold
mode CH 1Uint8 1 R\WEnum representing the backup threshold mode to be
used. If 0 it is the regular backup strategy . If 1 is
backup strategy with backup threshold.
0x0000222d  
(8749)Backup
threshold
mode CH 2Uint8 1 R\WEnum representing the backup threshold mode to be
used. If 0 it is the regular backup strategy . If 1 is
backup strategy with backup threshold.
0x0000222e  
(8750)Backup
threshold
mode CH 3Uint8 1 R\WEnum representing the backup threshold mode to be
used. If 0 it is the regular backup strategy . If 1 is
backup strategy with backup threshold.
0x0000222f  
(8751)Backup
threshold
mode CH 4Uint8 1 R\WEnum representing the backup threshold mode to be
used. If 0 it is the regular backup strategy . If 1 is
backup strategy with backup threshold.
# Backup threshold
# Thresholds for signal
# BlockId Start Address End Address Description
Thresholds CH 1 0x00002230 0x00002240 Thresholds for signal
Thresholds CH 2 0x00002240 0x00002250 Thresholds for signal
Thresholds CH 3 0x00002250 0x00002260 Thresholds for signal
Thresholds CH 4 0x00002260 0x00002270 Thresholds for signal

Thresholds CH 1
# Thresholds for signal
Offset Name Type Dim R \ W Description
0x00002230  
(8752)Threshold CH 1 source selection 1 Float 4 R\W Threshold for signal
0x00002234  
(8756)Threshold CH 1 source selection 2 Float 4 R\W Threshold for signal
0x00002238  
(8760)Threshold CH 1 source selection 3 Float 4 R\W Threshold for signal
0x0000223c  
(8764)Threshold CH 1 source selection 4 Float 4 R\W Threshold for signal
Thresholds CH 2
# Thresholds for signal
Offset Name Type Dim R \ W Description
0x00002240  
(8768)Threshold CH 2 source selection 1 Float 4 R\W Threshold for signal
0x00002244  
(8772)Threshold CH 2 source selection 2 Float 4 R\W Threshold for signal
0x00002248  
(8776)Threshold CH 2 source selection 3 Float 4 R\W Threshold for signal
0x0000224c  
(8780)Threshold CH 2 source selection 4 Float 4 R\W Threshold for signal
Thresholds CH 3
# Thresholds for signal
Offset Name Type Dim R \ W Description
0x00002250  
(8784)Threshold CH 3 source selection 1 Float 4 R\W Threshold for signal
0x00002254  
(8788)Threshold CH 3 source selection 2 Float 4 R\W Threshold for signal
0x00002258  
(8792)Threshold CH 3 source selection 3 Float 4 R\W Threshold for signal
0x0000225c  
(8796)Threshold CH 3 source selection 4 Float 4 R\W Threshold for signal

Thresholds CH 4
# Thresholds for signal
Offset Name Type Dim R \ W Description
0x00002260  
(8800)Threshold CH 4 source selection 1 Float 4 R\W Threshold for signal
0x00002264  
(8804)Threshold CH 4 source selection 2 Float 4 R\W Threshold for signal
0x00002268  
(8808)Threshold CH 4 source selection 3 Float 4 R\W Threshold for signal
0x0000226c  
(8812)Threshold CH 4 source selection 4 Float 4 R\W Threshold for signal
# PilotT oneEnable
if set to 0 pilot tone is disabled, if set to 1 is enabled
Offset Name Type Dim R \ W Description
0x00002270  
(8816)PilotT oneEnable
CH 1uint8 1 R\Wif set to 0 pilot tone is disabled, if set to 1 is
enabled
0x00002271  
(8817)PilotT oneEnable
CH 2uint8 1 R\Wif set to 0 pilot tone is disabled, if set to 1 is
enabled
0x00002272  
(8818)PilotT oneEnable
CH 3uint8 1 R\Wif set to 0 pilot tone is disabled, if set to 1 is
enabled
0x00002273  
(8819)PilotT oneEnable
CH 4uint8 1 R\Wif set to 0 pilot tone is disabled, if set to 1 is
enabled
# Pilot tone freq
# Pilot tone frequency in Hz
Offset Name Type Dim R \ W Description
0x00002274  
(8820)Pilot tone freq CH 1 Float 4 R\W Pilot tone frequency in Hz
0x00002278  
(8824)Pilot tone freq CH 2 Float 4 R\W Pilot tone frequency in Hz
0x0000227c  
(8828)Pilot tone freq CH 3 Float 4 R\W Pilot tone frequency in Hz
0x00002280  
(8832)Pilot tone freq CH 4 Float 4 R\W Pilot tone frequency in Hz

# Pilot tone high threshold
# Pilot tone high threshold in Hz
Offset Name Type Dim R \ W Description
0x00002284  
(8836)Pilot tone high threshold CH 1 Float 4 R\W Pilot tone high threshold in V rms
0x00002288  
(8840)Pilot tone high threshold CH 2 Float 4 R\W Pilot tone high threshold in V rms
0x0000228c  
(8844)Pilot tone high threshold CH 3 Float 4 R\W Pilot tone high threshold in V rms
0x00002290  
(8848)Pilot tone high threshold CH 4 Float 4 R\W Pilot tone high threshold in V rms
# Pilot tone low threshold
# Pilot tone low threshold
Offset Name Type Dim R \ W Description
0x00002294  
(8852)Pilot tone low threshold CH 1 Float 4 R\W Pilot tone low threshold in V rms
0x00002298  
(8856)Pilot tone low threshold CH 2 Float 4 R\W Pilot tone low threshold in V rms
0x0000229c  
(8860)Pilot tone low threshold CH 3 Float 4 R\W Pilot tone low threshold in V rms
0x000022a0  
(8864)Pilot tone low threshold CH 4 Float 4 R\W Pilot tone low threshold in V rms
# Pilot tone GPO enable
# Enable the ability to trigger the GPO in absence of pilot tone
Offset Name Type Dim R \ W Description
0x000022a4  
(8868)Pilot tone
# GPO enable
CH 1Uint32 4 R\WIf none of the sources on channel 1 has a valid
input pilot tone, by setting this field at 1 GPO is
triggered.
0x000022a8  
(8872)Pilot tone
# GPO enable
CH 2Uint32 4 R\WIf none of the sources on channel 2 has a valid
input pilot tone, by setting this field at 1 GPO is
triggered.
0x000022ac  
(8876)Pilot tone
# GPO enable
CH 3Uint32 4 R\WIf none of the sources on channel 3 has a valid
input pilot tone, by setting this field at 1 GPO is
triggered.
0x000022b0  
(8880)Pilot tone
# GPO enable
CH 4Uint32 4 R\WIf none of the sources on channel 4 has a valid
input pilot tone, by setting this field at 1 GPO is
triggered.
Minijack Anti-Pop Configuration
This area contains the configurations related to Minijack Anti-Pop.
# BlockId Start Address End Address Description
Enable 0x00002500 0x00002504 Parameter to enable or disable Minijack Anti-Pop.

# Enable
Parameter to enable or disable Minijack Anti-Pop.
Offset Name Type Dim R \ W Description
0x00002500  
(9472)Enable CH
1Uint8 1 R\WSet to 1 to enable Minijack Anti-Pop, set to 0 to
disable it.
0x00002501  
(9473)Enable CH
2Uint8 1 R\WSet to 1 to enable Minijack Anti-Pop, set to 0 to
disable it.

# Matrix
This area contains informations related to the Matrix.
Offset Name Type Dim R \ W Description
0x00003000  
(12288)Type uint32 4 R\W Represent the matrix type currently in use
0x00003004  
(12292)Source 1 pre
Muteuint8 1 R\W Pre mute to be applied to source 1
0x00003005  
(12293)Source 2 pre
Muteuint8 1 R\W Pre mute to be applied to source 2
0x00003006  
(12294)Source 3 pre
Muteuint8 1 R\W Pre mute to be applied to source 3
0x00003007  
(12295)Source 4 pre
Muteuint8 1 R\W Pre mute to be applied to source 4
0x00003008  
(12296)Source 1 pre
GainFloat 4 R\W Pre Gain to be applied to source 1
0x0000300c  
(12300)Source 2 pre
GainFloat 4 R\W Pre Gain to be applied to source 2
0x00003010  
(12304)Source 3 pre
GainFloat 4 R\W Pre Gain to be applied to source 3
0x00003014  
(12308)Source 4 pre
GainFloat 4 R\W Pre Gain to be applied to source 4
0x00003018  
(12312)Source 1 Gain 1 Float 4 R\WLinear Gain related to output 1 for the Source
1
0x0000301c  
(12316)Source 1 Gain 2 Float 4 R\WLinear Gain related to output 2 for the Source
1
0x00003020  
(12320)Source 1 Gain 3 Float 4 R\WLinear Gain related to output 3 for the Source
1
0x00003024  
(12324)Source 1 Gain 4 Float 4 R\WLinear Gain related to output 4 for the Source
1
0x00003028  
(12328)Source 2 Gain 1 Float 4 R\WLinear Gain related to output 1 for the Source
2
0x0000302c  
(12332)Source 2 Gain 2 Float 4 R\WLinear Gain related to output 2 for the Source
2
0x00003030  
(12336)Source 2 Gain 3 Float 4 R\WLinear Gain related to output 3 for the Source
2
0x00003034  
(12340)Source 2 Gain 4 Float 4 R\WLinear Gain related to output 4 for the Source
2
0x00003038  
(12344)Source 3 Gain 1 Float 4 R\WLinear Gain related to output 1 for the Source
3
0x0000303c  
(12348)Source 3 Gain 2 Float 4 R\WLinear Gain related to output 2 for the Source
3
0x00003040  
(12352)Source 3 Gain 3 Float 4 R\WLinear Gain related to output 3 for the Source
3
0x00003044  
(12356)Source 3 Gain 4 Float 4 R\WLinear Gain related to output 4 for the Source
3
0x00003048  
(12360)Source 4 Gain 1 Float 4 R\WLinear Gain related to output 1 for the Source
4
0x0000304c  
(12364)Source 4 Gain 2 Float 4 R\WLinear Gain related to output 2 for the Source
4
0x00003050  
(12368)Source 4 Gain 3 Float 4 R\WLinear Gain related to output 3 for the Source
4

0x00003054  
(12372)Source 4 Gain 4 Float 4 R\W Linear Gain related to output 4 for the Source
4
0x00003058  
(12376)Source 1 Mute 1 uint8 1 R\W Mute to be applied to source 1
0x00003059  
(12377)Source 1 Mute 2 uint8 1 R\W Mute to be applied to source 2
0x0000305a  
(12378)Source 1 Mute 3 uint8 1 R\W Mute to be applied to source 3
0x0000305b  
(12379)Source 1 Mute 4 uint8 1 R\W Mute to be applied to source 4
0x0000305c  
(12380)Source 2 Mute 1 uint8 1 R\W Mute to be applied to source 1
0x0000305d  
(12381)Source 2 Mute 2 uint8 1 R\W Mute to be applied to source 2
0x0000305e  
(12382)Source 2 Mute 3 uint8 1 R\W Mute to be applied to source 3
0x0000305f  
(12383)Source 2 Mute 4 uint8 1 R\W Mute to be applied to source 4
0x00003060  
(12384)Source 3 Mute 1 uint8 1 R\W Mute to be applied to source 1
0x00003061  
(12385)Source 3 Mute 2 uint8 1 R\W Mute to be applied to source 2
0x00003062  
(12386)Source 3 Mute 3 uint8 1 R\W Mute to be applied to source 3
0x00003063  
(12387)Source 3 Mute 4 uint8 1 R\W Mute to be applied to source 4
0x00003064  
(12388)Source 4 Mute 1 uint8 1 R\W Mute to be applied to source 1
0x00003065  
(12389)Source 4 Mute 2 uint8 1 R\W Mute to be applied to source 2
0x00003066  
(12390)Source 4 Mute 3 uint8 1 R\W Mute to be applied to source 3
0x00003067  
(12391)Source 4 Mute 4 uint8 1 R\W Mute to be applied to source 4
# User
This area contains informations related to the User block.
# BlockId Start Address End Address Description
# User Common
Settings0x00004000 0x00004038This area contains the user block common
settings
User EQ 0x00004100 0x00004280This area contains the user block common
settings

# User Common Settings
# This area contains the user block common settings
# BlockId Start Address End Address Description
User Gain 0x00004000 0x00004010 The user gain in linear
User Delay 0x00004010 0x00004020 The delay shading in seconds
User Polarity 0x00004020 0x00004024 The user polarity
User Mute 0x00004024 0x00004028 The mute shading
User Shading 0x00004028 0x00004038 The user shading
# User Gain
# The user gain in linear
Offset Name Type Dim R \ W Description
0x00004000  
(16384)User Gain 1 Float 4 R\W The user gain in linear CH 1
0x00004004  
(16388)User Gain 2 Float 4 R\W The user gain in linear CH 2
0x00004008  
(16392)User Gain 3 Float 4 R\W The user gain in linear CH 3
0x0000400c  
(16396)User Gain 4 Float 4 R\W The user gain in linear CH 4
# User Delay
# The delay shading in seconds
Offset Name Type Dim R \ W Description
0x00004010  
(16400)User Delay 1 Float 4 R\W The user delay in seconds CH 1
0x00004014  
(16404)User Delay 2 Float 4 R\W The user delay in seconds CH 2
0x00004018  
(16408)User Delay 3 Float 4 R\W The user delay in seconds CH 3
0x0000401c  
(16412)User Delay 4 Float 4 R\W The user delay in seconds CH 4

# User Polarity
# The user polarity
Offset Name Type Dim R \ W Description
0x00004020  
(16416)User Polarity 1 uint8 1 R\W The user polarity CH 1
0x00004021  
(16417)User Polarity 2 uint8 1 R\W The user polarity CH 2
0x00004022  
(16418)User Polarity 3 uint8 1 R\W The user polarity CH 3
0x00004023  
(16419)User Polarity 4 uint8 1 R\W The user polarity CH 4
# User Mute
# The mute shading
Offset Name Type Dim R \ W Description
0x00004024  
(16420)User Mute 1 uint8 1 R\W The user mute CH 1
0x00004025  
(16421)User Mute 2 uint8 1 R\W The user mute CH 2
0x00004026  
(16422)User Mute 3 uint8 1 R\W The user mute CH 3
0x00004027  
(16423)User Mute 4 uint8 1 R\W The user mute CH 4
# User Shading
# The user shading
Offset Name Type Dim R \ W Description
0x00004028  
(16424)User Shading 1 Float 4 R\W The user shading CH 1
0x0000402c  
(16428)User Shading 2 Float 4 R\W The user shading CH 2
0x00004030  
(16432)User Shading 3 Float 4 R\W The user shading CH 3
0x00004034  
(16436)User Shading 4 Float 4 R\W The user shading CH 4
# User EQ
# This area contains the user block common settings
# BlockId Start Address End Address Description
User EQ Channel 1 0x00004100 0x00004160 This area contains the user block EQ settings
User EQ Channel 2 0x00004160 0x000041c0 This area contains the user block EQ settings
User EQ Channel 3 0x000041c0 0x00004220 This area contains the user block EQ settings
User EQ Channel 4 0x00004220 0x00004280 This area contains the user block EQ settings

User EQ Channel 1
# This area contains the user block EQ settings
# BlockId Start Address End Address Description
User Eq Channel 1 BiQuad 1
settings0x00004100 0x000041 18This area contains the user equalizer
biQuad settings.
User Eq Channel 1 BiQuad 2
settings0x000041 18 0x00004130This area contains the user equalizer
biQuad settings.
User Eq Channel 1 BiQuad 3
settings0x00004130 0x00004148This area contains the user equalizer
biQuad settings.
User Eq Channel 1 BiQuad 4
settings0x00004148 0x00004160This area contains the user equalizer
biQuad settings.
User Eq Channel 1 BiQuad 1 settings
This area contains the user equalizer biQuad settings.
Offset Name Type Dim R \ W Description
0x00004100  
(16640)Enabled uint32 4 R\W The enable flag
0x00004104  
(16644)Type uint32 4 R\WThe filter type. V alid values are:  
# Values Type
0 Peaking
11 Low-Shelving
12 High-Shelving
13 Low-pass
14 High-pass
15 BandPass
16 Band-stop
17 All-pass
0x00004108  
(16648)Q Float 4 R\W The filter Q
0x0000410c  
(16652)Slope Float 4 R\W The filter Slope
0x000041 10 
(16656)Frequency uint32 4 R\W The filter frequency
0x000041 14 
(16660)Gain Float 4 R\W The linear gain

User Eq Channel 1 BiQuad 2 settings
This area contains the user equalizer biQuad settings.
Offset Name Type Dim R \ W Description
0x000041 18 
(16664)Enabled uint32 4 R\W The enable flag
0x000041 1c 
(16668)Type uint32 4 R\WThe filter type. V alid values are:  
# Values Type
0 Peaking
11 Low-Shelving
12 High-Shelving
13 Low-pass
14 High-pass
15 BandPass
16 Band-stop
17 All-pass
0x00004120  
(16672)Q Float 4 R\W The filter Q
0x00004124  
(16676)Slope Float 4 R\W The filter Slope
0x00004128  
(16680)Frequency uint32 4 R\W The filter frequency
0x0000412c  
(16684)Gain Float 4 R\W The linear gain
User Eq Channel 1 BiQuad 3 settings
This area contains the user equalizer biQuad settings.
Offset Name Type Dim R \ W Description
0x00004130  
(16688)Enabled uint32 4 R\W The enable flag
0x00004134  
(16692)Type uint32 4 R\WThe filter type. V alid values are:  
# Values Type
0 Peaking
11 Low-Shelving
12 High-Shelving
13 Low-pass
14 High-pass
15 BandPass
16 Band-stop
17 All-pass
0x00004138  
(16696)Q Float 4 R\W The filter Q
0x0000413c  
(16700)Slope Float 4 R\W The filter Slope
0x00004140  
(16704)Frequency uint32 4 R\W The filter frequency
0x00004144  
(16708)Gain Float 4 R\W The linear gain

User Eq Channel 1 BiQuad 4 settings
This area contains the user equalizer biQuad settings.
Offset Name Type Dim R \ W Description
0x00004148  
(16712)Enabled uint32 4 R\W The enable flag
0x0000414c  
(16716)Type uint32 4 R\WThe filter type. V alid values are:  
# Values Type
0 Peaking
11 Low-Shelving
12 High-Shelving
13 Low-pass
14 High-pass
15 BandPass
16 Band-stop
17 All-pass
0x00004150  
(16720)Q Float 4 R\W The filter Q
0x00004154  
(16724)Slope Float 4 R\W The filter Slope
0x00004158  
(16728)Frequency uint32 4 R\W The filter frequency
0x0000415c  
(16732)Gain Float 4 R\W The linear gain
User EQ Channel 2
# This area contains the user block EQ settings
# BlockId Start Address End Address Description
User Eq Channel 2 BiQuad 1
settings0x00004160 0x00004178This area contains the user equalizer
biQuad settings.
User Eq Channel 2 BiQuad 2
settings0x00004178 0x00004190This area contains the user equalizer
biQuad settings.
User Eq Channel 2 BiQuad 3
settings0x00004190 0x000041a8This area contains the user equalizer
biQuad settings.
User Eq Channel 2 BiQuad 4
settings0x000041a8 0x000041c0This area contains the user equalizer
biQuad settings.

User Eq Channel 2 BiQuad 1 settings
This area contains the user equalizer biQuad settings.
Offset Name Type Dim R \ W Description
0x00004160  
(16736)Enabled uint32 4 R\W The enable flag
0x00004164  
(16740)Type uint32 4 R\WThe filter type. V alid values are:  
# Values Type
0 Peaking
11 Low-Shelving
12 High-Shelving
13 Low-pass
14 High-pass
15 BandPass
16 Band-stop
17 All-pass
0x00004168  
(16744)Q Float 4 R\W The filter Q
0x0000416c  
(16748)Slope Float 4 R\W The filter Slope
0x00004170  
(16752)Frequency uint32 4 R\W The filter frequency
0x00004174  
(16756)Gain Float 4 R\W The linear gain
User Eq Channel 2 BiQuad 2 settings
This area contains the user equalizer biQuad settings.
Offset Name Type Dim R \ W Description
0x00004178  
(16760)Enabled uint32 4 R\W The enable flag
0x0000417c  
(16764)Type uint32 4 R\WThe filter type. V alid values are:  
# Values Type
0 Peaking
11 Low-Shelving
12 High-Shelving
13 Low-pass
14 High-pass
15 BandPass
16 Band-stop
17 All-pass
0x00004180  
(16768)Q Float 4 R\W The filter Q
0x00004184  
(16772)Slope Float 4 R\W The filter Slope
0x00004188  
(16776)Frequency uint32 4 R\W The filter frequency
0x0000418c  
(16780)Gain Float 4 R\W The linear gain

User Eq Channel 2 BiQuad 3 settings
This area contains the user equalizer biQuad settings.
Offset Name Type Dim R \ W Description
0x00004190  
(16784)Enabled uint32 4 R\W The enable flag
0x00004194  
(16788)Type uint32 4 R\WThe filter type. V alid values are:  
# Values Type
0 Peaking
11 Low-Shelving
12 High-Shelving
13 Low-pass
14 High-pass
15 BandPass
16 Band-stop
17 All-pass
0x00004198  
(16792)Q Float 4 R\W The filter Q
0x0000419c  
(16796)Slope Float 4 R\W The filter Slope
0x000041a0  
(16800)Frequency uint32 4 R\W The filter frequency
0x000041a4  
(16804)Gain Float 4 R\W The linear gain
User Eq Channel 2 BiQuad 4 settings
This area contains the user equalizer biQuad settings.
Offset Name Type Dim R \ W Description
0x000041a8  
(16808)Enabled uint32 4 R\W The enable flag
0x000041ac  
(16812)Type uint32 4 R\WThe filter type. V alid values are:  
# Values Type
0 Peaking
11 Low-Shelving
12 High-Shelving
13 Low-pass
14 High-pass
15 BandPass
16 Band-stop
17 All-pass
0x000041b0  
(16816)Q Float 4 R\W The filter Q
0x000041b4  
(16820)Slope Float 4 R\W The filter Slope
0x000041b8  
(16824)Frequency uint32 4 R\W The filter frequency
0x000041bc  
(16828)Gain Float 4 R\W The linear gain

User EQ Channel 3
# This area contains the user block EQ settings
# BlockId Start Address End Address Description
User Eq Channel 3 BiQuad 1
settings0x000041c0 0x000041d8This area contains the user equalizer
biQuad settings.
User Eq Channel 3 BiQuad 2
settings0x000041d8 0x000041f0This area contains the user equalizer
biQuad settings.
User Eq Channel 3 BiQuad 3
settings0x000041f0 0x00004208This area contains the user equalizer
biQuad settings.
User Eq Channel 3 BiQuad 4
settings0x00004208 0x00004220This area contains the user equalizer
biQuad settings.
User Eq Channel 3 BiQuad 1 settings
This area contains the user equalizer biQuad settings.
Offset Name Type Dim R \ W Description
0x000041c0  
(16832)Enabled uint32 4 R\W The enable flag
0x000041c4  
(16836)Type uint32 4 R\WThe filter type. V alid values are:  
# Values Type
0 Peaking
11 Low-Shelving
12 High-Shelving
13 Low-pass
14 High-pass
15 BandPass
16 Band-stop
17 All-pass
0x000041c8  
(16840)Q Float 4 R\W The filter Q
0x000041cc  
(16844)Slope Float 4 R\W The filter Slope
0x000041d0  
(16848)Frequency uint32 4 R\W The filter frequency
0x000041d4  
(16852)Gain Float 4 R\W The linear gain

User Eq Channel 3 BiQuad 2 settings
This area contains the user equalizer biQuad settings.
Offset Name Type Dim R \ W Description
0x000041d8  
(16856)Enabled uint32 4 R\W The enable flag
0x000041dc  
(16860)Type uint32 4 R\WThe filter type. V alid values are:  
# Values Type
0 Peaking
11 Low-Shelving
12 High-Shelving
13 Low-pass
14 High-pass
15 BandPass
16 Band-stop
17 All-pass
0x000041e0  
(16864)Q Float 4 R\W The filter Q
0x000041e4  
(16868)Slope Float 4 R\W The filter Slope
0x000041e8  
(16872)Frequency uint32 4 R\W The filter frequency
0x000041ec  
(16876)Gain Float 4 R\W The linear gain
User Eq Channel 3 BiQuad 3 settings
This area contains the user equalizer biQuad settings.
Offset Name Type Dim R \ W Description
0x000041f0  
(16880)Enabled uint32 4 R\W The enable flag
0x000041f4  
(16884)Type uint32 4 R\WThe filter type. V alid values are:  
# Values Type
0 Peaking
11 Low-Shelving
12 High-Shelving
13 Low-pass
14 High-pass
15 BandPass
16 Band-stop
17 All-pass
0x000041f8  
(16888)Q Float 4 R\W The filter Q
0x000041fc  
(16892)Slope Float 4 R\W The filter Slope
0x00004200  
(16896)Frequency uint32 4 R\W The filter frequency
0x00004204  
(16900)Gain Float 4 R\W The linear gain

User Eq Channel 3 BiQuad 4 settings
This area contains the user equalizer biQuad settings.
Offset Name Type Dim R \ W Description
0x00004208  
(16904)Enabled uint32 4 R\W The enable flag
0x0000420c  
(16908)Type uint32 4 R\WThe filter type. V alid values are:  
# Values Type
0 Peaking
11 Low-Shelving
12 High-Shelving
13 Low-pass
14 High-pass
15 BandPass
16 Band-stop
17 All-pass
0x00004210  
(16912)Q Float 4 R\W The filter Q
0x00004214  
(16916)Slope Float 4 R\W The filter Slope
0x00004218  
(16920)Frequency uint32 4 R\W The filter frequency
0x0000421c  
(16924)Gain Float 4 R\W The linear gain
User EQ Channel 4
# This area contains the user block EQ settings
# BlockId Start Address End Address Description
User Eq Channel 4 BiQuad 1
settings0x00004220 0x00004238This area contains the user equalizer
biQuad settings.
User Eq Channel 4 BiQuad 2
settings0x00004238 0x00004250This area contains the user equalizer
biQuad settings.
User Eq Channel 4 BiQuad 3
settings0x00004250 0x00004268This area contains the user equalizer
biQuad settings.
User Eq Channel 4 BiQuad 4
settings0x00004268 0x00004280This area contains the user equalizer
biQuad settings.

User Eq Channel 4 BiQuad 1 settings
This area contains the user equalizer biQuad settings.
Offset Name Type Dim R \ W Description
0x00004220  
(16928)Enabled uint32 4 R\W The enable flag
0x00004224  
(16932)Type uint32 4 R\WThe filter type. V alid values are:  
# Values Type
0 Peaking
11 Low-Shelving
12 High-Shelving
13 Low-pass
14 High-pass
15 BandPass
16 Band-stop
17 All-pass
0x00004228  
(16936)Q Float 4 R\W The filter Q
0x0000422c  
(16940)Slope Float 4 R\W The filter Slope
0x00004230  
(16944)Frequency uint32 4 R\W The filter frequency
0x00004234  
(16948)Gain Float 4 R\W The linear gain
User Eq Channel 4 BiQuad 2 settings
This area contains the user equalizer biQuad settings.
Offset Name Type Dim R \ W Description
0x00004238  
(16952)Enabled uint32 4 R\W The enable flag
0x0000423c  
(16956)Type uint32 4 R\WThe filter type. V alid values are:  
# Values Type
0 Peaking
11 Low-Shelving
12 High-Shelving
13 Low-pass
14 High-pass
15 BandPass
16 Band-stop
17 All-pass
0x00004240  
(16960)Q Float 4 R\W The filter Q
0x00004244  
(16964)Slope Float 4 R\W The filter Slope
0x00004248  
(16968)Frequency uint32 4 R\W The filter frequency
0x0000424c  
(16972)Gain Float 4 R\W The linear gain

User Eq Channel 4 BiQuad 3 settings
This area contains the user equalizer biQuad settings.
Offset Name Type Dim R \ W Description
0x00004250  
(16976)Enabled uint32 4 R\W The enable flag
0x00004254  
(16980)Type uint32 4 R\WThe filter type. V alid values are:  
# Values Type
0 Peaking
11 Low-Shelving
12 High-Shelving
13 Low-pass
14 High-pass
15 BandPass
16 Band-stop
17 All-pass
0x00004258  
(16984)Q Float 4 R\W The filter Q
0x0000425c  
(16988)Slope Float 4 R\W The filter Slope
0x00004260  
(16992)Frequency uint32 4 R\W The filter frequency
0x00004264  
(16996)Gain Float 4 R\W The linear gain
User Eq Channel 4 BiQuad 4 settings
This area contains the user equalizer biQuad settings.
Offset Name Type Dim R \ W Description
0x00004268  
(17000)Enabled uint32 4 R\W The enable flag
0x0000426c  
(17004)Type uint32 4 R\WThe filter type. V alid values are:  
# Values Type
0 Peaking
11 Low-Shelving
12 High-Shelving
13 Low-pass
14 High-pass
15 BandPass
16 Band-stop
17 All-pass
0x00004270  
(17008)Q Float 4 R\W The filter Q
0x00004274  
(17012)Slope Float 4 R\W The filter Slope
0x00004278  
(17016)Frequency uint32 4 R\W The filter frequency
0x0000427c  
(17020)Gain Float 4 R\W The linear gain

# Speaker Layout
This area contains informations related to the output routing.
# BlockId Start Address End Address Description
# Routing
Configuration0x00005000 0x00005004This area contains informations related to the
output routing.
Speaker Settings 0x00005004 0x000062f4This area contains informations related to the
output routing.
# Routing Configuration
This area contains informations related to the output routing.
Offset Name Type Dim R \ W Description
0x00005000  
(20480)Routing uint8[4] 4 R\Wbyte[4] [0,1,2,3] -> means 4 dif ferent speakers (66051
uint)
# Speaker Settings
This area contains informations related to the output routing.
# BlockId Start Address End Address Description
Speaker Description 0x00005004 0x00005644 Speaker Description
Brand Name 0x00005644 0x000057d4 Brand name
Family Name 0x000057d4 0x00005964 Family Name
Model Name 0x00005964 0x00005af4 Model Name
Application Name 0x00005af4 0x00005c84 Application Name
Speaker Note 0x00005c84 0x000062c4 Speaker Note
Speaker T ype 0x000062c4 0x000062d4 Speaker T ype
Preset T ype 0x000062d4 0x000062e4 Preset T ype
Is HiZ Active 0x000062e4 0x000062f4 Is HiZ Active
# Speaker Description
# Speaker Description
Offset Name Type Dim R \ W Description
0x00005004  
(20484)Speaker Description
Speaker 1char[400] 400 R\WSpeaker Description for
speaker 1
0x00005194  
(20884)Speaker Description
Speaker 2char[400] 400 R\WSpeaker Description for
speaker 2
0x00005324  
(21284)Speaker Description
Speaker 3char[400] 400 R\WSpeaker Description for
speaker 3
0x000054b4  
(21684)Speaker Description
Speaker 4char[400] 400 R\WSpeaker Description for
speaker 4

# Brand Name
# Brand name
Offset Name Type Dim R \ W Description
0x00005644  
(22084)Brand Name Speaker 1 char[100] 100 R\W Brand name for speaker 1
0x000056a8  
(22184)Brand Name Speaker 2 char[100] 100 R\W Brand name for speaker 2
0x0000570c  
(22284)Brand Name Speaker 3 char[100] 100 R\W Brand name for speaker 3
0x00005770  
(22384)Brand Name Speaker 4 char[100] 100 R\W Brand name for speaker 4
# Family Name
# Family Name
Offset Name Type Dim R \ W Description
0x000057d4  
(22484)Family Name Speaker 1 char[100] 100 R\W Family name for speaker 1
0x00005838  
(22584)Family Name Speaker 2 char[100] 100 R\W Family name for speaker 2
0x0000589c  
(22684)Family Name Speaker 3 char[100] 100 R\W Family name for speaker 3
0x00005900  
(22784)Family Name Speaker 4 char[100] 100 R\W Family name for speaker 4
# Model Name
# Model Name
Offset Name Type Dim R \ W Description
0x00005964  
(22884)Model Name Speaker 1 char[100] 100 R\W Model Name for speaker 1
0x000059c8  
(22984)Model Name Speaker 2 char[100] 100 R\W Model Name for speaker 2
0x00005a2c  
(23084)Model Name Speaker 3 char[100] 100 R\W Model Name for speaker 3
0x00005a90  
(23184)Model Name Speaker 4 char[100] 100 R\W Model Name for speaker 4

# Application Name
# Application Name
Offset Name Type Dim R \ W Description
0x00005af4  
(23284)Application Name Speaker
1char[100] 100 R\WApplication Name for speaker
1
0x00005b58  
(23384)Application Name Speaker
2char[100] 100 R\WApplication Name for speaker
2
0x00005bbc  
(23484)Application Name Speaker
3char[100] 100 R\WApplication Name for speaker
3
0x00005c20  
(23584)Application Name Speaker
4char[100] 100 R\WApplication Name for speaker
4
# Speaker Note
# Speaker Note
Offset Name Type Dim R \ W Description
0x00005c84  
(23684)Speaker Note Speaker 1 char[400] 400 R\W Speaker Note for speaker 1
0x00005e14  
(24084)Speaker Note Speaker 2 char[400] 400 R\W Speaker Note for speaker 2
0x00005fa4  
(24484)Speaker Note Speaker 3 char[400] 400 R\W Speaker Note for speaker 3
0x00006134  
(24884)Speaker Note Speaker 4 char[400] 400 R\W Speaker Note for speaker 4
# Speaker T ype
# Speaker T ype
Offset Name Type Dim R \ W Description
0x000062c4  
(25284)Speaker T ype Speaker 1 int32 4 R\W Speaker T ype for speaker 1
0x000062c8  
(25288)Speaker T ype Speaker 2 int32 4 R\W Speaker T ype for speaker 2
0x000062cc  
(25292)Speaker T ype Speaker 3 int32 4 R\W Speaker T ype for speaker 3
0x000062d0  
(25296)Speaker T ype Speaker 4 int32 4 R\W Speaker T ype for speaker 4

# Preset T ype
# Preset T ype
Offset Name Type Dim R \ W Description
0x000062d4  
(25300)Preset T ype Speaker 1 int32 4 R\W Preset T ype for speaker 1
0x000062d8  
(25304)Preset T ype Speaker 2 int32 4 R\W Preset T ype for speaker 2
0x000062dc  
(25308)Preset T ype Speaker 3 int32 4 R\W Preset T ype for speaker 3
0x000062e0  
(25312)Preset T ype Speaker 4 int32 4 R\W Preset T ype for speaker 4
# Is HiZ Active
# Is HiZ Active
Offset Name Type Dim R \ W Description
0x000062e4  
(25316)Is HiZ Active Speaker 1 uint32 4 R\W Is HiZ Active for speaker 1
0x000062e8  
(25320)Is HiZ Active Speaker 2 uint32 4 R\W Is HiZ Active for speaker 2
0x000062ec  
(25324)Is HiZ Active Speaker 3 uint32 4 R\W Is HiZ Active for speaker 3
0x000062f0  
(25328)Is HiZ Active Speaker 4 uint32 4 R\W Is HiZ Active for speaker 4
# Ways
This area contains informations related to the amplifiers ways.
# BlockId Start Address End Address Description
Way Common settings 0x00007000 0x000070a0 This area contains the way common settings.
Diagnostic 0x00007890 0x00007940 Ways Diagnostic area
Auto Setup Apply 0x00007940 0x00007950 Ways autosetup applied parameters area
# Way Common settings
This area contains the way common settings.
# BlockId Start Address End Address Description
# Is
Autosetupable0x00007000 0x00007010This is the out autsetup capable of way - 1 if
Autosetupable - else 0
Way gain 0x00007010 0x00007020 The way gain in linear
Way delay 0x00007020 0x00007030 The way delay in seconds
Way polarity 0x00007030 0x00007040 The way polarity
Way mute 0x00007040 0x00007050 The way mute
Way Name 0x00007050 0x00007090 Way Name
Way State 0x00007090 0x000070a0 Way State

# Is Autosetupable
This is the out autsetup capable of way - 1 if Autosetupable - else 0
Offset Name Type Dim R \ W Description
0x00007000  
(28672)Way 1 Is
Autosetupableuint32 4 R\WThis is the out autsetup capable of way - 1 if
Autosetupable - else 0
0x00007004  
(28676)Way 2 Is
Autosetupableuint32 4 R\WThis is the out autsetup capable of way - 1 if
Autosetupable - else 0
0x00007008  
(28680)Way 3 Is
Autosetupableuint32 4 R\WThis is the out autsetup capable of way - 1 if
Autosetupable - else 0
0x0000700c  
(28684)Way 4 Is
Autosetupableuint32 4 R\WThis is the out autsetup capable of way - 1 if
Autosetupable - else 0
# Way gain
# The way gain in linear
Offset Name Type Dim R \ W Description
0x00007010  
(28688)Way 1 gain Float 4 R\W The way gain in linear
0x00007014  
(28692)Way 2 gain Float 4 R\W The way gain in linear
0x00007018  
(28696)Way 3 gain Float 4 R\W The way gain in linear
0x0000701c  
(28700)Way 4 gain Float 4 R\W The way gain in linear
# Way delay
# The way delay in seconds
Offset Name Type Dim R \ W Description
0x00007020  
(28704)Way 1 delay Float 4 R\W The way delay in seconds
0x00007024  
(28708)Way 2 delay Float 4 R\W The way delay in seconds
0x00007028  
(28712)Way 3 delay Float 4 R\W The way delay in seconds
0x0000702c  
(28716)Way 4 delay Float 4 R\W The way delay in seconds

# Way polarity
# The way polarity
Offset Name Type Dim R \ W Description
0x00007030  
(28720)Way 1 polarity uint32 4 R\W The way polarity
0x00007034  
(28724)Way 2 polarity uint32 4 R\W The way polarity
0x00007038  
(28728)Way 3 polarity uint32 4 R\W The way polarity
0x0000703c  
(28732)Way 4 polarity uint32 4 R\W The way polarity
# Way mute
# The way mute
Offset Name Type Dim R \ W Description
0x00007040  
(28736)Way 1 mute uint32 4 R\W The way mute
0x00007044  
(28740)Way 2 mute uint32 4 R\W The way mute
0x00007048  
(28744)Way 3 mute uint32 4 R\W The way mute
0x0000704c  
(28748)Way 4 mute uint32 4 R\W The way mute
# Way Name
# Way Name
Offset Name Type Dim R \ W Description
0x00007050  
(28752)Way Name W ay 1 char[16] 16 R\W Way Name for way 1
0x00007060  
(28768)Way Name W ay 2 char[16] 16 R\W Way Name for way 2
0x00007070  
(28784)Way Name W ay 3 char[16] 16 R\W Way Name for way 3
0x00007080  
(28800)Way Name W ay 4 char[16] 16 R\W Way Name for way 4

# Way State
# Way State
Offset Name Type Dim R \ W Description
0x00007090  
(28816)Way State W ay 1 uint32 4 R\W Way State for way 1
0x00007094  
(28820)Way State W ay 2 uint32 4 R\W Way State for way 2
0x00007098  
(28824)Way State W ay 3 uint32 4 R\W Way State for way 3
0x0000709c  
(28828)Way State W ay 4 uint32 4 R\W Way State for way 4
# Diagnostic
# Ways Diagnostic area
# BlockId Start Address End Address Description
Diagnostic Pilot T one Generator 0x00007890 0x000078b4 Pilot T one Generator area
Diagnostic Pilot T one 0x000078b4 0x000078e8 Pilot T one area
Diagnostic Load Monitor 0x000078e8 0x0000791c Load Monitor area
# Diagnostic Pilot T one Generator
# Pilot T one Generator area
# BlockId Start Address End Address Description
Way Pilot T one Generator Enable 0x00007890 0x00007894Pilot T one Generator Enable for
way
# Way Pilot T one Generator
Frequency0x00007894 0x000078a4Pilot T one Generator Frequency for
way
# Way Pilot T one Generator
Amplitude0x000078a4 0x000078b4Pilot T one Generator Amplitude for
way
# Way Pilot T one Generator Enable
# Pilot T one Generator Enable for way
Offset Name Type Dim R \ W Description
0x00007890  
(30864)Way 1 Pilot T one Generator
Enableuint8 1 R\WPilot T one Generator Enable for
way 1
0x00007891  
(30865)Way 2 Pilot T one Generator
Enableuint8 1 R\WPilot T one Generator Enable for
way 2
0x00007892  
(30866)Way 3 Pilot T one Generator
Enableuint8 1 R\WPilot T one Generator Enable for
way 3
0x00007893  
(30867)Way 4 Pilot T one Generator
Enableuint8 1 R\WPilot T one Generator Enable for
way 4

# Way Pilot T one Generator Frequency
# Pilot T one Generator Frequency for way
Offset Name Type Dim R \ W Description
0x00007894  
(30868)Way 1 Pilot T one
# Generator
FrequencyFloat 4 R\WPilot T one Generator Frequency for way 1.
# Frequency may be rounded to closest integer
in order to enhance performances.
0x00007898  
(30872)Way 2 Pilot T one
# Generator
FrequencyFloat 4 R\WPilot T one Generator Frequency for way 2.
# Frequency may be rounded to closest integer
in order to enhance performances.
0x0000789c  
(30876)Way 3 Pilot T one
# Generator
FrequencyFloat 4 R\WPilot T one Generator Frequency for way 3.
# Frequency may be rounded to closest integer
in order to enhance performances.
0x000078a0  
(30880)Way 4 Pilot T one
# Generator
FrequencyFloat 4 R\WPilot T one Generator Frequency for way 4.
# Frequency may be rounded to closest integer
in order to enhance performances.
# Way Pilot T one Generator Amplitude
# Pilot T one Generator Amplitude for way
Offset Name Type Dim R \ W Description
0x000078a4  
(30884)Way 1 Pilot T one Generator
AmplitudeFloat 4 R\WPilot T one Generator Amplitude
for way 1
0x000078a8  
(30888)Way 2 Pilot T one Generator
AmplitudeFloat 4 R\WPilot T one Generator Amplitude
for way 2
0x000078ac  
(30892)Way 3 Pilot T one Generator
AmplitudeFloat 4 R\WPilot T one Generator Amplitude
for way 3
0x000078b0  
(30896)Way 4 Pilot T one Generator
AmplitudeFloat 4 R\WPilot T one Generator Amplitude
for way 4
# Diagnostic Pilot T one
# Pilot T one area
# BlockId Start Address End Address Description
Way Pilot T one Enable 0x000078b4 0x000078b8 Pilot T one area
Way Pilot T one Frequency 0x000078b8 0x000078c8 Pilot T one Frequency for way
Way Pilot T one Lowth 0x000078c8 0x000078d8 Pilot T one Lowth for way
Way Pilot T one Highth 0x000078d8 0x000078e8 Pilot T one Highth for way

# Way Pilot T one Enable
# Pilot T one area
Offset Name Type Dim R \ W Description
0x000078b4  
(30900)Way 1 Pilot T one Enable uint8 1 R\W Pilot T one Enable for way 1
0x000078b5  
(30901)Way 2 Pilot T one Enable uint8 1 R\W Pilot T one Enable for way 2
0x000078b6  
(30902)Way 3 Pilot T one Enable uint8 1 R\W Pilot T one Enable for way 3
0x000078b7  
(30903)Way 4 Pilot T one Enable uint8 1 R\W Pilot T one Enable for way 4
# Way Pilot T one Frequency
# Pilot T one Frequency for way
Offset Name Type Dim R \ W Description
0x000078b8  
(30904)Way 1 Pilot
# Tone
FrequencyFloat 4 R\WPilot T one Frequency for way 1. Frequency may
be rounded to closest integer in order to enhance
performances.
0x000078bc  
(30908)Way 2 Pilot
# Tone
FrequencyFloat 4 R\WPilot T one Frequency for way 2. Frequency may
be rounded to closest integer in order to enhance
performances.
0x000078c0  
(30912)Way 3 Pilot
# Tone
FrequencyFloat 4 R\WPilot T one Frequency for way 3. Frequency may
be rounded to closest integer in order to enhance
performances.
0x000078c4  
(30916)Way 4 Pilot
# Tone
FrequencyFloat 4 R\WPilot T one Frequency for way 4. Frequency may
be rounded to closest integer in order to enhance
performances.
# Way Pilot T one Lowth
# Pilot T one Lowth for way
Offset Name Type Dim R \ W Description
0x000078c8  
(30920)Way 1 Pilot T one Lowth Float 4 R\W Pilot T one Lowth for way 1
0x000078cc  
(30924)Way 2 Pilot T one Lowth Float 4 R\W Pilot T one Lowth for way 2
0x000078d0  
(30928)Way 3 Pilot T one Lowth Float 4 R\W Pilot T one Lowth for way 3
0x000078d4  
(30932)Way 4 Pilot T one Lowth Float 4 R\W Pilot T one Lowth for way 4

# Way Pilot T one Highth
# Pilot T one Highth for way
Offset Name Type Dim R \ W Description
0x000078d8  
(30936)Way 1 Pilot T one Highth Float 4 R\W Pilot T one Highth for way 1
0x000078dc  
(30940)Way 2 Pilot T one Highth Float 4 R\W Pilot T one Highth for way 2
0x000078e0  
(30944)Way 3 Pilot T one Highth Float 4 R\W Pilot T one Highth for way 3
0x000078e4  
(30948)Way 4 Pilot T one Highth Float 4 R\W Pilot T one Highth for way 4
# Diagnostic Load Monitor
# Load Monitor area
# BlockId Start Address End Address Description
Way Load Monitor Enable 0x000078e8 0x000078ec Load Monitor Enable for way
Way Load Monitor Frequency 0x000078ec 0x000078fc Load Monitor Frequency for way
Way Load Monitor Lowth 0x000078fc 0x0000790c Load Monitor Lowth for way
Way Load Monitor Highth 0x0000790c 0x0000791c Load Monitor Highth for way
# Way Load Monitor Enable
# Load Monitor Enable for way
Offset Name Type Dim R \ W Description
0x000078e8  
(30952)Way Load Monitor Enable W ay 1 uint8 1 R\W Load Monitor Enable for way 1
0x000078e9  
(30953)Way Load Monitor Enable W ay 2 uint8 1 R\W Load Monitor Enable for way 2
0x000078ea  
(30954)Way Load Monitor Enable W ay 3 uint8 1 R\W Load Monitor Enable for way 3
0x000078eb  
(30955)Way Load Monitor Enable W ay 4 uint8 1 R\W Load Monitor Enable for way 4

# Way Load Monitor Frequency
# Load Monitor Frequency for way
Offset Name Type Dim R \ W Description
0x000078ec  
(30956)Way Load
# Monitor
# Frequency W ay
1Float 4 R\WLoad Monitor Frequency for way 1. Frequency
may be rounded to closest integer in order to
enhance performances.
0x000078f0  
(30960)Way Load
# Monitor
# Frequency W ay
2Float 4 R\WLoad Monitor Frequency for way 2. Frequency
may be rounded to closest integer in order to
enhance performances.
0x000078f4  
(30964)Way Load
# Monitor
# Frequency W ay
3Float 4 R\WLoad Monitor Frequency for way 3. Frequency
may be rounded to closest integer in order to
enhance performances.
0x000078f8  
(30968)Way Load
# Monitor
# Frequency W ay
4Float 4 R\WLoad Monitor Frequency for way 4. Frequency
may be rounded to closest integer in order to
enhance performances.
# Way Load Monitor Lowth
# Load Monitor Lowth for way
Offset Name Type Dim R \ W Description
0x000078fc  
(30972)Way Load Monitor Lowth W ay 1 Float 4 R\W Load Monitor Lowth for way 1
0x00007900  
(30976)Way Load Monitor Lowth W ay 2 Float 4 R\W Load Monitor Lowth for way 2
0x00007904  
(30980)Way Load Monitor Lowth W ay 3 Float 4 R\W Load Monitor Lowth for way 3
0x00007908  
(30984)Way Load Monitor Lowth W ay 4 Float 4 R\W Load Monitor Lowth for way 4
# Way Load Monitor Highth
# Load Monitor Highth for way
Offset Name Type Dim R \ W Description
0x0000790c  
(30988)Way Load Monitor Highth W ay 1 Float 4 R\W Load Monitor Highth for way 1
0x00007910  
(30992)Way Load Monitor Highth W ay 2 Float 4 R\W Load Monitor Highth for way 2
0x00007914  
(30996)Way Load Monitor Highth W ay 3 Float 4 R\W Load Monitor Highth for way 3
0x00007918  
(31000)Way Load Monitor Highth W ay 4 Float 4 R\W Load Monitor Highth for way 4

# Auto Setup Apply
# Ways autosetup applied parameters area
# BlockId Start Address End Address Description
Gain 0x00007940 0x00007950 The gain
# Gain
# The gain
Offset Name Type Dim R \ W Description
0x00007940  
(31040)AutoSetup Gain W ay 1 float 4 R AutoSetup Gain for way 1
0x00007944  
(31044)AutoSetup Gain W ay 2 float 4 R AutoSetup Gain for way 2
0x00007948  
(31048)AutoSetup Gain W ay 3 float 4 R AutoSetup Gain for way 3
0x0000794c  
(31052)AutoSetup Gain W ay 4 float 4 R AutoSetup Gain for way 4
# Dante routing
This area contains informations related to Dante Routing.
# BlockId Start Address End Address Description
Gain 0x00008500 0x00008510 Dante route gain for output
DspT apType 0x00008510 0x00008514 Dante route dsp tap type for output
Channel 0x00008514 0x00008518 Dante route channel for output
# Gain
# Dante route gain for output
Offset Name Type Dim R \ W Description
0x00008500  
(34048)Out 1 Dante Route Gain float 4 R\W Dante route gain for output 1
0x00008504  
(34052)Out 2 Dante Route Gain float 4 R\W Dante route gain for output 2
0x00008508  
(34056)Out 3 Dante Route Gain float 4 R\W Dante route gain for output 3
0x0000850c  
(34060)Out 4 Dante Route Gain float 4 R\W Dante route gain for output 4

# DspT apType
# Dante route dsp tap type for output
Offset Name Type Dim R \ W Description
0x00008510  
(34064)Out 1 Dante Route
DspT apTypeuint8 1 R\WDante route dsp tap type for
output 1
0x0000851 1 
(34065)Out 2 Dante Route
DspT apTypeuint8 1 R\WDante route dsp tap type for
output 2
0x00008512  
(34066)Out 3 Dante Route
DspT apTypeuint8 1 R\WDante route dsp tap type for
output 3
0x00008513  
(34067)Out 4 Dante Route
DspT apTypeuint8 1 R\WDante route dsp tap type for
output 4
# Channel
# Dante route channel for output
Offset Name Type Dim R \ W Description
0x00008514  
(34068)Out 1 Dante Route Channel uint8 1 R\W Dante route channel for output 1
0x00008515  
(34069)Out 2 Dante Route Channel uint8 1 R\W Dante route channel for output 2
0x00008516  
(34070)Out 3 Dante Route Channel uint8 1 R\W Dante route channel for output 3
0x00008517  
(34071)Out 4 Dante Route Channel uint8 1 R\W Dante route channel for output 4
# GPI configuration
This area contains informations related to GPI.
# BlockId Start Address End Address Description
Mode 0x00009000 0x00009004 Mode configuration for GPI

# Mode
# Mode configuration for GPI
Offset Name Type Dim R \ W Description
0x00009000  
(36864)GPI 1
Modeuint8 1 R\WDescribes the configuration of GPI.  
# Code Mode
00Gain : the GPI is used to
control the relative channel
gain.
01Other : the GPI is used to
control another function.
0x00009001  
(36865)GPI 2
Modeuint8 1 R\WDescribes the configuration of GPI.  
# Code Mode
00Gain : the GPI is used to
control the relative channel
gain.
01Other : the GPI is used to
control another function.
0x00009002  
(36866)GPI 3
Modeuint8 1 R\WDescribes the configuration of GPI.  
# Code Mode
00Gain : the GPI is used to
control the relative channel
gain.
01Other : the GPI is used to
control another function.
0x00009003  
(36867)GPI 4
Modeuint8 1 R\WDescribes the configuration of GPI.  
# Code Mode
00Gain : the GPI is used to
control the relative channel
gain.
01Other : the GPI is used to
control another function.
# GPO configuration
This area contains informations related to GPO.
# BlockId Start Address End Address Description
Relay 0x00009e00 0x00009e0c Configuration for Relay

# Relay
# Configuration for Relay
Offset Name Type Dim R \ W Description
0x00009e00  
(40448)Relay
modeuint32 4 R\WDescribes the configuration of relay . 
 
# Code Mode
00Automatic : open relay when
faults indicated by fault
masks happens.
01Manual : set and clear relay
from protocol depending on
Relay State field.
0x00009e08  
(40456)Relay
# Set
Stateuint32 4 R\WIf Relay Mode is Manual set 0 to open Relay , set 1 to
close it.
# Power config
This area contains informations related to Standby and Power Configuration.
# BlockId Start Address End Address Description
Standby 0x0000a000 0x0000a00c Amplifier standby commands
# Standby
# Amplifier standby commands
Offset Name Type Dim R \ W Description
0x0000a000  
(40960)Standby
triggeruint32 4 WIf set to '1' activates the standby if set to '0'
deactivates it
0x0000a004  
(40964)Auto turn on
enableuint32 4 R\W
0x0000a008  
(40968)Auto Power
# Down
Enableuint32 4 R\WIf set to '1' activates the automatic standby ,
entering in standby state after 25 minutes without
input signal.  
if set to '0' the amplifier will not enter in automatic
standby .
# Readings
This area contains informations related to amplifier readings like meters.
# BlockId Start Address End Address Description
Slow Meters 0x0000b000 0x0000b710 This area contains the slow meters.
Fast Meters 0x0000b800 0x0000bbd0 This area contains the fast meters.

# Slow Meters
This area contains the slow meters.
# BlockId Start Address End Address Description
SlowMeter Ali 0x0000b000 0x0000b020 This area contains the Ali slow meters.
SlowMeter Ampli Channels 0x0000b0f4 0x0000b104 This area contains the Ampli slow meters.
SlowMeter SourceSelection 0x0000b300 0x0000b360This area contains the SourceSelection
slow meters.
SlowMeter W ays 0x0000b478 0x0000b4d8 This area contains the W ays slow meters.
SlowMeter PreW ays 0x0000b5e8 0x0000b608This area contains the PreW ays slow
meters.
SlowMeter Standby State 0x0000b638 0x0000b63cThis area contains the Standby State slow
meters.
# SlowMeter
ChannelAlarmStatuses0x0000b63c 0x0000b650This area contains the
ChannelAlarmStatuses slow meters.
SlowMeter AlarmStatus 0x0000b650 0x0000b65cThis area contains the AlarmStatus slow
meters.
SlowMeter MuteCodes 0x0000b700 0x0000b710This area contains the mute codes slow
meters.
# SlowMeter Ali
This area contains the Ali slow meters.
Offset Name Type Dim R \ W Description
0x0000b000  
(45056)TempT rasf Float 4 R Reads the T empT rasf
0x0000b004  
(45060)TempHeatSink Float 4 R Reads the T empHeatSink
0x0000b008  
(45064)VMainsRms Float 4 R Reads the VMainsRms
0x0000b00c  
(45068)VccP Float 4 R Reads the VccP
0x0000b010  
(45072)VccN Float 4 R Reads the VccN
0x0000b014  
(45076)FanCurrent Float 4 R Reads the FanCurrent
0x0000b018  
(45080)VAuxP Float 4 R Reads the V AuxP
0x0000b01c  
(45084)VAuxN Float 4 R Reads the V AuxN
# SlowMeter Ampli Channels
This area contains the Ampli slow meters.
# BlockId Start Address End Address Description
SlowMeter Ampli 0x0000b0f4 0x0000b104 This area contains the Ampli slow meters.

# SlowMeter Ampli
This area contains the Ampli slow meters.
Offset Name Type Dim R \ W Description
0x0000b0f4  
(45300)TempCh 1 Float 4 R Reads the T empCh
0x0000b0f8  
(45304)TempCh 2 Float 4 R Reads the T empCh
0x0000b0fc  
(45308)TempCh 3 Float 4 R Reads the T empCh
0x0000b100  
(45312)TempCh 4 Float 4 R Reads the T empCh
# SlowMeter SourceSelection
This area contains the SourceSelection slow meters.
# BlockId Start Address End Address Description
# PilotT oneDetectActual CH
10x0000b310 0x0000b320Reads the detected rms value of pilot T one
on CH 1
# PilotT oneDetectActual CH
20x0000b320 0x0000b330Reads the detected rms value of pilot T one
on CH 2
# PilotT oneDetectActual CH
30x0000b330 0x0000b340Reads the detected rms value of pilot T one
on CH 3
# PilotT oneDetectActual CH
40x0000b340 0x0000b350Reads the detected rms value of pilot T one
on CH 4
# PilotT oneDetectedActual
CH 10x0000b350 0x0000b354Reads the validity of detected pilot T one on
CH 1
# PilotT oneDetectedActual
CH 20x0000b354 0x0000b358Reads the validity of detected pilot T one on
CH 2
# PilotT oneDetectedActual
CH 30x0000b358 0x0000b35cReads the validity of detected pilot T one on
CH 3
# PilotT oneDetectedActual
CH 40x0000b35c 0x0000b360Reads the validity of detected pilot T one on
CH 4
PilotT oneDetectActual CH 1
Reads the detected rms value of pilot T one on CH 1
Offset Name Type DimR \
# WDescription
0x0000b310  
(45840)PilotT oneDetectActual CH
1 Source 1Float 4 RReads the detected rms value of pilot
Tone on CH 1 of Source 1
0x0000b314  
(45844)PilotT oneDetectActual CH
1 Source 2Float 4 RReads the detected rms value of pilot
Tone on CH 1 of Source 2
0x0000b318  
(45848)PilotT oneDetectActual CH
1 Source 3Float 4 RReads the detected rms value of pilot
Tone on CH 1 of Source 3
0x0000b31c  
(45852)PilotT oneDetectActual CH
1 Source 4Float 4 RReads the detected rms value of pilot
Tone on CH 1 of Source 4

PilotT oneDetectActual CH 2
Reads the detected rms value of pilot T one on CH 2
Offset Name Type DimR \
# WDescription
0x0000b320  
(45856)PilotT oneDetectActual CH
2 Source 1Float 4 RReads the detected rms value of pilot
Tone on CH 2 of Source 1
0x0000b324  
(45860)PilotT oneDetectActual CH
2 Source 2Float 4 RReads the detected rms value of pilot
Tone on CH 2 of Source 2
0x0000b328  
(45864)PilotT oneDetectActual CH
2 Source 3Float 4 RReads the detected rms value of pilot
Tone on CH 2 of Source 3
0x0000b32c  
(45868)PilotT oneDetectActual CH
2 Source 4Float 4 RReads the detected rms value of pilot
Tone on CH 2 of Source 4
PilotT oneDetectActual CH 3
Reads the detected rms value of pilot T one on CH 3
Offset Name Type DimR \
# WDescription
0x0000b330  
(45872)PilotT oneDetectActual CH
3 Source 1Float 4 RReads the detected rms value of pilot
Tone on CH 3 of Source 1
0x0000b334  
(45876)PilotT oneDetectActual CH
3 Source 2Float 4 RReads the detected rms value of pilot
Tone on CH 3 of Source 2
0x0000b338  
(45880)PilotT oneDetectActual CH
3 Source 3Float 4 RReads the detected rms value of pilot
Tone on CH 3 of Source 3
0x0000b33c  
(45884)PilotT oneDetectActual CH
3 Source 4Float 4 RReads the detected rms value of pilot
Tone on CH 3 of Source 4
PilotT oneDetectActual CH 4
Reads the detected rms value of pilot T one on CH 4
Offset Name Type DimR \
# WDescription
0x0000b340  
(45888)PilotT oneDetectActual CH
4 Source 1Float 4 RReads the detected rms value of pilot
Tone on CH 4 of Source 1
0x0000b344  
(45892)PilotT oneDetectActual CH
4 Source 2Float 4 RReads the detected rms value of pilot
Tone on CH 4 of Source 2
0x0000b348  
(45896)PilotT oneDetectActual CH
4 Source 3Float 4 RReads the detected rms value of pilot
Tone on CH 4 of Source 3
0x0000b34c  
(45900)PilotT oneDetectActual CH
4 Source 4Float 4 RReads the detected rms value of pilot
Tone on CH 4 of Source 4

PilotT oneDetectedActual CH 1
Reads the validity of detected pilot T one on CH 1
Offset Name Type DimR \
# WDescription
0x0000b350  
(45904)PilotT oneDetectedActual CH 1
Source 1uint8 1 RReads the validity of detected pilot
Tone on CH 1
0x0000b351  
(45905)PilotT oneDetectedActual CH 1
Source 2uint8 1 RReads the validity of detected pilot
Tone on CH 2
0x0000b352  
(45906)PilotT oneDetectedActual CH 1
Source 3uint8 1 RReads the validity of detected pilot
Tone on CH 3
0x0000b353  
(45907)PilotT oneDetectedActual CH 1
Source 4uint8 1 RReads the validity of detected pilot
Tone on CH 4
PilotT oneDetectedActual CH 2
Reads the validity of detected pilot T one on CH 2
Offset Name Type DimR \
# WDescription
0x0000b354  
(45908)PilotT oneDetectedActual CH 2
Source 1uint8 1 RReads the validity of detected pilot
Tone on CH 1
0x0000b355  
(45909)PilotT oneDetectedActual CH 2
Source 2uint8 1 RReads the validity of detected pilot
Tone on CH 2
0x0000b356  
(45910)PilotT oneDetectedActual CH 2
Source 3uint8 1 RReads the validity of detected pilot
Tone on CH 3
0x0000b357  
(4591 1)PilotT oneDetectedActual CH 2
Source 4uint8 1 RReads the validity of detected pilot
Tone on CH 4
PilotT oneDetectedActual CH 3
Reads the validity of detected pilot T one on CH 3
Offset Name Type DimR \
# WDescription
0x0000b358  
(45912)PilotT oneDetectedActual CH 3
Source 1uint8 1 RReads the validity of detected pilot
Tone on CH 1
0x0000b359  
(45913)PilotT oneDetectedActual CH 3
Source 2uint8 1 RReads the validity of detected pilot
Tone on CH 2
0x0000b35a  
(45914)PilotT oneDetectedActual CH 3
Source 3uint8 1 RReads the validity of detected pilot
Tone on CH 3
0x0000b35b  
(45915)PilotT oneDetectedActual CH 3
Source 4uint8 1 RReads the validity of detected pilot
Tone on CH 4

PilotT oneDetectedActual CH 4
Reads the validity of detected pilot T one on CH 4
Offset Name Type DimR \
# WDescription
0x0000b35c  
(45916)PilotT oneDetectedActual CH 4
Source 1uint8 1 RReads the validity of detected pilot
Tone on CH 1
0x0000b35d  
(45917)PilotT oneDetectedActual CH 4
Source 2uint8 1 RReads the validity of detected pilot
Tone on CH 2
0x0000b35e  
(45918)PilotT oneDetectedActual CH 4
Source 3uint8 1 RReads the validity of detected pilot
Tone on CH 3
0x0000b35f  
(45919)PilotT oneDetectedActual CH 4
Source 4uint8 1 RReads the validity of detected pilot
Tone on CH 4
# SlowMeter W ays
This area contains the W ays slow meters.
# BlockId Start Address End Address Description
PilotT oneDetection W ays 0x0000b478 0x0000b488Reads the detected rms
value of pilot T one
PilotT oneDetectionImpedance W ays 0x0000b488 0x0000b498Reads the detected
impedance value with pilot
# Tone
PilotT oneDetectedRms W ays 0x0000b4a8 0x0000b4acReads if the detected voltage
value is inside specified
range
PilotT oneDetectedImpedance W ays 0x0000b4ac 0x0000b4b0Reads if the detected
impedance value is inside
specified range
PilotT oneDetectionRmsIsV alid W ays 0x0000b4b4 0x0000b4b8Reads the validity of voltage
detected with pilot T one
# PilotT oneDetectionImpedanceRmsIsV alid
Ways0x0000b4b8 0x0000b4c8Reads the validity of
impedance detected with pilot
# Tone
# PilotT oneDetection W ays
# Reads the detected rms value of pilot T one
Offset Name Type DimR \
# WDescription
0x0000b478  
(46200)PilotT oneDetection W ays
CH 1Float 4 RReads the detected rms value of pilot
Tone on CH 1
0x0000b47c  
(46204)PilotT oneDetection W ays
CH 2Float 4 RReads the detected rms value of pilot
Tone on CH 2
0x0000b480  
(46208)PilotT oneDetection W ays
CH 3Float 4 RReads the detected rms value of pilot
Tone on CH 3
0x0000b484  
(46212)PilotT oneDetection W ays
CH 4Float 4 RReads the detected rms value of pilot
Tone on CH 4

# PilotT oneDetectionImpedance W ays
# Reads the detected impedance value with pilot T one
Offset Name Type DimR \
# WDescription
0x0000b488  
(46216)PilotT oneDetectionImpedance
Ways CH 1Float 4 RReads the detected impedance
value with pilot T one on CH 1
0x0000b48c  
(46220)PilotT oneDetectionImpedance
Ways CH 2Float 4 RReads the detected impedance
value with pilot T one on CH 2
0x0000b490  
(46224)PilotT oneDetectionImpedance
Ways CH 3Float 4 RReads the detected impedance
value with pilot T one on CH 3
0x0000b494  
(46228)PilotT oneDetectionImpedance
Ways CH 4Float 4 RReads the detected impedance
value with pilot T one on CH 4
# PilotT oneDetectedRms W ays
# Reads if the detected voltage value is inside specified range
Offset Name Type DimR \
# WDescription
0x0000b4a8  
(46248)PilotT oneDetectedRms
Ways CH 1uint8 1 RReads if the detected voltage value is inside
specified range on CH 1. If so data is 1 else
0.
0x0000b4a9  
(46249)PilotT oneDetectedRms
Ways CH 2uint8 1 RReads if the detected voltage value is inside
specified range on CH 2. If so data is 1 else
0.
0x0000b4aa  
(46250)PilotT oneDetectedRms
Ways CH 3uint8 1 RReads if the detected voltage value is inside
specified range on CH 3. If so data is 1 else
0.
0x0000b4ab  
(46251)PilotT oneDetectedRms
Ways CH 4uint8 1 RReads if the detected voltage value is inside
specified range on CH 4. If so data is 1 else
0.
# PilotT oneDetectedImpedance W ays
# Reads if the detected impedance value is inside specified range
Offset Name Type DimR \
# WDescription
0x0000b4ac  
(46252)PilotT oneDetectedImpedance
Ways CH 1uint8 1 RReads if the detected impedance
value is inside specified range on CH
## 1. If so data is 1 else 0.
0x0000b4ad  
(46253)PilotT oneDetectedImpedance
Ways CH 2uint8 1 RReads if the detected impedance
value is inside specified range on CH
## 2. If so data is 1 else 0.
0x0000b4ae  
(46254)PilotT oneDetectedImpedance
Ways CH 3uint8 1 RReads if the detected impedance
value is inside specified range on CH
## 3. If so data is 1 else 0.
0x0000b4af  
(46255)PilotT oneDetectedImpedance
Ways CH 4uint8 1 RReads if the detected impedance
value is inside specified range on CH
## 4. If so data is 1 else 0.

# PilotT oneDetectionRmsIsV alid W ays
# Reads the validity of voltage detected with pilot T one
Offset Name Type DimR \
# WDescription
0x0000b4b4  
(46260)PilotT oneDetectionRmsIsV alid
Ways CH 1uint8 1 RReads the validity of voltage
detected with pilot T one on CH 1. If
readings is valid data is 1 else 0.
0x0000b4b5  
(46261)PilotT oneDetectionRmsIsV alid
Ways CH 2uint8 1 RReads the validity of voltage
detected with pilot T one on CH 2. If
readings is valid data is 1 else 0.
0x0000b4b6  
(46262)PilotT oneDetectionRmsIsV alid
Ways CH 3uint8 1 RReads the validity of voltage
detected with pilot T one on CH 3. If
readings is valid data is 1 else 0.
0x0000b4b7  
(46263)PilotT oneDetectionRmsIsV alid
Ways CH 4uint8 1 RReads the validity of voltage
detected with pilot T one on CH 4. If
readings is valid data is 1 else 0.
# PilotT oneDetectionImpedanceRmsIsV alid W ays
# Reads the validity of impedance detected with pilot T one
Offset Name Type DimR \
# WDescription
0x0000b4b8  
(46264)PilotT oneDetectionImpedanceRmsIsV alid
Ways CH 1uint32 4 RReads the validity of
impedance detected with
pilot T one on CH 1. If
readings is valid data is
1 else 0.
0x0000b4bc  
(46268)PilotT oneDetectionImpedanceRmsIsV alid
Ways CH 2uint32 4 RReads the validity of
impedance detected with
pilot T one on CH 2. If
readings is valid data is
1 else 0.
0x0000b4c0  
(46272)PilotT oneDetectionImpedanceRmsIsV alid
Ways CH 3uint32 4 RReads the validity of
impedance detected with
pilot T one on CH 3. If
readings is valid data is
1 else 0.
0x0000b4c4  
(46276)PilotT oneDetectionImpedanceRmsIsV alid
Ways CH 4uint32 4 RReads the validity of
impedance detected with
pilot T one on CH 4. If
readings is valid data is
1 else 0.
# SlowMeter PreW ays
This area contains the PreW ays slow meters.
# BlockId Start Address End Address Description
SlowMeter ExternalGain 0x0000b5e8 0x0000b5f8This area contains the PreW ays
ExternalGain.
# SlowMeter GPI scaled
value0x0000b5f8 0x0000b608 This area contains the GPI scaled value.

# SlowMeter ExternalGain
This area contains the PreW ays ExternalGain.
Offset Name Type Dim R \ W Description
0x0000b5e8  
(46568)SlowMeter PreW ays CH 1 Float 4 R Reads the ExternalGain for channel 1
0x0000b5ec  
(46572)SlowMeter PreW ays CH 2 Float 4 R Reads the ExternalGain for channel 2
0x0000b5f0  
(46576)SlowMeter PreW ays CH 3 Float 4 R Reads the ExternalGain for channel 3
0x0000b5f4  
(46580)SlowMeter PreW ays CH 4 Float 4 R Reads the ExternalGain for channel 4
# SlowMeter GPI scaled value
This area contains the GPI scaled value.
Offset Name Type DimR \
# WDescription
0x0000b5f8  
(46584)SlowMeter GPI scaled value
CH 1Float 4 RReads the GPI scaled value for
channel 1
0x0000b5fc  
(46588)SlowMeter GPI scaled value
CH 2Float 4 RReads the GPI scaled value for
channel 2
0x0000b600  
(46592)SlowMeter GPI scaled value
CH 3Float 4 RReads the GPI scaled value for
channel 3
0x0000b604  
(46596)SlowMeter GPI scaled value
CH 4Float 4 RReads the GPI scaled value for
channel 4
# SlowMeter Standby State
This area contains the Standby State slow meters.
Offset Name Type Dim R \ W Description
0x0000b638  
(46648)Standby Active uint32 4 R If 1 the Standby is active, else 0.
# SlowMeter ChannelAlarmStatuses
This area contains the ChannelAlarmStatuses slow meters.
# BlockId Start Address End Address Description
SoaThermal Channel Alarm Statuses 0x0000b640 0x0000b644 Reads the SoaThermal Alarm
Temp Channel Alarm Statuses 0x0000b644 0x0000b648 Reads the T emp Alarm
VRail Channel Alarm Statuses 0x0000b648 0x0000b64c Reads the VRail Alarm

# SoaThermal Channel Alarm Statuses
# Reads the SoaThermal Alarm
Offset Name Type Dim R \ W Description
0x0000b640  
(46656)SoaThermal CH 1 uint8 1 R Reads the SoaThermal Alarm for CH 1
0x0000b641  
(46657)SoaThermal CH 2 uint8 1 R Reads the SoaThermal Alarm for CH 2
0x0000b642  
(46658)SoaThermal CH 3 uint8 1 R Reads the SoaThermal Alarm for CH 3
0x0000b643  
(46659)SoaThermal CH 4 uint8 1 R Reads the SoaThermal Alarm for CH 4
# Temp Channel Alarm Statuses
# Reads the T emp Alarm
Offset Name Type Dim R \ W Description
0x0000b644  
(46660)Temp CH 1 uint8 1 R Reads the T emp Alarm for CH 1
0x0000b645  
(46661)Temp CH 2 uint8 1 R Reads the T emp Alarm for CH 2
0x0000b646  
(46662)Temp CH 3 uint8 1 R Reads the T emp Alarm for CH 3
0x0000b647  
(46663)Temp CH 4 uint8 1 R Reads the T emp Alarm for CH 4
# VRail Channel Alarm Statuses
# Reads the VRail Alarm
Offset Name Type Dim R \ W Description
0x0000b648  
(46664)VRail CH 1 uint8 1 R Reads the VRail Alarm for CH 1
0x0000b649  
(46665)VRail CH 2 uint8 1 R Reads the VRail Alarm for CH 2
0x0000b64a  
(46666)VRail CH 3 uint8 1 R Reads the VRail Alarm for CH 3
0x0000b64b  
(46667)VRail CH 4 uint8 1 R Reads the VRail Alarm for CH 4

# SlowMeter AlarmStatus
This area contains the AlarmStatus slow meters.
Offset Name Type DimR \
# WDescription
0x0000b650  
(46672)Fan uint8 1 R Reads the Fan
0x0000b651  
(46673)HighOverT emperature uint8 1 RReads 1 when temperature of the amplifier
overcomes 95 C°, else 0.
0x0000b653  
(46675)PsTempAlarmStatus uint8 1 R Reads the PsT empAlarmStatus
0x0000b654  
(46676)VAuxAlarmStatus uint8 1 R Reads the V AuxAlarmStatus
0x0000b655  
(46677)GenericFault uint8 1 R Generic Fault
0x0000b656  
(46678)FaultCode uint8 1 RCode to identify any active fault.  
code fault
00 No Fault
01 HWGoodT
02 PGoodPOn
03 CtrlV er
04 RailsPOn
05 RailsOverV
06 RailsUnderV
07 OutDC
08 Fan Broken
09 Fan Short
10 Fan Stuck
11 Software
12 MainBoardV er
13 PGoodMon
14 FuseBlown
15 PsuT emp
16 HiFreq
17 Model
18 OverCurrPOn
0x0000b657  
(46679)GPO relay State uint8 1 RDescribes the actual state of relay: if 1 it is
closed, if 0 it is open.
0x0000b658  
(46680)Fault Code Flags uint32 4 RBitwise description of all active faults. Bit
position follow the codes of FaultCode
starting from LSB.

# SlowMeter MuteCodes
This area contains the mute codes slow meters.
# BlockId Start Address End Address Description
# Mute
# Codes
Flags0x0000b700 0x0000b710Bitwise description of all active mutes. Bit position starts
from LSB following the codes on mute code table.  
code fault
00 Reserved
01 Reserved
02 Reserved
03Positive Rail out of
range
04Negative Rails out of
range
05 Short Circuit
06 Reserved
07 Reserved
08 Over T emperature
09 High Frequency
10 Reserved
11 Reserved
12 Reserved
13 Reserved
14 Mains Under V oltage
15 Mains Over V oltage
16 Reserved
17 Reserved
18 Reserved
# Mute Codes Flags
Bitwise description of all active mutes. Bit position starts from LSB following the codes on mute code table.
Offset Name Type DimR \
# WDescription
0x0000b700  
(46848)Mute Code
Flags CH 1uint32 4 RIf a mute is active the bit in the position of the
corresponding code is set to 1
0x0000b704  
(46852)Mute Code
Flags CH 2uint32 4 RIf a mute is active the bit in the position of the
corresponding code is set to 1
0x0000b708  
(46856)Mute Code
Flags CH 3uint32 4 RIf a mute is active the bit in the position of the
corresponding code is set to 1
0x0000b70c  
(46860)Mute Code
Flags CH 4uint32 4 RIf a mute is active the bit in the position of the
corresponding code is set to 1

# Fast Meters
This area contains the fast meters.
# BlockId Start Address End Address Description
# FastMeter
SourceSelection0x0000b800 0x0000ba10This area contains the SourceSelection fast
meters.
FastMeter InputMatrix 0x0000ba40 0x0000ba60This area contains the InputMatrix fast
meters.
FastMeter W ays 0x0000bac0 0x0000bbb8 This area contains the W ays fast meters.
FastMeter PowerSupply 0x0000bbb8 0x0000bbc4This area contains the PowerSupply fast
meters.
# FastMeter SourceSelection
This area contains the SourceSelection fast meters.
# BlockId Start Address End Address Description
# FastMeter Source Selection
Source 10x0000b800 0x0000b880This area contains the source selection
fast meter for Source 1.
# FastMeter Source Selection
Source 20x0000b880 0x0000b900This area contains the source selection
fast meter for Source 2.
# FastMeter Source Selection
Source 30x0000b900 0x0000b980This area contains the source selection
fast meter for Source 3.
# FastMeter Source Selection
Source 40x0000b980 0x0000ba00This area contains the source selection
fast meter for Source 4.
# FastMeter SourceSelection
Backup Settings0x0000ba00 0x0000ba10This area contains the Source Selection
-> Backup Settings fast meters.
FastMeter Source Selection Source 1
This area contains the source selection fast meter for Source 1.
# BlockId Start Address End Address Description
Source 1 T ype 0x0000b800 0x0000b808
Source 1 Channel 0x0000b808 0x0000b810
Source 1 Peak 0x0000b810 0x0000b820 Reads the Source 1 Peak
Source 1 Rms 0x0000b820 0x0000b830 Reads the Source 1 Rms
Source 1 Presence 0x0000b830 0x0000b840 Reads the Source 1 Presence
Source 1 Clip 0x0000b840 0x0000b850 Reads the Source 1 Clip
Source 1 Spare 1 0x0000b850 0x0000b860 Source 1 Spare 1
Source 1 Spare 2 0x0000b860 0x0000b870 Source 1 Spare 2
Source 1 Spare 3 0x0000b870 0x0000b880 Source 1 Spare 3

Source 1 T ype
Deprecated since version 1.1.0
Offset Name Type Dim R \ W Description
0x0000b800  
(47104)Source 1 - T ype - Channel 1 uint16 2 R
0x0000b802  
(47106)Source 1 - T ype - Channel 2 uint16 2 R
0x0000b804  
(47108)Source 1 - T ype - Channel 3 uint16 2 R
0x0000b806  
(47110)Source 1 - T ype - Channel 4 uint16 2 R
Source 1 Channel
Deprecated since version 1.1.0
Offset Name Type Dim R \ W Description
0x0000b808  
(47112)Source 1 - Channel - Channel 1 uint16 2 R
0x0000b80a  
(47114)Source 1 - Channel - Channel 2 uint16 2 R
0x0000b80c  
(47116)Source 1 - Channel - Channel 3 uint16 2 R
0x0000b80e  
(47118)Source 1 - Channel - Channel 4 uint16 2 R
Source 1 Peak
Reads the Source 1 Peak
Offset Name Type DimR \
# WDescription
0x0000b810  
(47120)Source 1 - Peak - Channel
1Float 4 RReads the Source 1 - Peak for Channel
1.
0x0000b814  
(47124)Source 1 - Peak - Channel
2Float 4 RReads the Source 1 - Peak for Channel
2.
0x0000b818  
(47128)Source 1 - Peak - Channel
3Float 4 RReads the Source 1 - Peak for Channel
3.
0x0000b81c  
(47132)Source 1 - Peak - Channel
4Float 4 RReads the Source 1 - Peak for Channel
4.

Source 1 Rms
Reads the Source 1 Rms
Offset Name Type DimR \
# WDescription
0x0000b820  
(47136)Source 1 - Rms - Channel
1Float 4 RReads the Source 1 - Rms for Channel
1.
0x0000b824  
(47140)Source 1 - Rms - Channel
2Float 4 RReads the Source 1 - Rms for Channel
2.
0x0000b828  
(47144)Source 1 - Rms - Channel
3Float 4 RReads the Source 1 - Rms for Channel
3.
0x0000b82c  
(47148)Source 1 - Rms - Channel
4Float 4 RReads the Source 1 - Rms for Channel
4.
Source 1 Presence
Reads the Source 1 Presence
Offset Name Type DimR \
# WDescription
0x0000b830  
(47152)Source 1 - Presence -
Channel 1uint32 4 RReads the Source 1 - Presence for
Channel 1.
0x0000b834  
(47156)Source 1 - Presence -
Channel 2uint32 4 RReads the Source 1 - Presence for
Channel 2.
0x0000b838  
(47160)Source 1 - Presence -
Channel 3uint32 4 RReads the Source 1 - Presence for
Channel 3.
0x0000b83c  
(47164)Source 1 - Presence -
Channel 4uint32 4 RReads the Source 1 - Presence for
Channel 4.
Source 1 Clip
Reads the Source 1 Clip
Offset Name Type DimR \
# WDescription
0x0000b840  
(47168)Source 1 - Clip - Channel
1uint32 4 RReads the Source 1 - Clip for Channel
1.
0x0000b844  
(47172)Source 1 - Clip - Channel
2uint32 4 RReads the Source 1 - Clip for Channel
2.
0x0000b848  
(47176)Source 1 - Clip - Channel
3uint32 4 RReads the Source 1 - Clip for Channel
3.
0x0000b84c  
(47180)Source 1 - Clip - Channel
4uint32 4 RReads the Source 1 - Clip for Channel
4.

Source 1 Spare 1
Source 1 Spare 1
Offset Name Type DimR \
# WDescription
0x0000b850  
(47184)Source 1 - Spare 1 -
Channel 1uint32 4 RReads the Source 1 - Spare 1 for
Channel 1.
0x0000b854  
(47188)Source 1 - Spare 1 -
Channel 2uint32 4 RReads the Source 1 - Spare 1 for
Channel 2.
0x0000b858  
(47192)Source 1 - Spare 1 -
Channel 3uint32 4 RReads the Source 1 - Spare 1 for
Channel 3.
0x0000b85c  
(47196)Source 1 - Spare 1 -
Channel 4uint32 4 RReads the Source 1 - Spare 1 for
Channel 4.
Source 1 Spare 2
Source 1 Spare 2
Offset Name Type DimR \
# WDescription
0x0000b860  
(47200)Source 1 - Spare 2 -
Channel 1uint32 4 RReads the Source 1 - Spare 2 for
Channel 1.
0x0000b864  
(47204)Source 1 - Spare 2 -
Channel 2uint32 4 RReads the Source 1 - Spare 2 for
Channel 2.
0x0000b868  
(47208)Source 1 - Spare 2 -
Channel 3uint32 4 RReads the Source 1 - Spare 2 for
Channel 3.
0x0000b86c  
(47212)Source 1 - Spare 2 -
Channel 4uint32 4 RReads the Source 1 - Spare 2 for
Channel 4.
Source 1 Spare 3
Source 1 Spare 3
Offset Name Type DimR \
# WDescription
0x0000b870  
(47216)Source 1 - Spare 3 -
Channel 1uint32 4 RReads the Source 1 - Spare 3 for
Channel 1.
0x0000b874  
(47220)Source 1 - Spare 3 -
Channel 2uint32 4 RReads the Source 1 - Spare 3 for
Channel 2.
0x0000b878  
(47224)Source 1 - Spare 3 -
Channel 3uint32 4 RReads the Source 1 - Spare 3 for
Channel 3.
0x0000b87c  
(47228)Source 1 - Spare 3 -
Channel 4uint32 4 RReads the Source 1 - Spare 3 for
Channel 4.

FastMeter Source Selection Source 2
This area contains the source selection fast meter for Source 2.
# BlockId Start Address End Address Description
Source 2 T ype 0x0000b880 0x0000b888
Source 2 Channel 0x0000b888 0x0000b890
Source 2 Peak 0x0000b890 0x0000b8a0 Reads the Source 2 Peak
Source 2 Rms 0x0000b8a0 0x0000b8b0 Reads the Source 2 Rms
Source 2 Presence 0x0000b8b0 0x0000b8c0 Reads the Source 2 Presence
Source 2 Clip 0x0000b8c0 0x0000b8d0 Reads the Source 2 Clip
Source 2 Spare 1 0x0000b8d0 0x0000b8e0 Source 2 Spare 1
Source 2 Spare 2 0x0000b8e0 0x0000b8f0 Source 2 Spare 2
Source 2 Spare 3 0x0000b8f0 0x0000b900 Source 2 Spare 3
Source 2 T ype
Deprecated since version 1.1.0
Offset Name Type Dim R \ W Description
0x0000b880  
(47232)Source 2 - T ype - Channel 1 uint16 2 R
0x0000b882  
(47234)Source 2 - T ype - Channel 2 uint16 2 R
0x0000b884  
(47236)Source 2 - T ype - Channel 3 uint16 2 R
0x0000b886  
(47238)Source 2 - T ype - Channel 4 uint16 2 R
Source 2 Channel
Deprecated since version 1.1.0
Offset Name Type Dim R \ W Description
0x0000b888  
(47240)Source 2 - Channel - Channel 1 uint16 2 R
0x0000b88a  
(47242)Source 2 - Channel - Channel 2 uint16 2 R
0x0000b88c  
(47244)Source 2 - Channel - Channel 3 uint16 2 R
0x0000b88e  
(47246)Source 2 - Channel - Channel 4 uint16 2 R

Source 2 Peak
Reads the Source 2 Peak
Offset Name Type DimR \
# WDescription
0x0000b890  
(47248)Source 2 - Peak - Channel
1Float 4 RReads the Source 2 - Peak for Channel
1.
0x0000b894  
(47252)Source 2 - Peak - Channel
2Float 4 RReads the Source 2 - Peak for Channel
2.
0x0000b898  
(47256)Source 2 - Peak - Channel
3Float 4 RReads the Source 2 - Peak for Channel
3.
0x0000b89c  
(47260)Source 2 - Peak - Channel
4Float 4 RReads the Source 2 - Peak for Channel
4.
Source 2 Rms
Reads the Source 2 Rms
Offset Name Type DimR \
# WDescription
0x0000b8a0  
(47264)Source 2 - Rms - Channel
1Float 4 RReads the Source 2 - Rms for Channel
1.
0x0000b8a4  
(47268)Source 2 - Rms - Channel
2Float 4 RReads the Source 2 - Rms for Channel
2.
0x0000b8a8  
(47272)Source 2 - Rms - Channel
3Float 4 RReads the Source 2 - Rms for Channel
3.
0x0000b8ac  
(47276)Source 2 - Rms - Channel
4Float 4 RReads the Source 2 - Rms for Channel
4.
Source 2 Presence
Reads the Source 2 Presence
Offset Name Type DimR \
# WDescription
0x0000b8b0  
(47280)Source 2 - Presence -
Channel 1uint32 4 RReads the Source 2 - Presence for
Channel 1.
0x0000b8b4  
(47284)Source 2 - Presence -
Channel 2uint32 4 RReads the Source 2 - Presence for
Channel 2.
0x0000b8b8  
(47288)Source 2 - Presence -
Channel 3uint32 4 RReads the Source 2 - Presence for
Channel 3.
0x0000b8bc  
(47292)Source 2 - Presence -
Channel 4uint32 4 RReads the Source 2 - Presence for
Channel 4.

Source 2 Clip
Reads the Source 2 Clip
Offset Name Type DimR \
# WDescription
0x0000b8c0  
(47296)Source 2 - Clip - Channel
1uint32 4 RReads the Source 2 - Clip for Channel
1.
0x0000b8c4  
(47300)Source 2 - Clip - Channel
2uint32 4 RReads the Source 2 - Clip for Channel
2.
0x0000b8c8  
(47304)Source 2 - Clip - Channel
3uint32 4 RReads the Source 2 - Clip for Channel
3.
0x0000b8cc  
(47308)Source 2 - Clip - Channel
4uint32 4 RReads the Source 2 - Clip for Channel
4.
Source 2 Spare 1
Source 2 Spare 1
Offset Name Type DimR \
# WDescription
0x0000b8d0  
(47312)Source 2 - Spare 1 -
Channel 1uint32 4 RReads the Source 2 - Spare 1 for
Channel 1.
0x0000b8d4  
(47316)Source 2 - Spare 1 -
Channel 2uint32 4 RReads the Source 2 - Spare 1 for
Channel 2.
0x0000b8d8  
(47320)Source 2 - Spare 1 -
Channel 3uint32 4 RReads the Source 2 - Spare 1 for
Channel 3.
0x0000b8dc  
(47324)Source 2 - Spare 1 -
Channel 4uint32 4 RReads the Source 2 - Spare 1 for
Channel 4.
Source 2 Spare 2
Source 2 Spare 2
Offset Name Type DimR \
# WDescription
0x0000b8e0  
(47328)Source 2 - Spare 2 -
Channel 1uint32 4 RReads the Source 2 - Spare 2 for
Channel 1.
0x0000b8e4  
(47332)Source 2 - Spare 2 -
Channel 2uint32 4 RReads the Source 2 - Spare 2 for
Channel 2.
0x0000b8e8  
(47336)Source 2 - Spare 2 -
Channel 3uint32 4 RReads the Source 2 - Spare 2 for
Channel 3.
0x0000b8ec  
(47340)Source 2 - Spare 2 -
Channel 4uint32 4 RReads the Source 2 - Spare 2 for
Channel 4.

Source 2 Spare 3
Source 2 Spare 3
Offset Name Type DimR \
# WDescription
0x0000b8f0  
(47344)Source 2 - Spare 3 -
Channel 1uint32 4 RReads the Source 2 - Spare 3 for
Channel 1.
0x0000b8f4  
(47348)Source 2 - Spare 3 -
Channel 2uint32 4 RReads the Source 2 - Spare 3 for
Channel 2.
0x0000b8f8  
(47352)Source 2 - Spare 3 -
Channel 3uint32 4 RReads the Source 2 - Spare 3 for
Channel 3.
0x0000b8fc  
(47356)Source 2 - Spare 3 -
Channel 4uint32 4 RReads the Source 2 - Spare 3 for
Channel 4.
FastMeter Source Selection Source 3
This area contains the source selection fast meter for Source 3.
# BlockId Start Address End Address Description
Source 3 T ype 0x0000b900 0x0000b908
Source 3 Channel 0x0000b908 0x0000b910
Source 3 Peak 0x0000b910 0x0000b920 Reads the Source 3 Peak
Source 3 Rms 0x0000b920 0x0000b930 Reads the Source 3 Rms
Source 3 Presence 0x0000b930 0x0000b940 Reads the Source 3 Presence
Source 3 Clip 0x0000b940 0x0000b950 Reads the Source 3 Clip
Source 3 Spare 1 0x0000b950 0x0000b960 Source 3 Spare 1
Source 3 Spare 2 0x0000b960 0x0000b970 Source 3 Spare 2
Source 3 Spare 3 0x0000b970 0x0000b980 Source 3 Spare 3
Source 3 T ype
Deprecated since version 1.1.0
Offset Name Type Dim R \ W Description
0x0000b900  
(47360)Source 3 - T ype - Channel 1 uint16 2 R
0x0000b902  
(47362)Source 3 - T ype - Channel 2 uint16 2 R
0x0000b904  
(47364)Source 3 - T ype - Channel 3 uint16 2 R
0x0000b906  
(47366)Source 3 - T ype - Channel 4 uint16 2 R

Source 3 Channel
Deprecated since version 1.1.0
Offset Name Type Dim R \ W Description
0x0000b908  
(47368)Source 3 - Channel - Channel 1 uint16 2 R
0x0000b90a  
(47370)Source 3 - Channel - Channel 2 uint16 2 R
0x0000b90c  
(47372)Source 3 - Channel - Channel 3 uint16 2 R
0x0000b90e  
(47374)Source 3 - Channel - Channel 4 uint16 2 R
Source 3 Peak
Reads the Source 3 Peak
Offset Name Type DimR \
# WDescription
0x0000b910  
(47376)Source 3 - Peak - Channel
1Float 4 RReads the Source 3 - Peak for Channel
1.
0x0000b914  
(47380)Source 3 - Peak - Channel
2Float 4 RReads the Source 3 - Peak for Channel
2.
0x0000b918  
(47384)Source 3 - Peak - Channel
3Float 4 RReads the Source 3 - Peak for Channel
3.
0x0000b91c  
(47388)Source 3 - Peak - Channel
4Float 4 RReads the Source 3 - Peak for Channel
4.
Source 3 Rms
Reads the Source 3 Rms
Offset Name Type DimR \
# WDescription
0x0000b920  
(47392)Source 3 - Rms - Channel
1Float 4 RReads the Source 3 - Rms for Channel
1.
0x0000b924  
(47396)Source 3 - Rms - Channel
2Float 4 RReads the Source 3 - Rms for Channel
2.
0x0000b928  
(47400)Source 3 - Rms - Channel
3Float 4 RReads the Source 3 - Rms for Channel
3.
0x0000b92c  
(47404)Source 3 - Rms - Channel
4Float 4 RReads the Source 3 - Rms for Channel
4.

Source 3 Presence
Reads the Source 3 Presence
Offset Name Type DimR \
# WDescription
0x0000b930  
(47408)Source 3 - Presence -
Channel 1uint32 4 RReads the Source 3 - Presence for
Channel 1.
0x0000b934  
(47412)Source 3 - Presence -
Channel 2uint32 4 RReads the Source 3 - Presence for
Channel 2.
0x0000b938  
(47416)Source 3 - Presence -
Channel 3uint32 4 RReads the Source 3 - Presence for
Channel 3.
0x0000b93c  
(47420)Source 3 - Presence -
Channel 4uint32 4 RReads the Source 3 - Presence for
Channel 4.
Source 3 Clip
Reads the Source 3 Clip
Offset Name Type DimR \
# WDescription
0x0000b940  
(47424)Source 3 - Clip - Channel
1uint32 4 RReads the Source 3 - Clip for Channel
1.
0x0000b944  
(47428)Source 3 - Clip - Channel
2uint32 4 RReads the Source 3 - Clip for Channel
2.
0x0000b948  
(47432)Source 3 - Clip - Channel
3uint32 4 RReads the Source 3 - Clip for Channel
3.
0x0000b94c  
(47436)Source 3 - Clip - Channel
4uint32 4 RReads the Source 3 - Clip for Channel
4.
Source 3 Spare 1
Source 3 Spare 1
Offset Name Type DimR \
# WDescription
0x0000b950  
(47440)Source 3 - Spare 1 -
Channel 1uint32 4 RReads the Source 3 - Spare 1 for
Channel 1.
0x0000b954  
(47444)Source 3 - Spare 1 -
Channel 2uint32 4 RReads the Source 3 - Spare 1 for
Channel 2.
0x0000b958  
(47448)Source 3 - Spare 1 -
Channel 3uint32 4 RReads the Source 3 - Spare 1 for
Channel 3.
0x0000b95c  
(47452)Source 3 - Spare 1 -
Channel 4uint32 4 RReads the Source 3 - Spare 1 for
Channel 4.

Source 3 Spare 2
Source 3 Spare 2
Offset Name Type DimR \
# WDescription
0x0000b960  
(47456)Source 3 - Spare 2 -
Channel 1uint32 4 RReads the Source 3 - Spare 2 for
Channel 1.
0x0000b964  
(47460)Source 3 - Spare 2 -
Channel 2uint32 4 RReads the Source 3 - Spare 2 for
Channel 2.
0x0000b968  
(47464)Source 3 - Spare 2 -
Channel 3uint32 4 RReads the Source 3 - Spare 2 for
Channel 3.
0x0000b96c  
(47468)Source 3 - Spare 2 -
Channel 4uint32 4 RReads the Source 3 - Spare 2 for
Channel 4.
Source 3 Spare 3
Source 3 Spare 3
Offset Name Type DimR \
# WDescription
0x0000b970  
(47472)Source 3 - Spare 3 -
Channel 1uint32 4 RReads the Source 3 - Spare 3 for
Channel 1.
0x0000b974  
(47476)Source 3 - Spare 3 -
Channel 2uint32 4 RReads the Source 3 - Spare 3 for
Channel 2.
0x0000b978  
(47480)Source 3 - Spare 3 -
Channel 3uint32 4 RReads the Source 3 - Spare 3 for
Channel 3.
0x0000b97c  
(47484)Source 3 - Spare 3 -
Channel 4uint32 4 RReads the Source 3 - Spare 3 for
Channel 4.
FastMeter Source Selection Source 4
This area contains the source selection fast meter for Source 4.
# BlockId Start Address End Address Description
Source 4 T ype 0x0000b980 0x0000b988
Source 4 Channel 0x0000b988 0x0000b990
Source 4 Peak 0x0000b990 0x0000b9a0 Reads the Source 4 Peak
Source 4 Rms 0x0000b9a0 0x0000b9b0 Reads the Source 4 Rms
Source 4 Presence 0x0000b9b0 0x0000b9c0 Reads the Source 4 Presence
Source 4 Clip 0x0000b9c0 0x0000b9d0 Reads the Source 4 Clip
Source 4 Spare 1 0x0000b9d0 0x0000b9e0 Source 4 Spare 1
Source 4 Spare 2 0x0000b9e0 0x0000b9f0 Source 4 Spare 2
Source 4 Spare 3 0x0000b9f0 0x0000ba00 Source 4 Spare 3

Source 4 T ype
Deprecated since version 1.1.0
Offset Name Type Dim R \ W Description
0x0000b980  
(47488)Source 4 - T ype - Channel 1 uint16 2 R
0x0000b982  
(47490)Source 4 - T ype - Channel 2 uint16 2 R
0x0000b984  
(47492)Source 4 - T ype - Channel 3 uint16 2 R
0x0000b986  
(47494)Source 4 - T ype - Channel 4 uint16 2 R
Source 4 Channel
Deprecated since version 1.1.0
Offset Name Type Dim R \ W Description
0x0000b988  
(47496)Source 4 - Channel - Channel 1 uint16 2 R
0x0000b98a  
(47498)Source 4 - Channel - Channel 2 uint16 2 R
0x0000b98c  
(47500)Source 4 - Channel - Channel 3 uint16 2 R
0x0000b98e  
(47502)Source 4 - Channel - Channel 4 uint16 2 R
Source 4 Peak
Reads the Source 4 Peak
Offset Name Type DimR \
# WDescription
0x0000b990  
(47504)Source 4 - Peak - Channel
1Float 4 RReads the Source 4 - Peak for Channel
1.
0x0000b994  
(47508)Source 4 - Peak - Channel
2Float 4 RReads the Source 4 - Peak for Channel
2.
0x0000b998  
(47512)Source 4 - Peak - Channel
3Float 4 RReads the Source 4 - Peak for Channel
3.
0x0000b99c  
(47516)Source 4 - Peak - Channel
4Float 4 RReads the Source 4 - Peak for Channel
4.

Source 4 Rms
Reads the Source 4 Rms
Offset Name Type DimR \
# WDescription
0x0000b9a0  
(47520)Source 4 - Rms - Channel
1Float 4 RReads the Source 4 - Rms for Channel
1.
0x0000b9a4  
(47524)Source 4 - Rms - Channel
2Float 4 RReads the Source 4 - Rms for Channel
2.
0x0000b9a8  
(47528)Source 4 - Rms - Channel
3Float 4 RReads the Source 4 - Rms for Channel
3.
0x0000b9ac  
(47532)Source 4 - Rms - Channel
4Float 4 RReads the Source 4 - Rms for Channel
4.
Source 4 Presence
Reads the Source 4 Presence
Offset Name Type DimR \
# WDescription
0x0000b9b0  
(47536)Source 4 - Presence -
Channel 1uint32 4 RReads the Source 4 - Presence for
Channel 1.
0x0000b9b4  
(47540)Source 4 - Presence -
Channel 2uint32 4 RReads the Source 4 - Presence for
Channel 2.
0x0000b9b8  
(47544)Source 4 - Presence -
Channel 3uint32 4 RReads the Source 4 - Presence for
Channel 3.
0x0000b9bc  
(47548)Source 4 - Presence -
Channel 4uint32 4 RReads the Source 4 - Presence for
Channel 4.
Source 4 Clip
Reads the Source 4 Clip
Offset Name Type DimR \
# WDescription
0x0000b9c0  
(47552)Source 4 - Clip - Channel
1uint32 4 RReads the Source 4 - Clip for Channel
1.
0x0000b9c4  
(47556)Source 4 - Clip - Channel
2uint32 4 RReads the Source 4 - Clip for Channel
2.
0x0000b9c8  
(47560)Source 4 - Clip - Channel
3uint32 4 RReads the Source 4 - Clip for Channel
3.
0x0000b9cc  
(47564)Source 4 - Clip - Channel
4uint32 4 RReads the Source 4 - Clip for Channel
4.

Source 4 Spare 1
Source 4 Spare 1
Offset Name Type DimR \
# WDescription
0x0000b9d0  
(47568)Source 4 - Spare 1 -
Channel 1uint32 4 RReads the Source 4 - Spare 1 for
Channel 1.
0x0000b9d4  
(47572)Source 4 - Spare 1 -
Channel 2uint32 4 RReads the Source 4 - Spare 1 for
Channel 2.
0x0000b9d8  
(47576)Source 4 - Spare 1 -
Channel 3uint32 4 RReads the Source 4 - Spare 1 for
Channel 3.
0x0000b9dc  
(47580)Source 4 - Spare 1 -
Channel 4uint32 4 RReads the Source 4 - Spare 1 for
Channel 4.
Source 4 Spare 2
Source 4 Spare 2
Offset Name Type DimR \
# WDescription
0x0000b9e0  
(47584)Source 4 - Spare 2 -
Channel 1uint32 4 RReads the Source 4 - Spare 2 for
Channel 1.
0x0000b9e4  
(47588)Source 4 - Spare 2 -
Channel 2uint32 4 RReads the Source 4 - Spare 2 for
Channel 2.
0x0000b9e8  
(47592)Source 4 - Spare 2 -
Channel 3uint32 4 RReads the Source 4 - Spare 2 for
Channel 3.
0x0000b9ec  
(47596)Source 4 - Spare 2 -
Channel 4uint32 4 RReads the Source 4 - Spare 2 for
Channel 4.
Source 4 Spare 3
Source 4 Spare 3
Offset Name Type DimR \
# WDescription
0x0000b9f0  
(47600)Source 4 - Spare 3 -
Channel 1uint32 4 RReads the Source 4 - Spare 3 for
Channel 1.
0x0000b9f4  
(47604)Source 4 - Spare 3 -
Channel 2uint32 4 RReads the Source 4 - Spare 3 for
Channel 2.
0x0000b9f8  
(47608)Source 4 - Spare 3 -
Channel 3uint32 4 RReads the Source 4 - Spare 3 for
Channel 3.
0x0000b9fc  
(47612)Source 4 - Spare 3 -
Channel 4uint32 4 RReads the Source 4 - Spare 3 for
Channel 4.

# FastMeter SourceSelection Backup Settings
This area contains the Source Selection -> Backup Settings fast meters.
Offset Name Type Dim R \ W Description
0x0000ba00  
(47616)SelectedBackup 1 uint32 4 R Channel 1 - SelectedBackup
0x0000ba04  
(47620)SelectedBackup 2 uint32 4 R Channel 2 - SelectedBackup
0x0000ba08  
(47624)SelectedBackup 3 uint32 4 R Channel 3 - SelectedBackup
0x0000ba0c  
(47628)SelectedBackup 4 uint32 4 R Channel 4 - SelectedBackup
# FastMeter InputMatrix
This area contains the InputMatrix fast meters.
# BlockId Start Address End Address Description
# FastMeter Peak
InputMatrix0x0000ba40 0x0000ba50This area contains the InputMatrix Peak fast
meters.
# FastMeter Rms
InputMatrix0x0000ba50 0x0000ba60This area contains the InputMatrix Rmsfast
meters.
# FastMeter Peak InputMatrix
This area contains the InputMatrix Peak fast meters.
Offset Name Type Dim R \ W Description
0x0000ba40  
(47680)Peak InputMatrix 1 Float 4 R Reads the FastMeter InputMatrix 1 Peak
0x0000ba44  
(47684)Peak InputMatrix 2 Float 4 R Reads the FastMeter InputMatrix 2 Peak
0x0000ba48  
(47688)Peak InputMatrix 3 Float 4 R Reads the FastMeter InputMatrix 3 Peak
0x0000ba4c  
(47692)Peak InputMatrix 4 Float 4 R Reads the FastMeter InputMatrix 4 Peak
# FastMeter Rms InputMatrix
This area contains the InputMatrix Rmsfast meters.
Offset Name Type Dim R \ W Description
0x0000ba50  
(47696)Rms InputMatrix 1 Float 4 R Reads the FastMeter InputMatrix 1 Rms
0x0000ba54  
(47700)Rms InputMatrix 2 Float 4 R Reads the FastMeter InputMatrix 2 Rms
0x0000ba58  
(47704)Rms InputMatrix 3 Float 4 R Reads the FastMeter InputMatrix 3 Rms
0x0000ba5c  
(47708)Rms InputMatrix 4 Float 4 R Reads the FastMeter InputMatrix 4 Rms

# FastMeter W ays
This area contains the W ays fast meters.
# BlockId Start Address End Address Description
FastMeter W ays VPeak 0x0000bac0 0x0000bad0 Reads the VPeak - V oltage
FastMeter W ays VRms 0x0000bad0 0x0000bae0 Reads the VRms - V oltage
FastMeter W ays IPeak 0x0000bae0 0x0000baf0 Reads the IPeak - Current
FastMeter W ays IRms 0x0000baf0 0x0000bb00 Reads the IRms - Current
# FastMeter W ays
SoaGainReductionThermalLimiter0x0000bb10 0x0000bb20Reads the
# SoaGainReductionThermalLimiter
# FastMeter W ays
SoaGainReductionV oltageHfLimiter0x0000bb20 0x0000bb30Reads the
# SoaGainReductionV oltageHfLimiter
# FastMeter W ays
SoaGainReductionCurrentLongLimiter0x0000bb30 0x0000bb40Reads the
# SoaGainReductionCurrentLongLimiter
# FastMeter W ays
SoaGainReductionCurrentShortLimiter0x0000bb40 0x0000bb50Reads the
# SoaGainReductionCurrentShortLimiter
# FastMeter W ays
SoaGainReductionPowerLimiter0x0000bb50 0x0000bb60Reads the
# SoaGainReductionPowerLimiter
# FastMeter W ays
UserGainReductionV oltageLimiterPeak0x0000bb60 0x0000bb70Reads the
# UserGainReductionV oltageLimiterPeak
# FastMeter W ays
UserGainReductionV oltageLimiterRms0x0000bb70 0x0000bb80Reads the
# UserGainReductionV oltageLimiterRms
# FastMeter W ays
UserGainReductionClipLimiter0x0000bb80 0x0000bb90Reads the
# UserGainReductionClipLimiter
# FastMeter W ays
UserGainReductionT otal0x0000bb90 0x0000bba0 Reads the UserGainReductionT otal
FastMeter W ays SignalPresence 0x0000bba0 0x0000bba4 Reads the SignalPresence
FastMeter W ays Headroom 0x0000bba8 0x0000bbb8 Reads the Headroom
# FastMeter W ays VPeak
Reads the VPeak - V oltage
Offset Name Type Dim R \ W Description
0x0000bac0  
(47808)VPeak CH 1 Float 4 R Reads the VPeak - V oltage for Channel 1 - V oltage
0x0000bac4  
(47812)VPeak CH 2 Float 4 R Reads the VPeak - V oltage for Channel 2 - V oltage
0x0000bac8  
(47816)VPeak CH 3 Float 4 R Reads the VPeak - V oltage for Channel 3 - V oltage
0x0000bacc  
(47820)VPeak CH 4 Float 4 R Reads the VPeak - V oltage for Channel 4 - V oltage

# FastMeter W ays VRms
Reads the VRms - V oltage
Offset Name Type Dim R \ W Description
0x0000bad0  
(47824)VRms CH 1 Float 4 R Reads the VRms for Channel 1 - V oltage
0x0000bad4  
(47828)VRms CH 2 Float 4 R Reads the VRms for Channel 2 - V oltage
0x0000bad8  
(47832)VRms CH 3 Float 4 R Reads the VRms for Channel 3 - V oltage
0x0000badc  
(47836)VRms CH 4 Float 4 R Reads the VRms for Channel 4 - V oltage
# FastMeter W ays IPeak
Reads the IPeak - Current
Offset Name Type Dim R \ W Description
0x0000bae0  
(47840)IPeak CH 1 Float 4 R Reads the IPeak for Channel 1 - Current
0x0000bae4  
(47844)IPeak CH 2 Float 4 R Reads the IPeak for Channel 2 - Current
0x0000bae8  
(47848)IPeak CH 3 Float 4 R Reads the IPeak for Channel 3 - Current
0x0000baec  
(47852)IPeak CH 4 Float 4 R Reads the IPeak for Channel 4 - Current
# FastMeter W ays IRms
Reads the IRms - Current
Offset Name Type Dim R \ W Description
0x0000baf0  
(47856)IRms CH 1 Float 4 R Reads the IRms for Channel 1 - Current
0x0000baf4  
(47860)IRms CH 2 Float 4 R Reads the IRms for Channel 2 - Current
0x0000baf8  
(47864)IRms CH 3 Float 4 R Reads the IRms for Channel 3 - Current
0x0000bafc  
(47868)IRms CH 4 Float 4 R Reads the IRms for Channel 4 - Current

# FastMeter W ays SoaGainReductionThermalLimiter
# Reads the SoaGainReductionThermalLimiter
Offset Name Type DimR \
# WDescription
0x0000bb10  
(47888)SoaGainReductionThermalLimiter
CH 1Float 4 RReads the
# SoaGainReductionThermalLimiter
for Channel 1
0x0000bb14  
(47892)SoaGainReductionThermalLimiter
CH 2Float 4 RReads the
# SoaGainReductionThermalLimiter
for Channel 2
0x0000bb18  
(47896)SoaGainReductionThermalLimiter
CH 3Float 4 RReads the
# SoaGainReductionThermalLimiter
for Channel 3
0x0000bb1c  
(47900)SoaGainReductionThermalLimiter
CH 4Float 4 RReads the
# SoaGainReductionThermalLimiter
for Channel 4
# FastMeter W ays SoaGainReductionV oltageHfLimiter
# Reads the SoaGainReductionV oltageHfLimiter
Offset Name Type DimR \
# WDescription
0x0000bb20  
(47904)SoaGainReductionV oltageHfLimiter
CH 1Float 4 RReads the
# SoaGainReductionV oltageHfLimiter
for Channel 1
0x0000bb24  
(47908)SoaGainReductionV oltageHfLimiter
CH 2Float 4 RReads the
# SoaGainReductionV oltageHfLimiter
for Channel 2
0x0000bb28  
(47912)SoaGainReductionV oltageHfLimiter
CH 3Float 4 RReads the
# SoaGainReductionV oltageHfLimiter
for Channel 3
0x0000bb2c  
(47916)SoaGainReductionV oltageHfLimiter
CH 4Float 4 RReads the
# SoaGainReductionV oltageHfLimiter
for Channel 4
# FastMeter W ays SoaGainReductionCurrentLongLimiter
# Reads the SoaGainReductionCurrentLongLimiter
Offset Name Type DimR \
# WDescription
0x0000bb30  
(47920)SoaGainReductionCurrentLongLimiter
CH 1Float 4 RReads the
# SoaGainReductionCurrentLongLimiter
for Channel 1
0x0000bb34  
(47924)SoaGainReductionCurrentLongLimiter
CH 2Float 4 RReads the
# SoaGainReductionCurrentLongLimiter
for Channel 2
0x0000bb38  
(47928)SoaGainReductionCurrentLongLimiter
CH 3Float 4 RReads the
# SoaGainReductionCurrentLongLimiter
for Channel 3
0x0000bb3c  
(47932)SoaGainReductionCurrentLongLimiter
CH 4Float 4 RReads the
# SoaGainReductionCurrentLongLimiter
for Channel 4

# FastMeter W ays SoaGainReductionCurrentShortLimiter
# Reads the SoaGainReductionCurrentShortLimiter
Offset Name Type DimR \
# WDescription
0x0000bb40  
(47936)SoaGainReductionCurrentShortLimiter
CH 1Float 4 RReads the
# SoaGainReductionCurrentShortLimiter
for Channel 1
0x0000bb44  
(47940)SoaGainReductionCurrentShortLimiter
CH 2Float 4 RReads the
# SoaGainReductionCurrentShortLimiter
for Channel 2
0x0000bb48  
(47944)SoaGainReductionCurrentShortLimiter
CH 3Float 4 RReads the
# SoaGainReductionCurrentShortLimiter
for Channel 3
0x0000bb4c  
(47948)SoaGainReductionCurrentShortLimiter
CH 4Float 4 RReads the
# SoaGainReductionCurrentShortLimiter
for Channel 4
# FastMeter W ays SoaGainReductionPowerLimiter
# Reads the SoaGainReductionPowerLimiter
Offset Name Type DimR \
# WDescription
0x0000bb50  
(47952)SoaGainReductionPowerLimiter
CH 1Float 4 RReads the
# SoaGainReductionPowerLimiter
for Channel 1
0x0000bb54  
(47956)SoaGainReductionPowerLimiter
CH 2Float 4 RReads the
# SoaGainReductionPowerLimiter
for Channel 2
0x0000bb58  
(47960)SoaGainReductionPowerLimiter
CH 3Float 4 RReads the
# SoaGainReductionPowerLimiter
for Channel 3
0x0000bb5c  
(47964)SoaGainReductionPowerLimiter
CH 4Float 4 RReads the
# SoaGainReductionPowerLimiter
for Channel 4
# FastMeter W ays UserGainReductionV oltageLimiterPeak
# Reads the UserGainReductionV oltageLimiterPeak
Offset Name Type DimR \
# WDescription
0x0000bb60  
(47968)UserGainReductionV oltageLimiterPeak
CH 1Float 4 RReads the
# UserGainReductionV oltageLimiterPeak
for Channel 1
0x0000bb64  
(47972)UserGainReductionV oltageLimiterPeak
CH 2Float 4 RReads the
# UserGainReductionV oltageLimiterPeak
for Channel 2
0x0000bb68  
(47976)UserGainReductionV oltageLimiterPeak
CH 3Float 4 RReads the
# UserGainReductionV oltageLimiterPeak
for Channel 3
0x0000bb6c  
(47980)UserGainReductionV oltageLimiterPeak
CH 4Float 4 RReads the
# UserGainReductionV oltageLimiterPeak
for Channel 4

# FastMeter W ays UserGainReductionV oltageLimiterRms
# Reads the UserGainReductionV oltageLimiterRms
Offset Name Type DimR \
# WDescription
0x0000bb70  
(47984)UserGainReductionV oltageLimiterRms
CH 1Float 4 RReads the
# UserGainReductionV oltageLimiterRms
for Channel 1
0x0000bb74  
(47988)UserGainReductionV oltageLimiterRms
CH 2Float 4 RReads the
# UserGainReductionV oltageLimiterRms
for Channel 2
0x0000bb78  
(47992)UserGainReductionV oltageLimiterRms
CH 3Float 4 RReads the
# UserGainReductionV oltageLimiterRms
for Channel 3
0x0000bb7c  
(47996)UserGainReductionV oltageLimiterRms
CH 4Float 4 RReads the
# UserGainReductionV oltageLimiterRms
for Channel 4
# FastMeter W ays UserGainReductionClipLimiter
# Reads the UserGainReductionClipLimiter
Offset Name Type DimR \
# WDescription
0x0000bb80  
(48000)UserGainReductionClipLimiter
CH 1Float 4 RReads the
# UserGainReductionClipLimiter for
Channel 1
0x0000bb84  
(48004)UserGainReductionClipLimiter
CH 2Float 4 RReads the
# UserGainReductionClipLimiter for
Channel 2
0x0000bb88  
(48008)UserGainReductionClipLimiter
CH 3Float 4 RReads the
# UserGainReductionClipLimiter for
Channel 3
0x0000bb8c  
(48012)UserGainReductionClipLimiter
CH 4Float 4 RReads the
# UserGainReductionClipLimiter for
Channel 4
# FastMeter W ays UserGainReductionT otal
# Reads the UserGainReductionT otal
Offset Name Type DimR \
# WDescription
0x0000bb90  
(48016)UserGainReductionT otal
CH 1Float 4 RReads the UserGainReductionT otal for
Channel 1
0x0000bb94  
(48020)UserGainReductionT otal
CH 2Float 4 RReads the UserGainReductionT otal for
Channel 2
0x0000bb98  
(48024)UserGainReductionT otal
CH 3Float 4 RReads the UserGainReductionT otal for
Channel 3
0x0000bb9c  
(48028)UserGainReductionT otal
CH 4Float 4 RReads the UserGainReductionT otal for
Channel 4

# FastMeter W ays SignalPresence
# Reads the SignalPresence
Offset Name Type Dim R \ W Description
0x0000bba0  
(48032)SignalPresence CH 1 uint8 1 R Reads the SignalPresence for Channel 1
0x0000bba1  
(48033)SignalPresence CH 2 uint8 1 R Reads the SignalPresence for Channel 2
0x0000bba2  
(48034)SignalPresence CH 3 uint8 1 R Reads the SignalPresence for Channel 3
0x0000bba3  
(48035)SignalPresence CH 4 uint8 1 R Reads the SignalPresence for Channel 4
# FastMeter W ays Headroom
# Reads the Headroom
Offset Name Type Dim R \ W Description
0x0000bba8  
(48040)Headroom CH 1 Float 4 R Reads the Headroom for Channel 1
0x0000bbac  
(48044)Headroom CH 2 Float 4 R Reads the Headroom for Channel 2
0x0000bbb0  
(48048)Headroom CH 3 Float 4 R Reads the Headroom for Channel 3
0x0000bbb4  
(48052)Headroom CH 4 Float 4 R Reads the Headroom for Channel 4
# FastMeter PowerSupply
This area contains the PowerSupply fast meters.
Offset Name Type DimR \
# WDescription
0x0000bbb8  
(48056)SoaGainReductionPowerLimiter Float 4 RReads the
# SoaGainReductionPowerLimiter
0x0000bbbc  
(48060)SoaGainReductionT empT rLimiter Float 4 RReads the
# SoaGainReductionT empT rLimiter
0x0000bbc0  
(48064)SoaGainReductionT empHSLimiter Float 4 RReads the
# SoaGainReductionT empHSLimiter
# Heat Sink

# AutoSetup
This area contains informations related to the autosetup.
# BlockId Start Address End Address Description
# AutoSetup Parameters
Way 10x0000c000 0x0000c00cThis area contains informations related to the
autosetup.
# AutoSetup Parameters
Way 20x0000c00c 0x0000c018This area contains informations related to the
autosetup.
# AutoSetup Parameters
Way 30x0000c018 0x0000c024This area contains informations related to the
autosetup.
# AutoSetup Parameters
Way 40x0000c024 0x0000c030This area contains informations related to the
autosetup.
AutoSetup Results W ay 1 0x0000c100 0x0000c79cThis area contains informations related to
result.
AutoSetup Results W ay 2 0x0000c79c 0x0000ce38This area contains informations related to
result.
AutoSetup Results W ay 3 0x0000ce38 0x0000d4d4This area contains informations related to
result.
AutoSetup Results W ay 4 0x0000d4d4 0x0000db70This area contains informations related to
result.
AutoSetup Start 0x0000ef00 0x0000ef04This area contains informations related to
result.
AutoSetup Parameters W ay 1
This area contains informations related to the autosetup.
Offset Name Type Dim R \ W Description
0x0000c000  
(49152)AutoSetup flag
Parameter W ay 1uint32 4 R\WAutoSetup bitwise flags: LSB flag is used
for `apply` autosetup computed parameters.
0x0000c004  
(49156)Speaker V oltage
Way 1uint32 4 R\W AutoSetup speaker voltage
0x0000c008  
(49160)Sensitivity 1 float 4 R\W AutoSetup sensitivity
AutoSetup Parameters W ay 2
This area contains informations related to the autosetup.
Offset Name Type Dim R \ W Description
0x0000c00c  
(49164)AutoSetup flag
Parameter W ay 2uint32 4 R\WAutoSetup bitwise flags: LSB flag is used
for `apply` autosetup computed parameters.
0x0000c010  
(49168)Speaker V oltage
Way 2uint32 4 R\W AutoSetup speaker voltage
0x0000c014  
(49172)Sensitivity 2 float 4 R\W AutoSetup sensitivity

AutoSetup Parameters W ay 3
This area contains informations related to the autosetup.
Offset Name Type Dim R \ W Description
0x0000c018  
(49176)AutoSetup flag
Parameter W ay 3uint32 4 R\WAutoSetup bitwise flags: LSB flag is used
for `apply` autosetup computed parameters.
0x0000c01c  
(49180)Speaker V oltage
Way 3uint32 4 R\W AutoSetup speaker voltage
0x0000c020  
(49184)Sensitivity 3 float 4 R\W AutoSetup sensitivity
AutoSetup Parameters W ay 4
This area contains informations related to the autosetup.
Offset Name Type Dim R \ W Description
0x0000c024  
(49188)AutoSetup flag
Parameter W ay 4uint32 4 R\WAutoSetup bitwise flags: LSB flag is used
for `apply` autosetup computed parameters.
0x0000c028  
(49192)Speaker V oltage
Way 4uint32 4 R\W AutoSetup speaker voltage
0x0000c02c  
(49196)Sensitivity 4 float 4 R\W AutoSetup sensitivity
AutoSetup Results W ay 1
This area contains informations related to result.
# BlockId Start Address End Address Description
AutoSetup Settings Result 0x0000c100 0x0000c134 AutoSetup Settings Result
AutoSetup Impedance Result 0x0000c134 0x0000c79c AutoSetup Impedance Result

# AutoSetup Settings Result
# AutoSetup Settings Result
Offset Name Type Dim R \ W Description
0x0000c100  
(49408)AutoSetup
impMeasChannelDone 1uint32 4 R\WAutoSetup
impMeasChannelDone
0x0000c104  
(49412)AutoSetup stateResult 1 uint32 4 R\W AutoSetup stateResult
0x0000c108  
(49416)AutoSetup gain 1 float 4 R\W AutoSetup gain
0x0000c10c  
(49420)AutoSetup hiPassFc 1 float 4 R\W AutoSetup hiPassFc
0x0000c1 10 
(49424)AutoSetup hiPass Slope 1 uint32 4 R\W AutoSetup hiPass Slope
0x0000c1 14 
(49428)AutoSetup hiPass type 1 uint32 4 R\W AutoSetup hiPass type
0x0000c1 18 
(49432)AutoSetup zNom 1 float 4 R\W AutoSetup zNom
0x0000c1 1c 
(49436)AutoSetup peakLimiterThr 1 float 4 R\W AutoSetup peakLimiterThr
0x0000c120  
(49440)AutoSetup
peakLimiterAttackT ime 1float 4 R\WAutoSetup
peakLimiterAttackT ime
0x0000c124  
(49444)AutoSetup
peakLimiterReleaseT ime 1float 4 R\WAutoSetup
peakLimiterReleaseT ime
0x0000c128  
(49448)AutoSetup rmsLimiterThr 1 float 4 R\W AutoSetup rmsLimiterThr
0x0000c12c  
(49452)AutoSetup rmsLimiterAttackT ime
1float 4 R\WAutoSetup
rmsLimiterAttackT ime
0x0000c130  
(49456)AutoSetup
rmsLimiterReleaseT ime 1float 4 R\WAutoSetup
rmsLimiterReleaseT ime
# AutoSetup Impedance Result
# AutoSetup Impedance Result
Offset Name Type Dim R \ W Description
0x0000c134  
(49460)AutoSetup Impedance
Channeluint32 4 R\WAutoSetup Impedance
# Channel
0x0000c138  
(49464)AutoSetup Impedance
NumFrequint32 4 R\WAutoSetup Impedance
# NumFreq
0x0000c13c  
(49468)AutoSetup Impedance Freq float[136] 544 R\WAutoSetup Impedance
# Freq
0x0000c35c  
(50012)AutoSetup Impedance Z complex_t[136] 1088 R\WAutoSetup Impedance
Z

AutoSetup Results W ay 2
This area contains informations related to result.
# BlockId Start Address End Address Description
AutoSetup Settings Result 0x0000c79c 0x0000c7d0 AutoSetup Settings Result
AutoSetup Impedance Result 0x0000c7d0 0x0000ce38 AutoSetup Impedance Result
# AutoSetup Settings Result
# AutoSetup Settings Result
Offset Name Type Dim R \ W Description
0x0000c79c  
(51100)AutoSetup
impMeasChannelDone 1uint32 4 R\WAutoSetup
impMeasChannelDone
0x0000c7a0  
(51104)AutoSetup stateResult 1 uint32 4 R\W AutoSetup stateResult
0x0000c7a4  
(51108)AutoSetup gain 1 float 4 R\W AutoSetup gain
0x0000c7a8  
(51112)AutoSetup hiPassFc 1 float 4 R\W AutoSetup hiPassFc
0x0000c7ac  
(51116)AutoSetup hiPass Slope 1 uint32 4 R\W AutoSetup hiPass Slope
0x0000c7b0  
(51120)AutoSetup hiPass type 1 uint32 4 R\W AutoSetup hiPass type
0x0000c7b4  
(51124)AutoSetup zNom 1 float 4 R\W AutoSetup zNom
0x0000c7b8  
(51128)AutoSetup peakLimiterThr 1 float 4 R\W AutoSetup peakLimiterThr
0x0000c7bc  
(51132)AutoSetup
peakLimiterAttackT ime 1float 4 R\WAutoSetup
peakLimiterAttackT ime
0x0000c7c0  
(51136)AutoSetup
peakLimiterReleaseT ime 1float 4 R\WAutoSetup
peakLimiterReleaseT ime
0x0000c7c4  
(51140)AutoSetup rmsLimiterThr 1 float 4 R\W AutoSetup rmsLimiterThr
0x0000c7c8  
(51144)AutoSetup rmsLimiterAttackT ime
1float 4 R\WAutoSetup
rmsLimiterAttackT ime
0x0000c7cc  
(51148)AutoSetup
rmsLimiterReleaseT ime 1float 4 R\WAutoSetup
rmsLimiterReleaseT ime

# AutoSetup Impedance Result
# AutoSetup Impedance Result
Offset Name Type Dim R \ W Description
0x0000c7d0  
(51152)AutoSetup Impedance
Channeluint32 4 R\WAutoSetup Impedance
# Channel
0x0000c7d4  
(51156)AutoSetup Impedance
NumFrequint32 4 R\WAutoSetup Impedance
# NumFreq
0x0000c7d8  
(51160)AutoSetup Impedance Freq float[136] 544 R\WAutoSetup Impedance
# Freq
0x0000c9f8  
(51704)AutoSetup Impedance Z complex_t[136] 1088 R\WAutoSetup Impedance
Z
AutoSetup Results W ay 3
This area contains informations related to result.
# BlockId Start Address End Address Description
AutoSetup Settings Result 0x0000ce38 0x0000ce6c AutoSetup Settings Result
AutoSetup Impedance Result 0x0000ce6c 0x0000d4d4 AutoSetup Impedance Result

# AutoSetup Settings Result
# AutoSetup Settings Result
Offset Name Type Dim R \ W Description
0x0000ce38  
(52792)AutoSetup
impMeasChannelDone 1uint32 4 R\WAutoSetup
impMeasChannelDone
0x0000ce3c  
(52796)AutoSetup stateResult 1 uint32 4 R\W AutoSetup stateResult
0x0000ce40  
(52800)AutoSetup gain 1 float 4 R\W AutoSetup gain
0x0000ce44  
(52804)AutoSetup hiPassFc 1 float 4 R\W AutoSetup hiPassFc
0x0000ce48  
(52808)AutoSetup hiPass Slope 1 uint32 4 R\W AutoSetup hiPass Slope
0x0000ce4c  
(52812)AutoSetup hiPass type 1 uint32 4 R\W AutoSetup hiPass type
0x0000ce50  
(52816)AutoSetup zNom 1 float 4 R\W AutoSetup zNom
0x0000ce54  
(52820)AutoSetup peakLimiterThr 1 float 4 R\W AutoSetup peakLimiterThr
0x0000ce58  
(52824)AutoSetup
peakLimiterAttackT ime 1float 4 R\WAutoSetup
peakLimiterAttackT ime
0x0000ce5c  
(52828)AutoSetup
peakLimiterReleaseT ime 1float 4 R\WAutoSetup
peakLimiterReleaseT ime
0x0000ce60  
(52832)AutoSetup rmsLimiterThr 1 float 4 R\W AutoSetup rmsLimiterThr
0x0000ce64  
(52836)AutoSetup rmsLimiterAttackT ime
1float 4 R\WAutoSetup
rmsLimiterAttackT ime
0x0000ce68  
(52840)AutoSetup
rmsLimiterReleaseT ime 1float 4 R\WAutoSetup
rmsLimiterReleaseT ime
# AutoSetup Impedance Result
# AutoSetup Impedance Result
Offset Name Type Dim R \ W Description
0x0000ce6c  
(52844)AutoSetup Impedance
Channeluint32 4 R\WAutoSetup Impedance
# Channel
0x0000ce70  
(52848)AutoSetup Impedance
NumFrequint32 4 R\WAutoSetup Impedance
# NumFreq
0x0000ce74  
(52852)AutoSetup Impedance
Freqfloat[136] 544 R\WAutoSetup Impedance
# Freq
0x0000d094  
(53396)AutoSetup Impedance Z complex_t[136] 1088 R\WAutoSetup Impedance
Z

AutoSetup Results W ay 4
This area contains informations related to result.
# BlockId Start Address End Address Description
AutoSetup Settings Result 0x0000d4d4 0x0000d508 AutoSetup Settings Result
AutoSetup Impedance Result 0x0000d508 0x0000db70 AutoSetup Impedance Result
# AutoSetup Settings Result
# AutoSetup Settings Result
Offset Name Type Dim R \ W Description
0x0000d4d4  
(54484)AutoSetup
impMeasChannelDone 1uint32 4 R\WAutoSetup
impMeasChannelDone
0x0000d4d8  
(54488)AutoSetup stateResult 1 uint32 4 R\W AutoSetup stateResult
0x0000d4dc  
(54492)AutoSetup gain 1 float 4 R\W AutoSetup gain
0x0000d4e0  
(54496)AutoSetup hiPassFc 1 float 4 R\W AutoSetup hiPassFc
0x0000d4e4  
(54500)AutoSetup hiPass Slope 1 uint32 4 R\W AutoSetup hiPass Slope
0x0000d4e8  
(54504)AutoSetup hiPass type 1 uint32 4 R\W AutoSetup hiPass type
0x0000d4ec  
(54508)AutoSetup zNom 1 float 4 R\W AutoSetup zNom
0x0000d4f0  
(54512)AutoSetup peakLimiterThr 1 float 4 R\W AutoSetup peakLimiterThr
0x0000d4f4  
(54516)AutoSetup
peakLimiterAttackT ime 1float 4 R\WAutoSetup
peakLimiterAttackT ime
0x0000d4f8  
(54520)AutoSetup
peakLimiterReleaseT ime 1float 4 R\WAutoSetup
peakLimiterReleaseT ime
0x0000d4fc  
(54524)AutoSetup rmsLimiterThr 1 float 4 R\W AutoSetup rmsLimiterThr
0x0000d500  
(54528)AutoSetup rmsLimiterAttackT ime
1float 4 R\WAutoSetup
rmsLimiterAttackT ime
0x0000d504  
(54532)AutoSetup
rmsLimiterReleaseT ime 1float 4 R\WAutoSetup
rmsLimiterReleaseT ime

# AutoSetup Impedance Result
# AutoSetup Impedance Result
Offset Name Type Dim R \ W Description
0x0000d508  
(54536)AutoSetup Impedance
Channeluint32 4 R\WAutoSetup Impedance
# Channel
0x0000d50c  
(54540)AutoSetup Impedance
NumFrequint32 4 R\WAutoSetup Impedance
# NumFreq
0x0000d510  
(54544)AutoSetup Impedance
Freqfloat[136] 544 R\WAutoSetup Impedance
# Freq
0x0000d730  
(55088)AutoSetup Impedance Z complex_t[136] 1088 R\WAutoSetup Impedance
Z
# AutoSetup Start
This area contains informations related to result.
Offset Name Type Dim R \ W Description
0x0000ef00  
(61184)AutoSetup Start on
channeluint32 4 R\WWrite here the channel where init the
AutoSetup -> eg: `0` | `1` | `2` |`3`
# Zone Block
This area contains informations related to the amplifiers zones.
# BlockId Start Address End Address Description
# Zone Common
Settings0x0000f000 0x0000f038This area contains the zone block common
settings.
Zone EQ 0x0000f100 0x0000f340 This area contains the zone eq settings.
# Zone Common Settings
This area contains the zone block common settings.
# BlockId Start Address End Address Description
Enable 0x0000f000 0x0000f004 The zone enable.
Mute 0x0000f004 0x0000f008 The zone mute.
Gain 0x0000f008 0x0000f018 The zone gain in linear .
Source GUID 0x0000f018 0x0000f028 The zone source GUID.
Zone GUID 0x0000f028 0x0000f038 The zone GUID.

# Enable
The zone enable.
Offset Name Type Dim R \ W Description
0x0000f000  
(61440)Zone Enable 1 uint8 1 R\W The zone enable CH 1.
0x0000f001  
(61441)Zone Enable 2 uint8 1 R\W The zone enable CH 2.
0x0000f002  
(61442)Zone Enable 3 uint8 1 R\W The zone enable CH 3.
0x0000f003  
(61443)Zone Enable 4 uint8 1 R\W The zone enable CH 4.
# Mute
The zone mute.
Offset Name Type Dim R \ W Description
0x0000f004  
(61444)Zone Mute 1 uint8 1 R\W The zone mute CH 1.
0x0000f005  
(61445)Zone Mute 2 uint8 1 R\W The zone mute CH 2.
0x0000f006  
(61446)Zone Mute 3 uint8 1 R\W The zone mute CH 3.
0x0000f007  
(61447)Zone Mute 4 uint8 1 R\W The zone mute CH 4.
# Gain
The zone gain in linear .
Offset Name Type Dim R \ W Description
0x0000f008  
(61448)Zone Gain 1 Float 4 R\W The zone gain in linear CH 1.
0x0000f00c  
(61452)Zone Gain 2 Float 4 R\W The zone gain in linear CH 2.
0x0000f010  
(61456)Zone Gain 3 Float 4 R\W The zone gain in linear CH 3.
0x0000f014  
(61460)Zone Gain 4 Float 4 R\W The zone gain in linear CH 4.

# Source GUID
The zone source GUID.
Offset Name Type Dim R \ W Description
0x0000f018  
(61464)Source GUID 1 uint32 4 R\W The source GUID CH 1.
0x0000f01c  
(61468)Source GUID 2 uint32 4 R\W The source GUID CH 2.
0x0000f020  
(61472)Source GUID 3 uint32 4 R\W The source GUID CH 3.
0x0000f024  
(61476)Source GUID 4 uint32 4 R\W The source GUID CH 4.
# Zone GUID
The zone GUID.
Offset Name Type Dim R \ W Description
0x0000f028  
(61480)Zone GUID 1 uint32 4 R\W The zone GUID CH 1.
0x0000f02c  
(61484)Zone GUID 2 uint32 4 R\W The zone GUID CH 2.
0x0000f030  
(61488)Zone GUID 3 uint32 4 R\W The zone GUID CH 3.
0x0000f034  
(61492)Zone GUID 4 uint32 4 R\W The zone GUID CH 4.
# Zone EQ
This area contains the zone eq settings.
# BlockId Start Address End Address Description
Source EQ Channel 1 0x0000f100 0x0000f130 This area contains the source eq settings.
Source EQ Channel 2 0x0000f130 0x0000f160 This area contains the source eq settings.
Source EQ Channel 3 0x0000f160 0x0000f190 This area contains the source eq settings.
Source EQ Channel 4 0x0000f190 0x0000f1c0 This area contains the source eq settings.
Zone EQ Channel 1 0x0000f1c0 0x0000f220 This area contains the zone eq settings.
Zone EQ Channel 2 0x0000f220 0x0000f280 This area contains the zone eq settings.
Zone EQ Channel 3 0x0000f280 0x0000f2e0 This area contains the zone eq settings.
Zone EQ Channel 4 0x0000f2e0 0x0000f340 This area contains the zone eq settings.
Source EQ Channel 1
This area contains the source eq settings.
# BlockId Start Address End Address Description
Source Eq Channel 1 BiQuad 1
settings0x0000f100 0x0000f1 18This area contains the source equalizer
biQuad settings.
Source Eq Channel 1 BiQuad 2
settings0x0000f1 18 0x0000f130This area contains the source equalizer
biQuad settings.

Source Eq Channel 1 BiQuad 1 settings
This area contains the source equalizer biQuad settings.
Offset Name Type Dim R \ W Description
0x0000f100  
(61696)Enabled uint32 4 R\W The enable flag
0x0000f104  
(61700)Type uint32 4 R\WThe filter type. V alid values are:  
# Values Type
0 Peaking
11 Low-Shelving
12 High-Shelving
13 Low-pass
14 High-pass
15 BandPass
16 Band-stop
17 All-pass
0x0000f108  
(61704)Q Float 4 R\W The filter Q
0x0000f10c  
(61708)Slope Float 4 R\W The filter Slope
0x0000f1 10 
(61712)Frequency uint32 4 R\W The filter frequency
0x0000f1 14 
(61716)Gain Float 4 R\W The linear gain
Source Eq Channel 1 BiQuad 2 settings
This area contains the source equalizer biQuad settings.
Offset Name Type Dim R \ W Description
0x0000f1 18 
(61720)Enabled uint32 4 R\W The enable flag
0x0000f1 1c 
(61724)Type uint32 4 R\WThe filter type. V alid values are:  
# Values Type
0 Peaking
11 Low-Shelving
12 High-Shelving
13 Low-pass
14 High-pass
15 BandPass
16 Band-stop
17 All-pass
0x0000f120  
(61728)Q Float 4 R\W The filter Q
0x0000f124  
(61732)Slope Float 4 R\W The filter Slope
0x0000f128  
(61736)Frequency uint32 4 R\W The filter frequency
0x0000f12c  
(61740)Gain Float 4 R\W The linear gain

Source EQ Channel 2
This area contains the source eq settings.
# BlockId Start Address End Address Description
Source Eq Channel 2 BiQuad 1
settings0x0000f130 0x0000f148This area contains the source equalizer
biQuad settings.
Source Eq Channel 2 BiQuad 2
settings0x0000f148 0x0000f160This area contains the source equalizer
biQuad settings.
Source Eq Channel 2 BiQuad 1 settings
This area contains the source equalizer biQuad settings.
Offset Name Type Dim R \ W Description
0x0000f130  
(61744)Enabled uint32 4 R\W The enable flag
0x0000f134  
(61748)Type uint32 4 R\WThe filter type. V alid values are:  
# Values Type
0 Peaking
11 Low-Shelving
12 High-Shelving
13 Low-pass
14 High-pass
15 BandPass
16 Band-stop
17 All-pass
0x0000f138  
(61752)Q Float 4 R\W The filter Q
0x0000f13c  
(61756)Slope Float 4 R\W The filter Slope
0x0000f140  
(61760)Frequency uint32 4 R\W The filter frequency
0x0000f144  
(61764)Gain Float 4 R\W The linear gain

Source Eq Channel 2 BiQuad 2 settings
This area contains the source equalizer biQuad settings.
Offset Name Type Dim R \ W Description
0x0000f148  
(61768)Enabled uint32 4 R\W The enable flag
0x0000f14c  
(61772)Type uint32 4 R\WThe filter type. V alid values are:  
# Values Type
0 Peaking
11 Low-Shelving
12 High-Shelving
13 Low-pass
14 High-pass
15 BandPass
16 Band-stop
17 All-pass
0x0000f150  
(61776)Q Float 4 R\W The filter Q
0x0000f154  
(61780)Slope Float 4 R\W The filter Slope
0x0000f158  
(61784)Frequency uint32 4 R\W The filter frequency
0x0000f15c  
(61788)Gain Float 4 R\W The linear gain
Source EQ Channel 3
This area contains the source eq settings.
# BlockId Start Address End Address Description
Source Eq Channel 3 BiQuad 1
settings0x0000f160 0x0000f178This area contains the source equalizer
biQuad settings.
Source Eq Channel 3 BiQuad 2
settings0x0000f178 0x0000f190This area contains the source equalizer
biQuad settings.

Source Eq Channel 3 BiQuad 1 settings
This area contains the source equalizer biQuad settings.
Offset Name Type Dim R \ W Description
0x0000f160  
(61792)Enabled uint32 4 R\W The enable flag
0x0000f164  
(61796)Type uint32 4 R\WThe filter type. V alid values are:  
# Values Type
0 Peaking
11 Low-Shelving
12 High-Shelving
13 Low-pass
14 High-pass
15 BandPass
16 Band-stop
17 All-pass
0x0000f168  
(61800)Q Float 4 R\W The filter Q
0x0000f16c  
(61804)Slope Float 4 R\W The filter Slope
0x0000f170  
(61808)Frequency uint32 4 R\W The filter frequency
0x0000f174  
(61812)Gain Float 4 R\W The linear gain
Source Eq Channel 3 BiQuad 2 settings
This area contains the source equalizer biQuad settings.
Offset Name Type Dim R \ W Description
0x0000f178  
(61816)Enabled uint32 4 R\W The enable flag
0x0000f17c  
(61820)Type uint32 4 R\WThe filter type. V alid values are:  
# Values Type
0 Peaking
11 Low-Shelving
12 High-Shelving
13 Low-pass
14 High-pass
15 BandPass
16 Band-stop
17 All-pass
0x0000f180  
(61824)Q Float 4 R\W The filter Q
0x0000f184  
(61828)Slope Float 4 R\W The filter Slope
0x0000f188  
(61832)Frequency uint32 4 R\W The filter frequency
0x0000f18c  
(61836)Gain Float 4 R\W The linear gain

Source EQ Channel 4
This area contains the source eq settings.
# BlockId Start Address End Address Description
Source Eq Channel 4 BiQuad 1
settings0x0000f190 0x0000f1a8This area contains the source equalizer
biQuad settings.
Source Eq Channel 4 BiQuad 2
settings0x0000f1a8 0x0000f1c0This area contains the source equalizer
biQuad settings.
Source Eq Channel 4 BiQuad 1 settings
This area contains the source equalizer biQuad settings.
Offset Name Type Dim R \ W Description
0x0000f190  
(61840)Enabled uint32 4 R\W The enable flag
0x0000f194  
(61844)Type uint32 4 R\WThe filter type. V alid values are:  
# Values Type
0 Peaking
11 Low-Shelving
12 High-Shelving
13 Low-pass
14 High-pass
15 BandPass
16 Band-stop
17 All-pass
0x0000f198  
(61848)Q Float 4 R\W The filter Q
0x0000f19c  
(61852)Slope Float 4 R\W The filter Slope
0x0000f1a0  
(61856)Frequency uint32 4 R\W The filter frequency
0x0000f1a4  
(61860)Gain Float 4 R\W The linear gain

Source Eq Channel 4 BiQuad 2 settings
This area contains the source equalizer biQuad settings.
Offset Name Type Dim R \ W Description
0x0000f1a8  
(61864)Enabled uint32 4 R\W The enable flag
0x0000f1ac  
(61868)Type uint32 4 R\WThe filter type. V alid values are:  
# Values Type
0 Peaking
11 Low-Shelving
12 High-Shelving
13 Low-pass
14 High-pass
15 BandPass
16 Band-stop
17 All-pass
0x0000f1b0  
(61872)Q Float 4 R\W The filter Q
0x0000f1b4  
(61876)Slope Float 4 R\W The filter Slope
0x0000f1b8  
(61880)Frequency uint32 4 R\W The filter frequency
0x0000f1bc  
(61884)Gain Float 4 R\W The linear gain
Zone EQ Channel 1
This area contains the zone eq settings.
# BlockId Start Address End Address Description
Zone Eq Channel 1 BiQuad 1
settings0x0000f1c0 0x0000f1d8This area contains the zone equalizer
biQuad settings.
Zone Eq Channel 1 BiQuad 2
settings0x0000f1d8 0x0000f1f0This area contains the zone equalizer
biQuad settings.
Zone Eq Channel 1 BiQuad 3
settings0x0000f1f0 0x0000f208This area contains the zone equalizer
biQuad settings.
Zone Eq Channel 1 BiQuad 4
settings0x0000f208 0x0000f220This area contains the zone equalizer
biQuad settings.

Zone Eq Channel 1 BiQuad 1 settings
This area contains the zone equalizer biQuad settings.
Offset Name Type Dim R \ W Description
0x0000f1c0  
(61888)Enabled uint32 4 R\W The enable flag
0x0000f1c4  
(61892)Type uint32 4 R\WThe filter type. V alid values are:  
# Values Type
0 Peaking
11 Low-Shelving
12 High-Shelving
13 Low-pass
14 High-pass
15 BandPass
16 Band-stop
17 All-pass
0x0000f1c8  
(61896)Q Float 4 R\W The filter Q
0x0000f1cc  
(61900)Slope Float 4 R\W The filter Slope
0x0000f1d0  
(61904)Frequency uint32 4 R\W The filter frequency
0x0000f1d4  
(61908)Gain Float 4 R\W The linear gain
Zone Eq Channel 1 BiQuad 2 settings
This area contains the zone equalizer biQuad settings.
Offset Name Type Dim R \ W Description
0x0000f1d8  
(61912)Enabled uint32 4 R\W The enable flag
0x0000f1dc  
(61916)Type uint32 4 R\WThe filter type. V alid values are:  
# Values Type
0 Peaking
11 Low-Shelving
12 High-Shelving
13 Low-pass
14 High-pass
15 BandPass
16 Band-stop
17 All-pass
0x0000f1e0  
(61920)Q Float 4 R\W The filter Q
0x0000f1e4  
(61924)Slope Float 4 R\W The filter Slope
0x0000f1e8  
(61928)Frequency uint32 4 R\W The filter frequency
0x0000f1ec  
(61932)Gain Float 4 R\W The linear gain

Zone Eq Channel 1 BiQuad 3 settings
This area contains the zone equalizer biQuad settings.
Offset Name Type Dim R \ W Description
0x0000f1f0  
(61936)Enabled uint32 4 R\W The enable flag
0x0000f1f4  
(61940)Type uint32 4 R\WThe filter type. V alid values are:  
# Values Type
0 Peaking
11 Low-Shelving
12 High-Shelving
13 Low-pass
14 High-pass
15 BandPass
16 Band-stop
17 All-pass
0x0000f1f8  
(61944)Q Float 4 R\W The filter Q
0x0000f1fc  
(61948)Slope Float 4 R\W The filter Slope
0x0000f200  
(61952)Frequency uint32 4 R\W The filter frequency
0x0000f204  
(61956)Gain Float 4 R\W The linear gain
Zone Eq Channel 1 BiQuad 4 settings
This area contains the zone equalizer biQuad settings.
Offset Name Type Dim R \ W Description
0x0000f208  
(61960)Enabled uint32 4 R\W The enable flag
0x0000f20c  
(61964)Type uint32 4 R\WThe filter type. V alid values are:  
# Values Type
0 Peaking
11 Low-Shelving
12 High-Shelving
13 Low-pass
14 High-pass
15 BandPass
16 Band-stop
17 All-pass
0x0000f210  
(61968)Q Float 4 R\W The filter Q
0x0000f214  
(61972)Slope Float 4 R\W The filter Slope
0x0000f218  
(61976)Frequency uint32 4 R\W The filter frequency
0x0000f21c  
(61980)Gain Float 4 R\W The linear gain

Zone EQ Channel 2
This area contains the zone eq settings.
# BlockId Start Address End Address Description
Zone Eq Channel 2 BiQuad 1
settings0x0000f220 0x0000f238This area contains the zone equalizer
biQuad settings.
Zone Eq Channel 2 BiQuad 2
settings0x0000f238 0x0000f250This area contains the zone equalizer
biQuad settings.
Zone Eq Channel 2 BiQuad 3
settings0x0000f250 0x0000f268This area contains the zone equalizer
biQuad settings.
Zone Eq Channel 2 BiQuad 4
settings0x0000f268 0x0000f280This area contains the zone equalizer
biQuad settings.
Zone Eq Channel 2 BiQuad 1 settings
This area contains the zone equalizer biQuad settings.
Offset Name Type Dim R \ W Description
0x0000f220  
(61984)Enabled uint32 4 R\W The enable flag
0x0000f224  
(61988)Type uint32 4 R\WThe filter type. V alid values are:  
# Values Type
0 Peaking
11 Low-Shelving
12 High-Shelving
13 Low-pass
14 High-pass
15 BandPass
16 Band-stop
17 All-pass
0x0000f228  
(61992)Q Float 4 R\W The filter Q
0x0000f22c  
(61996)Slope Float 4 R\W The filter Slope
0x0000f230  
(62000)Frequency uint32 4 R\W The filter frequency
0x0000f234  
(62004)Gain Float 4 R\W The linear gain

Zone Eq Channel 2 BiQuad 2 settings
This area contains the zone equalizer biQuad settings.
Offset Name Type Dim R \ W Description
0x0000f238  
(62008)Enabled uint32 4 R\W The enable flag
0x0000f23c  
(62012)Type uint32 4 R\WThe filter type. V alid values are:  
# Values Type
0 Peaking
11 Low-Shelving
12 High-Shelving
13 Low-pass
14 High-pass
15 BandPass
16 Band-stop
17 All-pass
0x0000f240  
(62016)Q Float 4 R\W The filter Q
0x0000f244  
(62020)Slope Float 4 R\W The filter Slope
0x0000f248  
(62024)Frequency uint32 4 R\W The filter frequency
0x0000f24c  
(62028)Gain Float 4 R\W The linear gain
Zone Eq Channel 2 BiQuad 3 settings
This area contains the zone equalizer biQuad settings.
Offset Name Type Dim R \ W Description
0x0000f250  
(62032)Enabled uint32 4 R\W The enable flag
0x0000f254  
(62036)Type uint32 4 R\WThe filter type. V alid values are:  
# Values Type
0 Peaking
11 Low-Shelving
12 High-Shelving
13 Low-pass
14 High-pass
15 BandPass
16 Band-stop
17 All-pass
0x0000f258  
(62040)Q Float 4 R\W The filter Q
0x0000f25c  
(62044)Slope Float 4 R\W The filter Slope
0x0000f260  
(62048)Frequency uint32 4 R\W The filter frequency
0x0000f264  
(62052)Gain Float 4 R\W The linear gain

Zone Eq Channel 2 BiQuad 4 settings
This area contains the zone equalizer biQuad settings.
Offset Name Type Dim R \ W Description
0x0000f268  
(62056)Enabled uint32 4 R\W The enable flag
0x0000f26c  
(62060)Type uint32 4 R\WThe filter type. V alid values are:  
# Values Type
0 Peaking
11 Low-Shelving
12 High-Shelving
13 Low-pass
14 High-pass
15 BandPass
16 Band-stop
17 All-pass
0x0000f270  
(62064)Q Float 4 R\W The filter Q
0x0000f274  
(62068)Slope Float 4 R\W The filter Slope
0x0000f278  
(62072)Frequency uint32 4 R\W The filter frequency
0x0000f27c  
(62076)Gain Float 4 R\W The linear gain
Zone EQ Channel 3
This area contains the zone eq settings.
# BlockId Start Address End Address Description
Zone Eq Channel 3 BiQuad 1
settings0x0000f280 0x0000f298This area contains the zone equalizer
biQuad settings.
Zone Eq Channel 3 BiQuad 2
settings0x0000f298 0x0000f2b0This area contains the zone equalizer
biQuad settings.
Zone Eq Channel 3 BiQuad 3
settings0x0000f2b0 0x0000f2c8This area contains the zone equalizer
biQuad settings.
Zone Eq Channel 3 BiQuad 4
settings0x0000f2c8 0x0000f2e0This area contains the zone equalizer
biQuad settings.

Zone Eq Channel 3 BiQuad 1 settings
This area contains the zone equalizer biQuad settings.
Offset Name Type Dim R \ W Description
0x0000f280  
(62080)Enabled uint32 4 R\W The enable flag
0x0000f284  
(62084)Type uint32 4 R\WThe filter type. V alid values are:  
# Values Type
0 Peaking
11 Low-Shelving
12 High-Shelving
13 Low-pass
14 High-pass
15 BandPass
16 Band-stop
17 All-pass
0x0000f288  
(62088)Q Float 4 R\W The filter Q
0x0000f28c  
(62092)Slope Float 4 R\W The filter Slope
0x0000f290  
(62096)Frequency uint32 4 R\W The filter frequency
0x0000f294  
(62100)Gain Float 4 R\W The linear gain
Zone Eq Channel 3 BiQuad 2 settings
This area contains the zone equalizer biQuad settings.
Offset Name Type Dim R \ W Description
0x0000f298  
(62104)Enabled uint32 4 R\W The enable flag
0x0000f29c  
(62108)Type uint32 4 R\WThe filter type. V alid values are:  
# Values Type
0 Peaking
11 Low-Shelving
12 High-Shelving
13 Low-pass
14 High-pass
15 BandPass
16 Band-stop
17 All-pass
0x0000f2a0  
(62112)Q Float 4 R\W The filter Q
0x0000f2a4  
(62116)Slope Float 4 R\W The filter Slope
0x0000f2a8  
(62120)Frequency uint32 4 R\W The filter frequency
0x0000f2ac  
(62124)Gain Float 4 R\W The linear gain

Zone Eq Channel 3 BiQuad 3 settings
This area contains the zone equalizer biQuad settings.
Offset Name Type Dim R \ W Description
0x0000f2b0  
(62128)Enabled uint32 4 R\W The enable flag
0x0000f2b4  
(62132)Type uint32 4 R\WThe filter type. V alid values are:  
# Values Type
0 Peaking
11 Low-Shelving
12 High-Shelving
13 Low-pass
14 High-pass
15 BandPass
16 Band-stop
17 All-pass
0x0000f2b8  
(62136)Q Float 4 R\W The filter Q
0x0000f2bc  
(62140)Slope Float 4 R\W The filter Slope
0x0000f2c0  
(62144)Frequency uint32 4 R\W The filter frequency
0x0000f2c4  
(62148)Gain Float 4 R\W The linear gain
Zone Eq Channel 3 BiQuad 4 settings
This area contains the zone equalizer biQuad settings.
Offset Name Type Dim R \ W Description
0x0000f2c8  
(62152)Enabled uint32 4 R\W The enable flag
0x0000f2cc  
(62156)Type uint32 4 R\WThe filter type. V alid values are:  
# Values Type
0 Peaking
11 Low-Shelving
12 High-Shelving
13 Low-pass
14 High-pass
15 BandPass
16 Band-stop
17 All-pass
0x0000f2d0  
(62160)Q Float 4 R\W The filter Q
0x0000f2d4  
(62164)Slope Float 4 R\W The filter Slope
0x0000f2d8  
(62168)Frequency uint32 4 R\W The filter frequency
0x0000f2dc  
(62172)Gain Float 4 R\W The linear gain

Zone EQ Channel 4
This area contains the zone eq settings.
# BlockId Start Address End Address Description
Zone Eq Channel 4 BiQuad 1
settings0x0000f2e0 0x0000f2f8This area contains the zone equalizer
biQuad settings.
Zone Eq Channel 4 BiQuad 2
settings0x0000f2f8 0x0000f310This area contains the zone equalizer
biQuad settings.
Zone Eq Channel 4 BiQuad 3
settings0x0000f310 0x0000f328This area contains the zone equalizer
biQuad settings.
Zone Eq Channel 4 BiQuad 4
settings0x0000f328 0x0000f340This area contains the zone equalizer
biQuad settings.
Zone Eq Channel 4 BiQuad 1 settings
This area contains the zone equalizer biQuad settings.
Offset Name Type Dim R \ W Description
0x0000f2e0  
(62176)Enabled uint32 4 R\W The enable flag
0x0000f2e4  
(62180)Type uint32 4 R\WThe filter type. V alid values are:  
# Values Type
0 Peaking
11 Low-Shelving
12 High-Shelving
13 Low-pass
14 High-pass
15 BandPass
16 Band-stop
17 All-pass
0x0000f2e8  
(62184)Q Float 4 R\W The filter Q
0x0000f2ec  
(62188)Slope Float 4 R\W The filter Slope
0x0000f2f0  
(62192)Frequency uint32 4 R\W The filter frequency
0x0000f2f4  
(62196)Gain Float 4 R\W The linear gain

Zone Eq Channel 4 BiQuad 2 settings
This area contains the zone equalizer biQuad settings.
Offset Name Type Dim R \ W Description
0x0000f2f8  
(62200)Enabled uint32 4 R\W The enable flag
0x0000f2fc  
(62204)Type uint32 4 R\WThe filter type. V alid values are:  
# Values Type
0 Peaking
11 Low-Shelving
12 High-Shelving
13 Low-pass
14 High-pass
15 BandPass
16 Band-stop
17 All-pass
0x0000f300  
(62208)Q Float 4 R\W The filter Q
0x0000f304  
(62212)Slope Float 4 R\W The filter Slope
0x0000f308  
(62216)Frequency uint32 4 R\W The filter frequency
0x0000f30c  
(62220)Gain Float 4 R\W The linear gain
Zone Eq Channel 4 BiQuad 3 settings
This area contains the zone equalizer biQuad settings.
Offset Name Type Dim R \ W Description
0x0000f310  
(62224)Enabled uint32 4 R\W The enable flag
0x0000f314  
(62228)Type uint32 4 R\WThe filter type. V alid values are:  
# Values Type
0 Peaking
11 Low-Shelving
12 High-Shelving
13 Low-pass
14 High-pass
15 BandPass
16 Band-stop
17 All-pass
0x0000f318  
(62232)Q Float 4 R\W The filter Q
0x0000f31c  
(62236)Slope Float 4 R\W The filter Slope
0x0000f320  
(62240)Frequency uint32 4 R\W The filter frequency
0x0000f324  
(62244)Gain Float 4 R\W The linear gain

Zone Eq Channel 4 BiQuad 4 settings
This area contains the zone equalizer biQuad settings.
Offset Name Type Dim R \ W Description
0x0000f328  
(62248)Enabled uint32 4 R\W The enable flag
0x0000f32c  
(62252)Type uint32 4 R\WThe filter type. V alid values are:  
# Values Type
0 Peaking
11 Low-Shelving
12 High-Shelving
13 Low-pass
14 High-pass
15 BandPass
16 Band-stop
17 All-pass
0x0000f330  
(62256)Q Float 4 R\W The filter Q
0x0000f334  
(62260)Slope Float 4 R\W The filter Slope
0x0000f338  
(62264)Frequency uint32 4 R\W The filter frequency
0x0000f33c  
(62268)Gain Float 4 R\W The linear gain

# Dante Settings
This area contains UXT chip informations about status and settings. It includes as well available commands.
# BlockId Start Address End Address Description
General Info 0x00010000 0x00010074This area contains the general information about
the Ultimo chip
Network Basic 0x00010100 0x00010134This area contains the information about current
# Network Settings
# Model Manufacturer
Info0x00010200 0x00010268This area contains the information about
# Manufacturer
Audio Basic 0x00010300 0x00010324This area contains the information about Audio
# Basic Settings
# Routing RX Channels
Settings0x00010400 0x000106a0This area contains the information about Routing
# RX Channels Settings
# Routing TX Channels
Settings0x00010800 0x00010980This area contains the information about Routing
# TX Channels Settings
Device Identity 0x00010a00 0x00010aa5This area contains the information about Device
# Identity
Device SRate 0x00010b00 0x00010b00This area contains the information about Device
SRate.
Device AES67 0x00010c00 0x00010c00This area contains the information about Device
AES67.
# Device Routing
Performance0x00010d00 0x00010d00This area contains the information about Device
Routing Performance.
Device Lock Unlock 0x00010e00 0x00010e00This area contains the information about Device
Lock Unlock.
Device Basic Clock 0x00010f00 0x00010f00This area contains the information about Device
Basic Clock.
Device VLAN 0x0001 1000 0x0001 10f8This area contains the information about Device
VLAN.
Device Switch Status 0x0001 1200 0x0001 122cThis area contains the information about Device
Switch Status.
Set Dante Network 0x00012000 0x0001200cThis command sets the IP , Netmask and
Gateway for the UXT chip.  
To set DHCP , message field must be set to 0.
Set Dante ID 0x00012010 0x00012030 This command sets the UXT chip friendly name.
Set Dante Tx Label 0x00012030 0x00012052This command sets the label for a specific Tx
channel.
Dante T apping 0x00012060 0x000120a2This command links a Rx channel to the
specified Tx channel of a Tx device.
Dante Reboot 0x000120b0 0x000120b1 This command reboots the UXT chip.

# General Info
# This area contains the general information about the Ultimo chip
Offset Name Type DimR \
# WDescription
0x00010000  
(65536)Time of
Last Readuint32 4 RThe number of ticks when last read of this area has
been done.
0x00010004  
(65540)Time of
Prev Readuint32 4 RThe number of ticks when previous read of this
area has been done.
0x00010008  
(65544)Time of
# Last
Changeuint32 4 RThe number of ticks when this area has changed
last time.
0x0001000c  
(65548)Data is
Validuint32 4 RIf data read are valid this fields value is 1, if not is
0.
0x00010010  
(65552)Module ID
stringchar[32] 32 R ID string of Ultimo chip Manufacturer
0x00010030  
(65584)Model ID char[32] 32 R ID of Ultimo chip Model
0x00010050  
(65616)Software
Versionuint32 4 RSoftware version of Ultimo chip. The most
significant byte shows the first digit, the next byte
shows the second digit and the two least significant
byte show the third digit.
0x00010054  
(65620)Software
Builduint32 4 R Software build of Ultimo chip
0x00010058  
(65624)Firmware
Versionuint32 4 RFirmware version of Ultimo chip. The most
significant byte shows the first digit, the next byte
shows the second digit and the two least significant
byte show the third digit.
0x0001005c  
(65628)Firmware
Builduint32 4 R Firmware build of Ultimo chip
0x00010060  
(65632)BootLoader
Versionuint32 4 R BootLoader V ersion of Ultimo chip
0x00010064  
(65636)BootLoader
Builduint32 4 R BootLoader build of Ultimo chip
0x00010068  
(65640)Api V ersion uint32 4 R Api V ersion of Ultimo chip
0x0001006c  
(65644)Cap Flags uint32 4 R Cap Flags of Ultimo chip
0x00010070  
(65648)Status
Flagsuint32 4 R Status Flags of Ultimo chip

# Network Basic
# This area contains the information about current Network Settings
Offset Name Type Dim R \ W Description
0x00010100  
(65792)Time of
Last Readuint32 4 RThe number of ticks when last read of this area
has been done.
0x00010104  
(65796)Time of
Prev Readuint32 4 RThe number of ticks when previous read of this
area has been done.
0x00010108  
(65800)Time of
# Last
Changeuint32 4 RThe number of ticks when this area has changed
last time.
0x0001010c  
(65804)Data is
Validuint32 4 RIf data read are valid this fields value is 1, if not is
0.
0x000101 10 
(65808)Number of
Interfacesuint16 2 RNumber of available network interfaces. Mezzo
has only 1.
0x000101 14 
(65812)MAC
Addressuint8[6] 6 RUltimo MAC address expressed in big endian. If
MAC address is 00:1D:C1:AA:BB:CC, bytes are:  
 
offset bytes
0x00 0x00
0x01 0x1D
0x02 0xC1
0x03 0xAA
0x04 0xBB
0x05 0xCC
0x000101 1a 
(65818)Flags uint16 2 R Flags of Network Interface.
0x000101 1c 
(65820)Mode uint16 2 R If value is 4 the IP is static if not is Dynamic.
0x00010120  
(65824)Speed uint32 4 R Speed of the Network Interface
0x00010124  
(65828)Number of
Addressesuint16 2 R Number of Addresses on the Network interface
0x00010126  
(65830)Family uint16 2 R Family of the IP Address
0x00010128  
(65832)IPAddress uint8[4] 4 R\WIt's the IP address of this Network Interface.  
Is expressed in big endian, example:  
offset bytes
0x00 0xC0 (192)
0x01 0xA8 (168)
0x02 0x37 ( 55)
0x03 0x6C (108)
0x0001012c  
(65836)Net Mask uint8[4] 4 R\W It's the Net Mask of this Network Interface.
0x00010130  
(65840)Gateway uint8[4] 4 R\W It's the Gateway of this Network Interface.

# Model Manufacturer Info
# This area contains the information about Manufacturer
Offset Name Type DimR \
# WDescription
0x00010200  
(66048)Time of Last
Readuint32 4 RThe number of ticks when last read of this area
has been done.
0x00010204  
(66052)Time of Prev
Readuint32 4 RThe number of ticks when previous read of this
area has been done.
0x00010208  
(66056)Time of Last
Changeuint32 4 RThe number of ticks when this area has
changed last time.
0x0001020c  
(66060)Data is V alid uint32 4 RIf data read are valid this fields value is 1, if not
is 0.
0x00010210  
(66064)Manufacturer
IDchar 32 R ID of Ultimo chip Manufacturer
0x00010230  
(66096)Model ID char[32] 32 R ID of Ultimo chip Model
0x00010250  
(66128)Software
Versionuint32 4 R Software version of Ultimo chip
0x00010254  
(66132)Software Build uint32 4 R Software build of Ultimo chip
0x00010258  
(66136)Firmware
Versionuint32 4 R Firmware version of Ultimo chip
0x0001025c  
(66140)Firmware Build uint32 4 R Firmware build of Ultimo chip
0x00010260  
(66144)Cap Flags uint32 4 R Cap Flags of Ultimo chip
0x00010264  
(66148)Model V ersion uint32 4 R Model V ersion of Ultimo chip

# Audio Basic
# This area contains the information about Audio Basic Settings
Offset Name Type DimR \
# WDescription
0x00010300  
(66304)Time of Last
Readuint32 4 RThe number of ticks when last read of this area
has been done.
0x00010304  
(66308)Time of Prev
Readuint32 4 RThe number of ticks when previous read of this
area has been done.
0x00010308  
(66312)Time of Last
Changeuint32 4 RThe number of ticks when this area has changed
last time.
0x0001030c  
(66316)Data is V alid uint32 4 RIf data read are valid this fields value is 1, if not is
0.
0x00010310  
(66320)Status uint32 4 R Check Audinate Documentation
0x00010314  
(66324)Change Flags uint8 1 R Check Audinate Documentation
0x00010316  
(66326)Default
Encodinguint16 2 R Check Audinate Documentation
0x00010318  
(66328)Rx Channels uint16 2 R Number of Receiving Channels
0x0001031a  
(66330)Tx Channels uint16 2 R Number of T rasmitting Channels
0x0001031c  
(66332)Cap Flags uint32 4 R Check Audinate Documentation
0x00010320  
(66336)Default Sample
Rateuint32 4 R Check Audinate Documentation
# Routing RX Channels Settings
# This area contains the information about Routing RX Channels Settings
# BlockId Start Address End Address Description
RX Channel 1 Settings 0x00010400 0x000104a8 RX Channel 1 Settings
RX Channel 2 Settings 0x000104a8 0x00010550 RX Channel 2 Settings
RX Channel 3 Settings 0x00010550 0x000105f8 RX Channel 3 Settings
RX Channel 4 Settings 0x000105f8 0x000106a0 RX Channel 4 Settings

RX Channel 1 Settings
RX Channel 1 Settings
Offset Name Type DimR \
# WDescription
0x00010400  
(66560)Time of Last
Readuint32 4 RThe number of ticks when last read of this area
has been done.
0x00010404  
(66564)Time of Prev
Readuint32 4 RThe number of ticks when previous read of this
area has been done.
0x00010408  
(66568)Time of Last
Changeuint32 4 RThe number of ticks when this area has changed
last time.
0x0001040c  
(66572)Data is V alid uint32 4 RIf data read are valid this fields value is 1, if not
is 0.
0x00010410  
(66576)Channel
Namechar[32] 32 RNull-terminated default Rx channel 1 name
string.
0x00010430  
(66608)Encoding uint16 2 R Audio encoding used by this Rx channel 1.
0x00010434  
(66612)Sample Rate uint32 4 R Audio sample rate for Rx channel 1.
0x00010438  
(66616)PCM Map uint16 2 RBitmask of supported PCM encodings, in bytes
(eg 0x4 => 24 bits).
0x0001043a  
(66618)Channel
Flagsuint16 2 R Channel 1 flags.
0x0001043c  
(66620)Channel
Flags Maskuint16 2 RBitwise OR'd mask which specify which
channel_flags are valid.
0x0001043e  
(66622)Channel
Labelchar[32] 32 R Null-terminated Rx channel 1 label string.
0x0001045e  
(66654)Status uint16 2 R Subscription status of this Rx channel 1.
0x00010460  
(66656)Availability uint8 1 RA non-zero value indicates that channel 1 is
available to receive audio
0x00010461  
(66657)Active uint8 1 RA non-zero value indicates that channel 1 is
active
0x00010462  
(66658)Subscribed
Channelchar[32] 32 RNull-terminated string of the Tx channel that Rx
channel 1 is subscribed to.  
# If no subscription is active then this field is
NULL.
0x00010482  
(66690)Subscribe
Devicechar[32] 32 RNull-terminated string of the Tx device that Rx
channel 1 is subscribed to.  
# If no subscription is active then this field is
NULL.
0x000104a2  
(66722)Flow ID uint16 2 RFlow ID associted with this Rx channel, only
valid if channel 1 is subscribed.
0x000104a4  
(66724)Slot ID uint16 2 R Slot ID associated this this Rx channel 1.

RX Channel 2 Settings
RX Channel 2 Settings
Offset Name Type DimR \
# WDescription
0x000104a8  
(66728)Time of Last
Readuint32 4 RThe number of ticks when last read of this area
has been done.
0x000104ac  
(66732)Time of Prev
Readuint32 4 RThe number of ticks when previous read of this
area has been done.
0x000104b0  
(66736)Time of Last
Changeuint32 4 RThe number of ticks when this area has changed
last time.
0x000104b4  
(66740)Data is V alid uint32 4 RIf data read are valid this fields value is 1, if not
is 0.
0x000104b8  
(66744)Channel
Namechar[32] 32 RNull-terminated default Rx channel 1 name
string.
0x000104d8  
(66776)Encoding uint16 2 R Audio encoding used by this Rx channel 1.
0x000104dc  
(66780)Sample Rate uint32 4 R Audio sample rate for Rx channel 1.
0x000104e0  
(66784)PCM Map uint16 2 RBitmask of supported PCM encodings, in bytes
(eg 0x4 => 24 bits).
0x000104e2  
(66786)Channel
Flagsuint16 2 R Channel 1 flags.
0x000104e4  
(66788)Channel
Flags Maskuint16 2 RBitwise OR'd mask which specify which
channel_flags are valid.
0x000104e6  
(66790)Channel
Labelchar[32] 32 R Null-terminated Rx channel 1 label string.
0x00010506  
(66822)Status uint16 2 R Subscription status of this Rx channel 1.
0x00010508  
(66824)Availability uint8 1 RA non-zero value indicates that channel 1 is
available to receive audio
0x00010509  
(66825)Active uint8 1 RA non-zero value indicates that channel 1 is
active
0x0001050a  
(66826)Subscribed
Channelchar[32] 32 RNull-terminated string of the Tx channel that Rx
channel 1 is subscribed to.  
# If no subscription is active then this field is
NULL.
0x0001052a  
(66858)Subscribe
Devicechar[32] 32 RNull-terminated string of the Tx device that Rx
channel 1 is subscribed to.  
# If no subscription is active then this field is
NULL.
0x0001054a  
(66890)Flow ID uint16 2 RFlow ID associted with this Rx channel, only
valid if channel 1 is subscribed.
0x0001054c  
(66892)Slot ID uint16 2 R Slot ID associated this this Rx channel 1.

RX Channel 3 Settings
RX Channel 3 Settings
Offset Name Type DimR \
# WDescription
0x00010550  
(66896)Time of Last
Readuint32 4 RThe number of ticks when last read of this area
has been done.
0x00010554  
(66900)Time of Prev
Readuint32 4 RThe number of ticks when previous read of this
area has been done.
0x00010558  
(66904)Time of Last
Changeuint32 4 RThe number of ticks when this area has changed
last time.
0x0001055c  
(66908)Data is V alid uint32 4 RIf data read are valid this fields value is 1, if not
is 0.
0x00010560  
(66912)Channel
Namechar[32] 32 RNull-terminated default Rx channel 1 name
string.
0x00010580  
(66944)Encoding uint16 2 R Audio encoding used by this Rx channel 1.
0x00010584  
(66948)Sample Rate uint32 4 R Audio sample rate for Rx channel 1.
0x00010588  
(66952)PCM Map uint16 2 RBitmask of supported PCM encodings, in bytes
(eg 0x4 => 24 bits).
0x0001058a  
(66954)Channel
Flagsuint16 2 R Channel 1 flags.
0x0001058c  
(66956)Channel
Flags Maskuint16 2 RBitwise OR'd mask which specify which
channel_flags are valid.
0x0001058e  
(66958)Channel
Labelchar[32] 32 R Null-terminated Rx channel 1 label string.
0x000105ae  
(66990)Status uint16 2 R Subscription status of this Rx channel 1.
0x000105b0  
(66992)Availability uint8 1 RA non-zero value indicates that channel 1 is
available to receive audio
0x000105b1  
(66993)Active uint8 1 RA non-zero value indicates that channel 1 is
active
0x000105b2  
(66994)Subscribed
Channelchar[32] 32 RNull-terminated string of the Tx channel that Rx
channel 1 is subscribed to.  
# If no subscription is active then this field is
NULL.
0x000105d2  
(67026)Subscribe
Devicechar[32] 32 RNull-terminated string of the Tx device that Rx
channel 1 is subscribed to.  
# If no subscription is active then this field is
NULL.
0x000105f2  
(67058)Flow ID uint16 2 RFlow ID associted with this Rx channel, only
valid if channel 1 is subscribed.
0x000105f4  
(67060)Slot ID uint16 2 R Slot ID associated this this Rx channel 1.

RX Channel 4 Settings
RX Channel 4 Settings
Offset Name Type DimR \
# WDescription
0x000105f8  
(67064)Time of Last
Readuint32 4 RThe number of ticks when last read of this area
has been done.
0x000105fc  
(67068)Time of Prev
Readuint32 4 RThe number of ticks when previous read of this
area has been done.
0x00010600  
(67072)Time of Last
Changeuint32 4 RThe number of ticks when this area has changed
last time.
0x00010604  
(67076)Data is V alid uint32 4 RIf data read are valid this fields value is 1, if not
is 0.
0x00010608  
(67080)Channel
Namechar[32] 32 RNull-terminated default Rx channel 1 name
string.
0x00010628  
(67112)Encoding uint16 2 R Audio encoding used by this Rx channel 1.
0x0001062c  
(67116)Sample Rate uint32 4 R Audio sample rate for Rx channel 1.
0x00010630  
(67120)PCM Map uint16 2 RBitmask of supported PCM encodings, in bytes
(eg 0x4 => 24 bits).
0x00010632  
(67122)Channel
Flagsuint16 2 R Channel 1 flags.
0x00010634  
(67124)Channel
Flags Maskuint16 2 RBitwise OR'd mask which specify which
channel_flags are valid.
0x00010636  
(67126)Channel
Labelchar[32] 32 R Null-terminated Rx channel 1 label string.
0x00010656  
(67158)Status uint16 2 R Subscription status of this Rx channel 1.
0x00010658  
(67160)Availability uint8 1 RA non-zero value indicates that channel 1 is
available to receive audio
0x00010659  
(67161)Active uint8 1 RA non-zero value indicates that channel 1 is
active
0x0001065a  
(67162)Subscribed
Channelchar[32] 32 RNull-terminated string of the Tx channel that Rx
channel 1 is subscribed to.  
# If no subscription is active then this field is
NULL.
0x0001067a  
(67194)Subscribe
Devicechar[32] 32 RNull-terminated string of the Tx device that Rx
channel 1 is subscribed to.  
# If no subscription is active then this field is
NULL.
0x0001069a  
(67226)Flow ID uint16 2 RFlow ID associted with this Rx channel, only
valid if channel 1 is subscribed.
0x0001069c  
(67228)Slot ID uint16 2 R Slot ID associated this this Rx channel 1.

# Routing TX Channels Settings
# This area contains the information about Routing TX Channels Settings
# BlockId Start Address End Address Description
TX Channel 1 Settings 0x00010800 0x00010860 Tx Channel 1 Settings
TX Channel 2 Settings 0x00010860 0x000108c0 Tx Channel 2 Settings
TX Channel 3 Settings 0x000108c0 0x00010920 Tx Channel 3 Settings
TX Channel 4 Settings 0x00010920 0x00010980 Tx Channel 4 Settings
TX Channel 1 Settings
Tx Channel 1 Settings
Offset Name Type DimR \
# WDescription
0x00010800  
(67584)Time of Last
Readuint32 4 RThe number of ticks when last read of this area
has been done.
0x00010804  
(67588)Time of Prev
Readuint32 4 RThe number of ticks when previous read of this
area has been done.
0x00010808  
(67592)Time of Last
Changeuint32 4 RThe number of ticks when this area has
changed last time.
0x0001080c  
(67596)Data is V alid uint32 4 RIf data read are valid this fields value is 1, if not
is 0.
0x00010810  
(67600)Channel Name char[32] 32 RNull-terminated default Tx channel 1 name
string.
0x00010830  
(67632)Encoding uint16 2 R Audio encoding used by this Tx channel 1.
0x00010834  
(67636)Sample Rate uint32 4 R Audio sample rate for Tx channel 1.
0x00010838  
(67640)PCM Map uint16 2 RBitmask of supported PCM encodings, in bytes
(eg 0x4 => 24 bits).
0x0001083a  
(67642)Channel Flags uint16 2 R Channel 1 flags.
0x0001083c  
(67644)Channel Flags
Maskuint16 2 RBitwise OR'd mask which specify which
channel_flags are valid.
0x0001083e  
(67646)Channel Label char[32] 32 R Null-terminated Rx channel 1 label string.

TX Channel 2 Settings
Tx Channel 2 Settings
Offset Name Type DimR \
# WDescription
0x00010860  
(67680)Time of Last
Readuint32 4 RThe number of ticks when last read of this area
has been done.
0x00010864  
(67684)Time of Prev
Readuint32 4 RThe number of ticks when previous read of this
area has been done.
0x00010868  
(67688)Time of Last
Changeuint32 4 RThe number of ticks when this area has
changed last time.
0x0001086c  
(67692)Data is V alid uint32 4 RIf data read are valid this fields value is 1, if not
is 0.
0x00010870  
(67696)Channel Name char[32] 32 RNull-terminated default Tx channel 1 name
string.
0x00010890  
(67728)Encoding uint16 2 R Audio encoding used by this Tx channel 1.
0x00010894  
(67732)Sample Rate uint32 4 R Audio sample rate for Tx channel 1.
0x00010898  
(67736)PCM Map uint16 2 RBitmask of supported PCM encodings, in bytes
(eg 0x4 => 24 bits).
0x0001089a  
(67738)Channel Flags uint16 2 R Channel 1 flags.
0x0001089c  
(67740)Channel Flags
Maskuint16 2 RBitwise OR'd mask which specify which
channel_flags are valid.
0x0001089e  
(67742)Channel Label char[32] 32 R Null-terminated Rx channel 1 label string.

TX Channel 3 Settings
Tx Channel 3 Settings
Offset Name Type DimR \
# WDescription
0x000108c0  
(67776)Time of Last
Readuint32 4 RThe number of ticks when last read of this area
has been done.
0x000108c4  
(67780)Time of Prev
Readuint32 4 RThe number of ticks when previous read of this
area has been done.
0x000108c8  
(67784)Time of Last
Changeuint32 4 RThe number of ticks when this area has
changed last time.
0x000108cc  
(67788)Data is V alid uint32 4 RIf data read are valid this fields value is 1, if not
is 0.
0x000108d0  
(67792)Channel Name char[32] 32 RNull-terminated default Tx channel 1 name
string.
0x000108f0  
(67824)Encoding uint16 2 R Audio encoding used by this Tx channel 1.
0x000108f4  
(67828)Sample Rate uint32 4 R Audio sample rate for Tx channel 1.
0x000108f8  
(67832)PCM Map uint16 2 RBitmask of supported PCM encodings, in bytes
(eg 0x4 => 24 bits).
0x000108fa  
(67834)Channel Flags uint16 2 R Channel 1 flags.
0x000108fc  
(67836)Channel Flags
Maskuint16 2 RBitwise OR'd mask which specify which
channel_flags are valid.
0x000108fe  
(67838)Channel Label char[32] 32 R Null-terminated Rx channel 1 label string.

TX Channel 4 Settings
Tx Channel 4 Settings
Offset Name Type DimR \
# WDescription
0x00010920  
(67872)Time of Last
Readuint32 4 RThe number of ticks when last read of this area
has been done.
0x00010924  
(67876)Time of Prev
Readuint32 4 RThe number of ticks when previous read of this
area has been done.
0x00010928  
(67880)Time of Last
Changeuint32 4 RThe number of ticks when this area has
changed last time.
0x0001092c  
(67884)Data is V alid uint32 4 RIf data read are valid this fields value is 1, if not
is 0.
0x00010930  
(67888)Channel Name char[32] 32 RNull-terminated default Tx channel 1 name
string.
0x00010950  
(67920)Encoding uint16 2 R Audio encoding used by this Tx channel 1.
0x00010954  
(67924)Sample Rate uint32 4 R Audio sample rate for Tx channel 1.
0x00010958  
(67928)PCM Map uint16 2 RBitmask of supported PCM encodings, in bytes
(eg 0x4 => 24 bits).
0x0001095a  
(67930)Channel Flags uint16 2 R Channel 1 flags.
0x0001095c  
(67932)Channel Flags
Maskuint16 2 RBitwise OR'd mask which specify which
channel_flags are valid.
0x0001095e  
(67934)Channel Label char[32] 32 R Null-terminated Rx channel 1 label string.

# Device Identity
# This area contains the information about Device Identity
Offset Name Type DimR \
# WDescription
0x00010a00  
(68096)Time of Last
Readuint32 4 RThe number of ticks when last read of this area
has been done.
0x00010a04  
(68100)Time of Prev
Readuint32 4 RThe number of ticks when previous read of this
area has been done.
0x00010a08  
(68104)Time of Last
Changeuint32 4 RThe number of ticks when this area has
changed last time.
0x00010a0c  
(68108)Data is V alid uint32 4 RIf data read are valid this fields value is 1, if not
is 0.
0x00010a10  
(68112)Status Flags uint16 2 R Check for Audinate Documentation.
0x00010a12  
(68114)Process ID uint16 2 R Check for Audinate Documentation.
0x00010a14  
(68116)Device ID char[17] 17 R Device ID of Ultimo Chip.
0x00010a25  
(68133)Default Name char[32] 32 R Default Name of Ultimo Chip.
0x00010a45  
(68165)Friendly Name char[32] 32 R Friendly Name of Ultimo Chip.
0x00010a65  
(68197)Domain char[32] 32 R Domain of Ultimo Chip.
0x00010a85  
(68229)Advertised
Namechar[32] 32 R Advertised Name of Ultimo Chip.
# Device SRate
This area contains the information about Device SRate.
Offset Name Type Dim R \ W Description
Device AES67
This area contains the information about Device AES67.
Offset Name Type Dim R \ W Description
# Device Routing Performance
This area contains the information about Device Routing Performance.
Offset Name Type Dim R \ W Description
# Device Lock Unlock
This area contains the information about Device Lock Unlock.
Offset Name Type Dim R \ W Description

# Device Basic Clock
This area contains the information about Device Basic Clock.
Offset Name Type Dim R \ W Description
# Device VLAN
This area contains the information about Device VLAN.
# BlockId Start Address End Address Description
VLAN Config 0x0001 1000 0x0001 1018This area contains the information about VLAN
Config.
# Device VLAN ID
10x0001 1018 0x0001 1050 Check for Audinate Documentation.
# Device VLAN ID
20x0001 1050 0x0001 1088 Check for Audinate Documentation.
# Device VLAN ID
30x0001 1088 0x0001 10c0 Check for Audinate Documentation.
# Device VLAN ID
40x0001 10c0 0x0001 10f8 Check for Audinate Documentation.
# VLAN Config
This area contains the information about VLAN Config.
Offset Name Type DimR \
# WDescription
0x0001 1000  
(69632)Time of Last
Readuint32 4 RThe number of ticks when last read of this area
has been done.
0x0001 1004  
(69636)Time of Prev
Readuint32 4 RThe number of ticks when previous read of this
area has been done.
0x0001 1008  
(69640)Time of Last
Changeuint32 4 RThe number of ticks when this area has
changed last time.
0x0001 100c  
(69644)Data is V alid uint32 4 RIf data read are valid this fields value is 1, if not
is 0.
0x0001 1010  
(69648)VLAN Max Num uint8 1 R Check for Audinate Documentation.
0x0001 1011 
(69649)VLAN Num uint8 1 R Check for Audinate Documentation.
0x0001 1012  
(69650)VLAN Current ID uint8 1 R Possible values are: 1 for switched, 2 for split.
0x0001 1013  
(69651)VLAN Reboot ID uint8 1 R Check for Audinate Documentation.
0x0001 1014  
(69652)VLAN Config Port
Maskuint16 2 R Check for Audinate Documentation.

Device VLAN ID 1
Check for Audinate Documentation.
Offset Name Type Dim R \ W Description
0x0001 1018  
(69656)VLAN ID uint32 4 R Check for Audinate Documentation.
0x0001 101c  
(69660)VLAN Primary Bitmap uint32 4 R Check for Audinate Documentation.
0x0001 1020  
(69664)VLAN Secondary Bitmap uint32 4 R Check for Audinate Documentation.
0x0001 1024  
(69668)VLAN User 2 Bitmap uint32 4 R Check for Audinate Documentation.
0x0001 1028  
(69672)VLAN User 3 Bitmap uint32 4 R Check for Audinate Documentation.
0x0001 102c  
(69676)VLAN Name String char[33] 33 R Check for Audinate Documentation.
Device VLAN ID 2
Check for Audinate Documentation.
Offset Name Type Dim R \ W Description
0x0001 1050  
(69712)VLAN ID uint32 4 R Check for Audinate Documentation.
0x0001 1054  
(69716)VLAN Primary Bitmap uint32 4 R Check for Audinate Documentation.
0x0001 1058  
(69720)VLAN Secondary Bitmap uint32 4 R Check for Audinate Documentation.
0x0001 105c  
(69724)VLAN User 2 Bitmap uint32 4 R Check for Audinate Documentation.
0x0001 1060  
(69728)VLAN User 3 Bitmap uint32 4 R Check for Audinate Documentation.
0x0001 1064  
(69732)VLAN Name String char[33] 33 R Check for Audinate Documentation.
Device VLAN ID 3
Check for Audinate Documentation.
Offset Name Type Dim R \ W Description
0x0001 1088  
(69768)VLAN ID uint32 4 R Check for Audinate Documentation.
0x0001 108c  
(69772)VLAN Primary Bitmap uint32 4 R Check for Audinate Documentation.
0x0001 1090  
(69776)VLAN Secondary Bitmap uint32 4 R Check for Audinate Documentation.
0x0001 1094  
(69780)VLAN User 2 Bitmap uint32 4 R Check for Audinate Documentation.
0x0001 1098  
(69784)VLAN User 3 Bitmap uint32 4 R Check for Audinate Documentation.
0x0001 109c  
(69788)VLAN Name String char[33] 33 R Check for Audinate Documentation.

Device VLAN ID 4
Check for Audinate Documentation.
Offset Name Type Dim R \ W Description
0x0001 10c0  
(69824)VLAN ID uint32 4 R Check for Audinate Documentation.
0x0001 10c4  
(69828)VLAN Primary Bitmap uint32 4 R Check for Audinate Documentation.
0x0001 10c8  
(69832)VLAN Secondary Bitmap uint32 4 R Check for Audinate Documentation.
0x0001 10cc  
(69836)VLAN User 2 Bitmap uint32 4 R Check for Audinate Documentation.
0x0001 10d0  
(69840)VLAN User 3 Bitmap uint32 4 R Check for Audinate Documentation.
0x0001 10d4  
(69844)VLAN Name String char[33] 33 R Check for Audinate Documentation.
# Device Switch Status
This area contains the information about Device Switch Status.
# BlockId Start Address End Address Description
Switch Ports 0x0001 1200 0x0001 1214This area contains the information about Switch
Status Ports.
# Switch Ports
Status 10x0001 1214 0x0001 1220 Check for Audinate Documentation.
# Switch Ports
Status 20x0001 1220 0x0001 122c Check for Audinate Documentation.
# Switch Ports
This area contains the information about Switch Status Ports.
Offset Name Type DimR \
# WDescription
0x0001 1200  
(70144)Time of Last Read uint32 4 RThe number of ticks when last read of this
area has been done.
0x0001 1204  
(70148)Time of Prev Read uint32 4 RThe number of ticks when previous read
of this area has been done.
0x0001 1208  
(70152)Time of Last Change uint32 4 RThe number of ticks when this area has
changed last time.
0x0001 120c  
(70156)Data is V alid uint32 4 RIf data read are valid this fields value is 1,
if not is 0.
0x0001 1210  
(70160)Switch Status Enabled
Ports V aluesuint16 2 R Check for Audinate Documentation.
0x0001 1212  
(70162)Switch Status Ports
Numberuint8 1 R Check for Audinate Documentation.

Switch Ports Status 1
Check for Audinate Documentation.
Offset Name Type DimR \
# WDescription
0x0001 1214  
(70164)Valid Flags uint16 2 RValid flags bitmask indicating which fields in this
messages are valid.
0x0001 1216  
(70166)Link Speed uint16 2 R Link speed in Mbps.
0x0001 1218  
(70168)Port Number uint8 1 R Port number .
0x0001 1219  
(70169)Port Mode uint8 1 R Port mode.
0x0001 121a  
(70170)Link Flags
Maskuint8 1 R Bitmask of which bits in the Link Flags are valid.
0x0001 121b  
(70171)Link Flags uint8 1 R Bitmask of link flags.
0x0001 121c  
(70172)Error Count uint32 4 R Error count - RX errors, FCS errors, etc.
Switch Ports Status 2
Check for Audinate Documentation.
Offset Name Type DimR \
# WDescription
0x0001 1220  
(70176)Valid Flags uint16 2 RValid flags bitmask indicating which fields in this
messages are valid.
0x0001 1222  
(70178)Link Speed uint16 2 R Link speed in Mbps.
0x0001 1224  
(70180)Port Number uint8 1 R Port number .
0x0001 1225  
(70181)Port Mode uint8 1 R Port mode.
0x0001 1226  
(70182)Link Flags
Maskuint8 1 R Bitmask of which bits in the Link Flags are valid.
0x0001 1227  
(70183)Link Flags uint8 1 R Bitmask of link flags.
0x0001 1228  
(70184)Error Count uint32 4 R Error count - RX errors, FCS errors, etc.

# Set Dante Network
This command sets the IP , Netmask and Gateway for the UXT chip.  
To set DHCP , message field must be set to 0.
Offset Name Type Dim R \ W Description
0x00012000  
(73728)IPAddress uint8[4] 4 WIs the IP address.  
Is expressed in big endian.
0x00012004  
(73732)NetMask uint8[4] 4 WIs the NetMask address.  
Is expressed in big endian.
0x00012008  
(73736)DefaultGW uint8[4] 4 WIs the default gateway address.  
Is expressed in big endian.
# Set Dante ID
This command sets the UXT chip friendly name.
Offset Name Type Dim R \ W Description
0x00012010  
(73744)Dante
# Module ID
stringchar[32] 32 WID string of UXT chip. This array must be a null-
terminated string, so it can contain up to 31
characters.
# Set Dante Tx Label
This command sets the label for a specific Tx channel.
Offset Name Type Dim R \ W Description
0x00012030  
(73776)Dante Tx
channel
numberuint16 2 W Tx channel number , 0-based [0 -> 3].
0x00012032  
(73778)Dante Tx
channel name
stringchar[32] 32 WTx channel name string. This array must be a
null-terminated string, so it can contain up to
31 characters.
# Dante T apping
This command links a Rx channel to the specified Tx channel of a Tx device.
Offset Name Type Dim R \ W Description
0x00012060  
(73824)Dante Rx
channel
numberuint16 2 W Rx channel number , 0-based [0 -> 3].
0x00012062  
(73826)Dante Tx
channel name
stringchar[32] 32 WTx channel name string. This array must be a
null-terminated string, so it can contain up to
31 characters.
0x00012082  
(73858)Dante Tx
device name
stringchar[32] 32 WTx device name string. This array must be a
null-terminated string, so it can contain up to
31 characters.

# Dante Reboot
This command reboots the UXT chip.
Offset Name Type Dim R \ W Description
0x000120b0  
(73904)Dante Reboot uint8 1 W If set to `0xAC` reboots the UXT chip.
# OEM Spare Area
Empty Spare Area dedicated to OEM.
Offset Name Type Dim R \ W Description
0x00013000  
(77824)Spare Area char[256] 256 R\W Empty spare area for OEM.
# Blink
# The blink command
Offset Name Type Dim R \ W Description
0x00100000  
(1048576)Blink uint8 1 W If set to `1` starts blinking, if set to `0` stops blinking
# System Reboot
# The system reboot command
Offset Name Type Dim R \ W Description
0x00100001  
(1048577)System Reboot uint8 1 W If set to `0xAC` reboots the device
# Load Default Parameters
# Equivalent to an hardware Hard Reset
Offset Name Type Dim R \ W Description
0x00100002  
(1048578)Load Default
Parametersuint8 1 WIf set to `0x01` load the default parameters
of preset
# Firmware Area
This area contains the firmware. The max size for firmware is 1048576
Offset Name Type Dim R \ W Description
0x00700000  
(7340032)Firmware uint8[] 1048576 W Reads the T empT rasf

# Firmware Start
This area contains the new firmware information, use this to verify the firmware before flash it
Offset Name Type Dim R \ W Description
0x00900000  
(9437184)Firmware CRC uint16 2 W The firmware crc
0x00900002  
(9437186)Firmware size uint32 4 W The firmware size
# Firmware Flash Erase
# This will start the upgrade firmware
Offset Name Type Dim R \ W Description
0x00900010  
(9437200)Start upgrade uint8 1 W Starts the firmware upgrade