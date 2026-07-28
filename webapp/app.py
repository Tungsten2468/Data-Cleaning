"""
Data Explorer — web UI wrapper around the terminal query interface.

Reuses the same capabilities as queryInterface/ (choose a table, pick columns,
view rows, run calculations, filter by category / numeric range, export CSV) but
serves them through a polished single-page dashboard instead of stdin prompts.

Run:  python3 webapp/app.py   then open http://127.0.0.1:5000
"""

import io
import csv
import os
import sqlite3

from flask import Flask, jsonify, request, render_template, Response

# ---------------------------------------------------------------------------
# Database location
#
# The original terminal app connected to "syn_output_data/final_reports.db".
# That data folder was git-ignored, so the .db now lives at the repo root.
# We resolve it relative to this file and fall back to a few sensible spots so
# the app keeps working no matter where it's launched from.
# ---------------------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(HERE)

_DB_CANDIDATES = [
    os.environ.get("REPORTS_DB", ""),
    os.path.join(REPO_ROOT, "final_reports.db"),
    os.path.join(REPO_ROOT, "syn_output_data", "final_reports.db"),
    os.path.join(HERE, "final_reports.db"),
]
DB_PATH = next((p for p in _DB_CANDIDATES if p and os.path.exists(p)), None)
if DB_PATH is None:
    raise FileNotFoundError(
        "Could not find final_reports.db. Set the REPORTS_DB env var to its path."
    )

app = Flask(__name__)


def get_conn():
    return sqlite3.connect(DB_PATH)


# ---------------------------------------------------------------------------
# Schema helpers (mirror helpfulFunctions.getTables / getColumns / checkDataType)
# ---------------------------------------------------------------------------
def get_tables(conn):
    rows = conn.execute(
        "SELECT name FROM sqlite_master "
        "WHERE type='table' AND name NOT LIKE 'sqlite_%';"
    ).fetchall()
    return [r[0] for r in rows]


def get_columns(conn, table):
    rows = conn.execute(f'PRAGMA table_info("{table}");').fetchall()
    return [r[1] for r in rows]


def column_is_numeric(conn, table, column):
    """Numeric unless the first non-null value is a string (matches checkDataType)."""
    row = conn.execute(
        f'SELECT "{column}" FROM "{table}" WHERE "{column}" IS NOT NULL LIMIT 1'
    ).fetchone()
    if not row:
        return True
    return not isinstance(row[0], str)


def column_meta(conn, table):
    cols = get_columns(conn, table)
    meta = []
    for c in cols:
        numeric = column_is_numeric(conn, table, c)
        meta.append({"name": c, "type": "numerical" if numeric else "categorical"})
    return meta


def safe_columns(conn, table, requested):
    """Whitelist requested column names against the real schema (prevents injection)."""
    valid = set(get_columns(conn, table))
    return [c for c in requested if c in valid]


def valid_table(conn, table):
    return table in get_tables(conn)


# ---------------------------------------------------------------------------
# Filter -> SQL WHERE builder. Values are always parameterized.
# ---------------------------------------------------------------------------
def build_where(conn, table, filters):
    clauses, params = [], []
    for f in filters or []:
        col = f.get("column")
        if col not in get_columns(conn, table):
            continue
        ftype = f.get("type")
        if ftype == "category":
            clauses.append(f'"{col}" = ?')
            params.append(f.get("value"))
        elif ftype == "range":
            # original used strict >/< bounds
            start, end = f.get("start"), f.get("end")
            if start is not None:
                clauses.append(f'"{col}" > ?')
                params.append(float(start))
            if end is not None:
                clauses.append(f'"{col}" < ?')
                params.append(float(end))
    where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
    return where, params


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/tables")
def api_tables():
    with get_conn() as conn:
        tables = get_tables(conn)
        out = []
        for t in tables:
            n = conn.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
            out.append({"name": t, "rows": n})
        return jsonify({"db": os.path.basename(DB_PATH), "tables": out})


