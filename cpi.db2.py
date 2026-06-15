# ═══════════════════════════════════════════════════════════════════
# cpi_db.py --- محرك التخزين المزدوج للمنظومة
# Cross-Pollination Index · د. الحبيب خروبي · ESU-001
# يدعم: PostgreSQL (سحابي) + SQLite (محلي احتياطي)
# ═══════════════════════════════════════════════════════════════════

import sqlite3
import datetime
import json
import os

# ────────────────────────────────────────────────────────────────────
# الاتصال بقاعدة البيانات (PostgreSQL عبر st.secrets أو SQLite محلي)
# ────────────────────────────────────────────────────────────────────

def _get_pg_conn():
    """
    محاولة الاتصال بقاعدة البيانات PostgreSQL من خلال st.secrets.
    تدعم طريقتين:
    1. DATABASE_URL الكامل (الأفضل والمُوصى به)
    2. تفاصيل منفصلة (DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME) كخيار احتياطي
    """
    try:
        import streamlit as st
        import psycopg2
        
        # ✅ الطريقة الأولى: استخدام DATABASE_URL كاملاً (الأفضل)
        db_url = st.secrets.get("DATABASE_URL", "")
        if db_url:
            return psycopg2.connect(db_url, sslmode="require")
        
        # ✅ الطريقة الثانية: تفاصيل منفصلة (خيار احتياطي للمستخدمين المتقدمين)
        db_user = st.secrets.get("DB_USER", "")
        db_password = st.secrets.get("DB_PASSWORD", "")
        db_host = st.secrets.get("DB_HOST", "")
        db_port = st.secrets.get("DB_PORT", "5432")
        db_name = st.secrets.get("DB_NAME", "postgres")
        
        if db_user and db_password and db_host:
            conn_str = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
            return psycopg2.connect(conn_str, sslmode="require")
            
    except Exception:
        # لا نطبع الخطأ هنا، فقط نرجع None ليتحول إلى SQLite تلقائياً
        pass
    
    return None


def _get_sqlite_path():
    """مسار ملف قاعدة البيانات المحلية (SQLite)"""
    return os.path.join(os.path.expanduser("~"), ".cpi_dashboard.db")


# ────────────────────────────────────────────────────────────────────
# هيكل الجداول (DDL) لكل من PostgreSQL و SQLite
# ────────────────────────────────────────────────────────────────────

