#!/usr/bin/env python3
"""
TROUBLESHOOTING AVANÇADO - FRT Red Team Suite
Diagnóstico e resolução de problemas complexos
"""

import sys
import json
from pathlib import Path
from datetime import datetime

class DiagnosticTool:
    """Ferramenta de diagnóstico do sistema"""
    
    def __init__(self):
        self.base_dir = Path.home() / ".frt_suite"
        self.issues_found = []
        self.warnings = []
    
    def print_header(self):
        print("""
╔═════════════════════════════════════════════════════════════════════════╗
║                                                                         ║
║    🔧 FERRAMENTA DE DIAGNÓSTICO - FRT Red Team Suite                  ║
║                                                                         ║
║    Detecta e resolve problemas automaticamente                        ║
║                                                                         ║
╚═════════════════════════════════════════════════════════════════════════╝
        """)
    
    def check_python_version(self) -> bool:
        """Verifica versão do Python"""
        print("[*] Verificando Python...")
        
        version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        
        if sys.version_info < (3, 9):
            self.issues_found.append(f"Python {version} - Requer 3.9+")
            print(f"    ✗ Python {version} (Requer 3.9+)")
            return False
        
        print(f"    ✓ Python {version}")
        return True
    
    def check_dependencies(self) -> bool:
        """Verifica dependências instaladas"""
        print("[*] Verificando dependências...")
        
        deps = ["requests"]
        all_ok = True
        
        for dep in deps:
            try:
                __import__(dep)
                print(f"    ✓ {dep}")
            except ImportError:
                print(f"    ✗ {dep} - NÃO INSTALADO")
                self.issues_found.append(f"Dependência {dep} não instalada")
                all_ok = False
        
        return all_ok
    
    def check_directories(self) -> bool:
        """Verifica estrutura de diretórios"""
        print("[*] Verificando diretórios...")
        
        required_dirs = [
            ("Base", self.base_dir),
            ("Data", self.base_dir / "data"),
            ("Logs", self.base_dir / "logs"),
            ("Backups", self.base_dir / "backups"),
        ]
        
        all_ok = True
        
        for name, path in required_dirs:
            if path.exists():
                print(f"    ✓ {name}: {path}")
            else:
                print(f"    ✗ {name}: {path} (NÃO EXISTE)")
                self.warnings.append(f"Diretório {name} não existe - será criado automaticamente")
                all_ok = False
        
        return all_ok
    
    def check_tokens(self) -> bool:
        """Verifica tokens"""
        print("[*] Verificando tokens...")
        
        tokens_file = self.base_dir / "data" / "tokens.json"
        
        if not tokens_file.exists():
            print(f"    ✗ Nenhum token carregado")
            self.warnings.append("Nenhum token em ~.frt_suite/data/tokens.json")
            
            # Verificar se existe em local alternativo
            default_location = Path.home() / "captura_tokens.json"
            if default_location.exists():
                print(f"    ℹ Encontrado em: {default_location}")
                self.warnings.append(f"Copie para: {tokens_file}")
                return False
            else:
                self.issues_found.append("Nenhum arquivo de tokens encontrado")
                return False
        
        try:
            with open(tokens_file, 'r') as f:
                data = json.load(f)
            
            required_fields = ["access_token", "refresh_token", "tenant_id", "user_email"]
            missing = [f for f in required_fields if f not in data]
            
            if missing:
                print(f"    ✗ Campos obrigatórios faltando: {', '.join(missing)}")
                self.issues_found.append(f"Token incompleto: faltam {missing}")
                return False
            
            print(f"    ✓ Token válido para {data.get('user_email')}")
            return True
        
        except json.JSONDecodeError:
            print(f"    ✗ Erro ao ler tokens.json (JSON inválido)")
            self.issues_found.append("Arquivo tokens.json com erro JSON")
            return False
        except Exception as e:
            print(f"    ✗ Erro: {e}")
            self.issues_found.append(f"Erro ao ler tokens: {e}")
            return False
    
    def check_logs(self) -> bool:
        """Verifica logs"""
        print("[*] Verificando logs...")
        
        log_file = self.base_dir / "logs" / "frt_suite.log"
        
        if not log_file.exists():
            print(f"    ℹ Nenhum log encontrado (primeira execução?)")
            return True
        
        try:
            size_mb = log_file.stat().st_size / (1024 * 1024)
            
            if size_mb > 50:
                print(f"    ⚠ Log muito grande: {size_mb:.1f}MB")
                self.warnings.append(f"Arquivo de log está grande ({size_mb:.1f}MB) - considere limpar")
            else:
                print(f"    ✓ Log OK ({size_mb:.1f}MB)")
            
            return True
        except Exception as e:
            print(f"    ✗ Erro ao ler log: {e}")
            return False
    
    def check_config(self) -> bool:
        """Verifica configuração"""
        print("[*] Verificando configuração...")
        
        config_file = self.base_dir / "config.json"
        
        if not config_file.exists():
            print(f"    ℹ Nenhuma configuração personalizada")
            return True
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            print(f"    ✓ Configuração encontrada")
            print(f"      - Tenant: {config.get('tenant_domain', 'N/A')}")
            print(f"      - Rate limit: {config.get('requests_per_minute', 30)} req/min")
            
            return True
        except Exception as e:
            print(f"    ✗ Erro ao ler config: {e}")
            self.warnings.append(f"Erro na configuração: {e}")
            return False
    
    def run_full_diagnostic(self):
        """Executa diagnóstico completo"""
        self.print_header()
        
        checks = [
            self.check_python_version(),
            self.check_dependencies(),
            self.check_directories(),
            self.check_tokens(),
            self.check_logs(),
            self.check_config(),
        ]
        
        print("\n" + "="*80)
        print("RESUMO DO DIAGNÓSTICO")
        print("="*80)
        
        if self.issues_found:
            print(f"\n🔴 {len(self.issues_found)} PROBLEMA(S) ENCONTRADO(S):\n")
            for i, issue in enumerate(self.issues_found, 1):
                print(f"  {i}. {issue}")
        else:
            print("\n✓ Nenhum problema crítico encontrado!")
        
        if self.warnings:
            print(f"\n⚠️  {len(self.warnings)} AVISO(S):\n")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")
        
        success_count = sum(checks)
        total = len(checks)
        
        print(f"\n[*] Resultado: {success_count}/{total} verificações OK")
        
        return len(self.issues_found) == 0

