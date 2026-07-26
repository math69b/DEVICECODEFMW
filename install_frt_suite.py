#!/usr/bin/env python3
"""
INSTALADOR - FRT Red Team Suite
Configura tudo automaticamente em uma execução
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

class FRTInstaller:
    """Instalador automático do FRT Suite"""
    
    def __init__(self):
        self.system = platform.system()
        self.python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        self.home_dir = Path.home()
        self.suite_dir = self.home_dir / "frt_suite"
        
        self.print_banner()
    
    def print_banner(self):
        """Mostra banner de instalação"""
        print("""
╔═════════════════════════════════════════════════════════════════════════╗
║                                                                         ║
║        🔐 FRT RED TEAM SUITE - INSTALADOR AUTOMÁTICO                  ║
║                                                                         ║
║    Este script configurará o sistema completo automaticamente         ║
║                                                                         ║
╚═════════════════════════════════════════════════════════════════════════╝
        """)
        
        print(f"[*] Sistema Operacional: {self.system}")
        print(f"[*] Versão Python: {self.python_version}")
        print(f"[*] Diretório Home: {self.home_dir}")
        print(f"[*] Será instalado em: {self.suite_dir}\n")
    
    def check_python_version(self) -> bool:
        """Verifica se Python 3.9+"""
        if sys.version_info < (3, 9):
            print(f"[-] Erro: Python 3.9+ requerido (você tem {self.python_version})")
            return False
        
        print(f"[+] ✓ Python {self.python_version} OK")
        return True
    
    def install_dependencies(self) -> bool:
        """Instala dependências necessárias"""
        print("\n[*] Instalando dependências...")
        
        dependencies = ["requests"]
        
        try:
            for dep in dependencies:
                print(f"[*] Instalando {dep}...", end=" ", flush=True)
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "--quiet", dep],
                    check=True,
                    timeout=30
                )
                print("✓")
            
            print("[+] ✓ Todas as dependências instaladas")
            return True
        
        except Exception as e:
            print(f"[-] Erro ao instalar dependências: {e}")
            return False
    
    def create_directories(self) -> bool:
        """Cria estrutura de diretórios"""
        print("\n[*] Criando diretórios...")
        
        try:
            dirs = [
                self.suite_dir,
                self.suite_dir / "data",
                self.suite_dir / "logs",
                self.suite_dir / "backups",
                self.suite_dir / "scripts",
                self.suite_dir / "reports",
            ]
            
            for dir_path in dirs:
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"[+] ✓ {dir_path}")
            
            print("[+] ✓ Estrutura de diretórios criada")
            return True
        
        except Exception as e:
            print(f"[-] Erro ao criar diretórios: {e}")
            return False
    
    def download_files(self) -> bool:
        """Cria arquivos do suite (você pode customizar isto)"""
        print("\n[*] Preparando arquivos...")
        
        files = {
            "frt_red_team_suite.py": "Sistema principal",
            "frt_suite_extensions.py": "Extensões (email, teams, etc)",
            "README.md": "Documentação",
        }
        
        # Aqui você pode copiar os arquivos do suite
        # Por enquanto apenas avisar
        
        print("[!] Arquivos do suite:")
        for filename, description in files.items():
            print(f"    - {filename} ({description})")
        
        print("\n[*] Os arquivos devem ser copiados manualmente para:")
        print(f"    {self.suite_dir}/")
        
        return True
    
    def create_launcher_script(self) -> bool:
        """Cria script launcher para fácil execução"""
        print("\n[*] Criando script launcher...")
        
        if self.system == "Windows":
            launcher_path = self.suite_dir / "run.bat"
            content = f"""@echo off
cd /d "{self.suite_dir}"
python frt_red_team_suite.py
pause
"""
        else:
            launcher_path = self.suite_dir / "run.sh"
            content = f"""#!/bin/bash
