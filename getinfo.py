import sys
import csv
import requests
from ldap3 import Server, Connection, ALL
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import unicodedata

#Seção para denifir todas as configurações
arquivo_csv = 'users.csv'
termo_search = 'termo.txt'
path_remoto = '/var/www/html/logs/ws.log'
wsaci_host = '10.113.1.20'
username_wsaci = 'labnet'
local_log_path = 'lws.log'
lastline_file = 'linha.txt'
#curl_api = 'curl -g -X GET https://athenas.mpto.mp.br/athenas/'
url_api = 'https://athenas.mpto.mp.br/athenas/'
api_rhemployee = 'RHEmployeeRestful/v1/'
api_rhgeral = 'RHNaturalPersonRestful/v1/'
api_rhtelefones = 'RHTelefoneRestful/v1/'
api_workplace = 'RHEmployeeWorkplaceRestful/v1/'
headers = {
        'X-SERVICE-TOKEN-ALLOWED': 'f98943ecba0941841526578005be6d5c',
        'Authorization': '7d4b1d3a5bae8bbe881ecce609ca5e1a:754dc55edcbf4df44ec215d728bab183'
    }

LDAP_SERVER = 'ldap://10.113.1.240'
LDAP_USER = 'CN=Administrator,CN=Users,DC=dcmp,DC=mpto,DC=mp,DC=br'
LDAP_PASSWORD = '@dSrvsmb4#@!'
BASE_DN = 'DC=dcmp,DC=mpto,DC=mp,DC=br'
SERVICE_ACCOUNT_FILE = 'sac.json'
ADMIN_EMAIL = 'peronsouza@mpto.mp.br'
SCOPES = ['https://www.googleapis.com/auth/admin.directory.user']

def ldap_connection(username):
    try:
        # Cria um servidor LDAP
        ldap_server = Server(LDAP_SERVER, get_info=ALL)
        
        # Conecta ao servidor LDAP
        ldap_connection = Connection(ldap_server, LDAP_USER, LDAP_PASSWORD, auto_bind=True)
        
        # Verifica a conexão
        if ldap_connection.bound:
            print("Conexão com o servidor LDAP estabelecida com sucesso!")
            
            # Busca um usuário (por exemplo, por seu CN)
            ldap_connection.search(BASE_DN, f'(sAMAccountName={username})', attributes=['employeeNumber'])
            if ldap_connection.entries:
                #print("Usuário encontrado:")
                entry = ldap_connection.entries[0]
                entry = entry.employeeNumber.value
                return(entry)
            else:
                print("Usuário não encontrado no LDAP.")
                return 0
        else:
            print("Falha na conexão com o servidor LDAP.")
        
        # Desconecta
        ldap_connection.unbind()

    except Exception as e:
        print(f'Erro ao conectar ao servidor LDAP: {e}')

