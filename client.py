import argparse
import socket
from time import sleep, time
from typing import Optional, Tuple, Union, TYPE_CHECKING
from util.constants import ARG_DEFAULTS, DEBUG, WARNING
from util.logger import get_color_logger
from util.packet import decode_data_packet, Packet, PacketType
if TYPE_CHECKING:
    from util.packet import DataPacket


class PullClient:
    """
    Client for the Pull-Centric UDP-Based Protocol.
    """
    def __init__(self, args: argparse.Namespace):
        # Store details
        self.server = (args.address, args.server_port)
        self.client_id = args.id

        # Create logger
        self.logger = get_color_logger(self.__class__.__name__)
        self.logger.setLevel(WARNING if args.quiet else DEBUG)

        # Create server connection
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', args.client_port))
        self.sock.setblocking(1)
        self._timeout = 120.0

        # Transaction details
        self.txn_id = -1
        self.txn_start = -1
        self.txn_expiry = -1
    
    def _send_packet(self, packet: Union['Packet', str], no_wait: bool = False) -> Optional[Tuple[str, float]]:
        """
        Sends an arbitrary packet to the server and waits for a reply packet in return.

        :param packet: Packet to send (must be a valid Packet object or string)
        :return: Tuple of (response, rtt)
        """
        # Send packet
        self.sock.sendto(str(packet).encode(), self.server)
        if no_wait:
            self.logger.debug('Flung packet {} at server'.format(packet))
            return
        
        # Wait for response
        self.sock.settimeout(self._timeout)
        self.logger.info('Sent packet, waiting for {:.2f} sec'.format(self._timeout))
        now = time()
        try:
            packet, _ = self.sock.recvfrom(1024)
            response = packet.decode()
        except socket.timeout:
            self.logger.critical('Server not responding!')
            raise RuntimeError
        except Exception as e:
            self.logger.error('Could not decode response. Error: {}'.format(e))
        else:
            rtt = time() - now
        
        # Return response
        self.logger.info('Received response in {:.2f} sec'.format(rtt))
        self.logger.debug('Response: "{}"'.format(response))
        return response, rtt

    def send_init(self) -> float:
        """
        Sends an INITIATE packet to the server and waits for an ACCEPT packet in return.

        :return: RTT
        """
        # Send INIT packet
        packet = Packet(client_id=self.client_id, txn_id=self.txn_id, type=PacketType.INIT)
        response, rtt = self._send_packet(packet)

        # Parse transaction ID from ACCEPT message
        try:
            txn_id = int(response)
            now = time()
        except ValueError:
            if response == 'Existing alive transaction':
                self.logger.critical('Transaction in progress, try again later')
            else:
                self.logger.critical('Invalid ACCEPT packet: "{}"'.format(response))
            raise RuntimeError
        else:
            self.txn_id = txn_id
            self.txn_start = now
            self.txn_expiry = now + (120 - (rtt / 2))
            self.logger.success('Created transaction {0} (valid for {1:.2f} sec)'.format(txn_id, self.txn_expiry - self.txn_start))
        
        return rtt
    
    def send_pull(self, pull: int = 0, size: int = 0) -> Tuple['DataPacket', float]:
        """
        Sends a PULL packet to the server and waits for a DATA packet in response.
        
        :param pull: Starting byte of requested data portion
        :param size: Size of requested data portion
        :return: Tuple of (DataPacket, rtt)
        """
        # Send packet and wait for response
        packet = Packet(
            client_id=self.client_id,
            txn_id=self.txn_id,
            type=PacketType.PULL,
            pull=pull,
            size=size
        )
        response, rtt = self._send_packet(packet)

        # Decode data
        try:
            data_packet = decode_data_packet(response)
        except Exception as e:
            self.logger.error('Could not decode DATA packet. Error: {}'.format(e))
            raise RuntimeError
        
        return data_packet, rtt
    
    def send_ack(self, data_packet: 'DataPacket', final_data: Optional[str] = None):
        """
        Sends an ACK packet to the server.
        
        :param packet: DataPacket to acknowledge
        :param final_data: Final data to send with packet. Causes packet to be sent with the SUBMIT flag.
        """
        # Build packet
        packet = Packet(
            client_id=self.client_id,
            txn_id=self.txn_id,
            type=PacketType.ACK,
            uin=data_packet.uin,
            answer=data_packet.answer
        )
        if data_packet.last and final_data:
            packet.type |= PacketType.SUBMIT
            packet.data = final_data
        
        # Send packet
        self._send_packet(packet, no_wait=True)

    def begin(self):
        """
        Perform a complete pull transaction.
        """
        # Create transaction
        try:
            self.send_init()
        except:
            return

        # Additive increase parameters
        inc_delta = 2
        lkgs = 1

        # Start pulling data
        data = None
        pull = 0
        size = 1
        fixed_size = False
        final_data = ''
        while True:
            self.logger.info('Sending PULL packet with pull={0} size={1}'.format(pull, size))

            # Send PULL packet
            try:
                data, rtt = self.send_pull(pull, size)
            except Exception as e:
                self.logger.error('Could not send PULL packet. Error: {}'.format(e))
                
                if fixed_size:
                    self.logger.critical('Size already fixed, aborting.')
                    break
                else:
                    # The size might be too big, so restore last known good size and try again
                    size = lkgs
                    inc_delta = 0
                    fixed_size = True

                    # Sleep for 10 sec just like the server :)
                    self.logger.info('Fixing size to {} and sleeping for 10 sec'.format(size))
                    sleep(10)
            else:
                # Send acknowledgement
                self.logger.info('Acknowledging {}'.format(data))
                self.send_ack(data)
                
                # Append data to final data
                final_data += data.data

                # Send final data if this is the last packet
                if data.last:
                    self.logger.info('Sending final SUBMIT packet')
                    self.send_ack(data, final_data)
                    break
                
                # Update offset
                pull += size

                # Store last known good size
                lkgs = size

                # Increment size
                size += inc_delta

                # Update timeout
                self._timeout = rtt + 1.5
        
        self.logger.success('Transaction {0} completed in {1:.2f} sec'.format(self.txn_id, time() - self.txn_start))

if __name__ == '__main__':
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Pull data from a remote server using the Pull-Centric UDP-Based Protocol.')
    parser.add_argument('-a', '--address', type=str, default=ARG_DEFAULTS['server_addr'], help='IP address of receiver')
    parser.add_argument('-s', '--server-port', type=int, default=ARG_DEFAULTS['server_port'], help='port number of receiver')
    parser.add_argument('-c', '--client-port', type=int, default=ARG_DEFAULTS['client_port'], help='port number of sender')
    parser.add_argument('-i', '--id', type=str, default=ARG_DEFAULTS['client_id'], help='ID of sender')
    parser.add_argument('-q', '--quiet', action='store_true', help='Only show warnings and errors')
    parser.set_defaults(quiet=False)
    args = parser.parse_args()

    # Create logger
    logger = get_color_logger('main')
    logger.setLevel(WARNING if args.quiet else DEBUG)
    logger.info(f'Starting pull client with args {args}')
    
    # Create client
    client = PullClient(args)
    client.begin()
