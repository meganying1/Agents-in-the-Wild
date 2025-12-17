import os
import ast
import unittest
import tempfile

from matvisor.tools.property_search import SearchByProperty
from matvisor.database import example_dataframe as df


class TestSearchByProperty(unittest.TestCase):
    
    def setUp(self):
        # Create a temporary CSV file to act as database.csv
        self.temp_file = tempfile.NamedTemporaryFile(
            mode="w+", suffix=".csv", delete=False
        )
        df.to_csv(self.temp_file.name, index=False)

    def tearDown(self):
        # Clean up the temporary file after each test
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    def test_search_property_ranking(self):
        """
        With single numeric targets, results should be ranked by total distance.
        Expect Aluminum to be the closest to Density=2.7 and Melting=660.
        """
        search_tool = SearchByProperty()
        props = {"Density": 2.7, "Melting": 660}
        result_str = search_tool.forward(file_path=self.temp_file.name, properties=props)
        results = ast.literal_eval(result_str)
        self.assertIsInstance(results, list)
        self.assertGreaterEqual(len(results), 1)
        # Top-1 should be Aluminum
        self.assertEqual(results[0]["material"], "Aluminum")
        # total_distance should be smallest for the first result
        self.assertLessEqual(results[0]["total_distance"], results[-1]["total_distance"])

    def test_search_property_single_dimension(self):
        """
        For a single property target, Copper should be closest to Density≈8.91.
        """
        search_tool = SearchByProperty()
        props = {"Density": 8.915}
        result_str = search_tool.forward(file_path=self.temp_file.name, properties=props)
        results = ast.literal_eval(result_str)
        self.assertIsInstance(results, list)
        self.assertGreaterEqual(len(results), 1)
        self.assertEqual(results[0]["material"], "Copper")

    def test_property_search_unknown_property(self):
        """
        If a requested property is not found (by fuzzy match), return an error string.
        """
        search_tool = SearchByProperty()
        properties = {"Conductivity": 300}
        result_str = search_tool.forward(
            file_path=self.temp_file.name, properties=properties
        )
        self.assertEqual(result_str, "Error: Could not find property 'Conductivity'.")


if __name__ == "__main__":
    unittest.main()