# ============================================================================
# GUIA DE TROUBLESHOOTING POR ERRO
# ============================================================================

TROUBLESHOOTING_GUIDE = """
╔═════════════════════════════════════════════════════════════════════════╗
║                    GUIA DE TROUBLESHOOTING                             ║
╚═════════════════════════════════════════════════════════════════════════╝

## ERRO 1: "No module named 'requests'"

CAUSA:
  Dependência requests não instalada

SOLUÇÃO:
  pip install requests

OU (se usar Python 3):
  pip3 install requests

VERIFICAR:
  python -c "import requests; print(requests.__version__)"


## ERRO 2: "Token não encontrado"

CAUSA:
  Arquivo de tokens não está no local certo

SOLUÇÃO:
  1. Coloque o arquivo em um destes locais:
     ~/captura_tokens.json
     ~/.frt_suite/data/tokens.json
  
  2. Ou use opção 1 do menu:
     Menu → 1
     Digite o caminho completo

VERIFICAR:
  ls -la ~/captura_tokens.json
  ls -la ~/.frt_suite/data/tokens.json


## ERRO 3: "ConnectionError: Max retries exceeded"

CAUSA:
  1. Sem internet
  2. Firewall bloqueando
  3. Rate limited pelo Microsoft
  4. Tenant_id inválido

SOLUÇÃO:
  1. Verifique internet: ping google.com
  2. Aguarde 5 minutos (possível rate limit)
  3. Verifique tenant_id está correto
  4. Verifique firewall permite access.microsoft.com

VERIFICAR:
  curl -I https://login.microsoftonline.com


## ERRO 4: "401 Unauthorized"

CAUSA:
  1. Access Token expirou (1 hora)
  2. Refresh Token expirou (90 dias)
  3. Token foi revogado
  4. Permissões insuficientes

SOLUÇÃO:
  Menu → 3 (Renovar token)
  
  OU se RF também expirou:
  Precisa capturar novo token via Device Code Flow

VERIFICAR:
  Menu → 2 (Listar tokens)
  Veja quanto tempo resta


## ERRO 5: "403 Forbidden"

CAUSA:
  Usuário não tem permissão para esta ação
  Ex: Não é admin, não pode listar roles

SOLUÇÃO:
  Use outro app/usuário com mais privilégios
  OU
  Escalade privilégios (Fase 5)

EXEMPLO:
  Se enumerate_admins falha (403):
  - Usuário não tem permissão de leitura de roles
  - Precisa comprometer um admin primeiro


## ERRO 6: "SyntaxError: invalid syntax"

CAUSA:
  Versão do Python < 3.9
  OU arquivo corrompido

SOLUÇÃO:
  1. Verifique Python:
     python --version
  
  2. Se < 3.9, atualize:
     Baixe Python 3.9+ de python.org
  
  3. Se arquivo corrompido:
     Baixe novamente

VERIFICAR:
  python --version


## ERRO 7: "Permission denied" ao criar arquivos

CAUSA:
  ~/.frt_suite não tem permissão de escrita

SOLUÇÃO:
  chmod -R 755 ~/.frt_suite
  
  OU se quer ser mais restritivo:
  chmod -R 700 ~/.frt_suite


## ERRO 8: "JSON decode error"

CAUSA:
  Arquivo de tokens com formato inválido

SOLUÇÃO:
  Verifique formato do JSON:
  python -m json.tool ~/captura_tokens.json
  
  Se der erro, o JSON está inválido
  
  Corrija usando site como jsonlint.com


## ERRO 9: "TypeError: unsupported operand type(s)"

CAUSA:
  Tipos de dados incompatíveis no código
  Geralmente quando chama função errado

SOLUÇÃO:
  Verifique se está passando tipo certo
  
  Exemplo:
  ✗ exploit.read_emails(limit="10")  # String!
  ✓ exploit.read_emails(limit=10)    # Integer!


## ERRO 10: "AttributeError: 'NoneType' has no attribute 'x'"

CAUSA:
  Tentou acessar atributo de valor None
  Geralmente porque token_manager.get_token() retornou None

SOLUÇÃO:
  1. Certifique que carregou tokens
  2. Use rótulo correto
  
  Exemplo:
  ✗ token_manager.get_token("wrong_label")
  ✓ token_manager.get_token("primary")
  
  OU:
  token = token_manager.get_token("primary")
  if token is None:
      print("[-] Token não encontrado!")
      return


## ERRO 11: "Timeout exceeded"

CAUSA:
  Microsoft levou mais de 10s para responder
  Network lento
  Microsoft.com sobrecarregado

SOLUÇÃO:
  1. Tente novamente
  2. Aguarde alguns minutos
  3. Tente com taxa menor de requisições
  4. Verifique internet


## ERRO 12: "Cannot connect to proxy"

CAUSA:
  Se estiver usando proxy, configuração errada

SOLUÇÃO:
  1. Verifique proxy URL
  2. Desabilite proxy temporariamente
  3. Tente sem proxy


## ERRO 13: "File not found: /home/user/.frt_suite/logs/frt_suite.log"

CAUSA:
  Diretório /logs não foi criado

SOLUÇÃO:
  mkdir -p ~/.frt_suite/logs
  
  OU:
  Execute install_frt_suite.py para recriar


## ERRO 14: "KeyError: 'access_token'"

CAUSA:
  Arquivo tokens.json não tem campo 'access_token'

SOLUÇÃO:
  Verifique formato do arquivo:
  {
    "access_token": "eyJ0eXAi...",
    "refresh_token": "1.AVkA5L...",
    "tenant_id": "c1e8b8e4...",
    ...
  }


## ERRO 15: "UnicodeDecodeError"

CAUSA:
  Arquivo com encoding errado (não UTF-8)

SOLUÇÃO:
  Converta para UTF-8:
  iconv -f ISO-8859-1 -t UTF-8 file.json > file_utf8.json


---

## CHECKLIST SE NADA FUNCIONA

1. Python 3.9+?
   python --version

2. Requests instalado?
   pip install requests

3. Tokens carregados?
   ls -la ~/.frt_suite/data/tokens.json

4. Token válido?
   python -m json.tool ~/.frt_suite/data/tokens.json

5. Internet funcionando?
   ping 8.8.8.8

6. Microsoft.com acessível?
   curl https://graph.microsoft.com

7. Firewall permitindo?
   Check firewall rules

8. Tenant_id correto?
   Verifique em tokens.json

9. Token não expirou?
   Renovar: Menu → 3

10. Permissões suficientes?
    Tente com usuario admin

---

## COMO REPORTAR BUG

Se encontrar um bug:

1. Execute ferramenta de diagnóstico:
   python diagnostic_tool.py

2. Capture logs:
   cat ~/.frt_suite/logs/frt_suite.log > bug_report.log

3. Verifique Python:
   python --version

4. Verifique dependências:
   pip list | grep requests

5. Tente reproduzir em ambiente limpo

6. Reporte com:
   - Erro exato
   - Passos para reproduzir
   - Output do diagnóstico
   - Versão do Python
   - Sistema operacional

---

## RECURSOS ADICIONAIS

- Leia README_FRT_SUITE.md
- Consulte DOCUMENTACAO_TECNICA_FRT_ATTACK.md
- Veja exemplos_praticos_frt_suite.py
- Verifique logs em ~/.frt_suite/logs/

---

Ainda tem problema? Verifique se:
  ✓ Seguiu todas as instruções
  ✓ Leu o README
  ✓ Consultou documentação
  ✓ Executou ferramentas de diagnóstico
  ✓ Tentou sugestões acima
"""

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Ferramenta de Diagnóstico FRT Suite")
    parser.add_argument("--diagnose", action="store_true", help="Executar diagnóstico completo")
    parser.add_argument("--guide", action="store_true", help="Mostrar guia de troubleshooting")
    parser.add_argument("--fix", action="store_true", help="Tentar corrigir automaticamente")
    
    args = parser.parse_args()
    
    if args.guide or (not args.diagnose and not args.fix):
        print(TROUBLESHOOTING_GUIDE)
    
    if args.diagnose or args.fix:
        diagnostic = DiagnosticTool()
        success = diagnostic.run_full_diagnostic()
        
        if args.fix and not success:
            print("\n" + "="*80)
            print("TENTANDO CORRIGIR PROBLEMAS...")
            print("="*80)
            
            from pathlib import Path
            import sys
            
            # Criar diretórios
            base_dir = Path.home() / ".frt_suite"
            (base_dir / "data").mkdir(parents=True, exist_ok=True)
            (base_dir / "logs").mkdir(parents=True, exist_ok=True)
            (base_dir / "backups").mkdir(parents=True, exist_ok=True)
            
            print("[+] Diretórios criados")
            
            # Instalar requests
            try:
                import subprocess
                subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "requests"], timeout=30)
                print("[+] Requests instalado")
            except:
                print("[-] Erro ao instalar requests - instale manualmente:")
                print("    pip install requests")
            
            print("\n[+] Problemas básicos corrigidos!")
            print("[!] Para outros problemas, consulte o guia acima")
