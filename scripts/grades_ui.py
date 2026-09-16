"""Streamlit UI for adding/editing student ball and grade entries in assets/grades.json.

Run with:
    .venv/Scripts/python.exe -m streamlit run scripts/grades_ui.py
"""
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))
import grades_cli as gc

JSON_PATH = gc.DEFAULT_JSON_PATH

st.set_page_config(page_title="Grades editor", layout="wide")


def reload_data():
    st.session_state.data = gc.load(JSON_PATH)


if "data" not in st.session_state:
    reload_data()

data = st.session_state.data

st.title("Журнал успішності — редагування")
st.caption(f"Джерело: `{JSON_PATH}`")

with st.sidebar:
    if st.button("Перечитати файл", help="Скинути незбережені зміни та завантажити файл заново"):
        reload_data()
        st.rerun()

tab_edit, tab_manage, tab_overview = st.tabs(["Редагувати заняття", "Керування", "Огляд"])

with tab_edit:
    lessons = list(data["grades"].keys())
    if not lessons:
        st.info("Немає жодного заняття. Додайте його у вкладці «Керування».")
    else:
        lesson = st.selectbox("Заняття", lessons)
        students = data["students"]
        rows = []
        for s in students:
            entry = data["grades"][lesson].get(s)
            rows.append({
                "student": s,
                "ball": entry["ball"] if entry else None,
                "grade": entry["grade"] if entry else None,
            })
        df = pd.DataFrame(rows).set_index("student")

        edited = st.data_editor(
            df,
            use_container_width=True,
            num_rows="fixed",
            column_config={
                "ball": st.column_config.NumberColumn("Бал", min_value=0.0, step=0.1, format="%.2f"),
                "grade": st.column_config.NumberColumn("Оцінка", min_value=1, max_value=5, step=1, format="%d"),
            },
            key=f"editor_{lesson}",
        )

        if st.button("Зберегти заняття", type="primary"):
            for s, row in edited.iterrows():
                ball = None if pd.isna(row["ball"]) else float(row["ball"])
                grade = None if pd.isna(row["grade"]) else int(row["grade"])
                data["grades"][lesson][s] = None if ball is None and grade is None else {"ball": ball, "grade": grade}
            gc.save(JSON_PATH, data)
            st.success(f"Збережено заняття {lesson}")

with tab_manage:
    col_lessons, col_students = st.columns(2)

    with col_lessons:
        st.subheader("Заняття")
        new_lesson = st.text_input("Назва нового заняття", placeholder="27_GL")
        if st.button("Додати заняття"):
            if not new_lesson:
                st.error("Вкажіть назву заняття")
            elif new_lesson in data["grades"]:
                st.error(f"Заняття '{new_lesson}' вже існує")
            else:
                data["grades"][new_lesson] = {s: None for s in data["students"]}
                gc.save(JSON_PATH, data)
                st.success(f"Додано заняття '{new_lesson}'")
                st.rerun()

        lesson_to_remove = st.selectbox("Видалити заняття", [""] + list(data["grades"].keys()))
        if st.button("Видалити заняття", disabled=not lesson_to_remove):
            del data["grades"][lesson_to_remove]
            gc.save(JSON_PATH, data)
            st.success(f"Видалено заняття '{lesson_to_remove}'")
            st.rerun()

    with col_students:
        st.subheader("Студенти")
        new_student = st.text_input("Номер нового студента", placeholder="16")
        if st.button("Додати студента"):
            if not new_student:
                st.error("Вкажіть номер студента")
            elif new_student in data["students"]:
                st.error(f"Студент '{new_student}' вже існує")
            else:
                data["students"].append(new_student)
                for row in data["grades"].values():
                    row.setdefault(new_student, None)
                gc.save(JSON_PATH, data)
                st.success(f"Додано студента '{new_student}'")
                st.rerun()

        student_to_remove = st.selectbox("Видалити студента", [""] + data["students"])
        if st.button("Видалити студента", disabled=not student_to_remove):
            data["students"].remove(student_to_remove)
            for row in data["grades"].values():
                row.pop(student_to_remove, None)
            gc.save(JSON_PATH, data)
            st.success(f"Видалено студента '{student_to_remove}'")
            st.rerun()

with tab_overview:
    students = data["students"]
    lessons = list(data["grades"].keys())
    if not lessons or not students:
        st.info("Немає даних для відображення.")
    else:
        table = []
        for lesson in lessons:
            row = {"lesson": lesson}
            for s in students:
                entry = data["grades"][lesson].get(s)
                row[s] = f"{entry['ball']}/{entry['grade']}" if entry else "—"
            table.append(row)
        st.dataframe(pd.DataFrame(table).set_index("lesson"), use_container_width=True)
