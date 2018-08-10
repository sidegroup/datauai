# Instalando o CKAN  
A instalação do CKAN será realizada no ubuntu/xenial64.

Antes de instalar alguns pacotes, é necessário atualizar o apt-get:

    sudo apt-get update
  Agora os pacotes básicos poderão ser instalados:
  

    sudo apt-get install python-dev postgresql libpq-dev python-pip python-virtualenv git-core solr-jetty openjdk-8-jdk redis-server apache2 libapache2-mod-wsgi libapache2-mod-rpaf nginx --asume-yes --force-yes
Criando diretórios para desenvolvimento:

    mkdir -p /var/www/ckan/lib
    sudo ln -s /var/www/ckan/lib/ /usr/lib/ckan
    mkdir -p /var/www/ckan/etc
    sudo ln -s /var/www/ckan/etc /etc/ckan
Criando ambiente virtual Python (virtualenv) para instalar o CKAN e ativá-lo:

    sudo mkdir -p /usr/lib/ckan/default
    sudo chown `whoami` /usr/lib/ckan/default
    virtualenv --no-site-packages /usr/lib/ckan/default
É necessário que o ambiente criado seja ativado para que os pacotes sejam instalados corretamente

    . /usr/lib/ckan/default/bin/activate
Instalar a biblioteca setuptools para a configuração do setup.py. Obs.: um projeto é colocado no ambiente python a partir do setup.py

    sudo pip install setuptools==20.4
Instalar a última versão estável do CKAN (CKAN 2.7.0)

    cd /usr/lib/ckan/default
    sudo pip install -e 'git+https://github.com/ckan/ckan.git@ckan-2.7.0#egg=ckan'
### Configurando o banco de dados PostgreSQL

Criar um novo usuário:

    sudo -u postgres psql -c "CREATE USER ckan_default WITH PASSWORD 'senha';"
Criar um banco para o usuário criado anteriormente. Obs.: o nome do banco foi criado com o mesmo nome do usuário

    sudo -u postgres createdb -O ckan_default ckan_default -E utf-8
### Diretório para conter os arquivos de configuração do site:

    sudo mkdir -p /etc/ckan/default
    sudo chown -R `whoami` /etc/ckan/
    sudo chown -R `whoami` /var/www/ckan/etc
### Instalando os módulos Python que o CKAN requer em sua virtualenv

    sudo pip install -r /usr/lib/ckan/default/src/ckan/requirements.txt
### Criando arquivo de configuração CKAN

    cd /var/www/ckan/lib/default/src/ckan
    paster make-config ckan /etc/ckan/default/development.ini
### Configurar o arquivo de inicialização development.ini
Abra o development.ini para edição

    sudo nano /etc/ckan/default/development.ini
Procure por **sqlalchemy.url** e troque o **pass** pela senha criada anteriormente

    sqlalchemy.url = postgresql://ckan_default:senha@localhost/ckan_default
Procure por **ckan.site_url** e adicione uma url

    ckan.site_url = http://127.0.0.1:5000
Procure por **ckan.locale_default**. Obs.: o site irá renderizar já no idioma português

    ckan.locale_default = pt_BR