def api_request(valor, tipo):
	
	if tipo == "get_workid":#Opção básica para obter o id o Servidor
	
		filtro_rhemployee = f'[{{"property":"user__username","value":"{valor}"}}]'
		url_base = f'{url_api}{api_rhemployee}'
		
		#Faz a requisição curl
		response = requests.get(
                    url_base,
                    params={'filter': filtro_rhemployee},
                    headers=headers
                )
		if response.status_code == 200:
			data = response.json()
			count = data['count']
			if count >= 1:
				data = data['collection'][0].get('id')
				return data	
			else:
				return 0
			
	if tipo == "id_pf":#Opção 1
		filtro_rhemployee = f'[{{"property":"id","value":"{valor}"}}]'
		url_base = f'{url_api}{api_rhemployee}'

		#Faz a requisição curl
		response = requests.get(
                    url_base,
                    params={'filter': filtro_rhemployee},
                    headers=headers
                )
		if response.status_code == 200:
			data = response.json()
			data = data['collection'][0].get('pessoa_fisica')
			return(data)
			
	if tipo == "get_nome":#Opção 2
		filtro_rhgeral = f'[{{"property":"id","value":"{valor}","stage":1}}]'
		url_base = f'{url_api}{api_rhgeral}'
		
		#Faz a requisição curl
		data = requests.get(
                    url_base,
                    params={'filter': filtro_rhgeral},
                    headers=headers
                )
		if data.status_code == 200:
                	data = data.json()
                	data = data['collection'][0].get('nome')
                	return(data)
       
	if tipo == "get_matricula":#Opção 3
		filtro_rhemployee = f'[{{"property":"id","value":"{valor}"}}]'
		url_base = f'{url_api}{api_rhemployee}'

		#Faz a requisição curl
		response = requests.get(
                    url_base,
                    params={'filter': filtro_rhemployee},
                    headers=headers
                )
		if response.status_code == 200:
			data = response.json()
			data = data['collection'][0].get('matricula')
			return(data)
	
	if tipo == "get_mail":#Opção 4
		filtro_rhgeral = f'[{{"property":"id","value":"{valor}","stage":1}}]'
		url_base = f'{url_api}{api_rhgeral}'
		
		#Faz a requisição curl
		data = requests.get(
                    url_base,
                    params={'filter': filtro_rhgeral},
                    headers=headers
                )
		if data.status_code == 200:
                	data = data.json()
                	data = data['collection'][0].get('email_pessoal')
                	return(data)
                	
	if tipo == "get_phone":#Opção 5
		filtro = f'[{{"property":"person","value":"{valor}","stage":1}}]'
		url_base = f'{url_api}{api_rhtelefones}'
		
		#Faz a requisição curl
		data = requests.get(
                    url_base,
                    params={'filter': filtro},
                    headers=headers
                )
		if data.status_code == 200:
                	data = data.json()
                	ncount = data.get("count")
                	if ncount == 0:
                		data = "0"                		
                		return(data)
                		
                	else:
                		data = data['collection'][0].get('numero')
                		return(data)
                	
	if tipo == "get_lotacao":#Opção 6
		#valor = api_request(valor, tipo="get_workid_wmat")		
		filtro = f'[{{"property":"servidor_id","value":"{valor}","stage":1}},{{"property":"designacao","value":true,"stage":2}},{{"property":"ativo","value":true,"stage":3}}]'
		url_base = f'{url_api}{api_workplace}'
		
		#Faz a requisição curl
		data = requests.get(
                    url_base,
                    params={'filter': filtro},
                    headers=headers
                )
		if data.status_code == 200:
                	data = data.json()
                	count = data['count']
                	if count == 0:
                		data = "PROCURADORIA GERAL DE JUSTIÇA DO ESTADO DO TOCANTINS"
                		print(data)
                		return(data)               	
                	else:
                		data = data['collection'][0].get('lotacao_unicode')
                		return(data)
                	
	if tipo == "get_workid_wmat":#Opção 7
	
		filtro_rhemployee = f'[{{"property":"matricula","value":"{valor}"}}]'
		url_base = f'{url_api}{api_rhemployee}'
		
		#Faz a requisição curl
		response = requests.get(
                    url_base,
                    params={'filter': filtro_rhemployee},
                    headers=headers
                )
		if response.status_code == 200:
			data = response.json()
			count = data['count']
			if count >= 1:
				data = data['collection'][0].get('id')
				return data	
			else:
				return 0

def formatar_nome(nome):
    minusculas = {'da', 'de', 'do', 'das', 'dos', 'e'}
    palavras = nome.lower().split()
    
    nome_formatado = []
    for i, palavra in enumerate(palavras):
        if palavra in minusculas and i != 0:
            nome_formatado.append(palavra)
        else:
            nome_formatado.append(palavra.capitalize())
    
    nome_formatado = ' '.join(nome_formatado)
    
    #Separar name de surname
    cname = nome_formatado.split()
    name = cname[0].strip()
    surname = ' '.join(cname[1:]) if len(cname) > 1 else ''
    return(name, surname)

def r_scaracteres(surname):
	return ''.join(
	c for c in unicodedata.normalize('NFD', surname)
	if unicodedata.category(c) != 'Mn'
	).replace('ç', 'c').replace('Ç', 'C')

def formatar_senha(matricula, snome):
	surname = snome.lower().split()
	surname = surname[-1]
	surname = r_scaracteres(surname)
	
	senha = f'@MPTO{matricula}{surname}'
	return(senha)

def check_user(conta):
	try:
		# Autenticação com delegação
		credentials = service_account.Credentials.from_service_account_file(
		SERVICE_ACCOUNT_FILE, scopes=SCOPES)
		delegated_credentials = credentials.with_subject(ADMIN_EMAIL)

		service = build('admin', 'directory_v1', credentials=delegated_credentials)
		
		try:
			user = service.users().get(userKey=conta).execute()
			print(f"Usuário {conta} já existe. Nada a se fazer.")
			return 0
		except HttpError as error:
			if error.resp.status == 404:
				print(f"Usuário(a) {conta} não existe na Organização")
				return 1
				
			elif error.resp.status != 404:
				raise error
	
	except HttpError as error:
		print(f"Erro ao checar usuário: {error}")
