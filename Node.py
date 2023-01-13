import sys
import socket
import threading
import time
import pickle

# read arguments
PORT = int(sys.argv[1])
adj = []
num_nodes = 0
nodeList = {}
INF = 999999999
isupdated = True
cond_for_send = True
# read cost file
def read_costfile():
    global num_nodes
    global adj
    global nodeList
    global INF
    global PORT
    global isupdated
    # print("Reading cost file...")
    with open(f"{PORT}.costs") as f:
        first_line = f.readline()
        num_nodes = int(first_line)
        for line in f:
            line = line.strip()
            line = line.split()
            curr_node = int(line[0])
            adj.append(curr_node)
            nodeList[curr_node] = int(line[1])

        for port in range(3000, 3000 + num_nodes):
            if port not in adj and port != PORT:
                nodeList[port] = INF
            if port == PORT:
                nodeList[port] = 0

# print cost table
def print_costtable():
    global num_nodes
    global adj
    global nodeList
    global INF
    global PORT
    global isupdated

    for node in nodeList:
        print(f"{PORT} -{node} | {nodeList[node]}")

# send cost table to neighbors
def send_costtable():
    global num_nodes
    global adj
    global nodeList
    global INF
    global PORT
    global isupdated

    while cond_for_send:
        if isupdated:
            for node in adj:
                while True:
                    try:
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                            s.connect(("localhost", node))
                            nodeList['sender'] = PORT
                            s.sendall(pickle.dumps(nodeList))
                            del nodeList['sender']
                            s.close()
                            break
                    except:
                        pass
            isupdated = False


# receive cost table from neighbors
def receive_costtable():
    global num_nodes
    global adj
    global nodeList
    global INF
    global PORT
    global isupdated
    global cond_for_send

    socket.setdefaulttimeout(5)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("localhost", PORT))
    s.listen()

    while True:
        # print("Waiting for connection...")
        try:
            conn, addr = s.accept()
            data = conn.recv(1024)
            data = pickle.loads(data)
            conn.close()
            sender = data['sender']
            del data['sender']
            for node in data:
                if node != PORT:
                    if nodeList[node] > nodeList[sender] + data[node]:
                        nodeList[node] = nodeList[sender] + data[node]
                        isupdated = True
        except socket.timeout:
            cond_for_send = False

            break

def main():
    global num_nodes
    global adj
    global nodeList
    global INF
    global PORT
    global isupdated
    global cond_for_send

    read_costfile()
    send_thread = threading.Thread(target=send_costtable)
    receive_thread = threading.Thread(target=receive_costtable)
    receive_thread.start()
    time.sleep(3)
    send_thread.start()
    receive_thread.join()
    send_thread.join()
    print_costtable()

if __name__ == "__main__":
    main()
