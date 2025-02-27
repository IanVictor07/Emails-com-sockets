import socket
import threading
import json
import bcrypt
from datetime import datetime

# Configurações do servidor
HOST = 'localhost'
PORT = 8080

class EmailServer:
    def __init__(self, host=HOST, port=PORT):
        self.host = host
        self.port = port
        self.server_socket = None
        self.users = {}
        self.emails = {}
        self.running = False
        self.lock = threading.Lock()

    def start(self):
        """Inicia o servidor e aceita conexões."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.running = True
        print(f"Servidor rodando em {self.host}:{self.port}")
        
        while self.running:
            client_socket, client_address = self.server_socket.accept()
            threading.Thread(target=self.handle_client, args=(client_socket, client_address), daemon=True).start()
    
    def handle_client(self, client_socket, client_address):
        """Gerencia as solicitações dos clientes."""
        try:
            while self.running:
                data = client_socket.recv(4096)
                if not data:
                    break
                
                request = json.loads(data.decode('utf-8'))
                operation = request.get('operation')
                response = {'status': 'error', 'message': 'Operação desconhecida'}
                
                if operation == 'register':
                    response = self.register_user(request)
                elif operation == 'login':
                    response = self.authenticate_user(request)
                elif operation == 'send_email':
                    response = self.send_email(request)
                elif operation == 'receive_emails':
                    response = self.get_emails(request)
                elif operation == 'logout':
                    response = {'status': 'success', 'message': 'Logout realizado com sucesso'}
                elif operation == 'check_connection':
                    response = {'status': 'success', 'message': 'Servidor disponível'}
                
                client_socket.send(json.dumps(response).encode('utf-8'))
        finally:
            client_socket.close()

    def register_user(self, request):
        """Registra um novo usuário."""
        username = request.get('username')
        nome = request.get('nome')
        senha = request.get('senha')
        
        with self.lock:
            if username in self.users:
                return {'status': 'error', 'message': 'Usuário já existe'}
            
            hashed_password = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()
            self.users[username] = {'nome': nome, 'senha': hashed_password}
            self.emails[username] = []
            return {'status': 'success', 'message': 'Usuário registrado com sucesso'}
    
    def authenticate_user(self, request):
        """Autentica um usuário."""
        username = request.get('username')
        senha = request.get('senha')
        
        with self.lock:
            user = self.users.get(username)
            if user and bcrypt.checkpw(senha.encode(), user['senha'].encode()):
                return {'status': 'success', 'message': 'Login realizado', 'nome': user['nome']}
        return {'status': 'error', 'message': 'Credenciais inválidas'}
    
    def send_email(self, request):
        """Envia um e-mail."""
        remetente = request.get('remetente')
        destinatario = request.get('destinatario')
        assunto = request.get('assunto')
        corpo = request.get('corpo')
        
        with self.lock:
            if destinatario not in self.users:
                return {'status': 'error', 'message': 'Destinatário inexistente'}
            
            email = {
                'remetente': remetente,
                'destinatario': destinatario,
                'data_hora': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                'assunto': assunto,
                'corpo': corpo
            }
            self.emails[destinatario].append(email)
            return {'status': 'success', 'message': 'E-mail enviado com sucesso'}
    
    def get_emails(self, request):
        """Obtém os e-mails do usuário."""
        username = request.get('username')
        
        with self.lock:
            emails = self.emails.get(username, [])
            self.emails[username] = []
            return {'status': 'success', 'emails': emails}
    
    def stop(self):
        """Para o servidor."""
        self.running = False
        self.server_socket.close()
        print("Servidor encerrado.")

if __name__ == '__main__':
    server = EmailServer()
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()
