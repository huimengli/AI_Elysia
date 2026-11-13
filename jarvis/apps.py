from __future__ import annotations
"""本机常用应用表 —— 扫开始菜单快捷方式入库，`open_app` 先匹配这张表（records/2026-11-13-13-46-12.md）。

表建在现有的 `jarvis/data/events.db` 里（`apps` 表），不新建数据库文件、不发明新目录，
与 `jarvis/events.py` 同一套 sqlite 访问方式（WAL + `timeout`）。

`open_app` 的次序按需求写死：① 先匹配本表；② 不匹配才走其它路径（`APP_MAP` / 补 `.exe`）；
③ 启动后**复读证据**（进程/窗口出现才算成功），失败如实报并带原因。
"""
import json
import os
import subprocess
import sqlite3
import time
from datetime import datetime
from pathlib import Path

try:  # pypinyin 已在 venv（0.55.0），不新增依赖；缺失时音近层自动退化为纯字符相似度
    from pypinyin import Style, pinyin
except Exception:  # pragma: no cover
    pinyin = None

_DB = Path(__file__).parent / "data" / "events.db"

_SCHEMA = """CREATE TABLE IF NOT EXISTS apps (
    name TEXT PRIMARY KEY,
    norm TEXT NOT NULL,
    aliases TEXT NOT NULL DEFAULT '[]',
    launch TEXT NOT NULL,
    args TEXT NOT NULL DEFAULT '[]',
    kind TEXT NOT NULL DEFAULT 'exe',
    hits INTEGER NOT NULL DEFAULT 0,
    last_used TEXT,
    py TEXT NOT NULL DEFAULT '',
    py_tone TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS app_queries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    raw TEXT NOT NULL,
    matched TEXT NOT NULL,
    ts TEXT NOT NULL
);"""

# 已有表（13:50 灌入过）没有 py/py_tone 列，用 ALTER 幂等升级（已存在则忽略）。
_COLS = ("py", "py_tone")


def _ensure_schema() -> None:
    """幂等建表 + 补列。`populate()` 之外（工具独立调用、服务未启动）也要有表。"""
    _DB.parent.mkdir(parents=True, exist_ok=True)
    with _conn() as c:
        c.executescript(_SCHEMA)
        for col in _COLS:
            try:
                c.execute(f"ALTER TABLE apps ADD COLUMN {col} TEXT NOT NULL DEFAULT ''")
            except sqlite3.OperationalError:
                pass  # 列已存在


def _py_pair(name: str) -> tuple[str, str]:
    """(无声调拼音串, 带调拼音串) —— 索引列，灌入时算一次，不在每次调用现场算。

    HB-041（14:32 实测）：`pypinyin` 的 `errors="ignore"` 会**丢掉非中文字符**，所以纯英文
    应用名（`Google Chrome`、`OneDrive`、`aida64`，共 158 条）拼音串是**空串**，拼音直达层
    对它们完全失效；而「`dnSpy.exe - 快捷方式`」被索引成 `kuaijiefangshi`（只取中文部分），
    和 `HaoZip - 快捷方式` **撞车**。两处都修：**先剥「- 快捷方式」尾巴**，**没有中文时用名字
    本身的小写字母当索引**。
    """
    base = name
    for tail in (" - 快捷方式", " - Shortcut"):
        if base.endswith(tail):
            base = base[: -len(tail)]
    if pinyin is None:
        return (normalize(base), "")
    plain = "".join(x[0] for x in pinyin(base, style=Style.NORMAL, errors="ignore"))
    tone = "".join(x[0] for x in pinyin(base, style=Style.TONE, errors="ignore"))
    if not plain:  # 纯英文名：用字母本身
        letters = "".join(c.lower() for c in base if c.isalpha())
        return (normalize(letters), normalize(letters))
    return (normalize(plain), normalize(tone))


