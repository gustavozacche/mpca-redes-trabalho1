# -*- coding: utf-8 -*-
import socket
import time
from datetime import datetime

HOST = '127.0.0.1'     # Endereco IP do Servidor
PORT = 5000            # Porta que o Servidor esta

tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
dest = (HOST, PORT)
tcp.connect(dest)

tipo = 'ar'

print('Digite o local em que o AR se encontra na casa: ')
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

#Envia o protocolo para o servidor, afim de saber se está no horario de ligar.
hora = datetime.now().timestamp()
e_syn_ack['hora'] = hora
tcp.send(str(e_syn_ack).encode())

# Recebe a temperatura do servidor.
protocolo = tcp.recv(1024)
conv_protocolo = protocolo.decode()
e_protocolo = eval(conv_protocolo)
print(e_protocolo)

#Enquanto a temperatura não for CTRL-X.
while e_protocolo['payload'] != '\x18':

	if e_protocolo['payload'] == '999':
		print ('AR LIGADO por conta do horário')
		
	elif e_protocolo['payload'] == '-999':
		print ('AR DESLIGADO por conta do horário')
		
	elif e_protocolo['payload'] > '28':
		print ('AR LIGADO com temperatura: ', e_protocolo['payload'])
		
	else:		 
		print ('AR DESLIGADO com temperatura: ', e_protocolo['payload'])
		
	protocolo = tcp.recv(1024)
	conv_protocolo = protocolo.decode()
	e_protocolo = eval(conv_protocolo)

tcp.close()
