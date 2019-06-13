import socket
import time

HOST = '127.0.0.1'     # Endereco IP do Servidor
PORT = 5000            # Porta que o Servidor esta

tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
dest = (HOST, PORT)
tcp.connect(dest)


tipo = 'ar'

print('Digite o local em que o AR se encontra na casa: ')
local = input()

#Envia seu tipo e local ao servidor

msg_enviada = [tipo, local]
conv_msg_enviada = str(msg_enviada).encode()
tcp.send(conv_msg_enviada)


#Recebe seu dicionário do servidor
 
msg_recebida = tcp.recv(1024)
conv_msg_recebida = msg_recebida.decode()
e_msg_recebida = eval(conv_msg_recebida)
print('Primeira msg recebida do servidor: ', e_msg_recebida)


# Recebe a temperatura do servidor

temperatura = tcp.recv(1024)
conv_temperatura = temperatura.decode()
e_temperatura = eval(conv_temperatura)
print(e_temperatura)

#Enquanto a temperatura não for CTRL-X

while e_temperatura != '\x18':

	if e_temperatura > 28:
		
		print ('AR Ligado')
		
	else:
		 
		print ('AR Desligada')
		
	time.sleep(1)
	temperatura = tcp.recv(1024)
	conv_temperatura = temperatura.decode()
	e_temperatura = eval(conv_temperatura)
	print(e_temperatura)

tcp.close()
