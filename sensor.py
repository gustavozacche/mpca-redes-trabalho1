# -*- coding: utf-8 -*-
import socket
import time
import threading
from datetime import datetime

HOST = '127.0.0.1'     # Endereco IP do Servidor
PORT = 5000            # Porta que o Servidor esta

tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
dest = (HOST, PORT)
tcp.connect(dest)


tipo = 'sensorp'

print ('Digite o local em que o Sensor se encontra na casa: ')
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

# Recebe se há presença via teclado.
presenca = input()

#Função de contador de tempo do sensor de presença.
def contador(p):
	
	#Quando o contador termina, os campos do protocolo recebem suas respectivas atribuições, e a mensagem é enviada ao servidor.
	e_protocolo['payload'] = '0'
	e_protocolo['hora'] = datetime.now().timestamp()
	tcp.send(str(e_protocolo).encode())
	
while presenca !='\x18':
	
	#Envia a mensagem contendo a presença.
	e_protocolo['payload'] = presenca
	e_protocolo['hora'] = datetime.now().timestamp()
	tcp.send(str(e_protocolo).encode())
	
	#Se o que for digitado no teclado for 1, começa a thread do contador de tempo.
	if presenca == '1':
		t = threading.Timer(10.0, contador, presenca)
		t.start()
	
	#Aguarda o recebimento de nova presença.
	presenca = input()
	
	#Se houver nova presença enquanto o contador estiver ativo, cancele-o:
	if presenca == '1':
		try:
			t.cancel()
		except NameError:
			time.sleep(0.1)

tcp.close()