PG_DDL = """
CREATE TABLE IF NOT EXISTS cpi_sessions (
    id SERIAL PRIMARY KEY,
    team_name TEXT NOT NULL DEFAULT 'فريق',
    project_name TEXT NOT NULL DEFAULT 'مشروع',
    session_number INTEGER NOT NULL DEFAULT 1,
    session_date TEXT NOT NULL,
    score_eh REAL NOT NULL,
    score_l REAL NOT NULL,
    score_p REAL NOT NULL,
    score_g REAL NOT NULL,
    cpi_score_final REAL NOT NULL,
    alignment_index REAL,
    std_deviation REAL,
    participant_count INTEGER DEFAULT 1,
    maturity_level TEXT,
    lang TEXT DEFAULT 'ar',
    signatories TEXT DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cpi_signatories (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES cpi_sessions(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    sign_time TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS cpi_participants (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES cpi_sessions(id) ON DELETE CASCADE,
    member_name TEXT NOT NULL,
    specialization TEXT,
    role TEXT,
    score_eh REAL NOT NULL,
    score_l REAL NOT NULL,
    score_p REAL NOT NULL,
    score_g REAL NOT NULL,
    individual_cpi REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

SQLITE_DDL = """
CREATE TABLE IF NOT EXISTS cpi_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_name TEXT NOT NULL DEFAULT 'فريق',
    project_name TEXT NOT NULL DEFAULT 'مشروع',
    session_number INTEGER NOT NULL DEFAULT 1,
    session_date TEXT NOT NULL,
    score_eh REAL NOT NULL,
    score_l REAL NOT NULL,
    score_p REAL NOT NULL,
    score_g REAL NOT NULL,
    cpi_score_final REAL NOT NULL,
    alignment_index REAL,
    std_deviation REAL,
    participant_count INTEGER DEFAULT 1,
    maturity_level TEXT,
    lang TEXT DEFAULT 'ar',
    signatories TEXT DEFAULT '[]',
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS cpi_signatories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER REFERENCES cpi_sessions(id),
    name TEXT NOT NULL,
    sign_time TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS cpi_participants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER REFERENCES cpi_sessions(id),
    member_name TEXT NOT NULL,
    specialization TEXT,
    role TEXT,
    score_eh REAL NOT NULL,
    score_l REAL NOT NULL,
    score_p REAL NOT NULL,
    score_g REAL NOT NULL,
    individual_cpi REAL NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
);
"""

# أعمدة جديدة للإصدار v7 (تُضاف تلقائياً عند الترحيل)
_NEW_COLUMNS = [
    ("alignment_index", "REAL"),
    ("std_deviation", "REAL"),
    ("participant_count", "INTEGER DEFAULT 1"),
]


def _migrate_columns_pg(conn, cur):
    """ترحيل أعمدة v7 لـ PostgreSQL باستخدام IF NOT EXISTS (PG 9.6+)"""
    for col_name, col_type in _NEW_COLUMNS:
        try:
            cur.execute(f"ALTER TABLE cpi_sessions ADD COLUMN IF NOT EXISTS {col_name} {col_type}")
            conn.commit()
        except Exception:
            conn.rollback()


def _migrate_columns_sqlite(conn, cur):
    """ترحيل أعمدة v7 لـ SQLite بالتحقق من وجود الأعمدة أولاً"""
    cur.execute("PRAGMA table_info(cpi_sessions)")
    existing = {row[1] for row in cur.fetchall()}
    for col_name, col_type in _NEW_COLUMNS:
        if col_name not in existing:
            try:
                cur.execute(f"ALTER TABLE cpi_sessions ADD COLUMN {col_name} {col_type}")
                conn.commit()
            except Exception:
                pass


def init_db():
    """إنشاء الجداول وترحيل الأعمدة الجديدة إن لزم الأمر"""
    pg = _get_pg_conn()
    if pg:
        cur = pg.cursor()
        cur.execute(PG_DDL)
        pg.commit()
        _migrate_columns_pg(pg, cur)
        cur.close()
        pg.close()
    else:
        conn = sqlite3.connect(_get_sqlite_path())
        conn.executescript(SQLITE_DDL)
        conn.commit()
        cur = conn.cursor()
        _migrate_columns_sqlite(conn, cur)
        conn.close()


def save_cpi_session(payload: dict, signatories: list = None, participants: list = None) -> int:
    """
    حفظ جلسة CPI كاملة مع الموقعين والمشاركين.

    payload يجب أن يحتوي:
        team_name, project_name, session_number, session_date,
        score_eh, score_l, score_p, score_g, cpi_score_final,
        alignment_index (اختياري), std_deviation (اختياري),
        participant_count (اختياري), maturity_level (اختياري), lang (اختياري)

    signatories: قائمة الموقعين على الميثاق [{"name": "", "time": ""}]
    participants: قائمة المشاركين (لنمط PMP)
    """
    if signatories is None:
        signatories = []
    if participants is None:
        participants = []

    sigs_json = json.dumps(signatories, ensure_ascii=False)
    date_str = payload.get("session_date", datetime.datetime.now().strftime("%Y-%m-%d"))
    lang = payload.get("lang", "ar")
    align_idx = payload.get("alignment_index")
    std_dev = payload.get("std_deviation")
    p_count = payload.get("participant_count", 1)

    pg = _get_pg_conn()
    if pg:
        cur = pg.cursor()
        cur.execute("""
            INSERT INTO cpi_sessions
            (team_name, project_name, session_number, session_date,
             score_eh, score_l, score_p, score_g,
             cpi_score_final, alignment_index, std_deviation, participant_count,
             maturity_level, lang, signatories)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            payload["team_name"], payload["project_name"],
            int(payload["session_number"]), date_str,
            float(payload["score_eh"]), float(payload["score_l"]),
            float(payload["score_p"]), float(payload["score_g"]),
            float(payload["cpi_score_final"]),
            align_idx, std_dev, int(p_count),
            payload.get("maturity_level", ""), lang, sigs_json
        ))
        session_id = cur.fetchone()[0]

        for s in signatories:
            cur.execute("INSERT INTO cpi_signatories (session_id, name, sign_time) VALUES (%s, %s, %s)",
                        (session_id, s.get("name", ""), s.get("time", "")))
        pg.commit()
        cur.close()
        pg.close()
    else:
        conn = sqlite3.connect(_get_sqlite_path())
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO cpi_sessions
            (team_name, project_name, session_number, session_date,
             score_eh, score_l, score_p, score_g,
             cpi_score_final, alignment_index, std_deviation, participant_count,
             maturity_level, lang, signatories)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            payload["team_name"], payload["project_name"],
            int(payload["session_number"]), date_str,
            float(payload["score_eh"]), float(payload["score_l"]),
            float(payload["score_p"]), float(payload["score_g"]),
            float(payload["cpi_score_final"]),
            align_idx, std_dev, int(p_count),
            payload.get("maturity_level", ""), lang, sigs_json
        ))
        session_id = cur.lastrowid

        for s in signatories:
            cur.execute("INSERT INTO cpi_signatories (session_id, name, sign_time) VALUES (?, ?, ?)",
                        (session_id, s.get("name", ""), s.get("time", "")))
        conn.commit()
        conn.close()

    # حفظ المشاركين إن وُجدوا (لنمط PMP)
    if participants:
        save_participants(session_id, participants)

    return session_id


