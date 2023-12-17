import json
import socket
import threading
import time

# Função para lidar com a conexão de um cliente
def handle_client(client_socket, addr):
    print(f"Conexão de {addr}")

    while True:
        try:
            # Receber dados do cliente
            received_data = client_socket.recv(1024).decode()
            if not received_data:
                break

            print(f"Cliente {addr}: ")

            # Converter a string JSON em um objeto Python
            data_dict = json.loads(received_data)

            # Extrair os dados do dicionário
            message = data_dict.get('message', '')
            quantidadeCarros = data_dict.get('Quantidade_de_Carros_da_via_principal', 0)
            quantidadeVermelho = data_dict.get('Quantidade_de_Sinais_vermelhos_furados_da_via_principal', 0)
            quantidadeCarros2 = data_dict.get('Quantidade_de_Carros_da_via_auxiliar', 0)
            quantidadeVermelho2 = data_dict.get('Quantidade_de_Sinais_Vermelhos_furados_da_via_auxiliar', 0)

            # Fazer algo com os dados recebidos
            print(f"Mensagem: {message}")
            print(f"Quantidade de Carros da via principal: {quantidadeCarros}")
            print(f"Quantidade de sinais vermelhos furados na via principal: {quantidadeVermelho}")
            print(f"Quantidade de carros da via auxiliar:{quantidadeCarros2}")
            print(f"Quantidade de sinais vermelhos furados na via auxiliar: {quantidadeVermelho2}")

            # Enviar resposta para o cliente
            response = {"message": "Recebido: " + received_data}
            json_response = json.dumps(response)
            client_socket.send(json_response.encode())
            time.sleep(2)
        except Exception as e:
            print(f"Erro na conexão com {addr}: {e}")
            break

    # Fechar a conexão com o cliente
    client_socket.close()
    print(f"Conexão com {addr} fechada")

def server():
    # Configurar o servidor
    host = '164.41.98.29'  # Endereço IP do servidor --> rasp44, mas muda pro que ce for usar
    port = 1142 # Porta do servidor, parece que não pode usar a 13508

    # Criar um socket TCP/IP
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Vincular o socket ao endereço e porta
    server_socket.bind((host, port))

    # Aguardar conexões
    server_socket.listen(5)  # Permitir até 5 conexões pendentes

    print(f"Aguardando conexões em {host}:{port}")

    while True:
        # Aceitar a conexão do cliente
        client_socket, addr = server_socket.accept()

        # Iniciar uma nova thread para lidar com o cliente
        client_handler = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_handler.start()

if __name__ == "__main__":
    server()