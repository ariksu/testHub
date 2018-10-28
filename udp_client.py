import socket

target_host = "0.0.0.0"
target_port = 9999

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

client.sendto(b"ELF", (target_host, target_port))

data, address = client.recvfrom(4096)

print(data, address)
