import argparse
import socket
from time import time
from util.constants import ARG_DEFAULTS, DEBUG, WARNING, PacketType
from util.logger import get_color_logger


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

        # Transaction details
        self.txn_id = -1
        self.txn_start = -1
        self.txn_expiry = -1
    
    def build_packet(
        self,
        packet_type: int = PacketType.SUBMIT,
        pull: int = 0,
        size: int = 0,
        uin: int = 0,
        ans: int = 0,
        data: str = '0'
    ) -> str:
        """
        Build a packet to send to the server.

        :param packet_type: Type of packet
        :param pull: Starting byte of requested data portion
        :param size: Size of requested data portion
        :param uin: Unique identity number of challenge question
        :param ans: Answer to challenge question
        :param data: Decrypted data for verification
        :return: Packet to send to server, in bytes
        """
        packet = '{0}{1:08d}{2}{3:05d}{4:05d}{5:07d}{6}/{7}'.format(
            self.client_id,
            self.txn_id,
            packet_type,
            pull,
            size,
            uin,
            ans,
            data
        )
        self.logger.debug('Built packet: "{}"'.format(packet))
        return packet.encode()
    
    def send_init(self):
        """
        Sends an INITIATE packet to the server.
        """
        # Send INIT packet
        packet = self.build_packet(packet_type=PacketType.INIT)
        self.sock.sendto(packet, self.server)
        self.sock.settimeout(120)
        self.logger.info('Sent INITIATE packet, waiting for 120 sec')

        # Wait for ACCEPT packet
        try:
            packet, _ = self.sock.recvfrom(1024)
            now = time.time()
        except socket.timeout:
            self.logger.critical('Server not responding!')
            raise RuntimeError

        # Parse transaction ID from ACCEPT message
        try:
            response = packet.decode()
            txn_id = int(response)
        except ValueError:
            if response == 'Existing alive transaction':
                self.logger.critical('Transaction in progress, try again later')
            else:
                self.logger.critical('Invalid ACCEPT packet: "{}"'.format(response))
            raise RuntimeError
        else:
            self.txn_id = txn_id
            self.txn_start = now
            self.txn_expiry = now + 120
            self.logger.success('Created transaction {0} (valid for {1:.2f} sec)'.format(txn_id, self.txn_expiry - time.time()))
    
    def begin(self):
        """
        Start a transaction.
        """
        self.send_init()


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
