# -*- coding: utf-8 -*-
import socket
import threading
import random
import time
from datetime import datetime

HOST = ''              # Endereco IP do Servidor.
PORT = 5000            # Porta em que o Servidor está.


#Função para criar o dicionário dos aparelhos.
def criaDicAparelhos(gl_aparelhos, local, tipo):
	
	#Cria o ID dos aparelhos.
	global gl_id
	gl_id += 1
	
	gl_aparelhos = {gl_id: {'local': local, 'tipo': tipo,}}
    
	return gl_aparelhos


#Função que recebe as conexões dos aparelhos e passa os parâmetros para a criação dos dicionários.
def conecta(con, cliente):
	
	print('Conectado por', cliente)

	#Dicionários auxiliares
	aparelhos_aux = {}
	ambientes_aux = {}
	
	while True:
		
		#Recebe a primeira mensagem das conexões.
		syn = con.recv(1024)
		
		#Se não houver mensagem, termine.
		if not syn:
			
			break
		
		else:
			
			#Decodifica a mensagem
			deco_syn = syn.decode()
		
			#Transforma a string decodificada em objeto.
			e_syn = eval(deco_syn)
			
			#Retira o tipo e local do aparelhos, da mensagem recebida.
			tipo = e_syn[0]
			local = e_syn[1]
			
			#Cria o dicionário auxiliar dos aparelhos.
			aparelhos_aux = criaDicAparelhos(aparelhos_aux, local, tipo)
			print(aparelhos_aux)
			
			#Varre o dicionário auxiliar dos aparelhos.
			for chave in aparelhos_aux:
				
				#Cria o protocolo e envia de volta a mensagem contendo o dicionário.
				protocolo = {'id': chave, 'tipo': tipo, 'local': local, 'hora': datetime.now().timestamp(), 'payload': ''} 
				con.sendall(str(protocolo).encode())
				
				#Insere o socket no dicionário do aparelhos
				aparelhos_aux[chave].update({'conexao': con})
				
				#Insere o dicionário auxiliar no dicionário global
				gl_aparelhos.update(aparelhos_aux)
			
			return True
		
	return False

#Função que recebe mensagem dos sensores [Sensor de presença, tomada e de temperatura (termometro)].
#Além disso, essa função vai receber uma única mensagem do ar condicionado, afim de que se verifique o horário no momento em que o ar é iniciado.
def recebe(nova_con, cliente):
	
	#Enquanto receber mensagens, inicia a trhead responsável por gravá-las.
	while True:
		
		#Recebe a mensagem.
		msg_sensor = nova_con.recv(1024)
				
		if not msg_sensor:
			
			break
		
		else:
			
			#Decodifica a mensagem.
			deco_msg_sensor = msg_sensor.decode()
		
			#Transforma a string decodificada em objeto.
			e_msg_sensor = eval(deco_msg_sensor)
			
			#Início da thread grava
			thread_grava = threading.Thread(target=grava, args=(e_msg_sensor,))
			thread_grava.start()
			
			#Trava o recebimento de mensagens ao mesmo tempo. 
			thread_grava.join()

# Função que grava as mensagens dos sensores e as passa como parâmetro para os leitores (lampada e ar), ou para um arquivo, caso da tomada. 
def grava(msg_sensor):
	
	#Verifica o tipo de sensor contido na mensagem. 
	if msg_sensor['tipo'] == 'sensorp':
		
		#Passa os parâmetros para a lâmpada
		lampada(msg_sensor['local'], msg_sensor['payload'])

	#Verifica o tipo de sensor contido na mensagem. 
	if msg_sensor['tipo'] == 'tomada':
		
		#Passa os parâmetros para o arquivo.
		with open('consumo.txt', 'a') as arq:
			arq.write('Local da tomada: ')
			arq.write(str(msg_sensor['local']))
			arq.write('; ID da tomada: ')
			arq.write(str(msg_sensor['id']))
			arq.write('; Consumo gerado em KWh: ')
			arq.write(str(msg_sensor['payload']))
			arq.write('\n')

	#Verifica o tipo de sensor contido na mensagem. 
	if msg_sensor['tipo'] == 'termometro':
		
		#Passa os parâmetros para o ar
		ar(msg_sensor['local'], msg_sensor['payload'])
				
	#Verifica o tipo de sensor contido na mensagem. 
	if msg_sensor['tipo'] == 'ar':
		
		#Verifica a hora, dependendo do horário inicia ligado ou desligado.
		if 	datetime.now().strftime('%H:%M') >= '18:00':
			
			ar(msg_sensor['local'], '999')
			
		elif datetime.now().strftime('%H:%M') < '07:00':
			
			ar(msg_sensor['local'], '999')
			
		elif '07:00' <= datetime.now().strftime('%H:%M') < '18:00' :
			
			ar(msg_sensor['local'], '-999')

	return True

