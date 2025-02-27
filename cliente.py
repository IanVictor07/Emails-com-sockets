import socket
import json
import os
import bcrypt
import time

# Configurações do cliente
HOST = 'localhost'
PORT = 8080

class EmailClient:
    def __init__(self):
        self.server_host = HOST
        self.server_port = PORT
        self.socket = None
        self.current_user = None
        self.current_user_name = None

    def connect_to_server(self):
        """Conecta ao servidor."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_host, self.server_port))
            return True
        except Exception as e:
            print(f"Erro ao conectar com o servidor: {e}")
            return False

    def send_request(self, request_data):
        """Envia uma solicitação ao servidor e recebe a resposta."""
        try:
            if not self.socket:
                if not self.connect_to_server():
                    return {'status': 'error', 'message': 'Não foi possível conectar ao servidor'}
            
            self.socket.send(json.dumps(request_data).encode('utf-8'))
            response = self.socket.recv(8192)
            return json.loads(response.decode('utf-8'))
        except Exception as e:
            return {'status': 'error', 'message': f'Erro na comunicação: {e}'}
    
    def register_user(self):
        """Registra um novo usuário."""
        nome = input("Nome completo: ")
        username = input("Nome de usuário: ")
        senha = input("Senha: ")
        
        response = self.send_request({'operation': 'register', 'nome': nome, 'username': username, 'senha': senha})
        print(response['message'])
        input("Pressione Enter para continuar...")

    def login(self):
        """Realiza login."""
        username = input("Nome de usuário: ")
        senha = input("Senha: ")
        
        response = self.send_request({'operation': 'login', 'username': username, 'senha': senha})
        if response['status'] == 'success':
            self.current_user = username
            self.current_user_name = response['nome']
        print(response['message'])
        input("Pressione Enter para continuar...")

    def send_email(self):
        """Envia um novo e-mail."""
        destinatario = input("Destinatário: ")
        assunto = input("Assunto: ")
        corpo = input("Corpo do e-mail: ")
        
        response = self.send_request({'operation': 'send_email', 'remetente': self.current_user, 'destinatario': destinatario, 'assunto': assunto, 'corpo': corpo})
        print(response['message'])
        input("Pressione Enter para continuar...")
    
    def receive_emails(self):
        """Recebe e-mails da caixa de entrada."""
        response = self.send_request({'operation': 'receive_emails', 'username': self.current_user})
        if response['status'] == 'success':
            emails = response.get('emails', [])
            for i, email in enumerate(emails, 1):
                print(f"[{i}] {email['remetente']}: {email['assunto']}")
        else:
            print(response['message'])
        input("Pressione Enter para continuar...")
    
    def logout(self):
        """Realiza logout."""
        self.current_user = None
        self.current_user_name = None
        print("Logout realizado com sucesso.")
        input("Pressione Enter para continuar...")
    
    def check_connection(self):
        """Verifica a conexão com o servidor."""
        response = self.send_request({'operation': 'check_connection'})
        print(response['message'])
        input("Pressione Enter para continuar...")

    def menu(self):
        """Exibe o menu do cliente."""
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("1) Apontar Servidor")
            print("2) Cadastrar Conta")
            print("3) Acessar E-mail")
            print("4) Enviar E-mail")
            print("5) Receber E-mails")
            print("6) Logout")
            print("0) Sair")
            
            opcao = input("Escolha uma opção: ")
            if opcao == '1':
                self.check_connection()
            elif opcao == '2':
                self.register_user()
            elif opcao == '3':
                self.login()
            elif opcao == '4' and self.current_user:
                self.send_email()
            elif opcao == '5' and self.current_user:
                self.receive_emails()
            elif opcao == '6' and self.current_user:
                self.logout()
            elif opcao == '0':
                print("Encerrando o programa...")
                break
            else:
                print("Opção inválida!")
                time.sleep(1)

if __name__ == "__main__":
    client = EmailClient()
    client.menu()
