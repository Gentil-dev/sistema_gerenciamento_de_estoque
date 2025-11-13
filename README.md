# 🪵 CD Porta — Sistema de Controle de Estoque de Portas Laqueadas

## 🧭 Visão Geral
O **CD Porta** é um sistema web simples e profissional de controle de estoque de portas laqueadas, desenvolvido em **Python (Flask)** com **PostgreSQL**.  
O projeto é responsivo, acessível via navegador (desktop e celular) e projetado para uso interno, com área pública e área administrativa protegida por senha.

---

## ⚙️ Funcionalidades Principais

### 1️⃣ Estrutura Geral
- Backend em **Flask** e banco **PostgreSQL**.  
- Sistema leve, rápido e com **interface responsiva**.  
- Acesso público para consultas e relatórios, e **área do gerente com senha**.  

---

### 2️⃣ Acesso Público
- Página inicial moderna com logo central, botões e link para a área do gerente.  
- Consultas abertas ao público:  
  - **/estoque** — consulta em tempo real do estoque.  
  - **/relatorio** — emissão de relatórios completos ou individuais.  
- Campo de **filtro dinâmico** para busca instantânea.  

---

### 3️⃣ Área do Gerente
Acesso restrito com login via `/gerente`.  
Painel administrativo completo com as rotas:
- `/cadastro` → Cadastrar novos produtos.  
- `/entrada` → Registrar entrada de produtos.  
- `/saida` → Registrar saída de produtos.  
- `/excluir` → Excluir produtos.  
- `/historico` → Visualizar e imprimir o histórico de ações.  
- `/logout` → Encerrar sessão do gerente.  

---

### 4️⃣ Histórico Automatizado
- Todas as ações (cadastro, entrada, saída, exclusão) são registradas em **`historico.txt`**.  
- Inclui data, hora, produto e tipo de ação.  
- Tela dedicada com visualização e opção de impressão.  

---

### 5️⃣ Relatórios de Estoque
- Exibe **produto, quantidade, preço e total**.  
- Calcula automaticamente o **valor total do estoque**.  
- Permite **filtrar por produto individual**.  
- Layout profissional e botão “🖨️ Imprimir Relatório”.  
- Impressão limpa (sem botões ou bordas desnecessárias).  

---

### 6️⃣ Consulta de Estoque (Pública)
- Tabela moderna e responsiva com:
  - Cabeçalho fixo e linhas alternadas (efeito zebra).  
  - Campo de busca em tempo real.  
  - Botão “🖨️ Imprimir Estoque”.  
- Compatível com celular e pronto para impressão limpa.  

---

### 7️⃣ Visual e UX
- Design profissional e consistente entre páginas.  
- Gradiente suave no fundo, tipografia moderna (**Segoe UI / Poppins**).  
- Efeitos visuais sutis (sombra, transição e destaque da logo).  
- Layout adaptado para **mobile-first design**.  

---

### 8️⃣ Implantação
- Pronto para **deploy na Render** ou outro PaaS compatível.  
- Banco de dados configurado via variável de ambiente `DATABASE_URL`.  
- Estrutura modular e otimizada para produção.  

---

## 🧩 Tecnologias Utilizadas
- **Python 3.10+**  
- **Flask** (microframework web)  
- **SQLAlchemy** (ORM para banco PostgreSQL)  
- **HTML5 / CSS3 / JavaScript**  
- **PostgreSQL**  
- **Render.com** (deploy sugerido)

---

## 📄 Licença
Este projeto é de uso interno e educacional, podendo ser adaptado livremente conforme necessidade.

---

💙 Desenvolvido com foco em **simplicidade, clareza e eficiência.**

----------------------------------------------------------------

— Projeto “CD Porta” (Sistema de Controle de Estoque de Portas Laqueadas):

🧱 Funcionalidades do Sistema — CD Porta
1️⃣ Estrutura Geral

Sistema web desenvolvido em Python + Flask, com PostgreSQL como banco de dados.

Projeto simples, rápido e sem necessidade de login público — mas com área administrativa protegida por senha.

Totalmente responsivo, compatível com celulares, tablets e desktops.

2️⃣ Acesso Público

Página inicial (/) moderna e profissional, com logo, botões de acesso e área do gerente.

Qualquer visitante pode:

Consultar o estoque em tempo real (/estoque);

Emitir relatórios completos ou individuais (/relatorio);

Filtrar produtos por nome, de forma dinâmica e instantânea.

Visual limpo, com layout tipo “dashboard corporativo”.

3️⃣ Área do Gerente

Login seguro via /gerente, com sessão controlada.

Painel administrativo completo (/painel) com acesso às funções principais:

Cadastrar Produto — nome, quantidade, preço unitário e observações.

Registrar Entrada de Produto — atualiza o estoque somando a quantidade.

Registrar Saída de Produto — subtrai quantidades do estoque com validação.

Excluir Produto — remove registros permanentemente do banco.

Histórico de Movimentações — lista todas as ações realizadas pelo gerente.

Logout — encerra a sessão com segurança.

4️⃣ Histórico Automatizado

Todas as ações do gerente (cadastro, entrada, saída, exclusão) são gravadas automaticamente em historico.txt.

Histórico mostra data, hora, tipo da ação e produto afetado.

Pode ser visualizado e impresso diretamente pela interface /historico.

5️⃣ Relatórios de Estoque

Relatório completo (/relatorio) com:

Produto, quantidade, preço unitário e total por item.

Cálculo automático do valor total do estoque.

Botão para imprimir relatório em layout limpo (oculta elementos desnecessários).

Novo recurso: filtro de relatório individual, permitindo selecionar e imprimir apenas um produto específico.

6️⃣ Consulta de Estoque (Pública)

Tabela moderna e responsiva com:

Efeito zebra, cabeçalho fixo e espaçamento ideal.

Campo de busca instantânea (sem recarregar página).

Botão “Imprimir Estoque” com modo de impressão otimizado.

Totalmente integrada ao banco PostgreSQL.

7️⃣ Visual e Experiência

Layout profissional e consistente entre todas as páginas.

Paleta com tons de azul corporativo e cinza neutro, fonte Segoe UI / Poppins.

Sombras e transições sutis em elementos visuais (botões e logo).

Fundo em gradiente suave, projetado para leveza visual e contraste.

8️⃣ Implantação

Estruturado para deploy na Render (ou outro PaaS compatível com Flask e PostgreSQL).

Banco de dados configurado via variável de ambiente DATABASE_URL.

Código organizado e pronto para produção.