#Função que coordena as lâmpadas
def lampada(local, stat):
	
	#Varre o dicionário global de aparelhos pelo id (chave)
	for chave in gl_aparelhos:
		
		#Verifica se o tipo encontrado é lâmpada.
		if gl_aparelhos[chave]['tipo'] == 'lampada':
			
			#Verifica o local da lâmpada.
			if gl_aparelhos[chave]['local'] == local:
				
				#Se a lâmpada foi encontrada no local certo, envia os parâmetros na forma de protocolo.
				protocolo = {'id': chave, 'tipo': gl_aparelhos[chave]['tipo'], 'local': local, 'hora': datetime.now().timestamp(), 'payload': stat}
				gl_aparelhos[chave]['conexao'].send(str(protocolo).encode())

#Função que coordena os condicionadores de ar.
def ar(local, temp):
	
	#Varre o dicionário global de aparelhos pelo id (chave)
	for chave in gl_aparelhos:
		
		#Verifica se o tipo encontrado é um ar condicionado.
		if gl_aparelhos[chave]['tipo'] == 'ar':
			
			protocolo = {'id': chave, 'tipo': gl_aparelhos[chave]['tipo'], 'local': local, 'hora': datetime.now().timestamp(), 'payload': temp}
			
			#Checa o local do ar. Se atender aos parâmetros dos horários de ligar ou desligar, aciona a casa toda.
			if local == 'casa' and temp == '999':								
				gl_aparelhos[chave]['conexao'].send(str(protocolo).encode())
				
			elif local == 'casa' and temp == '-999':
				gl_aparelhos[chave]['conexao'].send(str(protocolo).encode())
			
			#Se foi apenas o termômetro que enviou a temperatura, envia o protolo.
			elif gl_aparelhos[chave]['local'] == local:
				gl_aparelhos[chave]['conexao'].send(str(protocolo).encode())

#Função que define e checa os horários de ligar ou desligar o ar condicionado.
def horario_do_ar():

	horario_inicial = '18:00'
	
	horario_final = '07:00'
	
	while True:
		
		time.sleep(30)
		if horario_inicial == datetime.now().strftime('%H:%M'):
			ar('casa', '999')
		elif horario_final == datetime.now().strftime('%H:%M'):
			ar('casa', '-999')


tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
orig = (HOST, PORT)
tcp.bind(orig)
tcp.listen(1)

gl_aparelhos = {} #Dicionário global dos aparelhos conectados.

gl_id = 0 #ID global

#Cria a thread que controla o horário do ar condicionado
thread_horario_do_ar = threading.Thread(target=horario_do_ar)
thread_horario_do_ar.daemon = True
thread_horario_do_ar.start()

while True:
	
	#Aceita conexões 	
	con, cliente = tcp.accept()
	
	#Cria a thread conecta, que executa a função que recebe as conexões dos aparelhos e passa os parâmetros para a criação dos dicionários.
	thread_conecta = threading.Thread(target=conecta, args=(con, cliente))
	thread_conecta.start()
	thread_conecta.join() #Trava a execução enquanto recebe a localização dos diversos dispositivos.
	
	#Varre o dicionário de aparelhos com a chave gl_id.
	for gl_id in gl_aparelhos:
		
		#A conexão de cada aparelho é guardada em nova_con.
		nova_con = gl_aparelhos[gl_id]['conexao']
		
		#Cria a thread recebe, que recebe mensagem dos sensores.	
		thread_recebe = threading.Thread(target=recebe, args=(nova_con, cliente))
		thread_recebe.start()

tcp.close()
