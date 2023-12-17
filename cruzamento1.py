import RPi.GPIO as GPIO
import threading
import time
import socket
import json 

# removendo os warnings
GPIO.setwarnings(False)

# Inicialize a biblioteca GPIO e seus respectivos pinos
GPIO.setmode(GPIO.BCM)
SEMAFORO1PINO1 = 9
SEMAFORO1PINO2 = 11
SEMAFORO2PINO1 = 5
SEMAFORO2PINO2 = 6
BOTAO1 = 13
BOTAO2 = 19
SENSORAUXILIAR1 = 26
SENSORAUXILIAR2 = 22
SENSORPRINCIPAL1 = 0
SENSORPRINCIPAL2 = 27
BUZZER = 17

#saidas --> valores que podem mudar
GPIO.setup(SEMAFORO1PINO1, GPIO.OUT)
GPIO.setup(SEMAFORO1PINO2, GPIO.OUT)
GPIO.setup(SEMAFORO2PINO1, GPIO.OUT)
GPIO.setup(SEMAFORO2PINO2, GPIO.OUT) # GPIO.OUT --> PODE ALTERAR
# entradas - leitura
GPIO.setup(BOTAO1, GPIO.IN) #GPIO.IN --> LEITURA
GPIO.setup(BOTAO2, GPIO.IN)
GPIO.setup(SENSORAUXILIAR1, GPIO.IN)
GPIO.setup(SENSORAUXILIAR2, GPIO.IN)
GPIO.setup(SENSORPRINCIPAL1, GPIO.IN)
GPIO.setup(SENSORPRINCIPAL2, GPIO.IN)
GPIO.setup(BUZZER, GPIO.OUT)
GPIO.setup(BOTAO1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BOTAO2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(SENSORPRINCIPAL1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(SENSORAUXILIAR1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

#Parte do client para a comunicação tcp.ip

# Configuracao da parte do client para mandarmos os dados para o central.py

# Configurar o cliente
host = '164.41.98.29'  # Endereço IP do servidor rasp44 --> muda pro que vc for usar pra testar
port = 1142    # Porta do servidor
# tem que passar a mensagem de qual cruzamento vem e os dados
def client():
    global quantidadeCarros, quantidadeVermelho, quantidadeCarros2, quantidadeVermelho2  # Declare essas variáveis como globais
    global client_socket 
    client_socket = None
    
    while True:
        try:
            if client_socket is None:
                # Criar um socket TCP/IP
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                # Conectar-se ao servidor
                client_socket.connect((host, port))

            while True:
                # Criar um dicionário com os dados a serem enviados
                data_to_send = {
                    'message': "conectado ao cruzamento 1",
                    'Quantidade_de_Carros_da_via_principal': quantidadeCarros,
                    'Quantidade_de_Sinais_vermelhos_furados_da_via_principal': quantidadeVermelho,
                    'Quantidade_de_Carros_da_via_auxiliar': quantidadeCarros2,
                    'Quantidade_de_Sinais_Vermelhos_furados_da_via_auxiliar': quantidadeVermelho2,
                }

                # Converta o dicionário em uma string JSON
                json_data = json.dumps(data_to_send)

                # Enviar mensagem para o servidor
                client_socket.send(json_data.encode())

                # Receber resposta do servidor
                received_data = client_socket.recv(1024).decode()
                print("Servidor:", received_data)

                if received_data == '':
                    print('Erro ao enviar mensagem para o servidor, tentando novamente...')
                    client_socket.close()
                    return client()

                time.sleep(2)

                # Imprimir dados em linhas separadas
                print("\nDados Enviados:")
                print(f"Mensagem: {data_to_send['message']}")
                print(f"Quantidade de Carros da via principal: {data_to_send['Quantidade_de_Carros_da_via_principal']}")
                print(f"Quantidade de Sinais vermelhos furados na via principal: {data_to_send['Quantidade_de_Sinais_vermelhos_furados_da_via_principal']}\n")
                print(f"Quantidade de Carros da via auxiliar: {data_to_send['Quantidade_de_Carros_da_via_auxiliar']}")
                print(f"Quantidade de Sinais vermelhos furados na via auxiliar: {data_to_send['Quantidade_de_Sinais_vermelhos_furados_da_via_auxiliar']}\n")

                
                
        except Exception as e:
            print("Erro:", e)
            print("Tentando estabelecer conexão com o servidor...")
            time.sleep(1)
            return client()



#variaveis globais
valorBotao2 = 0
valorBotao1 = 0
count = 0
count2 = 0
# sensores
quantidadeCarros = 0
quantidadeVermelho = 0
sensorTempo = 0
contaCarro = 0
#lógica para a via auxiliar
contaCarro2 = 0
quantidadeCarros2= 0
quantidadeVermelho2 = 0

def buzzer():
    GPIO.output(BUZZER, GPIO.HIGH)

def trocaBotao(): 
    return GPIO.input(BOTAO1)
    
def passaCarro():
    return GPIO.input(SENSORPRINCIPAL1)              

def sinalDesligado():     
    GPIO.output(SEMAFORO1PINO1, GPIO.LOW)
    GPIO.output(SEMAFORO1PINO2, GPIO.LOW)

def sinalAmarelo():
    GPIO.output(SEMAFORO1PINO1, GPIO.HIGH)
    GPIO.output(SEMAFORO1PINO2, GPIO.LOW)
    
def sinalVerde():
    GPIO.output(SEMAFORO1PINO1, GPIO.LOW)
    GPIO.output(SEMAFORO1PINO2, GPIO.HIGH)
    
def sinalVermelho():
    GPIO.output(SEMAFORO1PINO1, GPIO.HIGH)
    GPIO.output(SEMAFORO1PINO2, GPIO.HIGH)
    
   # funcao para trocar a cor do sinal no melhor dos cenarios 
def comportamentoPadrao( valorBotao1):
    global count
    if count >= 0 and count <= 20:
        sinalVerde()
        if valorBotao1 == 1 and (count >= 10 and count <= 20): #altera comportamento padrao
            print("entrou sinal amarelo")
            count = 20
    elif count > 20 and count <=22:
        sinalAmarelo()
    else:
        sinalVermelho()    
        if valorBotao1 == 1 and (count > 27 and count <= 32): #altera comportamento padrao
            print("entrou sinal verde")
            sinalVerde()
                
def trocaBotao1():
    global valorBotao1
    while True:
        valorBotao1 = trocaBotao()
        time.sleep(0.340)

#verificando se o sinal esta vermelho para ver se o carro passou nesse momento
def isSinalVermelho():
    return GPIO.input(SEMAFORO1PINO1) == 1 and GPIO.input(SEMAFORO1PINO2)==1
 
def verificaCarroPassou():
    global contaCarro
    while True:
        contaCarro = passaCarro()
        time.sleep(0.1)     

def passaCarro1():
    global quantidadeCarros
    while True:
        if passaCarro() == 1:
            quantidadeCarros +=1
            time.sleep(0.340) #passando o mesmo tempo do botao

def passouVermelho():       
    global quantidadeVermelho
    global contaCarro
    while True:         
        if contaCarro and (isSinalVermelho()):
            quantidadeVermelho +=1
        time.sleep(0.1) #pensar num tempo melhor
 
                          
def trocaSinal():
    global count
    while True:
        comportamentoPadrao( valorBotao1)
        time.sleep(1)
        count +=1
        if count == 32:
            count = 0


    
# replicando a logica para o outro semaforo

#-------------------------------------------------------------------------------------

def trocaBotao_2(): 
    return GPIO.input(BOTAO2)                  


def passaCarro_2():
    return GPIO.input(SENSORAUXILIAR1)      
             
                  
def trocaBotao2():
    global valorBotao2
    while True:
        valorBotao2 = trocaBotao_2()
        time.sleep(0.340)
                  
def sinalDesligado2():
    GPIO.output(SEMAFORO2PINO1, GPIO.LOW)
    GPIO.output(SEMAFORO2PINO2, GPIO.LOW)
    
def sinalAmarelo2():
    GPIO.output(SEMAFORO2PINO1, GPIO.HIGH)
    GPIO.output(SEMAFORO2PINO2, GPIO.LOW)
    
def sinalVerde2():
    GPIO.output(SEMAFORO2PINO1, GPIO.LOW)
    GPIO.output(SEMAFORO1PINO2, GPIO.HIGH)
    
def sinalVermelho2():
    GPIO.output(SEMAFORO2PINO1, GPIO.HIGH)
    GPIO.output(SEMAFORO2PINO2, GPIO.HIGH)

  
   # funcao para trocar a cor do sinal no melhor dos cenarios 
def comportamentoPadrao2( valorBotao2):
    global count2
    if count2 >= 0 and count2 <= 20:
        sinalVermelho2()
        if valorBotao2 == 1 and (count2 >= 10 and count2 <= 20): #altera comportamento padrao
            print("entrou sinal verde")
            count2 = 20
    elif count2 > 20 and count2 <=30:
        sinalVerde2()
        if valorBotao2 == 1 and (count2 >= 25 and count2 <=30):
            count2 = 30
    else:
        sinalAmarelo2()  
          
def trocaSinal2():
    global count2
    while True:
        comportamentoPadrao2( valorBotao2)
        time.sleep(1)
        count2 +=1
        if count2 == 32:
            count2 = 0
            

#verificando se o sinal esta vermelho
def isSinalVermelho2():
    return GPIO.input(SEMAFORO2PINO1) == 1 and GPIO.input(SEMAFORO2PINO2)==1

def verificaCarroPassou2():
    global contaCarro2
    while True:
        contaCarro2= passaCarro_2()
        time.sleep(0.1)     

def passaCarro2():
    global quantidadeCarros2
    while True:
        if passaCarro_2() == 1:
            quantidadeCarros2 +=1
            time.sleep(0.340) #passando o mesmo tempo do botao

def passouVermelho2():       
    global quantidadeVermelho2
    global contaCarro2
    while True:          
        if contaCarro2 and (isSinalVermelho2()):
            quantidadeVermelho2 +=1
        time.sleep(0.1) 
            
#----------------------------------------------------------------------------------
            
# Trouxe todas minhas Threads para o final para garantir que nenhuma vai travar meu programa e não rode alguma das funções acima            
temporizador2 = threading.Thread(target=trocaSinal2)
acionaBotao2 = threading.Thread(target=trocaBotao2)
acionaContaCarro= threading.Thread(target=passaCarro1)
acionaContaCarro2= threading.Thread(target=passaCarro2)
contaVermelho = threading.Thread(target=passouVermelho)
contaVermelho2 = threading.Thread(target=passouVermelho2)
temporizador = threading.Thread(target=trocaSinal)
acionaBotao1 = threading.Thread(target=trocaBotao1)
acionaClient = threading.Thread(target=client)
acionaVerificaCarroPassou = threading.Thread(target=verificaCarroPassou)
acionaVerificaCarroPassou2 = threading.Thread(target=verificaCarroPassou2)
#start
temporizador2.start()
acionaBotao2.start()
acionaContaCarro.start()
acionaContaCarro2.start()
contaVermelho.start()
contaVermelho2.start()
temporizador.start()
acionaBotao1.start()
acionaClient.start()
acionaVerificaCarroPassou.start()
acionaVerificaCarroPassou2.start()
#join
temporizador2.join()
acionaBotao2.join()
acionaContaCarro.join() 
contaVermelho.join()   
temporizador.join()
acionaBotao1.join()
acionaClient.join()
acionaVerificaCarroPassou.join()
acionaContaCarro2.join()
contaVermelho2.join()
acionaVerificaCarroPassou2.join()