import bluetooth
import subprocess

def set_network_configuration(ssid, password):
    # Command to configure Wi-Fi network
    cmd = f"sudo wpa_cli -i wlan0 disconnect && \
           sudo wpa_passphrase {ssid} {password} | sudo tee -a /etc/wpa_supplicant/wpa_supplicant.conf > /dev/null && \
           sudo wpa_cli -i wlan0 reconfigure"
    subprocess.run(cmd, shell=True)

def start_server():
    server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    server_socket.bind(("", bluetooth.PORT_ANY))
    server_socket.listen(1)

    port = server_socket.getsockname()[1]

    bluetooth.advertise_service(server_socket, "MyAdminService",
                                service_id="1234567890123456",
                                service_classes=[bluetooth.SERIAL_PORT_CLASS],
                                profiles=[bluetooth.SERIAL_PORT_PROFILE])

    print("Waiting for connection on RFCOMM channel", port)

    client_socket, client_info = server_socket.accept()
    print("Accepted connection from", client_info)

    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            # Process received data here
            data_str = data.decode("utf-8").strip()
            if data_str.startswith("SET_NETWORK:"):
                _, ssid, password = data_str.split(":")
                set_network_configuration(ssid, password)
                client_socket.send("Network configuration updated successfully.".encode("utf-8"))
    except Exception as e:
        print("Error:", e)

    client_socket.close()
    server_socket.close()

if __name__ == "__main__":
    start_server()
