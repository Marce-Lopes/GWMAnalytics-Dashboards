# Relatório de Bolso GWM - Documentação Técnica

## Introdução
Este guia explica **como executar** o painel e **como ele foi construído**. Foi escrito para usuários com **zero** experiência em programação.

## Parte 1: Como Funciona (A "Mágica")
Antes de rodar, entenda o fluxo:
1.  **O Motor (Python)**: A linguagem de programação que processa a lógica.
2.  **A Interface (Streamlit)**: Uma ferramenta que transforma código Python em um site. Não escrevemos HTML/CSS do zero; o Streamlit faz o trabalho pesado.
3.  **Os Dados (ClickHouse)**: O painel **não** armazena dados. Ele se conecta a um banco de dados remoto (ClickHouse) para buscar números de vendas ao vivo.
4.  **Os Visuais (Plotly)**: A ferramenta usada para desenhar os gráficos e mapas interativos.

**O Fluxo:**
`Seu Computador` -> `Pede Dados` -> `Banco de Dados (Remoto)` -> `Retorna Números` -> `Painel Desenha Gráficos`

---

## Parte 2: Guia de Instalação (Passo a Passo)

### Passo 1: Instalar o Python
1.  Vá para [python.org](https://www.python.org/downloads/) e baixe a versão mais recente.
2.  **CRÍTICO**: Ao instalar, marque a caixa **"Add Python to PATH"** (Adicionar Python ao PATH) na parte inferior da janela do instalador. Se você esquecer isso, os comandos não funcionarão!

### Passo 2: Obter o Código
1.  Baixe esta pasta do projeto (por exemplo, "Baixar ZIP" e extraia).
2.  Abra a pasta. Você deve ver arquivos como `app.py` e `requirements.txt`.

### Passo 3: Abrir o "Centro de Comando"
Precisamos usar uma interface de texto para falar com o computador.
1.  **Windows**: Pressione `Iniciar`, digite `PowerShell` e abra.
2.  **Mac**: Pressione `Cmd + Espaço`, digite `Terminal` e abra.
3.  Digite `cd` (espaço) e arraste a pasta do projeto para dentro da janela do terminal. Vai ficar parecido com:
    ```bash
    cd C:\Usuarios\SeuNome\Downloads\retencao
    ```
4.  Pressione **Enter**.

### Passo 4: Instalar as "Ferramentas" (Bibliotecas)
Precisamos baixar as ferramentas (Streamlit, Plotly, etc.) que o projeto usa.
Digite este comando e pressione **Enter**:
```bash
pip install -r requirements.txt
```
*Você verá muito texto rolando. Isso é normal. Espere parar.*

### Passo 5: Rodar o Painel
Digite este comando e pressione **Enter**:
```bash
streamlit run app.py
```
Uma nova aba abrirá no seu navegador de internet com o painel!

---

## Parte 3: Por Baixo do Capô (Para Curiosos)
Se você quiser entender a estrutura do código:
-   **`app.py`**: O "Gerente". Ele decide o que mostrar na tela (Gráficos, Tabelas, Filtros).
-   **`database.py`**: O "Mensageiro". Contém as **Consultas SQL** (instruções) enviadas ao banco de dados para pegar números específicos (ex: "Selecione todas as vendas de ontem").
-   **`styles.py`**: O "Estilista". Contém o código CSS para dar ao painel o visual "Luxury" (fontes, cores, espaçamento).

## Solução de Problemas
-   **"Failed to connect to database"**:
    -   Como o banco de dados é remoto, você pode precisar estar na **VPN** da empresa ou na rede do escritório.
    -   O painel não funciona offline.
-   **"Command not found"**:
    -   Você provavelmente esqueceu de marcar **"Add Python to PATH"** durante a instalação. Reinstale o Python e marque essa caixa.
