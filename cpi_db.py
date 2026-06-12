# ═══════════════════════════════════════════════════════════════════
#  cpi_db.py — محرك التخزين المزدوج للمنظومة
#  Cross-Pollination Index · د. الحبيب خروبي · ESU-001
#  يدعم: PostgreSQL (سحابي) + SQLite (محلي احتياطي)
# ═══════════════════════════════════════════════════════════════════

import sqlite3
import datetime
import json
import os


def _get_pg_conn():
    try:
        import streamlit as st
        db_url = st.secrets.get("DATABASE_URL", "")
        if not db_url:
            return None
        import psycopg2
        return psycopg2.connect(db_url, sslmode="require")
    except Exception:
        return None


def _get_sqlite_path():
    return os.path.join(os.path.expanduser("~"), ".cpi_dashboard.db")


PG_DDL = """
CREATE TABLE IF NOT EXISTS cpi_sessions (
    id              SERIAL PRIMARY KEY,
    team_name       TEXT NOT NULL DEFAULT 'فريق',
    project_name    TEXT NOT NULL DEFAULT 'مشروع',
    session_number  INTEGER NOT NULL DEFAULT 1,
    session_date    TEXT NOT NULL,
    score_eh        REAL NOT NULL,
    score_l         REAL NOT NULL,
    score_p         REAL NOT NULL,
    score_g         REAL NOT NULL,
    cpi_score_final REAL NOT NULL,
    maturity_level  TEXT,
    lang            TEXT DEFAULT 'ar',
    signatories     TEXT DEFAULT '[]',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS cpi_signatories (
    id          SERIAL PRIMARY KEY,
    session_id  INTEGER REFERENCES cpi_sessions(id) ON DELETE CASCADE,
    name        TEXT NOT NULL,
    sign_time   TEXT NOT NULL
);
"""

SQLITE_DDL = """
CREATE TABLE IF NOT EXISTS cpi_sessions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    team_name       TEXT NOT NULL DEFAULT 'فريق',
    project_name    TEXT NOT NULL DEFAULT 'مشروع',
    session_number  INTEGER NOT NULL DEFAULT 1,
    session_date    TEXT NOT NULL,
    score_eh        REAL NOT NULL,
    score_l         REAL NOT NULL,
    score_p         REAL NOT NULL,
    score_g         REAL NOT NULL,
    cpi_score_final REAL NOT NULL,
    maturity_level  TEXT,
    lang            TEXT DEFAULT 'ar',
    signatories     TEXT DEFAULT '[]',
    created_at      TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS cpi_signatories (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id  INTEGER REFERENCES cpi_sessions(id),
    name        TEXT NOT NULL,
    sign_time   TEXT NOT NULL
);
"""


def init_db():
    pg = _get_pg_conn()
    if pg:
        cur = pg.cursor()
        cur.execute(PG_DDL)
        pg.commit(); cur.close(); pg.close()
    else:
        conn = sqlite3.connect(_get_sqlite_path())
        conn.executescript(SQLITE_DDL)
        conn.commit(); conn.close()


def save_cpi_session(payload: dict, signatories: list = None) -> int:
    if signatories is None:
        signatories = []
    sigs_json = json.dumps(signatories, ensure_ascii=False)
    date_str  = payload.get("session_date", datetime.datetime.now().strftime("%Y-%m-%d"))
    lang      = payload.get("lang", "ar")

    pg = _get_pg_conn()
    if pg:
        cur = pg.cursor()
        cur.execute("""
            INSERT INTO cpi_sessions
              (team_name,project_name,session_number,session_date,
               score_eh,score_l,score_p,score_g,
               cpi_score_final,maturity_level,lang,signatories)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            RETURNING id
        """, (payload["team_name"], payload["project_name"],
              int(payload["session_number"]), date_str,
              float(payload["score_eh"]), float(payload["score_l"]),
              float(payload["score_p"]), float(payload["score_g"]),
              float(payload["cpi_score_final"]),
              payload.get("maturity_level",""), lang, sigs_json))
        sid = cur.fetchone()[0]
        for s in signatories:
            cur.execute("INSERT INTO cpi_signatories (session_id,name,sign_time) VALUES (%s,%s,%s)",
                        (sid, s.get("name",""), s.get("time","")))
        pg.commit(); cur.close(); pg.close()
        return sid
    else:
        conn = sqlite3.connect(_get_sqlite_path())
        cur  = conn.cursor()
        cur.execute("""
            INSERT INTO cpi_sessions
              (team_name,project_name,session_number,session_date,
               score_eh,score_l,score_p,score_g,
               cpi_score_final,maturity_level,lang,signatories)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """, (payload["team_name"], payload["project_name"],
              int(payload["session_number"]), date_str,
              float(payload["score_eh"]), float(payload["score_l"]),
              float(payload["score_p"]), float(payload["score_g"]),
              float(payload["cpi_score_final"]),
              payload.get("maturity_level",""), lang, sigs_json))
        sid = cur.lastrowid
        for s in signatories:
            cur.execute("INSERT INTO cpi_signatories (session_id,name,sign_time) VALUES (?,?,?)",
                        (sid, s.get("name",""), s.get("time","")))
        conn.commit(); conn.close()
        return sid


