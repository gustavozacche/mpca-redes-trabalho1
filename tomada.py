# -*- coding: utf-8 -*-
import socket
import time
import random
from datetime import datetime
import threading

HOST = '127.0.0.1'     # Endereco IP do Servidor
PORT = 5000            # Porta que o Servidor esta

tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
dest = (HOST, PORT)
tcp.connect(dest)


tipo = 'tomada'

print('Digite o local em que a tomada se encontra na casa: ')
local = input()

#Envia seu tipo e local ao servidor
hora = datetime.now().timestamp()
syn = [tipo, local, hora]
conv_syn = str(syn).encode()
tcp.send(conv_syn)

#Recebe seu dicionário do servidor
syn_ack = tcp.recv(1024)
conv_syn_ack = syn_ack.decode()
e_syn_ack = eval(conv_syn_ack)

e_protocolo = e_syn_ack

#Função que aguarda a contagem de tempo.
def timeout():
	print('Gerando relatório de consumo.')

while True:
	
	#Gera um consumo aleatório.
	kwh = random.randint(1, 1000)
	e_protocolo['payload'] = kwh
	e_protocolo['hora'] = datetime.now().timestamp()
	tcp.send(str(e_protocolo).encode())
	
	t = threading.Timer(2 * 60, timeout)
	t.start()
	t.join()
    
tcp.close()
