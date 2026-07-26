# 🔐 FRT Red Team Suite - Sistema Completo

Sistema integrado em Python para estudo, teste e defesa de **Family Refresh Token (FRT) Attacks** em Microsoft 365/Azure AD.

**Versão:** 1.0  
**Python:** 3.9+  
**Status:** ✅ Production Ready  

---

## 📦 O Que Está Incluído?

### Sistema Principal
```
frt_red_team_suite.py (1500+ linhas)
├─ TokenManager (gerenciar tokens)
├─ PhishingModule (Fase 1: Captura)
├─ FRTAnalyzer (Fase 2: Análise)
├─ ExploitationModule (Fase 3: Exploração)
├─ PersistenceModule (Fase 4: Persistência)
└─ FRTMenu (Interface completa)
```

### Extensões (Optional)
```
frt_suite_extensions.py (700+ linhas)
├─ EmailModule (Enviar emails/phishing)
├─ TeamsModule (Interagir com Teams)
├─ EvadeModule (Evasão de detecção)
├─ KQLModule (Queries de detecção)
└─ ReportModule (Gerar relatórios)
```

---

## 🚀 Instalação Rápida

### Passo 1: Instalar Dependências

```bash
pip install requests
```

Pronto! É o único requisito externo.

### Passo 2: Fazer Download

Copie `frt_red_team_suite.py` e `frt_suite_extensions.py` para seu diretório:

```bash
mkdir ~/frt_suite
cd ~/frt_suite
cp frt_red_team_suite.py .
cp frt_suite_extensions.py .
```

### Passo 3: Primeira Execução

```bash
python frt_red_team_suite.py
```

Você verá o menu principal com todas as opções.

---

## 🎯 Como Usar

### Fluxo Básico (5 passos)

```bash
# 1. Executar o suite
python frt_red_team_suite.py

# 2. Carregar tokens (opção 1)
# Seleciona arquivo captura_tokens.json automaticamente

# 3. Analisar FRT (opção 20)
# Testa qual apps estão disponíveis

# 4. Exploração (opção 35)
# Coleta rápida: usuários, admins, emails, arquivos

# 5. Gerar relatório (opção 50)
# Cria relatório com dados coletados
```

---

## 📋 Menu de Opções Completo

### Seção TOKENS (1-5)

```
1) Carregar tokens          → Lê arquivo JSON com tokens
2) Listar tokens            → Mostra status de todos os tokens
3) Renovar access token     → Usa refresh token para renovar
4) Validar tokens           → Verifica se tokens estão válidos
5) Fazer backup             → Backup seguro dos tokens
```

**Exemplo:**
```
Escolha: 1
[+] Arquivo encontrado: ~/captura_tokens.json
[+] Token carregado com sucesso!
```

---

### Seção FASE 1: CAPTURA (10-11)

```
10) Simular Device Code Flow    → Simula phishing
11) Gerar código de phishing     → Gera código para vítima
```

**Exemplo:**
```
Escolha: 10
Tenant ID: YOUR_TENANT_ID
[+] Device Code Flow iniciado!
[+] Código para usuário: G9Z7M
[+] Acesse: https://microsoft.com/devicelogin
```

---

### Seção FASE 2: ANÁLISE (20-21)

```
20) Analisar FRT                 → Testa qual apps trabalham
21) Verificar análise anterior   → Mostra resultados salvos
```

**Exemplo:**
```
Escolha: 20
[*] Testando Microsoft Office... ✓
[*] Testando Microsoft Teams... ✓
[*] Testando OneDrive... ✓
[+] Análise completa!
[+] Resultados: frt_analysis.json
```

---

### Seção FASE 3: EXPLORAÇÃO (30-35)

```
30) Enumerar usuários           → Lista usuários do tenant
31) Encontrar Global Admins     → Localiza admins
32) Ler emails                  → Lê caixa de entrada
33) Listar arquivos OneDrive    → Lista arquivos
34) Enumerar Teams              → Lista Teams do usuário
35) Coleta rápida               → Executa TUDO acima
```