# 开始菜单里没有、但每天都在用的系统应用（中文规范名 + 英文别名 + 启动命令）。
# 20 轮实测「记事本」的窗口标题是中文、进程名是英文（record_6/7），所以**两边都要收**。
_EXTRAS = [
    ("记事本", ["notepad"], "notepad.exe", "exe", []),
    ("画图", ["paint", "mspaint"], "mspaint.exe", "exe", []),
    ("计算器", ["calculator", "calc"], "calc.exe", "exe", []),
    ("设置", ["settings", "windows settings"], "ms-settings:", "uri", []),
    ("任务管理器", ["task manager", "taskmgr"], "taskmgr.exe", "exe", []),
    ("资源管理器", ["explorer", "file explorer"], "explorer.exe", "exe", []),
    ("控制面板", ["control panel"], "control.exe", "exe", []),
    ("终端", ["terminal", "windows terminal", "wt"], "wt.exe", "exe", []),
    ("命令提示符", ["cmd", "command prompt"], "cmd.exe", "exe", []),
    ("录音机", ["sound recorder", "voice recorder"], "SoundRecorder.exe", "exe", []),
    ("截图工具", ["snipping tool", "screen sketch"], "SnippingTool.exe", "exe", []),
]

_START_DIRS = [
    os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"),
    r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs",
]


def normalize(s: str) -> str:
    """规范名：去掉「 - 快捷方式」尾巴、小写、去空格与标点，用于匹配比对。"""
    s = s.strip()
    for tail in (" - 快捷方式", " - Shortcut", " - Shortcut"):
        if s.endswith(tail):
            s = s[: -len(tail)]
    drop = set(" .-_()（）·")
    return "".join(c.lower() for c in s if c not in drop)


def _ps_json(ps: str) -> list[dict]:
    """Run PowerShell and decode UTF-8 JSON output (never text=True, see HB-034)."""
    r = subprocess.run(["powershell", "-NoProfile", "-command", ps],
                       capture_output=True, text=False, timeout=60)
    out = r.stdout.decode("utf-8", errors="ignore").strip()
    if not out:
        return []
    try:
        data = json.loads(out)
    except json.JSONDecodeError:
        return []
    return data if isinstance(data, list) else [data]


def scan_start_menu() -> list[dict]:
    """扫开始菜单 .lnk，取显示名 + 目标 + 参数（用 WScript.Shell COM，不需要 Temp 编译）。"""
    ps = (
        "[Console]::OutputEncoding=[System.Text.Encoding]::UTF8;"
        "$sh = New-Object -ComObject WScript.Shell; $rows = @();"
        "foreach ($d in @('" + "','".join(_START_DIRS) + "')) {"
        "  if (Test-Path $d) { Get-ChildItem -Path $d -Recurse -Filter *.lnk -Force | ForEach-Object {"
        "    $s = $sh.CreateShortcut($_.FullName);"
        "    $rows += [pscustomobject]@{name=$_.BaseName; target=$s.TargetPath; args=$s.Arguments}"
        "  } }"
        "}; $rows | ConvertTo-Json -Compress"
    )
    return _ps_json(ps)


def _conn() -> sqlite3.Connection:
    return sqlite3.connect(str(_DB), timeout=5.0)


def populate() -> dict:
    """建表 + 灌入开始菜单条目与系统应用别名，返回统计。"""
    _DB.parent.mkdir(parents=True, exist_ok=True)
    with _conn() as c:
        c.executescript(_SCHEMA)
        for col in _COLS:
            try:
                c.execute(f"ALTER TABLE apps ADD COLUMN {col} TEXT NOT NULL DEFAULT ''")
            except sqlite3.OperationalError:
                pass
        c.execute("PRAGMA journal_mode=WAL")
    added = skipped = no_target = 0
    rows: list[tuple] = []
    for item in scan_start_menu():
        name = (item.get("name") or "").strip()
        target = (item.get("target") or "").strip()
        if not name:
            continue
        if not target:
            no_target += 1  # UWP/占位快捷方式没有 exe，跳过
            continue
        args = [a for a in (item.get("args") or "").split() if a]
        py, pyt = _py_pair(name)
        rows.append((name, normalize(name), json.dumps([normalize(name)], ensure_ascii=False),
                     target, json.dumps(args, ensure_ascii=False), "lnk", py, pyt))
    for name, aliases, launch, kind, args in _EXTRAS:
        py, pyt = _py_pair(name)
        rows.append((name, normalize(name), json.dumps([normalize(a) for a in aliases],
                                                       ensure_ascii=False),
                     launch, json.dumps(args, ensure_ascii=False), kind, py, pyt))
    with _conn() as c:
        for r in rows:
            try:
                c.execute("INSERT INTO apps (name, norm, aliases, launch, args, kind, py, py_tone) "
                          "VALUES (?, ?, ?, ?, ?, ?, ?, ?)", r)
                added += 1
            except sqlite3.IntegrityError:
                skipped += 1
    filled = _fill_missing_pinyin()
    return {"added": added, "skipped_existing": skipped, "no_target_skipped": no_target,
            "pinyin_filled": filled, "total": _total()}


