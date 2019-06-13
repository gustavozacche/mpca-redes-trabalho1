# -*- coding: utf-8 -*-
import socket
import time
from datetime import datetime

HOST = '127.0.0.1'     # Endereco IP do Servidor
PORT = 5000            # Porta que o Servidor esta

tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
dest = (HOST, PORT)
tcp.connect(dest)

tipo = 'lampada'

print('Digite o local em que a LAMPADA se encontra na casa: ')
local = input()

#Envia seu tipo e local ao servidor.
hora = datetime.now().timestamp()
syn = [tipo, local, hora]
conv_syn = str(syn).encode()
tcp.send(conv_syn)

#Recebe seu dicionário do servidor.
syn_ack = tcp.recv(1024)
conv_syn_ack = syn_ack.decode()
e_syn_ack = eval(conv_syn_ack)
print('Primeira msg recebida do servidor: ', e_syn_ack)


# Recebe a presença do servidor.
protocolo = tcp.recv(1024)
conv_protocolo = protocolo.decode()
e_protocolo = eval(conv_protocolo)
print(e_protocolo)

#Enquanto o status não for CTRL-X.
while e_protocolo['payload'] != '\x18':

	if e_protocolo['payload'] == '1':
		
		print ('Lampada Ligada')
		
	else:
		 
		print ('Lampada Desligada')
		
	protocolo = tcp.recv(1024)
	conv_protocolo = protocolo.decode()
	e_protocolo = eval(conv_protocolo)

tcp.close()