def load_historical_scores(team_name: str = None, limit: int = 200) -> list:
    pg = _get_pg_conn()
    if pg:
        cur = pg.cursor()
        if team_name:
            cur.execute("""
                SELECT id,team_name,project_name,session_number,session_date,
                       score_eh,score_l,score_p,score_g,cpi_score_final,
                       maturity_level,lang,signatories,created_at
                FROM cpi_sessions WHERE team_name=%s
                ORDER BY session_date ASC, session_number ASC LIMIT %s
            """, (team_name, limit))
        else:
            cur.execute("""
                SELECT id,team_name,project_name,session_number,session_date,
                       score_eh,score_l,score_p,score_g,cpi_score_final,
                       maturity_level,lang,signatories,created_at
                FROM cpi_sessions
                ORDER BY session_date ASC, session_number ASC LIMIT %s
            """, (limit,))
        cols = [d[0] for d in cur.description]
        rows = [dict(zip(cols, r)) for r in cur.fetchall()]
        cur.close(); pg.close()
        return rows
    else:
        conn = sqlite3.connect(_get_sqlite_path())
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        if team_name:
            cur.execute("SELECT * FROM cpi_sessions WHERE team_name=? ORDER BY session_date ASC, session_number ASC LIMIT ?", (team_name, limit))
        else:
            cur.execute("SELECT * FROM cpi_sessions ORDER BY session_date ASC, session_number ASC LIMIT ?", (limit,))
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows


def get_statistics() -> dict:
    pg = _get_pg_conn()
    if pg:
        cur = pg.cursor()
        cur.execute("""
            SELECT COUNT(*) AS total_sessions,
                   ROUND(AVG(cpi_score_final)::numeric,1) AS avg_cpi,
                   COUNT(DISTINCT team_name) AS total_teams,
                   ROUND(AVG(score_eh)::numeric,2) AS avg_eh,
                   ROUND(AVG(score_l)::numeric,2)  AS avg_l,
                   ROUND(AVG(score_p)::numeric,2)  AS avg_p,
                   ROUND(AVG(score_g)::numeric,2)  AS avg_g
            FROM cpi_sessions
        """)
        cols = [d[0] for d in cur.description]
        row  = cur.fetchone()
        stats = dict(zip(cols, row)) if row else {}
        cur.execute("""
            SELECT team_name, ROUND(AVG(cpi_score_final)::numeric,1) AS ac
            FROM cpi_sessions GROUP BY team_name ORDER BY ac DESC LIMIT 1
        """)
        top = cur.fetchone()
        stats["top_team"]     = top[0] if top else "—"
        stats["top_team_cpi"] = top[1] if top else 0
        cur.execute("SELECT cpi_score_final,session_date FROM cpi_sessions ORDER BY created_at DESC LIMIT 5")
        stats["trend_last_5"] = [{"cpi": r[0], "date": r[1]} for r in cur.fetchall()]
        cur.close(); pg.close()
    else:
        conn = sqlite3.connect(_get_sqlite_path())
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("""
            SELECT COUNT(*) AS total_sessions,
                   ROUND(AVG(cpi_score_final),1) AS avg_cpi,
                   COUNT(DISTINCT team_name) AS total_teams,
                   ROUND(AVG(score_eh),2) AS avg_eh,
                   ROUND(AVG(score_l),2)  AS avg_l,
                   ROUND(AVG(score_p),2)  AS avg_p,
                   ROUND(AVG(score_g),2)  AS avg_g
            FROM cpi_sessions
        """)
        row = cur.fetchone()
        stats = dict(row) if row else {}
        cur.execute("SELECT team_name, ROUND(AVG(cpi_score_final),1) AS ac FROM cpi_sessions GROUP BY team_name ORDER BY ac DESC LIMIT 1")
        top = cur.fetchone()
        stats["top_team"]     = top["team_name"] if top else "—"
        stats["top_team_cpi"] = top["ac"]        if top else 0
        cur.execute("SELECT cpi_score_final,session_date FROM cpi_sessions ORDER BY created_at DESC LIMIT 5")
        stats["trend_last_5"] = [{"cpi": r["cpi_score_final"], "date": r["session_date"]} for r in cur.fetchall()]
        conn.close()

    dims = {k: float(stats.get(f"avg_{k.lower()}", 0) or 0)
            for k in ["EH","L","P","G"]}
    stats["worst_dimension"] = min(dims, key=dims.get) if any(dims.values()) else "—"
    stats["dims_avg"] = dims
    return stats


