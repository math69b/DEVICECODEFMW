#!/usr/bin/env python3
"""
CONFIGURAÇÃO AVANÇADA - FRT Red Team Suite
Customização, tuning e configurações avançadas
"""

import json
from pathlib import Path
from typing import Dict, Any

class ConfigurationGuide:
    """Guia de configuração avançada"""
    
    # ========================================================================
    # CONFIGURAÇÕES PADRÃO
    # ========================================================================
    
    DEFAULT_CONFIG = {
        # TENANT
        "tenant_id": "YOUR_TENANT_ID",
        "tenant_domain": "your-domain.com",
        
        # TOKENS
        "token_renewal_interval_hours": 24,
        "auto_renew_enabled": True,
        "backup_tokens_before_renew": True,
        
        # RATE LIMITING (Evasão)
        "requests_per_minute": 30,
        "random_delay_min_seconds": 0.5,
        "random_delay_max_seconds": 2,
        "enable_rate_limiting": True,
        
        # LOGGING
        "enable_logging": True,
        "log_level": "INFO",  # DEBUG, INFO, WARNING, ERROR
        "max_log_size_mb": 50,
        "backup_logs_on_rotate": True,
        
        # BACKUP
        "backup_frequency_days": 7,
        "auto_backup_enabled": True,
        "backup_location": "~/.frt_suite/backups",
        
        # EVASÃO
        "business_hours_only": False,
        "business_hours_start": 8,
        "business_hours_end": 18,
        "randomize_user_agent": True,
        "slow_exfiltration_enabled": False,
        "exfiltration_speed_kbps": 100,
        
        # SEGURANÇA
        "encrypt_tokens_at_rest": False,
        "require_confirmation_on_sensitive_ops": True,
        "track_all_actions": True,
        
        # NOTIFICAÇÕES
        "enable_notifications": False,
        "notification_email": "your-email@company.com",
        "notify_on_success": True,
        "notify_on_error": True,
        
        # API LIMITS
        "max_results_per_query": 100,
        "timeout_seconds": 10,
        "retry_count": 3,
        "retry_delay_seconds": 5,
        
        # BEHAVIOR
        "create_html_reports": True,
        "create_json_reports": True,
        "open_reports_after_generation": False,
        "auto_cleanup_old_data": False,
        "cleanup_older_than_days": 90,
    }
    
    # ========================================================================
    # PROFILES (Perfis Pré-configurados)
    # ========================================================================
    
    PROFILES = {
        "cautious": {
            "requests_per_minute": 10,
            "random_delay_min_seconds": 2,
            "random_delay_max_seconds": 5,
            "business_hours_only": True,
            "enable_rate_limiting": True,
            "track_all_actions": True,
            "require_confirmation_on_sensitive_ops": True,
        },
        
        "normal": {
            "requests_per_minute": 30,
            "random_delay_min_seconds": 0.5,
            "random_delay_max_seconds": 2,
            "business_hours_only": False,
            "enable_rate_limiting": True,
            "track_all_actions": True,
            "require_confirmation_on_sensitive_ops": True,
        },
        
        "aggressive": {
            "requests_per_minute": 100,
            "random_delay_min_seconds": 0,
            "random_delay_max_seconds": 0.5,
            "business_hours_only": False,
            "enable_rate_limiting": False,
            "track_all_actions": False,
            "require_confirmation_on_sensitive_ops": False,
        },
        
        "stealth": {
            "requests_per_minute": 5,
            "random_delay_min_seconds": 5,
            "random_delay_max_seconds": 10,
            "business_hours_only": True,
            "enable_rate_limiting": True,
            "randomize_user_agent": True,
            "slow_exfiltration_enabled": True,
            "exfiltration_speed_kbps": 50,
            "track_all_actions": False,
        },
    }
    
    @classmethod
    def create_default_config(cls, config_path: Path) -> Dict[str, Any]:
        """Cria configuração padrão"""
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(cls.DEFAULT_CONFIG, f, indent=2)
        
        return cls.DEFAULT_CONFIG
    
    @classmethod
    def load_config(cls, config_path: Path) -> Dict[str, Any]:
        """Carrega configuração"""
        if not config_path.exists():
            return cls.create_default_config(config_path)
        
        with open(config_path, 'r') as f:
            return json.load(f)
    
    @classmethod
    def apply_profile(cls, profile_name: str, config_path: Path):
        """Aplica um profile pré-configurado"""
        if profile_name not in cls.PROFILES:
            print(f"[-] Profile '{profile_name}' não existe")
            print(f"[*] Profiles disponíveis: {', '.join(cls.PROFILES.keys())}")
            return False
        
        config = cls.load_config(config_path)
        config.update(cls.PROFILES[profile_name])
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"[+] Profile '{profile_name}' aplicado com sucesso")
        return True

