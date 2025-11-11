"""
UDP Communication Manager for Powersoft Mezzo Amplifiers.

This module handles asynchronous UDP socket communication with Mezzo amplifiers,
including request/response matching, timeout handling, and connection management.
"""
import asyncio
import logging
from typing import Optional, Dict, Tuple
from dataclasses import dataclass, field
from datetime import datetime

from .pbus_protocol import PBusPacket, PBusCommand, PBusResponse, generate_tag

_LOGGER = logging.getLogger(__name__)

# Constants
DEFAULT_PORT = 8002
DEFAULT_TIMEOUT = 2.0  # seconds
MAX_PACKET_SIZE = 2048  # bytes
BROADCAST_ADDRESS = "255.255.255.255"


@dataclass
class PendingRequest:
    """Represents a pending request awaiting response."""
    tag: bytes
    future: asyncio.Future
    timestamp: datetime = field(default_factory=datetime.now)


class UDPManager:
    """
    Manages UDP communication with a Powersoft Mezzo amplifier.

    Handles asynchronous sending and receiving of PBus protocol packets,
    with request/response matching via TAG and timeout handling.
    """

    def __init__(
        self,
        host: str,
        port: int = DEFAULT_PORT,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        """
        Initialize the UDP manager.

        Args:
            host: IP address of the amplifier
            port: UDP port (default 8002)
            timeout: Default timeout for requests in seconds
        """
        self.host = host
        self.port = port
        self.timeout = timeout

        self._transport: Optional[asyncio.DatagramTransport] = None
        self._protocol: Optional['UDPProtocol'] = None
        self._pending_requests: Dict[bytes, PendingRequest] = {}
        self._is_connected = False
        self._lock = asyncio.Lock()

    async def connect(self) -> None:
        """
        Create the UDP socket and start listening.

        Raises:
            OSError: If socket creation fails
        """
        if self._is_connected:
            _LOGGER.debug("Already connected to %s:%d", self.host, self.port)
            return

        try:
            _LOGGER.info("Connecting to %s:%d", self.host, self.port)

            loop = asyncio.get_event_loop()

            # Create UDP endpoint
            self._transport, self._protocol = await loop.create_datagram_endpoint(
                lambda: UDPProtocol(self._handle_response),
                remote_addr=(self.host, self.port),
            )

            self._is_connected = True
            _LOGGER.info("Successfully connected to %s:%d", self.host, self.port)

        except OSError as err:
            _LOGGER.error("Failed to connect to %s:%d: %s", self.host, self.port, err)
            raise

    async def disconnect(self) -> None:
        """Close the UDP socket and clean up resources."""
        if not self._is_connected:
            return

        _LOGGER.info("Disconnecting from %s:%d", self.host, self.port)

        # Cancel all pending requests
        for request in self._pending_requests.values():
            if not request.future.done():
                request.future.cancel()

        self._pending_requests.clear()

        # Close transport
        if self._transport:
            self._transport.close()
            self._transport = None

        self._protocol = None
        self._is_connected = False
        _LOGGER.info("Disconnected from %s:%d", self.host, self.port)

    async def send_request(
        self,
        commands: list[PBusCommand],
        timeout: Optional[float] = None,
    ) -> list[PBusResponse]:
        """
        Send a request and wait for response.

        Args:
            commands: List of PBus commands to send
            timeout: Timeout in seconds (uses default if None)

        Returns:
            List of PBus responses

        Raises:
            ConnectionError: If not connected
            TimeoutError: If response not received within timeout
            ValueError: If response parsing fails
        """
        if not self._is_connected:
            raise ConnectionError("Not connected to amplifier")

        if timeout is None:
            timeout = self.timeout

        async with self._lock:
            # Generate unique TAG
            tag = generate_tag()

            # Ensure TAG is unique
            while tag in self._pending_requests:
                tag = generate_tag()

            # Build request packet
            packet = PBusPacket.build_request(tag, commands)

            # Create future for response
            future = asyncio.get_event_loop().create_future()
            self._pending_requests[tag] = PendingRequest(tag, future)

            try:
                # Send packet
                _LOGGER.debug(
                    "Sending request to %s:%d (TAG: %s, size: %d bytes)",
                    self.host,
                    self.port,
                    tag.hex(),
                    len(packet),
                )
                self._transport.sendto(packet)

                # Wait for response with timeout
                try:
                    responses = await asyncio.wait_for(future, timeout=timeout)
                    _LOGGER.debug(
                        "Received response from %s:%d (TAG: %s, %d responses)",
                        self.host,
                        self.port,
                        tag.hex(),
                        len(responses),
                    )
                    return responses

                except asyncio.TimeoutError:
                    _LOGGER.warning(
                        "Request timeout after %.1fs (TAG: %s)",
                        timeout,
                        tag.hex(),
                    )
                    raise TimeoutError(
                        f"No response received within {timeout}s"
                    ) from None

            finally:
                # Clean up pending request
                self._pending_requests.pop(tag, None)

    def _handle_response(self, data: bytes, addr: Tuple[str, int]) -> None:
        """
        Handle received UDP packet.

        Args:
            data: Raw packet data
            addr: Source address tuple (host, port)
        """
        try:
            # Parse response packet
            tag, responses = PBusPacket.parse_response(data)

            _LOGGER.debug(
                "Received packet from %s:%d (TAG: %s, size: %d bytes)",
                addr[0],
                addr[1],
                tag.hex(),
                len(data),
            )

            # Find matching pending request
            pending = self._pending_requests.get(tag)
            if pending:
                # Set result on future
                if not pending.future.done():
                    pending.future.set_result(responses)
            else:
                _LOGGER.warning(
                    "Received response with unknown TAG: %s", tag.hex()
                )

        except ValueError as err:
            _LOGGER.error("Failed to parse response packet: %s", err)
        except Exception as err:
            _LOGGER.exception("Unexpected error handling response: %s", err)

    @property
    def is_connected(self) -> bool:
        """Check if connected to amplifier."""
        return self._is_connected

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()


class UDPProtocol(asyncio.DatagramProtocol):
    """
    Asyncio DatagramProtocol implementation for receiving UDP packets.
    """

    def __init__(self, callback):
        """
        Initialize the protocol.

        Args:
            callback: Callback function(data, addr) to handle received packets
        """
        self.callback = callback
        self.transport = None

    def connection_made(self, transport):
        """Called when connection is established."""
        self.transport = transport

    def datagram_received(self, data: bytes, addr: Tuple[str, int]):
        """
        Called when a datagram is received.

        Args:
            data: Received bytes
            addr: Source address tuple
        """
        self.callback(data, addr)

    def error_received(self, exc: Exception):
        """
        Called when an error is received.

        Args:
            exc: Exception that occurred
        """
        _LOGGER.error("UDP error: %s", exc)

    def connection_lost(self, exc: Optional[Exception]):
        """
        Called when connection is lost.

        Args:
            exc: Exception if connection lost due to error
        """
        if exc:
            _LOGGER.error("UDP connection lost: %s", exc)


class UDPBroadcaster:
    """
    Utility for broadcasting UDP packets for device discovery.
    """

    @staticmethod
    async def broadcast(
        commands: list[PBusCommand],
        port: int = DEFAULT_PORT,
        timeout: float = 5.0,
    ) -> Dict[str, list[PBusResponse]]:
        """
        Broadcast a request and collect responses from all devices.

        Args:
            commands: PBus commands to broadcast
            port: UDP port to broadcast on
            timeout: Time to wait for responses

        Returns:
            Dictionary mapping IP addresses to response lists
        """
        responses_by_host = {}
        response_event = asyncio.Event()

        def handle_response(data: bytes, addr: Tuple[str, int]):
            """Handle broadcast responses."""
            try:
                _, responses = PBusPacket.parse_response(data)
                responses_by_host[addr[0]] = responses
                _LOGGER.debug("Broadcast response from %s", addr[0])
            except ValueError as err:
                _LOGGER.debug("Invalid broadcast response from %s: %s", addr[0], err)

        try:
            # Create UDP endpoint for broadcast
            loop = asyncio.get_event_loop()
            transport, protocol = await loop.create_datagram_endpoint(
                lambda: UDPProtocol(handle_response),
                local_addr=('0.0.0.0', 0),
                allow_broadcast=True,
            )

            try:
                # Build and send broadcast packet
                tag = generate_tag()
                packet = PBusPacket.build_request(tag, commands)

                _LOGGER.info("Broadcasting discovery packet on port %d", port)
                transport.sendto(packet, (BROADCAST_ADDRESS, port))

                # Wait for timeout to collect responses
                await asyncio.sleep(timeout)

            finally:
                transport.close()

        except OSError as err:
            _LOGGER.error("Failed to broadcast: %s", err)

        _LOGGER.info("Broadcast complete, received %d responses", len(responses_by_host))
        return responses_by_host

    @staticmethod
    async def broadcast_quattro(
        timeout: float = 5.0,
    ) -> Dict[str, bytes]:
        """
        Broadcast a QUATTROCANALI discovery request and collect responses.

        Args:
            timeout: Time to wait for responses

        Returns:
            Dictionary mapping IP addresses to raw response data
        """
        from .quattro_protocol import build_power_command, DEFAULT_PORT as QUATTRO_PORT, QuattroResponse

        responses_by_host = {}

        def handle_response(data: bytes, addr: Tuple[str, int]):
            """Handle QUATTROCANALI broadcast responses."""
            try:
                # Just store raw response data - we'll check if it's valid QUATTRO protocol
                if len(data) > 0:
                    responses_by_host[addr[0]] = data
                    _LOGGER.debug("QUATTROCANALI broadcast response from %s", addr[0])
            except Exception as err:
                _LOGGER.debug("Error handling QUATTROCANALI response from %s: %s", addr[0], err)

        try:
            # Create UDP endpoint for broadcast
            loop = asyncio.get_event_loop()
            transport, protocol = await loop.create_datagram_endpoint(
                lambda: UDPProtocol(handle_response),
                local_addr=('0.0.0.0', 0),
                allow_broadcast=True,
            )

            try:
                # Build a PING command for discovery
                # PING is the simplest connectivity test with no side effects
                from .quattro_protocol import build_ping_command
                ping_cmd = build_ping_command()
                packet = ping_cmd.build_packet()

                _LOGGER.info("Broadcasting QUATTROCANALI PING on port %d", QUATTRO_PORT)
                transport.sendto(packet, (BROADCAST_ADDRESS, QUATTRO_PORT))

                # Wait for timeout to collect responses
                await asyncio.sleep(timeout)

            finally:
                transport.close()

        except OSError as err:
            _LOGGER.error("Failed to broadcast QUATTROCANALI: %s", err)

        _LOGGER.info("QUATTROCANALI broadcast complete, received %d responses", len(responses_by_host))
        return responses_by_host