def save_participants(session_id: int, participants: list) -> int:
    """حفظ قائمة المشاركين المرتبطين بجلسة (لنمط PMP)"""
    pg = _get_pg_conn()
    if pg:
        cur = pg.cursor()
        for p in participants:
            sc = p.get("scores", {})
            cur.execute("""
                INSERT INTO cpi_participants
                (session_id, member_name, specialization, role,
                 score_eh, score_l, score_p, score_g, individual_cpi)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                session_id, p.get("name", ""), p.get("specialization", ""), p.get("role", ""),
                float(sc.get("EH", 0)), float(sc.get("L", 0)),
                float(sc.get("P", 0)), float(sc.get("G", 0)),
                float(p.get("individual_cpi", 0))
            ))
        pg.commit()
        cur.close()
        pg.close()
    else:
        conn = sqlite3.connect(_get_sqlite_path())
        cur = conn.cursor()
        for p in participants:
            sc = p.get("scores", {})
            cur.execute("""
                INSERT INTO cpi_participants
                (session_id, member_name, specialization, role,
                 score_eh, score_l, score_p, score_g, individual_cpi)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id, p.get("name", ""), p.get("specialization", ""), p.get("role", ""),
                float(sc.get("EH", 0)), float(sc.get("L", 0)),
                float(sc.get("P", 0)), float(sc.get("G", 0)),
                float(p.get("individual_cpi", 0))
            ))
        conn.commit()
        conn.close()
    return len(participants)