**Exemplo:**
```
Escolha: 35
[*] Executando coleta rápida...
[*] Enumerando usuários...
[+] 45 usuários encontrados
[*] Procurando Global Admins...
[+] 3 Global Admins encontrados
[*] Lendo últimos emails...
[+] 20 emails lidos
[+] Coleta completa!
```

---

### Seção FASE 4: PERSISTÊNCIA (40-42)

```
40) Configurar renovação automática
41) Verificar status persistência
42) Criar dispositivo virtual
```

**Exemplo:**
```
Escolha: 40
[*] Configurando renovação automática a cada 24h...
[+] Sistema renovará token automaticamente
```

---

### Seção OUTROS (50-52, 99)

```
50) Gerar relatório              → Cria report.json
51) Ver logs                     → Mostra arquivo de logs
52) Limpar dados                 → Delete TODOS os dados
99) Sair                         → Encerra programa
```

---

## 📁 Estrutura de Diretórios

O sistema cria automaticamente:

```
~/.frt_suite/
├─ data/
│  ├─ tokens.json               # Tokens salvos
│  ├─ users_enum.json           # Usuários enumerados
│  ├─ admins_enum.json          # Admins encontrados
│  ├─ emails_read.json          # Emails lidos
│  ├─ onedrive_files.json       # Arquivos OneDrive
│  ├─ frt_analysis.json         # Resultado análise FRT
│  └─ report.json               # Relatório
│
├─ logs/
│  └─ frt_suite.log             # Log de todas operações
│
└─ backups/
   └─ tokens_backup_*.json      # Backups de tokens
```

---

## 🔑 Configuração Inicial

### Carregar Tokens (Obrigatório)

O arquivo de tokens deve estar em um destes locais:

**Automático:**
```
~/captura_tokens.json
```

**Manual:**
```
Escolha 1 no menu
Digite caminho: /seu/caminho/tokens.json
```

**Formato esperado:**
```json
{
  "access_token": "eyJ0eXAi...",
  "refresh_token": "1.AVkA5L...",
  "tenant_id": "c1e8b8e4-9fce...",
  "tenant_domain": "contoso.net.br",
  "user_id": "1e825e83-6e9c...",
  "user_email": "andrew.testes@contoso.net.br",
  "expires_in": 3600
}
```

---

## 📊 Exemplos Práticos

### Exemplo 1: Reconhecimento Completo (30 min)

```bash
# 1. Iniciar
python frt_red_team_suite.py

# 2. Menu → 1 (Carregar tokens)
# Automático

# 3. Menu → 20 (Analisar FRT)
# Testa quais apps funcionam
# Resultado: 5 apps disponíveis

# 4. Menu → 35 (Coleta rápida)
# Enumera usuários, admins, emails, onedrive
# Resultado: 2.5GB de dados

# 5. Menu → 50 (Gerar relatório)
# Cria report.html e report.json
```

---

### Exemplo 2: Enviar Email de Phishing (com extensões)

```python
# Abrir em Python shell:

from frt_red_team_suite import *
from frt_suite_extensions import EmailModule

menu = FRTMenu()
menu.token_manager.list_tokens()

email = EmailModule(menu.token_manager)
email.send_phishing_email(
    to="admin@company.com",
    target_name="Carlos"
)
```

---

### Exemplo 3: Teams Enumeration (com extensões)

```python
from frt_red_team_suite import *
from frt_suite_extensions import TeamsModule

menu = FRTMenu()
teams = TeamsModule(menu.token_manager)

# Listar teams
teams_list = teams.list_teams()

# Listar canais de um team
if teams_list:
    team_id = teams_list[0]['id']
    channels = teams.list_channels(team_id)
```

---

### Exemplo 4: Evasão de Detecção (com extensões)

```python
from frt_suite_extensions import EvadeModule
import time

# Rate limiting realista
interval = EvadeModule.rate_limit_requests(30)  # 30 req/min

# Fazer requisição cada X segundos
for i in range(100):
    # Fazer algo
    time.sleep(interval)

# User-Agent realista
headers = EvadeModule.randomize_user_agent()

# Exfiltração lenta
EvadeModule.slow_exfiltration(
    data_size_mb=500,
    duration_hours=24
)
```

