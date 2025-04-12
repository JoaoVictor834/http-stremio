# Setup Windows
### 1. Baixe a ferramenta openssl
Algumas fontes não funcionam com o proxy padrão do Stremio e precisam ser acessadas por um proxy customizado que, nesse caso, será hosteado no localhost. Porém, o Stremio exige uma conexão HTTPS para streams até mesmo no localhost, o que significa que o servidor local precisa de um certificado SLL confiável, o qual pode ser facilmente criado usando a ferramenta `openssl`.
#### Chocolatey
Execute o seguinte comando para instalar o openssl usando Chocolatey:
```console
choco install openssl
```
#### Instalação Manual
TODO

### 2. Crie um certificado autoassinado
1. Navegue ao diretório onde o arquivo `ssl.conf` está localizado e execute o seguinte comando:
```console
openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -keyout localhost.key -out localhost.crt -config ssl.conf -extensions v3_req
```
Isso criará os arquivos `localhost.crt` e `localhost.key`.

### 3. Adicione o certificado à lista de certificados confiáveis do Windows
#### Método 1 (padrão)
1. Navegue ao diretório onde os arquivos da etapa anterior foram criados e clique com o botão esquerdo duas vezes no arquivo `localhost.crt`
2. Na janela do certificado, clique na opção `Instalar Certificado`
3. Escolha o local que preferir e, em seguida, clique em `Avançar`
4. Na janela seguinte, selecione a opção `Colocar todos os certificados no repositório a seguir:` 
5. Clique em `Procurar` e selecione a opção `Autoridades de Certificação Raiz Confiáveis`, em seguida clique em `Avançar` e conclua a ação.

#### Método 2 (para certificados sem a extensão .crt)
1. Pressione `Win + R`, digite `certlm.msc` e pressione `Enter`
2. Procure por `Autoridades de Certificação Raiz Confiáveis` > `Certificados`
3. Clique com o botão direito em `Certificados` e selecione `Todas as Tarefas` > `Importar`
4. Navegue até o arquivo contendo o certificado e confirme sua instalação no repositório `Autoridades de Certificação Raiz Confiáveis`

### 4. Instalar dependências
1. Execute o seguinte comando para instalar as dependências:
```console
pip install -r requirements.txt
```

# Como usar
1. Execute o seguinte comando para iniciar o servidor:
```console
python main.py
```
2. Instale o addon através da url `https://127.0.0.1:6222/manifest.json`