def load_historical_scores(team_name: str = None, limit: int = 200) -> list:
    """استرجاع الجلسات التاريخية من قاعدة البيانات"""
    pg = _get_pg_conn()
    if pg:
        cur = pg.cursor()
        if team_name:
            cur.execute("""
                SELECT id, team_name, project_name, session_number, session_date,
                       score_eh, score_l, score_p, score_g, cpi_score_final,
                       alignment_index, std_deviation, participant_count,
                       maturity_level, lang, signatories, created_at
                FROM cpi_sessions WHERE team_name=%s
                ORDER BY session_date ASC, session_number ASC LIMIT %s
            """, (team_name, limit))
        else:
            cur.execute("""
                SELECT id, team_name, project_name, session_number, session_date,
                       score_eh, score_l, score_p, score_g, cpi_score_final,
                       alignment_index, std_deviation, participant_count,
                       maturity_level, lang, signatories, created_at
                FROM cpi_sessions
                ORDER BY session_date ASC, session_number ASC LIMIT %s
            """, (limit,))
        cols = [d[0] for d in cur.description]
        rows = [dict(zip(cols, r)) for r in cur.fetchall()]
        cur.close()
        pg.close()
        return rows
    else:
        conn = sqlite3.connect(_get_sqlite_path())
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        if team_name:
            cur.execute("""
                SELECT * FROM cpi_sessions WHERE team_name=?
                ORDER BY session_date ASC, session_number ASC LIMIT ?
            """, (team_name, limit))
        else:
            cur.execute("""
                SELECT * FROM cpi_sessions
                ORDER BY session_date ASC, session_number ASC LIMIT ?
            """, (limit,))
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows


def load_session_participants(session_id: int) -> list:
    """استرجاع كل المشاركين المرتبطين بجلسة معينة"""
    pg = _get_pg_conn()
    if pg:
        cur = pg.cursor()
        cur.execute("""
            SELECT id, session_id, member_name, specialization, role,
                   score_eh, score_l, score_p, score_g, individual_cpi, created_at
            FROM cpi_participants WHERE session_id=%s ORDER BY id ASC
        """, (session_id,))
        cols = [d[0] for d in cur.description]
        rows = [dict(zip(cols, r)) for r in cur.fetchall()]
        cur.close()
        pg.close()
        return rows
    else:
        conn = sqlite3.connect(_get_sqlite_path())
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM cpi_participants WHERE session_id=? ORDER BY id ASC", (session_id,))
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows


def get_alignment_stats(session_id: int) -> dict:
    """استرجاع مؤشرات الانسجام الإدراكي (CAI) لجلسة معينة + بيانات المشاركين"""
    pg = _get_pg_conn()
    if pg:
        cur = pg.cursor()
        cur.execute("""
            SELECT cpi_score_final, alignment_index, std_deviation, participant_count
            FROM cpi_sessions WHERE id=%s
        """, (session_id,))
        row = cur.fetchone()
        cur.close()
        pg.close()
    else:
        conn = sqlite3.connect(_get_sqlite_path())
        cur = conn.cursor()
        cur.execute("""
            SELECT cpi_score_final, alignment_index, std_deviation, participant_count
            FROM cpi_sessions WHERE id=?
        """, (session_id,))
        row = cur.fetchone()
        conn.close()

    if not row:
        return {}

    participants = load_session_participants(session_id)
    return {
        "collective_cpi": row[0],
        "alignment_index": row[1],
        "std_deviation": row[2],
        "participant_count": row[3],
        "participants": participants,
    }