def _fill_missing_pinyin() -> int:
    """重算全部行的拼音（227 行，pypinyin 现场算一次约 20 ms，不在查询时算）。"""
    n = 0
    with _conn() as c:
        names = [r[0] for r in c.execute("SELECT name FROM apps").fetchall()]
        for name in names:
            py, pyt = _py_pair(name)
            c.execute("UPDATE apps SET py = ?, py_tone = ? WHERE name = ?", (py, pyt, name))
            n += 1
    return n


def _total() -> int:
    with _conn() as c:
        return int(c.execute("SELECT COUNT(*) FROM apps").fetchone()[0])


def total() -> int:
    """公开入口：表里的应用条数（`open_app` 的失败文案要用）。"""
    return _total()


def running(target: str) -> str | None:
    """公开入口：复读到进程名，读不到返回 None。"""
    return _running(target)


# --- ASR 容错层（records/2026-11-13-13-46-12.md 追加节，阈值写死，不许临场调） ---

_HIGH = 0.66   # 高置信：直接打开
_GAP = 0.12    # top1 与次优的差距要求
_LOW = 0.45    # 低于此值不算音近，交给其它路径


def _lev(a: str, b: str) -> int:
    """字符级 Levenshtein 距离（纯 python，227 条短串，开销可忽略）。"""
    if a == b:
        return 0
        # 上一行是 a==b 短路
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[len(b)]


