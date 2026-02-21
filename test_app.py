import unittest

import app


class TestAppHelpers(unittest.TestCase):
    def test_chunk_text_small(self):
        self.assertEqual(list(app.chunk_text("abcdef", size=10)), ["abcdef"])

    def test_chunk_text_split(self):
        self.assertEqual(list(app.chunk_text("abcdefghij", size=4)), ["abcd", "efgh", "ij"])

    def test_build_prompt_contains_question_and_context(self):
        prompt = app.build_prompt("CTX", "What?")
        self.assertIn("CTX", prompt)
        self.assertIn("What?", prompt)


if __name__ == "__main__":
    unittest.main()
