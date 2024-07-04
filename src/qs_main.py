from quicksaver import QuickSaver
# TODO: remove 'raspi' prefix from files because all files are for RasPi
#from raspi_listener import RasPiListener
import json


# TODO: finalize this but I think I should maybe put it in a different file.
# I should also use the 15 line function rule (from SWE class), and that will look better in a different file.
def connect_wlan():
    """
    if self.config['setup_network']:
        self.wlan_ap = network.WLAN(network.AP_IF)
        self.wlan_ap.active(False)
        self.wlan = network.WLAN(network.STA_IF)
        try:
            self.wlan.active(True)
            self.wlan.connect(self.config['wlan']['ssid'], self.config['wlan']['password'])
            self.wlan.config(dhcp_hostname=self.config['wlan']['mdns'])
        except Exception as e:
            self.oled.show(e.__class__.__name__, str(e))
            if str(e) == "Wifi Internal Error":
                time.sleep(3)
                import machine
                machine.reset()
            else:
                raise
        print("network configured")
    else:
        self.wlan = network.WLAN()
        print("using existing network configuration")

    self.ip = self.wlan.ifconfig()[0]
            print("connected at {} as {}".format(self.ip, self.config['wlan']['mdns']))
    """
    pass


def main():
    # Load config file and get playlist IDs
    with open('config.json', 'r') as infile:
        config = json.load(infile)

    # TODO: consider checking if playlist IDs exist on Spotify
    # if not, create new ones and save the IDs to config file.
    main_playlist = config['playlists']['main_playlist']
    other_playlist = config['playlists']['other_playlist']

    # initialize the main quick saver component and start the input listener
    print('starting QuickSaver!')
    quicksaver = QuickSaver(ConsoleListener, SystemNotifier, main_playlist, other_playlist)
    quicksaver.start_quicksaver()  # renamed from `start_input_listener`


if __name__ == "__main__":
    main()