def get_all_teams() -> list:
    pg = _get_pg_conn()
    if pg:
        cur = pg.cursor()
        cur.execute("SELECT DISTINCT team_name FROM cpi_sessions ORDER BY team_name")
        teams = [r[0] for r in cur.fetchall()]
        cur.close(); pg.close()
        return teams
    else:
        conn = sqlite3.connect(_get_sqlite_path())
        cur  = conn.cursor()
        cur.execute("SELECT DISTINCT team_name FROM cpi_sessions ORDER BY team_name")
        teams = [r[0] for r in cur.fetchall()]
        conn.close()
        return teams


def delete_session(session_id: int) -> bool:
    pg = _get_pg_conn()
    if pg:
        cur = pg.cursor()
        cur.execute("DELETE FROM cpi_sessions WHERE id=%s", (session_id,))
        pg.commit(); cur.close(); pg.close()
    else:
        conn = sqlite3.connect(_get_sqlite_path())
        conn.execute("DELETE FROM cpi_sessions WHERE id=?", (session_id,))
        conn.commit(); conn.close()
    return True


def delete_team_sessions(team_name: str) -> int:
    pg = _get_pg_conn()
    if pg:
        cur = pg.cursor()
        cur.execute("DELETE FROM cpi_sessions WHERE team_name=%s", (team_name,))
        count = cur.rowcount
        pg.commit(); cur.close(); pg.close()
    else:
        conn = sqlite3.connect(_get_sqlite_path())
        cur  = conn.cursor()
        cur.execute("DELETE FROM cpi_sessions WHERE team_name=?", (team_name,))
        count = cur.rowcount
        conn.commit(); conn.close()
    return count


def export_all_csv() -> str:
    sessions = load_historical_scores(limit=9999)
    if not sessions:
        return ""
    headers = ["id","team_name","project_name","session_number","session_date",
                "score_eh","score_l","score_p","score_g","cpi_score_final",
                "maturity_level","lang","created_at"]
    lines = [",".join(headers)]
    for s in sessions:
        lines.append(",".join(str(s.get(h,"")) for h in headers))
    return "\n".join(lines)


if __name__ == "__main__":
    init_db()
    print("✅ قاعدة البيانات جاهزة")
    sid = save_cpi_session({
        "team_name": "فريق الاختبار", "project_name": "جلسة اختبار",
        "session_number": 1, "session_date": "2026-06-11",
        "score_eh": 3, "score_l": 2, "score_p": 3, "score_g": 4,
        "cpi_score_final": 75.0, "maturity_level": "المستوى 4",
    })
    print(f"✅ جلسة محفوظة ID={sid}")
    print(f"✅ إحصائيات: {get_statistics()}")
