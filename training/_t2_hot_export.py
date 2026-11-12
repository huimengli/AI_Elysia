r"""hot_phrases 导出（records/2026-11-12-23-58-00.md，承接 records/2026-11-11-21-36-30.md 第 3 项）。

`hot_phrases` 的 `near_miss` 行是「真人近音误识」（爱丽安娜 / 爱丽丝 / 米希雅 / 泰利西亚 这类），
可以导出成训练与验收的负样本来源。本脚本把表按 `kind` 导出 CSV，**只读、不写库**：

- 默认读现役 `memory.db`（`config.yaml memory.db_path`），写 `.tmp/hot_phrases_<时间戳>.csv`；
- `DB=<路径>` 指定别的库（临时库跑判据，不污染现役库）；`KIND=near_miss` 只导某类；
- 列固定 `kind,text,count,first_seen,last_seen`，按 `count` 降序。

Run:  .venv\Scripts\python.exe training\_t2_hot_export.py
      .venv\Scripts\python.exe training\_t2_hot_export.py  # DB=... KIND=near_miss 见上
"""
import csv
import os
import sys
import time

ROOT = r"C:\Users\楼听\Desktop\git\JarvisAi"
sys.path.insert(0, ROOT)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DB = os.environ.get("DB", "")
KIND = os.environ.get("KIND", "")
OUT = os.path.join(ROOT, ".tmp", f"hot_phrases_{time.strftime('%Y-%m-%d-%H-%M-%S')}.csv")


def main() -> int:
    from sqlalchemy import create_engine, text

    if DB:
        db = DB
    else:
        import yaml
        raw = yaml.safe_load(open(os.path.join(ROOT, "config.yaml"), encoding="utf-8"))["memory"]["db_path"]
        db = raw if os.path.isabs(raw) else os.path.join(ROOT, raw)
    eng = create_engine(f"sqlite:///{db}")
    with eng.connect() as conn:
        if KIND:
            rows = conn.execute(text(
                "SELECT kind, text, count, first_seen, last_seen FROM hot_phrases "
                "WHERE kind = :k ORDER BY count DESC, last_seen DESC"
            ), {"k": KIND}).fetchall()
        else:
            rows = conn.execute(text(
                "SELECT kind, text, count, first_seen, last_seen FROM hot_phrases "
                "ORDER BY count DESC, last_seen DESC"
            )).fetchall()
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["kind", "text", "count", "first_seen", "last_seen"])
        w.writerows(rows)
    kinds = {}
    for r in rows:
        kinds[r[0]] = kinds.get(r[0], 0) + 1
    print(f"[导出] 库 {db} → {OUT}，共 {len(rows)} 行，kind 分布 {kinds}", flush=True)
    print(f"[近音] near_miss 前 10：{[r[1] for r in rows if r[0] == 'near_miss'][:10]}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