---

### Exemplo 5: Exportar KQL Queries

```python
from frt_suite_extensions import KQLModule

# Exportar todas as queries
KQLModule.export_kql_queries("kql_queries.txt")

# Obter uma query específica
query = KQLModule.get_query("frt_testing")
print(query)
```

---

## 🛡️ Boas Práticas de Segurança

### Proteja Seus Tokens

```bash
# Criptografe o arquivo de tokens
gpg -c ~/.frt_suite/data/tokens.json

# Ou use permissões restritivas
chmod 600 ~/.frt_suite/data/tokens.json
```

### Use com Responsabilidade

```
✅ PERMITIDO:
   - Testar contra seu próprio tenant
   - Defender sua organização
   - Pesquisa educacional autorizada
   - Penteste com autorização escrita

❌ NÃO PERMITIDO:
   - Atacar sistemas sem autorização
   - Comprometer organizações
   - Roubo de dados
   - Qualquer atividade ilegal
```

---

## 🐛 Troubleshooting

### Problema: "Token não encontrado"

```
Solução 1: Verifique se captura_tokens.json está em ~/
Solução 2: Use opção 1 do menu e especifique o caminho
Solução 3: Copie tokens_enum para local certo
```

### Problema: "ConnectionError: Max retries exceeded"

```
Solução 1: Verifique conexão internet
Solução 2: Aguarde (pode estar rate limited)
Solução 3: Verifique se tenant_id está correto
```

### Problema: "401 Unauthorized"

```
Solução 1: Token expirou - use opção 3 (renovar)
Solução 2: Permissões insuficientes para este app
Solução 3: Refresh token também expirou (90 dias passaram)
```

### Problema: "Token renovado mas não funciona"

```
Solução: Aguarde 30s - pode estar em sincronização
```

---

## 📈 Melhorias Futuras

Versão 2.0 planejada:

```
✅ Interface Web (Flask/Django)
✅ Banco de dados (SQLite)
✅ Multi-usuario (RBAC)
✅ Integração com C2 (Sliver/Cobalt Strike)
✅ Machine Learning para evasão
✅ Docker containers
✅ CI/CD pipeline
```

---

## 📞 Suporte

### Verificar Logs

```bash
cat ~/.frt_suite/logs/frt_suite.log
```

### Limpar e Recomeçar

```bash
# Opção 52 no menu (Limpar dados)
# Ou manual:
rm -rf ~/.frt_suite
```

### Resetar a Estado Padrão

```bash
python frt_red_team_suite.py
# Menu → 52 → s
```

---

## 📚 Documentação Relacionada

Consulte também:

- `DOCUMENTACAO_TECNICA_FRT_ATTACK.md` - Detalhes técnicos
- `DIAGRAMAS_ATTACK_CHAIN.md` - Diagramas visuais
- `MODELO_ARTIGO_FRT_ATTACK.md` - Artigo publicável
- `GUIA_PUBLICACAO.md` - Estratégia de publicação

---

## 📄 Licença

MIT License - Use livremente com responsabilidade

```
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
```

---

## 👨‍💻 Desenvolvido por

**math69b** - Cybersecurity Analyst & Red Teamer  
Especializado em Microsoft Identity e Azure AD Security

---

## 🙏 Agradecimentos

- Secureworks - Pesquisa original do FRT
- Microsoft - Documentação OAuth 2.0
- Comunidade de Segurança - Feedback e contribuições

---

**Última atualização:** Junho 2026  
**Versão:** 1.0 - Production Ready

---

## 📞 Dúvidas?

```
1. Consulte o menu (opção 51 - Ver logs)
2. Verifique este README
3. Leia DOCUMENTACAO_TECNICA_FRT_ATTACK.md
4. Contate suporte técnico
```

**Boa sorte com seus testes!** 🚀