def criar_usuario_google_workspace(username, pname, sname, senha, email, telefone, lotacao):

    try:
        # Autenticação com delegação
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        delegated_credentials = credentials.with_subject(ADMIN_EMAIL)

        service = build('admin', 'directory_v1', credentials=delegated_credentials)

        # Criação do usuário
        if len(telefone) < 11:#Checa se o telefone de recuperação tem 11 caracteres.
        	user_info = {
        		"primaryEmail": username,
        		"password": senha,
        		"name": {
        			"givenName": pname,
        			"familyName": sname
        		},
        		"orgUnitPath": "/",
        		"recoveryEmail": email,
        		"organizations": [{
                    		"department": lotacao
                			}],
        		"emails": [
        			{
        				"address": email,
        				"type": "home",
        				"primary": True
        				}
        				],
        		"phones": [
        			{
        				"value": telefone,
        				"type": "mobile",
        				"primary": True
        				}
        				]
        			}
        				
        else:
        	user_info = {
        		"primaryEmail": username,
        		"password": senha,
        		"name": {
        			"givenName": pname,
        			"familyName": sname
        		},
        		"orgUnitPath": "/",
        		"recoveryEmail": email,
        		"recoveryPhone": '+55'+telefone,
        		"organizations": [{
                    		"department": lotacao
                			}],
        		"emails": [
        			{
        				"address": email,
        				"type": "home",
        				"primary": True
        				}
        				],
        		"phones": [
        			{
        				"value": telefone,
        				"type": "mobile",
        				"primary": True
        				}
        				]
        			}
        
        user = service.users().insert(body=user_info).execute()
        print(f"Usuário {username} criado com sucesso.")       

    except HttpError as error:
        print(f"Erro ao criar usuário: {error}")

def add_gp(username, grupo):
	
	SCOPE_GM = ['https://www.googleapis.com/auth/admin.directory.group.member']
	
	try:
		credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPE_GM)
		delegated_credentials = credentials.with_subject(ADMIN_EMAIL)		

		service = build('admin', 'directory_v1', credentials=delegated_credentials)
		
		try:
			service.members().insert(
				groupKey=grupo,
				body={'email': username, 'role': 'MEMBER'}
				).execute()
			print(f"Usuário {username} inserido no grupo de e-mail {grupo}")
			return 0
		
		except Exception as e:
			print(f"Erro ao adicionar {username} ao grupo {grupo}: {e}")
        
	except HttpError as error:
		print(f"Erro ao adicionar usuário ao grupo de e-mail: {error}")
		return False
			    
################################################################################################################################################
with open(arquivo_csv, newline='', encoding='utf-8') as file:
	csv_reader = csv.reader(file)
#       next(csv_reader)  # Se o CSV tiver cabeçalho, pulamos a primeira linha


	for row in csv_reader:
		username = row[0]
		#username = input("Digite o username:")
		#id_employee = api_request(username, tipo="get_workid")
		#if id_employee == 0:
		#	ldap_matricula = ldap_connection(username)			
		#	if ldap_matricula == 0:
		#		print(f"Usuário não encontrado nas bases. Fechando o script...")
		#		sys.exit()
		#	else:
		#		id_employee = api_request(ldap_matricula, tipo="get_workid_wmat")
		ldap_matricula = ldap_connection(username)
		if ldap_matricula == 0:
			print(f"Usuário não encontrado nas bases. Fechando o script...")
			sys.exit()
		else:
			id_employee = api_request(ldap_matricula, tipo="get_workid_wmat") 
								
		id_pessoaf = api_request(id_employee, tipo="id_pf")
		matricula = api_request(id_employee, tipo="get_matricula")
		nome = api_request(id_pessoaf, tipo="get_nome")
		pname, sname = formatar_nome(nome)
		email = api_request(id_pessoaf, tipo="get_mail")
		email = email.lower()
		telefone = api_request(id_pessoaf, tipo="get_phone")
		lotacao = api_request(id_employee, tipo="get_lotacao")
		username = f'{username}@mpto.mp.br'
		
		#Função para definir a senhada conta
		senha = formatar_senha(matricula, sname)

		print(f"######################################################################################################################")
		print(f"Dados:")
		print(f"{username}")
		print(f"{id_pessoaf},")
		print(f"matrícula: {matricula},")
		print(f"Primeiro Nome: {pname},")
		print(f"Segundo Nome: {sname},")
		print(f"{email},")
		print(f"{telefone},")
		print(f"Senha: {senha}")
		print(f"{lotacao}")
		
		#sys.exit()
		
		c_user = check_user(username)
		if c_user == 1:
			print(f"Chamando função para criar usuário no Google WorkSpace")
			criar_usuario_google_workspace(username, pname, sname, senha, email, telefone, lotacao)
			grupo = "servidores_adm@mpto.mp.br"
			c_user = add_gp(username, grupo)
			if c_user == 0:
				print(f"Conta de e-mail {username} criada.\nA senha para o primeiro acesso segue o padrão @MPTO+matrícula+último nome. Exemplo, @MPTO123465silva.")