def get_statistics() -> dict:
    """إحصائيات عامة للمنصة"""
    pg = _get_pg_conn()
    if pg:
        cur = pg.cursor()
        cur.execute("""
            SELECT COUNT(*) AS total_sessions,
                   ROUND(AVG(cpi_score_final)::numeric,1) AS avg_cpi,
                   COUNT(DISTINCT team_name) AS total_teams,
                   ROUND(AVG(score_eh)::numeric,2) AS avg_eh,
                   ROUND(AVG(score_l)::numeric,2) AS avg_l,
                   ROUND(AVG(score_p)::numeric,2) AS avg_p,
                   ROUND(AVG(score_g)::numeric,2) AS avg_g
            FROM cpi_sessions
        """)
        cols = [d[0] for d in cur.description]
        row = cur.fetchone()
        stats = dict(zip(cols, row)) if row else {}

        cur.execute("""
            SELECT team_name, ROUND(AVG(cpi_score_final)::numeric,1) AS ac
            FROM cpi_sessions GROUP BY team_name ORDER BY ac DESC LIMIT 1
        """)
        top = cur.fetchone()
        stats["top_team"] = top[0] if top else "---"
        stats["top_team_cpi"] = top[1] if top else 0

        cur.execute("SELECT cpi_score_final, session_date FROM cpi_sessions ORDER BY created_at DESC LIMIT 5")
        stats["trend_last_5"] = [{"cpi": r[0], "date": r[1]} for r in cur.fetchall()]

        cur.close()
        pg.close()
    else:
        conn = sqlite3.connect(_get_sqlite_path())
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("""
            SELECT COUNT(*) AS total_sessions,
                   ROUND(AVG(cpi_score_final),1) AS avg_cpi,
                   COUNT(DISTINCT team_name) AS total_teams,
                   ROUND(AVG(score_eh),2) AS avg_eh,
                   ROUND(AVG(score_l),2) AS avg_l,
                   ROUND(AVG(score_p),2) AS avg_p,
                   ROUND(AVG(score_g),2) AS avg_g
            FROM cpi_sessions
        """)
        row = cur.fetchone()
        stats = dict(row) if row else {}

        cur.execute("""
            SELECT team_name, ROUND(AVG(cpi_score_final),1) AS ac
            FROM cpi_sessions GROUP BY team_name ORDER BY ac DESC LIMIT 1
        """)
        top = cur.fetchone()
        stats["top_team"] = top["team_name"] if top else "---"
        stats["top_team_cpi"] = top["ac"] if top else 0

        cur.execute("SELECT cpi_score_final, session_date FROM cpi_sessions ORDER BY created_at DESC LIMIT 5")
        stats["trend_last_5"] = [{"cpi": r["cpi_score_final"], "date": r["session_date"]} for r in cur.fetchall()]

        conn.close()

    dims = {k: float(stats.get(f"avg_{k.lower()}", 0) or 0) for k in ["EH", "L", "P", "G"]}
    stats["worst_dimension"] = min(dims, key=dims.get) if any(dims.values()) else "---"
    stats["dims_avg"] = dims
    return stats


def get_all_teams() -> list:
    """قائمة جميع الفرق المسجلة"""
    pg = _get_pg_conn()
    if pg:
        cur = pg.cursor()
        cur.execute("SELECT DISTINCT team_name FROM cpi_sessions ORDER BY team_name")
        teams = [r[0] for r in cur.fetchall()]
        cur.close()
        pg.close()
        return teams
    else:
        conn = sqlite3.connect(_get_sqlite_path())
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT team_name FROM cpi_sessions ORDER BY team_name")
        teams = [r[0] for r in cur.fetchall()]
        conn.close()
        return teams


def delete_session(session_id: int) -> bool:
    """حذف جلسة معينة"""
    pg = _get_pg_conn()
    if pg:
        cur = pg.cursor()
        cur.execute("DELETE FROM cpi_sessions WHERE id=%s", (session_id,))
        pg.commit()
        cur.close()
        pg.close()
    else:
        conn = sqlite3.connect(_get_sqlite_path())
        conn.execute("DELETE FROM cpi_sessions WHERE id=?", (session_id,))
        conn.commit()
        conn.close()
    return True


def delete_team_sessions(team_name: str) -> int:
    """حذف جميع جلسات فريق معين"""
    pg = _get_pg_conn()
    if pg:
        cur = pg.cursor()
        cur.execute("DELETE FROM cpi_sessions WHERE team_name=%s", (team_name,))
        count = cur.rowcount
        pg.commit()
        cur.close()
        pg.close()
    else:
        conn = sqlite3.connect(_get_sqlite_path())
        cur = conn.cursor()
        cur.execute("DELETE FROM cpi_sessions WHERE team_name=?", (team_name,))
        count = cur.rowcount
        conn.commit()
        conn.close()
    return count


