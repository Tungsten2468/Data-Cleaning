# Data Explorer — Web UI

A polished web front-end for the terminal query interface in `queryInterface/`.
It wraps the same capabilities (choose a table, pick columns, view rows, run
calculations, filter by category / numeric range, export CSV) in a single-page
dashboard suitable for client demos.

## Run

```bash
pip3 install flask pandas          # one-time
python3 webapp/app.py              # serves http://127.0.0.1:5001
```

Then open **http://127.0.0.1:5001** in a browser.

- Port defaults to `5001` (macOS uses 5000 for AirPlay). Override with `PORT=8080 python3 webapp/app.py`.
- The database is auto-located at the repo root (`final_reports.db`). Override with `REPORTS_DB=/path/to.db`.

## What it does

| Terminal action        | Web equivalent                                    |
|------------------------|---------------------------------------------------|
| pick table / columns   | Data source panel (checkbox column picker)        |
| (V)iew                 | Results table + KPI cards                          |
| (C)alculations         | Calculations panel (Total/Avg/Median/High/Low, or Count for categories) |
| (F)ilter category/range| Filters panel (chips; stack multiple)             |
| (S)ave to .CSV         | Export CSV button                                 |
| —                      | Distribution chart (bonus, for demos)             |

Calculations and CSV export respect the active filters. Column names are
whitelisted against the real schema and all filter values are parameterized.