# ========================================================================
# GUIA DE CONFIGURAÇÃO
# ========================================================================

CONFIGURATION_GUIDE = """
╔═════════════════════════════════════════════════════════════════════════╗
║                                                                         ║
║             GUIA DE CONFIGURAÇÃO AVANÇADA - FRT Suite                 ║
║                                                                         ║
║    Como customizar o sistema para seus casos de uso específicos       ║
║                                                                         ║
╚═════════════════════════════════════════════════════════════════════════╝

## 1. ARQUIVO DE CONFIGURAÇÃO

Localização: ~/.frt_suite/config.json

Criado automaticamente na primeira execução.
Customize conforme suas necessidades.

---

## 2. CONFIGURAÇÕES PRINCIPAIS

### 2.1 Tenant

```json
{
  "tenant_id": "YOUR_TENANT_ID",
  "tenant_domain": "yourdomain.com"
}
```

IMPORTANTE: Coloque o ID correto do seu tenant!

Como encontrar:
  1. Azure Portal → Azure Active Directory
  2. Properties → Directory ID
  3. Copie o GUID


### 2.2 Renovação de Token

```json
{
  "token_renewal_interval_hours": 24,
  "auto_renew_enabled": true,
  "backup_tokens_before_renew": true
}
```

Opções:
  - 1 hora: Renovação frequente (mais requisições)
  - 12 horas: Balance entre controle e requisições
  - 24 horas: Menos requisições (mais stealth)


### 2.3 Rate Limiting (Evasão)

```json
{
  "requests_per_minute": 30,
  "random_delay_min_seconds": 0.5,
  "random_delay_max_seconds": 2,
  "enable_rate_limiting": true
}
```

Recomendações:
  - Detecção baixa: 10-20 req/min (mais lento)
  - Detecção média: 30-50 req/min (balance)
  - Detecção alta: 100+ req/min (rápido mas detectável)


### 2.4 Logging

```json
{
  "enable_logging": true,
  "log_level": "INFO",
  "max_log_size_mb": 50,
  "backup_logs_on_rotate": true
}
```

Log Levels:
  - DEBUG: Tudo (verboso)
  - INFO: Informações importantes
  - WARNING: Apenas avisos
  - ERROR: Apenas erros


### 2.5 Evasão

```json
{
  "business_hours_only": true,
  "business_hours_start": 8,
  "business_hours_end": 18,
  "randomize_user_agent": true,
  "slow_exfiltration_enabled": true,
  "exfiltration_speed_kbps": 100
}
```

Técnicas:
  - Business hours only: Parecer atividade normal
  - Random User-Agent: Não parecer automático
  - Slow exfiltration: Evitar alertas de volume


### 2.6 Segurança

```json
{
  "encrypt_tokens_at_rest": false,
  "require_confirmation_on_sensitive_ops": true,
  "track_all_actions": true
}
```

IMPORTANTE:
  - encrypt_tokens_at_rest: Criptografe tokens em disco
  - require_confirmation: Peça confirmação em ações críticas


---

## 3. PROFILES PRÉ-CONFIGURADOS

Aplicar rapidamente diferentes configurações:

### Profile: CAUTIOUS (Muito stealth)

```bash
python config_manager.py --profile cautious
```

Características:
  - Muito lento (10 req/min)
  - Horário comercial apenas
  - Delays longos (2-5s)
  - Rastreamento total de ações
  - Não vai ser detectado

Uso: Quando target tem SOC muito bom


### Profile: NORMAL (Recomendado)

```bash
python config_manager.py --profile normal
```

Características:
  - Balance entre velocidade e stealth
  - 30 req/min
  - Delays 0.5-2s
  - Sem restrição de horário
  - Rastreamento de ações

Uso: Caso de uso padrão


### Profile: AGGRESSIVE (Rápido)

```bash
python config_manager.py --profile aggressive
```

Características:
  - Muito rápido (100 req/min)
  - Sem delays
  - Sem horário restrito
  - Detectável
  - Sem rastreamento

Uso: Quando quer resultado rápido e risco não importa


### Profile: STEALTH (Ultra stealth)

```bash
python config_manager.py --profile stealth
```

Características:
  - Extremamente lento (5 req/min)
  - Delays muito longos (5-10s)
  - Horário comercial apenas
  - Exfiltração lenta (50 KB/s)
  - Quase impossível detectar

Uso: Persistência de longa duração


---

## 4. CUSTOMIZAÇÃO AVANÇADA

### 4.1 Modificar Diretamente

Edite ~/.frt_suite/config.json com seu editor favorito:

```bash
nano ~/.frt_suite/config.json
```

Exemplo:
```json
{
  "requests_per_minute": 50,
  "business_hours_only": false,
  "slow_exfiltration_enabled": true
}
```


### 4.2 Usar Variáveis de Ambiente

```bash
export FRT_TENANT_ID="seu-tenant-id"
export FRT_REQUESTS_PER_MIN=50
export FRT_BUSINESS_HOURS_ONLY=true

python frt_red_team_suite.py
```


### 4.3 Criar Perfil Customizado

```python
from frt_config import ConfigurationGuide

custom_profile = {
    "requests_per_minute": 45,
    "business_hours_only": True,
    "randomize_user_agent": True,
    "slow_exfiltration_enabled": True,
    "exfiltration_speed_kbps": 150,
}

ConfigurationGuide.PROFILES["myprofile"] = custom_profile
```

Depois:
```bash
python config_manager.py --profile myprofile
```


---

## 5. OTIMIZAÇÕES POR CENÁRIO

### Cenário: Lab/Teste Rápido

```json
{
  "requests_per_minute": 100,
  "random_delay_min_seconds": 0,
  "random_delay_max_seconds": 0.1,
  "enable_rate_limiting": false,
  "business_hours_only": false
}
```

### Cenário: Tenant com SOC Ativo

```json
{
  "requests_per_minute": 10,
  "random_delay_min_seconds": 2,
  "random_delay_max_seconds": 5,
  "business_hours_only": true,
  "randomize_user_agent": true,
  "slow_exfiltration_enabled": true
}
```

### Cenário: Longa Persistência (Semanas/Meses)

```json
{
  "requests_per_minute": 5,
  "random_delay_min_seconds": 5,
  "random_delay_max_seconds": 10,
  "business_hours_only": true,
  "token_renewal_interval_hours": 72,
  "auto_renew_enabled": true,
  "slow_exfiltration_enabled": true,
  "exfiltration_speed_kbps": 50
}
```

### Cenário: Escalada Rápida (Compromete Admin)

```json
{
  "requests_per_minute": 50,
  "random_delay_min_seconds": 0.5,
  "random_delay_max_seconds": 1,
  "business_hours_only": false,
  "require_confirmation_on_sensitive_ops": false
}
```

---

## 6. MONITORAR CONFIGURAÇÃO

### Ver Configuração Atual

```bash
python config_manager.py --show
```

### Validar Configuração

```bash
python config_manager.py --validate
```

### Resetar para Padrão

```bash
python config_manager.py --reset
```

---

## 7. DICAS DE PERFORMANCE

### Para Requisições Mais Rápidas:
  - Aumente requests_per_minute
  - Diminua delays aleatórios
  - Desabilite rate limiting

### Para Menos Detecção:
  - Diminua requests_per_minute
  - Aumente delays
  - Ative business_hours_only
  - Ative slow_exfiltration

### Para Melhor Logging:
  - Use log_level: "DEBUG"
  - Aumente max_log_size_mb
  - Ative backup_logs_on_rotate

---

## 8. INTEGRAÇÃO COM OUTRAS FERRAMENTAS

### Sliver C2

```json
{
  "slack_webhook": "https://hooks.slack.com/...",
  "notify_on_success": true,
  "c2_callback": "http://attacker.com/callback"
}
```

### ELK Stack

```json
{
  "elasticsearch_host": "localhost:9200",
  "elasticsearch_index": "frt-suite",
  "send_logs_to_elasticsearch": true
}
```

### SIEM (Splunk)

```json
{
  "splunk_host": "splunk.company.com",
  "splunk_port": 8088,
  "splunk_token": "your-hec-token",
  "send_to_splunk": true
}
```

---

## 9. TROUBLESHOOTING DE CONFIGURAÇÃO

### Erro: "Invalid configuration"

Solução:
  1. Verifique JSON syntax
  2. Use jsonlint.com para validar
  3. Copie DEFAULT_CONFIG e customize

### Config não é carregada

Solução:
  1. Verifique ~/. frt_suite/config.json existe
  2. Verifique permissões: chmod 644 ~/.frt_suite/config.json
  3. Delete e deixe ser recreada

### Alterações não funcionam

Solução:
  1. Reinicie o suite
  2. Verifique mudança foi salva
  3. Use --validate para confirmar

---

## 10. SEGURANÇA DE CONFIGURAÇÃO

IMPORTANTE:

1. Nunca comite config com tenant_id em repositório público
2. Proteja arquivo:
   chmod 600 ~/.frt_suite/config.json

3. Se trabalha em equipe:
   - Crie template sem valores sensíveis
   - Cada pessoa tem seu próprio config.json
   - Use variáveis de ambiente para secrets

Exemplo template:
```json
{
  "tenant_id": "${TENANT_ID}",
  "tenant_domain": "${TENANT_DOMAIN}",
  "requests_per_minute": 30,
  ...
}
```

Depois:
```bash
export TENANT_ID="seu-id"
python config_substitute.py config.template.json config.json
```

---

## RESUMO: VALORES RECOMENDADOS

Começante:
  - Profile: normal
  - Requests: 30/min
  - Delays: 0.5-2s
  - Logging: INFO

Intermediário:
  - Profile: custom
  - Requests: 20-50/min
  - Delays: 1-5s
  - Logging: DEBUG

Avançado:
  - Profile: stealth
  - Requests: 5-20/min
  - Delays: 5-15s
  - Logging: WARNING

---

Para detalhes, consulte:
  - README_FRT_SUITE.md
  - DOCUMENTACAO_TECNICA_FRT_ATTACK.md
  - Arquivo ~/.frt_suite/config.json (comentado)
"""

