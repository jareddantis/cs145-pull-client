from dataclasses import dataclass
from enum import IntFlag
from string import ascii_lowercase
from sympy import factorint


# Packet types
class PacketType(IntFlag):
    SUBMIT = 1
    ACK = 2
    PULL = 4
    INIT = 8


# Packet format
@dataclass
class Packet:
    client_id: str
    txn_id: int
    type: PacketType = PacketType.INIT
    pull: int = 0
    size: int = 0
    uin: int = 0
    answer: int = 0
    data: str = '0'

    def __str__(self):
        return '{0}{1:08d}{2}{3:05d}{4:05d}{5:07d}{6}/{7}'.format(
            self.client_id,
            self.txn_id,
            self.type,
            self.pull,
            self.size,
            self.uin,
            self.answer,
            self.data
        )

    def __repr__(self):
        return '<Packet \'{}\'>'.format(str(self))


# Decoded data packet format
@dataclass
class DataPacket:
    txn_id: str
    uin: int
    uin_ans: int
    data: str


# Packet decoder
def decode_data_packet(packet: str) -> DataPacket:
    if len(packet) <= 25:
        raise ValueError('Data packet too short: {}'.format(packet))
    elif packet[:3] != 'TXN':
        raise ValueError('Invalid data packet: {}'.format(packet))
    
    try:
        txn_id = packet[3:11]
        uin = int(packet[14:21])
        
        # Look for the 'DATA' substring
        data_start = packet.find('DATA')
        if data_start == -1:
            raise ValueError('No DATA substring found')

        # Extract data
        encrypted_data = packet[data_start + 4:].lower()

        # Extract challenge
        challenge = int(packet[24:data_start])

        # Factorize challenge question
        factors = factorint(challenge).keys()

        # Decode data using Caesar cipher with shift equal to the smallest factor
        data = ''
        key = min(factors)
        for c in encrypted_data:
            if c in ascii_lowercase:
                pos = ascii_lowercase.index(c)
                data += ascii_lowercase[(pos - key) % 26]
            else:
                data += c
        
        # Return decoded data packet
        return DataPacket(
            txn_id=txn_id,
            uin=uin,
            uin_ans=max(factors),
            data=data
        )
    except Exception as e:
        raise ValueError('Could not decode packet: {}'.format(e)) from e
