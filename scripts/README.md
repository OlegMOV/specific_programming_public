# Grades tooling

Scripts for editing `assets/grades.json` (used by `grades_view.html`).

## Setup

```
py -3 -m venv .venv
.venv/Scripts/python.exe -m pip install -r scripts/requirements.txt
```

## CLI (`grades_cli.py`)

```
.venv/Scripts/python.exe scripts/grades_cli.py set 25_GL 06 3.7 4
.venv/Scripts/python.exe scripts/grades_cli.py add-student 16
.venv/Scripts/python.exe scripts/grades_cli.py list --lesson 25_GL
```

Run with `-h` for the full command list.

## UI (`grades_ui.py`)

Streamlit app for editing ball/grade per lesson in a table, plus adding/removing
students and lessons.

```
.venv/Scripts/python.exe -m streamlit run scripts/grades_ui.py
```

Opens at http://localhost:8501. Edits save straight to `assets/grades.json`.
