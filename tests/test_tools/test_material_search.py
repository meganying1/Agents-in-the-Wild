import os
import ast
import unittest
import tempfile

from matvisor.tools.material_search import SearchByMaterial
from matvisor.database import example_dataframe


class TestSearchByMaterial(unittest.TestCase):

    def setUp(self):
        # Create a temporary CSV file to act as database.csv
        self.temp_file = tempfile.NamedTemporaryFile(
            mode="w+", suffix=".csv", delete=False
        )
        example_dataframe.to_csv(self.temp_file.name, index=False)

    def tearDown(self):
        # Clean up the temporary file after each test
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    def test_search_material(self):
        """
        Search for materials in the database with a mildly different input.
        """
        search_tool = SearchByMaterial()
        result_str = search_tool.forward(
            file_path=self.temp_file.name, material="Coppperr"
        )
        # It should return a string representation of a list of dicts
        results = ast.literal_eval(result_str)
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 1)
        record = results[0]
        self.assertEqual(record["Material"], "Copper")
        self.assertAlmostEqual(float(record["Density min"]), 8.90, places=2)
        self.assertAlmostEqual(float(record["Density max"]), 8.98, places=2)
        self.assertAlmostEqual(float(record["Melting min"]), 1083, places=2)
        self.assertAlmostEqual(float(record["Melting max"]), 1085, places=2)
        self.assertAlmostEqual(float(record["Young's modulus min"]), 110, places=2)
        self.assertAlmostEqual(float(record["Young's modulus max"]), 120, places=2)


if __name__ == "__main__":
    unittest.main()