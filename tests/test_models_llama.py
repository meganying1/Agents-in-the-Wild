import unittest
from matvisor import models_llama


class TestModelsLlama(unittest.TestCase):

    def test_fake_model_generates_parsable(self):
        """
        Testing the Fake LLM model.
        """
        m = models_llama.FakeModel()
        msg = m.generate([{"role":"user","content":"ping"}])
        # Must look like a smolagents message
        self.assertTrue(hasattr(msg, "content"))
        self.assertTrue(hasattr(msg, "token_usage"))
        self.assertTrue(hasattr(msg.token_usage, "input_tokens"))
        self.assertTrue(hasattr(msg.token_usage, "output_tokens"))
        self.assertTrue(hasattr(msg.token_usage, "total_tokens"))
        # Must be parsable by CodeAgent
        self.assertIn("<code>", msg.content)
        self.assertIn("</code>", msg.content)
        self.assertIn("final_answer(", msg.content)

    def test_token_usage_totals(self):
        """
        Test token usage calculator.
        """
        tu = models_llama.TokenUsage(input_tokens=3, output_tokens=7)
        self.assertEqual(tu.total_tokens, 10)

    def test_llama_cpp_model_with_dummy_llm(self):
        """
        Use a tiny DummyLLM so we don't load any GGUF.
        """

        class DummyLLM:
            def create_chat_completion(self, messages, stop=None, max_tokens=256, temperature=0.2):
                return {
                    "choices": [{"message": {"content": "ok"}}],
                    "usage": {"prompt_tokens": 11, "completion_tokens": 5, "total_tokens": 16},
                }

        model = models_llama.LlamaCppModel(DummyLLM())
        msg = model.generate([{"role": "user", "content": "hi"}])
        self.assertEqual(msg.content, "ok")
        self.assertEqual(msg.token_usage.input_tokens, 11)
        self.assertEqual(msg.token_usage.output_tokens, 5)
        self.assertEqual(msg.token_usage.total_tokens, 16)


if __name__ == "__main__":
    unittest.main()