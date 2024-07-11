import network
import socket
import time
import struct
import machine

NTP_DELTA = 2208988800
# DIFF = -(4 * 3600)  # Subtract 4 hours to go from UTC -> EST
DIFF = 3 * 3600  # Add 3 hours to go from UTC -> Lebanon

host = "pool.ntp.org"
rtc = machine.RTC()


def set_time():
    # Get the external time reference
    rp2.country('US')
    NTP_QUERY = bytearray(48)
    NTP_QUERY[0] = 0x1B
    addr = socket.getaddrinfo(host, 123)[0][-1]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.settimeout(1)
        res = s.sendto(NTP_QUERY, addr)
        msg = s.recv(48)
    finally:
        s.close()

    # Set our internal time
    val = struct.unpack("!I", msg[40:44])[0]
    tm = val - NTP_DELTA
    tm += DIFF
    t = time.gmtime(tm)

    # (year, month, day, weekday, hours, minutes, seconds, subseconds)
    rtc.datetime((t[0],t[1],t[2],t[6]+1,t[3],t[4],t[5],0))

def _now_timestring():
    timestamp=rtc.datetime()
    return "%04d-%02d-%02d %02d:%02d:%02d"%(timestamp[0:3] + timestamp[4:7])