def export_all_csv() -> str:
    """تصدير جميع الجلسات بصيغة CSV"""
    sessions = load_historical_scores(limit=9999)
    if not sessions:
        return ""
    headers = [
        "id", "team_name", "project_name", "session_number", "session_date",
        "score_eh", "score_l", "score_p", "score_g", "cpi_score_final",
        "maturity_level", "lang", "created_at"
    ]
    lines = [",".join(headers)]
    for s in sessions:
        lines.append(",".join(str(s.get(h, "")) for h in headers))
    return "\n".join(lines)


# ────────────────────────────────────────────────────────────────────
# PMP --- Participatory Measurement Protocol (CPI v7.0)
# حسابات القياس التشاركي: CPI الفردي/الجماعي + مؤشر الانسجام CAI
# ────────────────────────────────────────────────────────────────────

DIM_KEYS_ORDER = ["EH", "L", "P", "G"]


def calculate_collective_stats(participants_scores: list) -> dict:
    """
    حساب الإحصائيات الجماعية من تقييمات المشاركين.

    Args:
        participants_scores: قائمة من dicts، كل عنصر {"EH":x, "L":x, "P":x, "G":x}
                             (قيم 1-4 لكل بُعد)

    Returns:
        dict: {
            "collective_cpi": float,
            "std_deviation": float,
            "alignment_index": float,
            "individual_cpis": list,
            "gap_by_dimension": dict,
        }
    """
    if not participants_scores:
        return {
            "collective_cpi": 0.0, "std_deviation": 0.0, "alignment_index": 100.0,
            "individual_cpis": [], "gap_by_dimension": {k: 0.0 for k in DIM_KEYS_ORDER},
        }

    individual_cpis = []
    for p in participants_scores:
        total = sum(float(p.get(k, 0)) for k in DIM_KEYS_ORDER)
        individual_cpis.append(round(total / 16 * 100, 2))

    n = len(individual_cpis)
    collective_cpi = sum(individual_cpis) / n

    if n > 1:
        variance = sum((x - collective_cpi) ** 2 for x in individual_cpis) / n
        std_dev = variance ** 0.5
    else:
        std_dev = 0.0

    # CAI = (1 - std/25) * 100 --- σ_max = 25 (أقصى تشتت ممكن)
    alignment_index = max(0.0, (1 - std_dev / 25)) * 100

    # الفجوة لكل بُعد على حدة
    gap_by_dimension = {}
    for k in DIM_KEYS_ORDER:
        vals = [float(p.get(k, 0)) for p in participants_scores]
        m = sum(vals) / len(vals)
        if len(vals) > 1:
            v = sum((x - m) ** 2 for x in vals) / len(vals)
            gap_by_dimension[k] = round(v ** 0.5, 2)
        else:
            gap_by_dimension[k] = 0.0

    return {
        "collective_cpi": round(collective_cpi, 1),
        "std_deviation": round(std_dev, 2),
        "alignment_index": round(alignment_index, 1),
        "individual_cpis": individual_cpis,
        "gap_by_dimension": gap_by_dimension,
    }


