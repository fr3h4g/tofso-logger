import socket
import network
import os
import gc
import wifi
import time
import machine


last_client_socket = None
server_socket = None


def parse_buf(buf):
    new_buf = b""
    discard_count = 0
    for i in range(len(buf)):
        byte = buf[i]
        if byte == 0xFF:
            discard_count = 2
            byte = 0
        elif discard_count > 0:
            discard_count -= 1
            byte = 0

        if byte:
            new_buf += chr(byte)

    return new_buf


def accept_telnet_connect(telnet_server):
    global last_client_socket

    if last_client_socket:
        # close any previous clients
        last_client_socket.close()

    last_client_socket, remote_addr = telnet_server.accept()
    print("Telnet connection from:", remote_addr)
    last_client_socket.setblocking(False)

    # last_client_socket.sendall(bytes([255, 252, 34])) # dont allow line mode
    # last_client_socket.sendall(bytes([255, 251, 1])) # turn off local echo
    logged_in = False

    last_client_socket.send(
        "Welcome to tofso-logger telnet server!\r\nPlease login.\r\n"
    )
    last_client_socket.send("Password: ")

    while True:
        buf = last_client_socket.read()
        if buf:
            if buf == b"\x03" or buf == b"\xff\xf4\xff\xfd\x06":
                if last_client_socket:
                    last_client_socket.close()
                break
            password = parse_buf(buf).decode("utf-8").rstrip("\r\n").lower()
            if password:
                if password == "vatten":
                    logged_in = True
                    break
                else:
                    last_client_socket.send("Password: ")

    if logged_in:
        last_client_socket.send("Logged in. Welcome.\r\n")
        last_client_socket.send("To list available commands type help.\r\n>")
        while True:
            buf = last_client_socket.read()
            if buf:
                if buf == b"\x03" or buf == b"\xff\xf4\xff\xfd\x06":
                    if last_client_socket:
                        last_client_socket.close()
                    break
                command = parse_buf(buf).decode("utf-8").rstrip("\r\n").lower()
                print(command)

                if command == "mem":
                    last_client_socket.send(free(full=True))

                if command == "df":
                    last_client_socket.send(df())

                if command == "help":
                    last_client_socket.send(help())

                if command == "exit":
                    if last_client_socket:
                        last_client_socket.close()
                    break

                if command == "reboot":
                    last_client_socket.send(
                        "rebooting tofso-logger in 10 secounds...\r\n"
                    )
                    if last_client_socket:
                        last_client_socket.close()
                    time.sleep(10)
                    machine.reset()

                last_client_socket.send(">")


def df():
    s = os.statvfs("//")
    return "Free diskspace: {0} MB \r\n".format((int(s[0]) * int(s[3])) / 1048576)


def free(full=False):
    gc.collect()
    F = gc.mem_free()
    A = gc.mem_alloc()
    T = F + A
    P = "{0:.2f}%".format(F / T * 100)
    if not full:
        return P
    else:
        return "Memory total:{0} free:{1} ({2})\r\n".format(T, F, P)


def help():
    return (
        "tofso-logger help\r\n"
        "\r\n"
        "available commands:\r\n"
        "    df          disk space usage\r\n"
        "    exit        exit telnet session\r\n"
        "    help        show this help\r\n"
        "    mem         memory usage\r\n"
        "    reboot      reboot the processor\r\n"
    )


def start():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    ai = socket.getaddrinfo("0.0.0.0", 23)
    addr = ai[0][4]

    server_socket.bind(addr)
    server_socket.listen(1)
    server_socket.setsockopt(socket.SOL_SOCKET, 20, accept_telnet_connect)

    for i in (network.AP_IF, network.STA_IF):
        wlan = network.WLAN(i)
        if wlan.active():
            print("Telnet server started on {}:{}".format(wlan.ifconfig()[0], 23))


if __name__ == "__main__":
    wlan = wifi.connect()
    if wlan:
        print(wlan.ifconfig())

        start()

        while True:
            pass