@app.route("/api/columns")
def api_columns():
    table = request.args.get("table", "")
    with get_conn() as conn:
        if not valid_table(conn, table):
            return jsonify({"error": "unknown table"}), 400
        rows = conn.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
        return jsonify({"table": table, "rows": rows, "columns": column_meta(conn, table)})


@app.route("/api/query", methods=["POST"])
def api_query():
    body = request.get_json(force=True)
    table = body.get("table", "")
    limit = int(body.get("limit") or 0)
    filters = body.get("filters", [])

    with get_conn() as conn:
        if not valid_table(conn, table):
            return jsonify({"error": "unknown table"}), 400
        cols = safe_columns(conn, table, body.get("columns", []))
        if not cols:
            cols = get_columns(conn, table)

        col_sql = ", ".join(f'"{c}"' for c in cols)
        where, params = build_where(conn, table, filters)

        count = conn.execute(
            f'SELECT COUNT(*) FROM "{table}"{where}', params
        ).fetchone()[0]

        sql = f'SELECT {col_sql} FROM "{table}"{where}'
        if limit and limit > 0:
            sql += f" LIMIT {limit}"
        rows = conn.execute(sql, params).fetchall()

        return jsonify(
            {
                "columns": cols,
                "rows": [list(r) for r in rows],
                "returned": len(rows),
                "matched": count,
                "limited": bool(limit and limit > 0),
            }
        )


@app.route("/api/calculate", methods=["POST"])
def api_calculate():
    body = request.get_json(force=True)
    table = body.get("table", "")
    column = body.get("column", "")
    op = (body.get("op") or "").upper()          # T,H,L,A,M  or COUNT (categorical)
    value = body.get("value")                    # for categorical COUNT
    filters = body.get("filters", [])

    with get_conn() as conn:
        if not valid_table(conn, table):
            return jsonify({"error": "unknown table"}), 400
        if column not in get_columns(conn, table):
            return jsonify({"error": "unknown column"}), 400

        where, params = build_where(conn, table, filters)
        numeric = column_is_numeric(conn, table, column)

        if not numeric or op == "COUNT":
            # count occurrences of a specific categorical value
            extra = " AND " if where else " WHERE "
            sql = f'SELECT COUNT(*) FROM "{table}"{where}{extra}"{column}" = ?'
            res = conn.execute(sql, params + [value]).fetchone()[0]
            return jsonify({"op": "COUNT", "column": column, "value": value, "result": res})

        agg = {"T": "SUM", "H": "MAX", "L": "MIN", "A": "AVG"}
        label = {"T": "Total", "H": "Highest", "L": "Lowest", "A": "Average", "M": "Median"}
        if op == "M":
            vals = [
                r[0]
                for r in conn.execute(
                    f'SELECT "{column}" FROM "{table}"{where} ORDER BY "{column}"', params
                ).fetchall()
                if r[0] is not None
            ]
            if not vals:
                return jsonify({"error": "no data"}), 400
            n = len(vals)
            mid = n // 2
            result = vals[mid] if n % 2 else (vals[mid - 1] + vals[mid]) / 2
        elif op in agg:
            result = conn.execute(
                f'SELECT {agg[op]}("{column}") FROM "{table}"{where}', params
            ).fetchone()[0]
        else:
            return jsonify({"error": "unknown op"}), 400

        return jsonify({"op": label.get(op, op), "column": column, "result": result})


@app.route("/api/values")
def api_values():
    """Distinct values for a categorical column (for filter dropdowns)."""
    table = request.args.get("table", "")
    column = request.args.get("column", "")
    with get_conn() as conn:
        if not valid_table(conn, table) or column not in get_columns(conn, table):
            return jsonify({"error": "bad request"}), 400
        rows = conn.execute(
            f'SELECT DISTINCT "{column}" FROM "{table}" '
            f'WHERE "{column}" IS NOT NULL ORDER BY "{column}"'
        ).fetchall()
        return jsonify({"values": [r[0] for r in rows]})