# ========================================================================
# CONFIG MANAGER CLI
# ========================================================================

class ConfigManager:
    """Gerenciador de configuração CLI"""
    
    def __init__(self, config_path: Path = None):
        if config_path is None:
            config_path = Path.home() / ".frt_suite" / "config.json"
        
        self.config_path = config_path
        self.guide = ConfigurationGuide()
    
    def show(self):
        """Mostra configuração atual"""
        config = self.guide.load_config(self.config_path)
        
        print("\n" + "="*80)
        print("CONFIGURAÇÃO ATUAL")
        print("="*80 + "\n")
        
        print(json.dumps(config, indent=2))
    
    def validate(self) -> bool:
        """Valida configuração"""
        try:
            config = self.guide.load_config(self.config_path)
            
            required_fields = [
                "tenant_id", "tenant_domain", "requests_per_minute",
                "token_renewal_interval_hours", "enable_logging"
            ]
            
            missing = [f for f in required_fields if f not in config]
            
            if missing:
                print(f"[-] Campos obrigatórios faltando: {missing}")
                return False
            
            print("[+] Configuração válida!")
            return True
        
        except Exception as e:
            print(f"[-] Erro: {e}")
            return False
    
    def reset(self):
        """Reseta para padrão"""
        self.guide.create_default_config(self.config_path)
        print(f"[+] Configuração resetada para padrão")
        print(f"[*] Edite {self.config_path} para customizar")
    
    def apply_profile(self, profile_name: str):
        """Aplica um profile"""
        self.guide.apply_profile(profile_name, self.config_path)

# ========================================================================
# MAIN
# ========================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="FRT Suite Configuration Manager")
    parser.add_argument("--show", action="store_true", help="Mostra config atual")
    parser.add_argument("--validate", action="store_true", help="Valida config")
    parser.add_argument("--reset", action="store_true", help="Reseta para padrão")
    parser.add_argument("--profile", help="Aplica um profile")
    parser.add_argument("--guide", action="store_true", help="Mostra guia de configuração")
    parser.add_argument("--list-profiles", action="store_true", help="Lista profiles disponíveis")
    
    args = parser.parse_args()
    
    manager = ConfigManager()
    
    if args.guide or (not args.show and not args.validate and not args.reset and 
                     not args.profile and not args.list_profiles):
        print(CONFIGURATION_GUIDE)
    
    if args.show:
        manager.show()
    
    if args.validate:
        manager.validate()
    
    if args.reset:
        confirm = input("[!] Tem certeza? (s/n): ").strip().lower()
        if confirm == 's':
            manager.reset()
    
    if args.profile:
        manager.apply_profile(args.profile)
    
    if args.list_profiles:
        print("\nProfiles disponíveis:\n")
        for name in ConfigurationGuide.PROFILES.keys():
            print(f"  - {name}")