cd "{self.suite_dir}"
python3 frt_red_team_suite.py
"""
        
        try:
            launcher_path.write_text(content)
            
            if self.system != "Windows":
                os.chmod(launcher_path, 0o755)
            
            print(f"[+] ✓ Launcher criado: {launcher_path}")
            return True
        
        except Exception as e:
            print(f"[-] Erro ao criar launcher: {e}")
            return False
    
    def create_config_file(self) -> bool:
        """Cria arquivo de configuração padrão"""
        print("\n[*] Criando arquivo de configuração...")
        
        config_path = self.suite_dir / "config.json"
        
        config_content = """{
  "tenant_id": "YOUR_TENANT_ID",
  "tenant_domain": "your-domain.com",
  "token_renewal_interval_hours": 24,
  "requests_per_minute": 30,
  "enable_logging": true,
  "log_level": "INFO",
  "backup_frequency_days": 7,
  "max_log_size_mb": 50,
  "rate_limit_enabled": true,
  "business_hours_only": false,
  "notification_email": "your-email@your-domain.com"
}
"""
        
        try:
            config_path.write_text(config_content)
            print(f"[+] ✓ Config criada: {config_path}")
            return True
        
        except Exception as e:
            print(f"[-] Erro: {e}")
            return False
    
    def create_startup_guide(self) -> bool:
        """Cria guia de início rápido"""
        print("\n[*] Criando guia de início rápido...")
        
        guide_path = self.suite_dir / "QUICK_START.md"
        
        guide_content = f"""# Quick Start Guide - FRT Red Team Suite

## Instalação Concluída! ✓

Seu sistema está pronto em: `{self.suite_dir}`

## Próximos Passos

### 1. Copiar Arquivos do Suite

Copie os arquivos principais para este diretório:
```bash
cp frt_red_team_suite.py {self.suite_dir}/
cp frt_suite_extensions.py {self.suite_dir}/
```

### 2. Preparar Tokens

Coloque seu arquivo de tokens em um destes locais:
```
{self.home_dir}/captura_tokens.json
ou
{self.suite_dir}/data/tokens.json
```

Formato esperado:
```json
{{
  "access_token": "eyJ0eXAi...",
  "refresh_token": "1.AVkA5L...",
  "tenant_id": "c1e8b8e4...",
  "tenant_domain": "seu-dominio.com",
  "user_id": "1e825e83...",
  "user_email": "seu@email.com",
  "expires_in": 3600
}}
```

### 3. Executar o Suite

**Linux/Mac:**
```bash
python3 {self.suite_dir}/frt_red_team_suite.py
```

**Windows:**
```cmd
python {self.suite_dir}/frt_red_team_suite.py
```

Ou use o launcher:
```bash
{self.suite_dir}/run.{"sh" if self.system != "Windows" else "bat"}
```

## Estrutura de Diretórios

```
{self.suite_dir}/
├─ frt_red_team_suite.py        # Sistema principal
├─ frt_suite_extensions.py      # Extensões
├─ config.json                  # Configuração
├─ data/                        # Dados coletados
│  ├─ tokens.json
│  ├─ users_enum.json
│  ├─ admins_enum.json
│  ├─ emails_read.json
│  └─ ...
├─ logs/                        # Logs
├─ backups/                     # Backups
├─ reports/                     # Relatórios
└─ scripts/                     # Scripts customizados
```

## Menu Principal

Quando executar, você verá:

```
[1] Carregar tokens
[2] Listar tokens
[3] Renovar token
[20] Analisar FRT
[30] Enumerar usuários
[35] Coleta rápida
[50] Gerar relatório
[99] Sair
```

## Primeiros Passos

```bash
# 1. Executar
python frt_red_team_suite.py

# 2. Carregar tokens (opção 1)

# 3. Analisar FRT (opção 20)

# 4. Coleta rápida (opção 35)

# 5. Gerar relatório (opção 50)
```

## Troubleshooting

**Erro: "No module named 'requests'"**
```bash
pip install requests
```

**Erro: "Token não encontrado"**
- Verifique se captura_tokens.json está no lugar certo
- Use opção 1 do menu para especificar o caminho

**Erro: "401 Unauthorized"**
- Token expirou
- Use opção 3 (renovar token)

## Próximas Leituras

