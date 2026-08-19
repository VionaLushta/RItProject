"""Local tests for the Student model and JSON storage helpers."""

from __future__ import annotations

import json
import tempfile
import unittest
import warnings
from pathlib import Path

from backend.student import Student
from backend.storage import (
    add_question_record,
    get_question_history,
    load_data,
    save_data,
    save_student_statistics,
)


class StudentStorageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.storage_path = Path(self.temp_dir.name) / "history.json"

    def test_student_object_and_counters(self) -> None:
        student = Student("Ava")

        student.add_question()
        student.add_quiz()
        student.add_correct_answer()
        student.add_incorrect_answer()

        self.assertEqual(student.name, "Ava")
        self.assertEqual(student.questions_asked, 1)
        self.assertEqual(student.quizzes_completed, 1)
        self.assertEqual(student.correct_answers, 1)
        self.assertEqual(student.incorrect_answers, 1)
        self.assertEqual(
            student.to_dict(),
            {
                "name": "Ava",
                "questions_asked": 1,
                "quizzes_completed": 1,
                "correct_answers": 1,
                "incorrect_answers": 1,
            },
        )

    def test_load_save_and_reload(self) -> None:
        data = load_data(self.storage_path)
        self.assertEqual(data, {"questions": [], "quizzes": [], "statistics": {}})

        data["questions"].append({"question": "What is Python?", "answer": "A programming language."})
        save_data(data, self.storage_path)

        reloaded = load_data(self.storage_path)
        self.assertEqual(reloaded["questions"], [{"question": "What is Python?", "answer": "A programming language."}])
        self.assertEqual(reloaded["quizzes"], [])
        self.assertEqual(reloaded["statistics"], {})

    def test_add_question_and_get_history(self) -> None:
        add_question_record("What is Python?", "A programming language.", self.storage_path)

        history = get_question_history(self.storage_path)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["question"], "What is Python?")
        self.assertEqual(history[0]["answer"], "A programming language.")

    def test_save_student_statistics(self) -> None:
        student = Student("Mila")
        student.add_question()
        student.add_quiz()
        student.add_correct_answer()

        save_student_statistics(student, self.storage_path)
        reloaded = load_data(self.storage_path)

        self.assertIn("Mila", reloaded["statistics"])
        self.assertEqual(
            reloaded["statistics"]["Mila"],
            {
                "name": "Mila",
                "questions_asked": 1,
                "quizzes_completed": 1,
                "correct_answers": 1,
                "incorrect_answers": 0,
            },
        )

    def test_missing_file_handling(self) -> None:
        missing_path = Path(self.temp_dir.name) / "missing.json"
        self.assertFalse(missing_path.exists())

        data = load_data(missing_path)
        self.assertEqual(data, {"questions": [], "quizzes": [], "statistics": {}})

    def test_empty_and_invalid_json_handling(self) -> None:
        empty_path = Path(self.temp_dir.name) / "empty.json"
        empty_path.write_text("", encoding="utf-8")

        with warnings.catch_warnings(record=True) as caught_empty:
            warnings.simplefilter("always")
            empty_data = load_data(empty_path)

        self.assertEqual(empty_data, {"questions": [], "quizzes": [], "statistics": {}})
        self.assertTrue(any("empty" in str(item.message).lower() for item in caught_empty))

        invalid_path = Path(self.temp_dir.name) / "invalid.json"
        invalid_path.write_text("{ not valid json", encoding="utf-8")

        with warnings.catch_warnings(record=True) as caught_invalid:
            warnings.simplefilter("always")
            invalid_data = load_data(invalid_path)

        self.assertEqual(invalid_data, {"questions": [], "quizzes": [], "statistics": {}})
        self.assertTrue(any("invalid json" in str(item.message).lower() for item in caught_invalid))

    def test_history_file_is_valid_json_after_save(self) -> None:
        student = Student("Noah")
        save_student_statistics(student, self.storage_path)

        with self.storage_path.open("r", encoding="utf-8") as file:
            raw = json.load(file)

        self.assertEqual(raw["statistics"]["Noah"]["name"], "Noah")


if __name__ == "__main__":
    unittest.main()