Procure por solr_url e descomente (tire o #)

    solr_url = http://127.0.0.1:8983/solr
Procure por **ckan.site_title**

    ckan.site_title = dataUAI
Procure por **ckan.site_logo**

    ckan.site_logo = /base/images/dataUAI-logo.png
### Editar o arquivo de configuração jetty8
Abra o **jetty8.conf** para edição:

    sudo nano /etc/default/jetty8
Procure por **JETTY_HOST**, descomente (tire o #) e adicione um host:

    JETTY_HOST=127.0.0.1
Procure por **JETTY_PORT**, descomente (tire o #) e adicione uma porta:

    JETTY_PORT=8983
Para completar a configuração do jetty8:

    sudo mv /etc/solr/conf/schema.xml /etc/solr/conf/schema.xml.bak
    sudo ln-s /usr/lib/ckan/default/src/ckan/ckan/config/solr/chema.xml /etc/solr/conf/schema.xml
    sudo service jetty8 restart
### Atualizando ports.conf

    sudo nano /etc/apache2/ports.conf
Procure por **Listen** e troque a porta

    Listen 8080
### Criando link who.ini

    ln -s /usr/lib/ckan/default/src/ckan/who.ini /etc/ckan/default/who.ini
### Redirecionamento de requisição WSGI
Crie um arquivo com o nome apache.wsgi:

    sudo nano /etc/ckan/default/apache.wsgi
Dentro do apache.wsgi escreva esse código:

    import os
    activate_this = os.path.join('/usr/lib/ckan/default/bin/activate_this.py')
    execfile(activate_this, dict(__file__=activate_this))

    from paste.deploy import loadapp
    config_filepath = 
    os.path.join.(os.path.dirname(os.path.abspath(__file__)), 'development.ini')
    from paste.script.util.logging_config import fileConfig
    fileConfig(config_filepath)
    application = loadapp('config:%s' % config_filepath)
### Criar um arquivo de configuração do ckan para o apache
Obs.: Para mudar a url, basta ir em /etc/ckan/default/development.ini e em seguida alterar em **ckan.site.url**
Depois ir em /etc/apache2/sites-available/ckan_default.conf e colocar a nova url (que foi alterada do ckan.site.url) em ServerName

    sudo nano /etc/apache2/sites-available/ckan_default.conf
Dentro do ckan_default.conf escreva esse código

    <VirtualHost 127.0.0.1:8000>
	    ServerName http://127.0.0.1:5000
	    WSGIScriptAlias / /etc/ckan/default/apache.wsgi
	    # Pass authorization info on (needed for rest api).
	    WSGIPassAuthorization On
	    #Deploy as a daemon (avoids conflicts between CKAN instances).
	    WSGIDaemonProcess ckan_default display-name=ckan_default processes=2 threads=15

	    WSGIProcessGroup ckan_default

	    ErrorLog /var/log/apache2/ckan_default.error.log
	    CustomLog /var/log/apache2/ckan_default.custom.log combined

	    <IfModule mod_rpaf.c>
		    RPAFenable On
		    RPAFsethostname On
		    RPAFproxy_ips 127.0.0.1
		</IfModule>

	    <Directory />
		    Require all granted
		</Directory>
	</VirtualHost>
### Criar um arquivo de configuração do ckan para o gninx

    sudo nano /etc/nginx/sites/available/ckan.conf

Dentro do ckan.conf escreva esse código:

    proxy_cache_path /tmp/nginx_cache levels=1:2 keys_zone = cache:30m
    max_size=250m;
    proxy_temp_path /tmp/nginx_proxy 1 2;

    server {
	    client_max_body_size 100M;
	    location / {
		    proxy_pass http://127.0.0.1:8080/;
		    proxy_set_header X-Forwarded-For $remote_addr;
		    proxy_set_header Host $host;
		    proxy_cache cache;
		    proxy_cache_bypass $cookie_auth_tkt;
		    proxy_no_cache $cookie_auth_tkt;
		    proxy_cache_valid 30m;
		    proxy_cache_key $host$scheme$proxy_host$request_uri;
		    # In emergency comment out line to force caching
		    # proxy_ignore_headers X-Accel_expires Expires Cache-Control;
		}
	}
### Ativando o site CKAN no apache2

    sudo a2ensite ckan_default
    sudo a2dissite 000-default
    sudo rm -i /etc/nginx/sites-enabled/default
    sudo ln -s /etc/nginx/sites-available/ckan /etc/nginx/sites-enabled/ckan_default
    sudo service apache2 restart
    sudo service nginx reload
### Criando usuário admin
O CKAN possui um usuário default, vamos alterar sua senha para melhor segurança. Siga os seguintes passos:

    cd /usr/lib/ckan/defaut/src/ckan
Após o comando a seguir, ele irá pedir uma nova senha
Obs.: o nome do usuário default do CKAN é "default"

    paster user setpass default -c /etc/ckan/default/development.ini
### Startar o CKAN

    . /usr/lib/ckan/default/bin/activate
    cd /usr/lib/ckan/default/src/ckan
    paster db init -c /etc/ckan/default/development.ini
# Instalando o tema
### Clonar o repositório

    cd /var/www/ckan/lib/default/src
    git clone https://github.com/sidegroup/datauai
### Subir para o ambiente python

    cd /var/www/ckan/lib/default/src/datauai/ckanext-ifpb_theme
    sudo python setup.py develop
### Adicionar o tema no development.ini
Abra o **development.ini** para edição:

    sudo nano /etc/ckan/default/development.ini
Procure por **ckan.plugins** e adicione o **ifpb_theme** no final:

    ckan.plugins = stats text_view image_view recline_view ifpb_theme
# Instalando dependências do tema
### Configurar FileStore
Obs.: FileStore serve para a realização dos uploads

Criar diretório para guardar os recursos:

    sudo mkdir -p /var/lib/ckan/default
Inserir o path criado anteriormente no **development.ini**

Abra o **development.ini** para a edição:

    sudo nano /etc/ckan/default/development.ini
Procure por **ckan.storage_path**, descomente (tire o #) e adicione o path:

    ckan.storage_path = /var/lib/ckan/default
Procure por **ckan.max_resource_size** e **ckan.max_image_size** e descomente-os
Obs.: valores são em megabytes

    ckan.max_resource_size = 10
    ckan.max_image_size = 2
Adicionar permissões:

    sudo chown www-data /var/lib/ckan/default
    sudo chmod ugo+rwx /var/lib/ckan/default
Restartar o apache2:

    sudo service apache2 reload
### Configurar DataStore
Obs.: DataStore utiliza outro banco de dados para armazenar dados dos recursos (ex: csv)

Abra o **development.ini** para edição:

    sudo nano /etc/ckan/default/development.ini
Procure por **ckan.plugins** e adicione **datastore** no final:

    ckan.plugins = stats text_view image_view recline_view ifpb_theme datastore
Criar um novo usuário no postgres:

    sudo -u postgres createuser -S -D -R -P -l datastore_default
Criar um novo banco:

    sudo -u postgres createdb -O ckan_default datastore_default -E utf-8
Abra o **development.ini** para a edição:

    sudo nano /etc/ckan/default/development.ini
Procure por **ckan.datastore.write_url** e **ckan.datastore.read_url**, descomente (tire o #) e adicione o path do postgres

    ckan.datastore.write_url = postgresql://ckan_default:senha@localhost/datastore_default

    ckan.datastore.read_url = postgresql://datastore_default:senha@localhost/datastore_default
Adicionar permissões:

    cd /var/www/ckan/lib/default/src/ckan
    paster --plugin=ckan datastore set-permissions -c /etc/ckan/default/development.ini | sudo -u postgres psql --set ON_ERROR_STOP=1
### Configurar DataPusher
Obs.: DataPusher roda separado do ckan. Ele é um intermediário para salvar os recursos no DataStore

Instalar os pacotes básicos para o DataPusher:

    sudo apt-get install python-dev python-virtualenv build-essential libxslt1-dev libxm12-dev git libffi-dev
Criar um virtualenv para datapusher:

    sudo virtualenv /usr/lib/ckan/datapusher
Clone DataPusher:

    sudo mkdir /usr/lib/ckan/datapusher/src
    cd /usr/lib/ckan/datapusher/src
    sudo git clone -b 0.0.13 https://github.com/ckan/datapusher.git
Instalar DataPusher:

    cd datapusher
    sudo /usr/lib/ckan/datapusher/bin/pip install -r requirements.txt
    sudo /usr/lib/ckan/datapusher/bin/python setup.py develop
Apache config:

    sudo cp deployment/datapusher.apache2-4.conf /etc/apache2/sites-available/datapusher.conf
WSGI config:

    sudo cp deployment/datapusher.wsgi /etc/ckan/
DataPusher settings:

    sudo cp deployment/datapusher_settings.py /etc/ckan/
Abrir nova porta no apache2:

    sudo sh -c 'echo "NameVirtualHost *:8800" >> /etc/apache2/ports.conf'
    sudo sh -c 'echo "Listen 8800" >> /etc/apache2/ports.conf'
Ativar DataPusher no apache2:

    sudo a2ensite datapusher
Abra o **development.ini** para edição:

    sudo nano /etc/ckan/default/development.ini
Procure por **ckan.plugins** e adicione **datapusher** no final:

    ckan.plugins = stats text_view image_view recline_view ifpb_theme datastore datapusher
Procure por **ckan.datapusher.url**, descomente e adicione essa url:

    ckan.datapusher.url = http://0.0.0.0:8800/
Descomente os itens a seguir:

    ckan.datapusher.formats = csv xls xlsx tsc application/csv application/vnd.ms-$
    ckan.datapusher.assume_task_stale_after = 3600
Reinicie o apache2:

    sudo service apache2 restart
### Configurar Resource Proxy
Obs.: Resource Proxy permite o acesso de plugins de visualização a arquivos externos.

Abra o **development.ini** para edição:

    sudo nano /etc/ckan/default/development.ini
Procure por **ckan.plugins** e adicione **resource_proxy** no final:

    ckan.plugins = stats text_view image_view recline_view ifpb_theme datastore datapusher resource_proxy
Descomente os itens a seguir:
Obs.: 1048576 = 1 MB

    ckan.resource_proxy.max_file_size = 1048576
    ckan.resource_proxy.chunk_size = 4096
### Criar novas tabelas no banco
Foi criado o model `app.py` e será necessário fazer os seguintes procedimentos para gerar a tabela no banco

Entre na lnha de comando do python:

    python
Importe o pacote do python para a manipulação do banco:

    import sqlalchemy as sa
Crie uma engine com a conexão do banco:

    engine = sa.create_engine('postgresql://ckan_default:senha@localhost/ckan_default')
Importe o pacote model do tema:

    from ckanext.ifpb_theme import model as m
No pacote model do tema tem um método público que inicializa as classes mapeadas:

    m.init_model(engine)
O pacote model contém uma classe (Repository) que manipula a persistência e nele contém um método **create_db** que pega todas as classes mapeadas e gera tabelas no banco:

    m.repo.create_db()
### Configurar a permissão de usuário
Obs.: Foram criadas novas permissões para o menu de aplicativo

Abra o **development.ini** para a edição:

    sudo nano /etc/ckan/default/development.ini
Procure por **Authorization Settings** e abaixo do último "ckan.auth" adicione os seguintes itens:

Permissão para um usuário comum criar um novo aplicativo:

    ckan.auth.user_create_apps = false
Permissão para um usuário comum atualizar o aplicativo:

    ckan.auth.user_update_apps = false
Permissão para um usuário comum excluir o aplicativo:

    ckan.auth.user_delete_apps = false

# Instalar fonte

Geralmente uma fonte contém vários arquivos com extensão .otf, copie esses arquivos para o path /usr/share/fonts.

Após a cópia da fonte, feche os programas abertos e execute:

    sudo fc-cache -f -v
Agora inicie o ckan utilizando o script do tópico "Instalando CKAN".

Obs.: Se caso der algum erro, é devido a threads que rodam em segundo plano. Para resolver, basta fechar o cmd e abrir novamente ou excluir esses processos.

Obs.: Para realizar o login, é necessário digitar o path **/user/login**.