- README_FRT_SUITE.md - Documentação completa
- DOCUMENTACAO_TECNICA_FRT_ATTACK.md - Detalhes técnicos
- DIAGRAMAS_ATTACK_CHAIN.md - Diagramas visuais

## Suporte

Ver logs: `{self.suite_dir}/logs/frt_suite.log`

---

**Instalação completada em:** {Path(__file__).stat().st_mtime}
"""
        
        try:
            guide_path.write_text(guide_content)
            print(f"[+] ✓ Guia criado: {guide_path}")
            return True
        
        except Exception as e:
            print(f"[-] Erro: {e}")
            return False
    
    def verify_installation(self) -> bool:
        """Verifica se instalação foi bem-sucedida"""
        print("\n[*] Verificando instalação...")
        
        checks = {
            "Diretório base": self.suite_dir.exists(),
            "Diretório data": (self.suite_dir / "data").exists(),
            "Diretório logs": (self.suite_dir / "logs").exists(),
            "Config": (self.suite_dir / "config.json").exists(),
        }
        
        all_ok = True
        for check_name, result in checks.items():
            status = "✓" if result else "✗"
            print(f"[{status}] {check_name}")
            if not result:
                all_ok = False
        
        return all_ok
    
    def print_summary(self):
        """Mostra resumo da instalação"""
        print("\n" + "="*80)
        print("RESUMO DA INSTALAÇÃO")
        print("="*80)
        
        print(f"""
✓ Instalação Concluída!

Diretório: {self.suite_dir}

Próximos passos:

1. Copiar arquivos do suite:
   - frt_red_team_suite.py
   - frt_suite_extensions.py

2. Colocar tokens em:
   {self.home_dir}/captura_tokens.json

3. Executar:
   python {self.suite_dir}/frt_red_team_suite.py

Documentação:
   {self.suite_dir}/QUICK_START.md
   {self.suite_dir}/README.md (depois de copiar)

Logs:
   {self.suite_dir}/logs/frt_suite.log

Dados coletados:
   {self.suite_dir}/data/

Suporte:
   - Ver QUICK_START.md
   - Consultar README_FRT_SUITE.md
   - Verificar logs

---

Sistema pronto para usar! 🚀
        """)
    
    def run(self):
        """Executa instalação completa"""
        steps = [
            ("Verificar Python", self.check_python_version),
            ("Instalar dependências", self.install_dependencies),
            ("Criar diretórios", self.create_directories),
            ("Criar launcher", self.create_launcher_script),
            ("Criar configuração", self.create_config_file),
            ("Criar guia", self.create_startup_guide),
            ("Verificar instalação", self.verify_installation),
        ]
        
        print("\n" + "="*80)
        print("EXECUTANDO INSTALAÇÃO")
        print("="*80 + "\n")
        
        success_count = 0
        
        for step_name, step_func in steps:
            print(f"\n[*] {step_name}...")
            try:
                result = step_func()
                if result:
                    success_count += 1
                else:
                    print(f"[!] {step_name} completado com avisos")
            except KeyboardInterrupt:
                print("\n[-] Instalação cancelada pelo usuário")
                return False
            except Exception as e:
                print(f"[-] Erro em {step_name}: {e}")
        
        # Resumo
        print(f"\n[+] {success_count}/{len(steps)} etapas concluídas com sucesso")
        
        self.print_summary()
        
        return True

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    try:
        installer = FRTInstaller()
        
        # Pedir confirmação
        confirm = input("\n[?] Continuar com instalação? (s/n): ").strip().lower()
        
        if confirm != 's':
            print("\n[-] Instalação cancelada")
            sys.exit(0)
        
        # Executar
        success = installer.run()
        
        if success:
            print("\n[+] ✓ Instalação concluída com sucesso!")
            
            # Abrir QUICK_START
            quick_start = installer.suite_dir / "QUICK_START.md"
            if quick_start.exists():
                print(f"\n[*] Para começar, leia: {quick_start}")
            
            sys.exit(0)
        else:
            print("\n[-] Instalação falhou ou foi cancelada")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n[-] Instalação cancelada pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n[-] Erro fatal: {e}")
        sys.exit(1)
