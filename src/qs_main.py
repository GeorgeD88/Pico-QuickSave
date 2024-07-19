from web_connect import try_wifi_networks
from quicksaver import QuickSaver
from rtc_time import set_time
import ujson
import errno


def main():
    # Load config
    try:
        config = config.get_config()
    except OSError as e:
        if e.errno == errno.ENOENT:
            print(f'[{errno.errorcode[e.errno]}]', 'Config file does not exist')

    # Connect to Wi-Fi network
    network_details = config['wlan']
    connected_ssid = try_wifi_networks(network_details)

    # After Pico is connected to Wi-Fi, set the current time
    set_time()

    # Initialize the main QuickSaver component and start running QuickSaver
    quicksaver = QuickSaver(ConsoleListener, SystemNotifier, main_playlist, other_playlist)
    quicksaver.start_quicksaver()


if __name__ == "__main__":
    main()
