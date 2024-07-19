from notifier import trigger_wifi_connecting_status, trigger_wifi_connection_failed
import config_handler as config
from time import sleep
import machine
import network
import socket


def _connect_network(ssid: str, password: str, conn_attempt_time: int = 12) -> bool:
    """ Attempts to connect to the given network using the provided SSID and password. """

    # Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    # Wait given time for connection
    for _ in range(conn_attempt_time):
        if wlan.isconnected() is True:
            print(f'Wlan connected to {ssid}:', wlan.ifconfig())
            return True

        trigger_wifi_connecting_status()
        print('Waiting for connection...')
        sleep(0.73)  # 1s - 0.27s from the notifier wifi status

    # Wlan failed to connect to given network
    trigger_wifi_connection_failed()
    return False

def try_wifi_networks(network_details: dict) -> str:
    """ Loops through the given network details and tries to connect to it.
        If it fails to connect to a network, attempts to connect to the next one."""

    # Loop through the networks from highest to lowest priority
    for network in network_details:
        ssid, password = network['ssid'], network['password']

        # If network is connected successfully, returns the SSID of the connected network
        try:
            if _connect_network(ssid, password) is True:
                return ssid
        except KeyboardInterrupt:
            machine.reset()

    # Returns None if it fails to connect to any network
    return None
