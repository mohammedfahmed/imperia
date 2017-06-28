import subprocess
import time
import socket

# visualization
subprocess.Popen(["/home/ubuntu/Software/sdt-linux-amd64-2.1/sdt3d/sdt3d.sh", "LISTEN TCP,50000"])
time.sleep(15)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', 50000)

sock.connect(server_address)
sock.sendall(b"bgbounds 35.2,32.75,34.5,32.8\n")
sock.sendall(b"sprite soldier2 image /home/ubuntu/Python/models/sdt3dmaps/soldier.gif size 28,60\n")
sock.sendall(b"node s1 type soldier2 pos 35.09,32.73 label off\n")
sock.sendall(b"node s2 type soldier2 pos 34.98,32.79 label off\n")
sock.sendall(b"link s1,s2\n")