def _ratio(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return 1.0 - _lev(a, b) / max(len(a), len(b))


def _py(s: str, tones: bool) -> str:
    if pinyin is None:
        return ""
    style = Style.TONE if tones else Style.NORMAL
    return "".join(x[0] for x in pinyin(s, style=style, errors="ignore"))


def similarity(q: str, name: str) -> float:
    """取「字符形近 / 带调拼音 / 无声调拼音」三者最大 —— whisper 常丢音调、近音替换。"""
    best = _ratio(q, name)
    for tones in (True, False):
        pq, pn = _py(q, tones), _py(name, tones)
        if pq and pn:
            best = max(best, _ratio(pq, pn))
    return best


def fuzzy_match(query: str, limit: int = 3) -> list[tuple[float, dict]]:
    """音近/形近层。**读索引列算相似度**（不再每行现算 pypinyin，见 14:22 追加节）。"""
    q = normalize(query)
    if not q:
        return []
    q_py, q_pyt = _py_pair(q)  # 查询拼音只算一次
    with _conn() as c:
        rows = [dict(zip(_KEYS, r)) for r in c.execute(_COLS_SEL).fetchall()]
    scored = []
    for d in rows:
        s = max(_ratio(q, d["norm"]), _ratio(q, d["name"]))
        if q_py:
            s = max(s, _ratio(q_py, d["py"]), _ratio(q_pyt, d["py_tone"]))
        for al in json.loads(d["aliases"] or "[]"):  # 英文别名做字符比对
            s = max(s, _ratio(q, al))
        scored.append((s, d))
    scored.sort(key=lambda x: -x[0])
    return scored[:limit]


def register_alias(name: str, raw: str) -> None:
    """音近命中后把用户原话登记成别名，下次走精确层（自学习）。**绝不抛异常**。"""
    key = normalize(raw)
    if not key:
        return
    try:
        _ensure_schema()
        with _conn() as c:
            row = c.execute("SELECT aliases FROM apps WHERE name = ?", (name,)).fetchone()
            if not row:
                return
            aliases = json.loads(row[0] or "[]")
            if key not in aliases:
                aliases.append(key)
                c.execute("UPDATE apps SET aliases = ? WHERE name = ?",
                          (json.dumps(aliases, ensure_ascii=False), name))
            c.execute("INSERT INTO app_queries (raw, matched, ts) VALUES (?, ?, ?)",
                      (raw, name, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    except Exception as e:
        print(f"[Apps] WARN: 别名登记失败 {raw!r} -> {name!r}: {e}")


def fuzzy_open(query: str) -> tuple[str, str]:
    """音近层入口。返回 ("opened", 文案) / ("candidates", 文案) / ("none", "")。"""
    scored = fuzzy_match(query)
    if not scored:
        return "none", ""
    top, row = scored[0]
    gap = top - (scored[1][0] if len(scored) > 1 else 0.0)
    if top >= _HIGH and gap >= _GAP:
        ok, msg = launch(row)
        if ok:
            register_alias(row["name"], query)
            return "opened", f"{msg}（按音近匹配，你说的是「{query}」，已登记为别名）"
        return "none", msg
    if top >= _LOW:
        names = "、".join(r["name"] for _, r in scored if _ >= _LOW)
        return "candidates", (f"「{query}」没听准，列表里最接近的是：{names}。"
                              f"要打开哪一个？（音近相似度 {top:.2f}，我不替你选）")
    return "none", ""


_COLS_SEL = "SELECT name, norm, aliases, launch, args, kind, hits, last_used, py, py_tone FROM apps"
_KEYS = ("name", "norm", "aliases", "launch", "args", "kind", "hits", "last_used", "py", "py_tone")


def match(query: str) -> list[dict]:
    """按规范化后的名称匹配：拼音直达（查询是纯字母串时）→ 精确 → 唯一子串；返回候选。"""
    q = normalize(query)
    if not q:
        return []
    with _conn() as c:
        rows = [dict(zip(_KEYS, r)) for r in c.execute(_COLS_SEL).fetchall()]
    # ① 拼音直达：用户/ASR 给的是字母拼音（jishiben），与索引列完全相等才算命中
    if q.isascii():
        exact = [r for r in rows if r["py"] == q]
        if exact:
            return exact
    # ② 精确（norm / 别名）
    exact = [r for r in rows if r["norm"] == q or q in json.loads(r["aliases"] or "[]")]
    if exact:
        return exact
    # ③ 拼音前缀/包含 → 候选（交给上层判「不静默乱选」）
    if q.isascii():
        subs = [r for r in rows if q in r["py"]]
        if subs:
            return subs
    # ④ 子串
    subs = [r for r in rows if q in r["norm"] or r["norm"] in q]
    return subs


def record_hit(name: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with _conn() as c:
        c.execute("UPDATE apps SET hits = hits + 1, last_used = ? WHERE name = ?",
                  (ts, name))


def _running(target: str) -> str | None:
    """复读证据：目标 exe 是否已在进程里。返回进程名或 None。"""
    stem = os.path.splitext(os.path.basename(target))[0].lower()
    if not stem:
        return None
    ps = ("[Console]::OutputEncoding=[System.Text.Encoding]::UTF8;"
          f"Get-Process -Name '{stem}' -ErrorAction SilentlyContinue | "
          "Select-Object -First 1 -ExpandProperty Name")
    r = subprocess.run(["powershell", "-NoProfile", "-command", ps],
                       capture_output=True, text=False, timeout=15)
    out = r.stdout.decode("utf-8", errors="ignore").strip()
    return out if out else None


def launch(row: dict, timeout_s: float = 6.0) -> tuple[bool, str]:
    """按表里的 launch 启动，并**复读到进程出现**才算成功。返回 (成功, 文案)。"""
    target = row["launch"]
    args = json.loads(row["args"] or "[]")
    kind = row["kind"]
    if kind == "uri":  # ms-settings: 之类，没有对应进程，只能确认命令被接受
        try:
            os.startfile(target)
            return True, f"已打开：{row['name']}（{target}，URI 类无进程可复读）"
        except Exception as e:
            return False, f"打不开「{row['name']}」：{e}"
    exe = target if target.lower().endswith(".exe") else target + ".exe"
    try:
        subprocess.Popen([exe] + args)
    except Exception as e:
        return False, f"打不开「{row['name']}」：{e}"
    stem = os.path.splitext(os.path.basename(exe))[0].lower()
    waited = 0.0
    while waited < timeout_s:
        proc = _running(exe)
        if proc:
            record_hit(row["name"])
            return True, f"已打开：{row['name']}（从应用列表匹配，复读确认进程 {proc}）"
        time.sleep(0.5)
        waited += 0.5
    return False, (f"启动了「{row['name']}」但**复读到不了进程 {stem}**，"
                   f"不能算成功（{target}）")
