# -*- coding: utf-8 -*-
import socket
import time
from datetime import datetime

HOST = '127.0.0.1'     # Endereco IP do Servidor
PORT = 5000            # Porta que o Servidor esta

tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
dest = (HOST, PORT)
tcp.connect(dest)


tipo = 'termometro' 

print ('Digite o local em que o TERMOMETRO se encontra na casa: ')
local = input()

#Envia seu tipo e local ao servidor.
hora = datetime.now().timestamp()
syn = [tipo, local, hora]
conv_syn = str(syn).encode()
tcp.send(conv_syn)

#Recebe seu dicionário do servidor.
protocolo = tcp.recv(1024)
conv_protocolo = protocolo.decode()
e_protocolo = eval(conv_protocolo)
print('MSG recebida do servidor: ', e_protocolo)

# Recebe a Temperatura via teclado.
temperatura = input()
print ('Detecção de Temperatura: ', temperatura)

#Enquanto a temperatura não for 999, continua recebendo a temperatura via teclado e envia o protocolo para o servidor
while temperatura != '999':
				
	e_protocolo['payload'] = temperatura
	e_protocolo['hora'] = datetime.now().timestamp()
	tcp.send(str(e_protocolo).encode())	
	temperatura = input()
	
tcp.close()