@app.route("/api/bounds")
def api_bounds():
    """Min/max for a numeric column (for range filter hints)."""
    table = request.args.get("table", "")
    column = request.args.get("column", "")
    with get_conn() as conn:
        if not valid_table(conn, table) or column not in get_columns(conn, table):
            return jsonify({"error": "bad request"}), 400
        mn, mx = conn.execute(
            f'SELECT MIN("{column}"), MAX("{column}") FROM "{table}"'
        ).fetchone()
        return jsonify({"min": mn, "max": mx})


@app.route("/api/distribution")
def api_distribution():
    """Grouped counts for a column — powers the demo chart.

    Categorical -> count per value. Numeric -> counts bucketed into bins.
    """
    table = request.args.get("table", "")
    column = request.args.get("column", "")
    with get_conn() as conn:
        if not valid_table(conn, table) or column not in get_columns(conn, table):
            return jsonify({"error": "bad request"}), 400

        if column_is_numeric(conn, table, column):
            mn, mx = conn.execute(
                f'SELECT MIN("{column}"), MAX("{column}") FROM "{table}"'
            ).fetchone()
            if mn is None:
                return jsonify({"labels": [], "counts": [], "kind": "numeric"})
            # small integer range -> exact buckets, else 10 bins
            distinct = conn.execute(
                f'SELECT COUNT(DISTINCT "{column}") FROM "{table}"'
            ).fetchone()[0]
            if distinct <= 12:
                rows = conn.execute(
                    f'SELECT "{column}", COUNT(*) FROM "{table}" '
                    f'GROUP BY "{column}" ORDER BY "{column}"'
                ).fetchall()
                return jsonify(
                    {
                        "labels": [str(r[0]) for r in rows],
                        "counts": [r[1] for r in rows],
                        "kind": "numeric",
                    }
                )
            bins = 10
            width = (mx - mn) / bins or 1
            labels, counts = [], []
            for i in range(bins):
                lo = mn + i * width
                hi = mn + (i + 1) * width
                if i == bins - 1:
                    c = conn.execute(
                        f'SELECT COUNT(*) FROM "{table}" WHERE "{column}" >= ? AND "{column}" <= ?',
                        (lo, hi),
                    ).fetchone()[0]
                else:
                    c = conn.execute(
                        f'SELECT COUNT(*) FROM "{table}" WHERE "{column}" >= ? AND "{column}" < ?',
                        (lo, hi),
                    ).fetchone()[0]
                labels.append(f"{lo:.0f}–{hi:.0f}")
                counts.append(c)
            return jsonify({"labels": labels, "counts": counts, "kind": "numeric"})

        rows = conn.execute(
            f'SELECT "{column}", COUNT(*) AS c FROM "{table}" '
            f'GROUP BY "{column}" ORDER BY c DESC LIMIT 20'
        ).fetchall()
        return jsonify(
            {
                "labels": [str(r[0]) for r in rows],
                "counts": [r[1] for r in rows],
                "kind": "categorical",
            }
        )


@app.route("/api/export", methods=["POST"])
def api_export():
    body = request.get_json(force=True)
    table = body.get("table", "")
    filters = body.get("filters", [])
    limit = int(body.get("limit") or 0)

    with get_conn() as conn:
        if not valid_table(conn, table):
            return jsonify({"error": "unknown table"}), 400
        cols = safe_columns(conn, table, body.get("columns", []))
        if not cols:
            cols = get_columns(conn, table)
        col_sql = ", ".join(f'"{c}"' for c in cols)
        where, params = build_where(conn, table, filters)
        sql = f'SELECT {col_sql} FROM "{table}"{where}'
        if limit and limit > 0:
            sql += f" LIMIT {limit}"
        rows = conn.execute(sql, params).fetchall()

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(cols)
    writer.writerows(rows)
    fname = body.get("filename") or f"{table}_export"
    if not fname.endswith(".csv"):
        fname += ".csv"
    return Response(
        buf.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={fname}"},
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    print(f"Serving data from: {DB_PATH}")
    print(f"Open http://127.0.0.1:{port} in your browser.")
    app.run(debug=True, port=port)