def cai_interpretation(cai: float, lang: str = "ar") -> dict:
    """تفسير مؤشر الانسجام الإدراكي CAI حسب النطاق"""
    bands = {
        "ar": [
            (75, 101, "انسجام إدراكي عالٍ", "الفريق يرى الواقع بشكل متقارب — استمرارية وتوثيق", "#059669"),
            (50, 75, "فجوة إدراكية ملحوظة", "تدخل فوري — خطر على التلاقح المعرفي — راجع اللغة المشتركة والتوجيه", "#D97706"),
            (0, 50, "انقسام إدراكي حاد", "جلسة طارئة — إعادة تعريف الرؤية المشتركة", "#DC2626"),
        ],
        "en": [
            (75, 101, "High Cognitive Alignment", "The team perceives reality similarly — maintain and document practices", "#059669"),
            (50, 75, "Notable Perception Gap", "Immediate intervention required — review shared language and guidance", "#D97706"),
            (0, 50, "Severe Cognitive Divide", "Emergency session — completely redefine shared vision", "#DC2626"),
        ],
        "fr": [
            (75, 101, "Alignement cognitif élevé", "L'équipe perçoit la réalité de façon similaire — continuité", "#059669"),
            (50, 75, "Écart de perception notable", "Intervention immédiate requise — revoir le langage commun", "#D97706"),
            (0, 50, "Division cognitive sévère", "Session d'urgence — redéfinir la vision partagée", "#DC2626"),
        ],
    }
    for lo, hi, title, desc, color in bands.get(lang, bands["ar"]):
        if lo <= cai < hi:
            return {"title": title, "desc": desc, "color": color}
    return {"title": "---", "desc": "---", "color": "#94A3B8"}


def discussion_prompt(cai: float, lang: str = "ar") -> str:
    """السؤال المحفز للنقاش بناءً على مستوى CAI"""
    prompts = {
        "ar": {
            "low": "ما الذي يسبب هذا الاختلاف الجوهري في رؤيتنا لواقع الفريق؟",
            "mid": "أين تتركز أكبر الفجوات؟ هل هي في بُعد معين (مثل اللغة أو التواضع)؟",
            "high": "ما الذي ساعدنا على تحقيق هذا الانسجام؟ كيف نستفيد منه في الأبعاد الأخرى؟",
        },
        "en": {
            "low": "What is causing this fundamental difference in how we see the team's reality?",
            "mid": "Where are the biggest gaps concentrated? Is it a specific dimension (e.g. Language or Humility)?",
            "high": "What helped us achieve this alignment? How can we leverage it in other dimensions?",
        },
        "fr": {
            "low": "Qu'est-ce qui cause cette différence fondamentale dans notre perception de la réalité de l'équipe ?",
            "mid": "Où se concentrent les plus grands écarts ? Est-ce une dimension spécifique (Langage, Humilité) ?",
            "high": "Qu'est-ce qui nous a aidés à atteindre cet alignement ? Comment l'exploiter dans d'autres dimensions ?",
        },
    }
    if cai < 50:
        return prompts[lang]["low"]
    elif cai < 75:
        return prompts[lang]["mid"]
    else:
        return prompts[lang]["high"]


# ────────────────────────────────────────────────────────────────────
# اختبار سريع عند تشغيل الملف مباشرة
# ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    print("✅ قاعدة البيانات جاهزة (مع مخطط v7)")

    # اختبار PMP
    participants = [
        {"name": "أحمد", "specialization": "طب الأسنان", "role": "خبير سريري",
         "scores": {"EH": 3, "L": 2, "P": 4, "G": 3}},
        {"name": "سارة", "specialization": "هندسة برمجيات", "role": "مطور خوارزميات",
         "scores": {"EH": 2, "L": 1, "P": 3, "G": 2}},
    ]
    stats = calculate_collective_stats([p["scores"] for p in participants])
    print(f"✅ Collective stats: {stats}")

    for p, cpi in zip(participants, stats["individual_cpis"]):
        p["individual_cpi"] = cpi

    sid = save_cpi_session({
        "team_name": "فريق الاختبار",
        "project_name": "جلسة PMP اختبار",
        "session_number": 1,
        "session_date": "2026-06-15",
        "score_eh": 2.5,
        "score_l": 1.5,
        "score_p": 3.5,
        "score_g": 2.5,
        "cpi_score_final": stats["collective_cpi"],
        "alignment_index": stats["alignment_index"],
        "std_deviation": stats["std_deviation"],
        "participant_count": len(participants),
        "maturity_level": "المستوى 3",
    }, participants=participants)
    print(f"✅ جلسة PMP محفوظة ID={sid}")
    print(f"✅ CAI interpretation: {cai_interpretation(stats['alignment_index'])}")
