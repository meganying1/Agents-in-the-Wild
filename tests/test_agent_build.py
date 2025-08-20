import unittest
from matvisor import agent_build, models_llama


class TestAgentBuild(unittest.TestCase):

    def test_build_agent_with_fake_model_runs(self):
        """
        Test building agent with fake model runs
        """
        agent = agent_build.build_agent(models_llama.FakeModel(), verbosity="debug")
        out = agent.run("Say 'hello' then call final_answer('done').")
        self.assertIsInstance(out, str)
        self.assertEqual(out.strip().lower(), "done")


if __name__ == "__main__":
    unittest.main()