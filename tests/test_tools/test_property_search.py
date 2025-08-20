import os
import ast
import unittest
import tempfile

from matvisor.tools.property_search import SearchByProperty
from matvisor.database import example_dataframe


class TestSearchByProperty(unittest.TestCase):
    
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

    def test_search_property_all(self):
        """
        Search for materials within a range of the property.
        """
        search_tool = SearchByProperty()
        # Use a valid property present in the database: Density
        props = {"Density": {"min": 0, "max": 10}}
        result_str = search_tool.forward(file_path=self.temp_file.name, properties=props)
        results = ast.literal_eval(result_str)
        self.assertEqual(results, ["Copper", "Aluminum", "Iron"])  # Only Copper should match

    def test_search_property_one(self):
        """
        Search for materials within a range of the property.
        """
        search_tool = SearchByProperty()
        # Use a valid property present in the database: Density
        props = {"Density": {"min": 8.91, "max": 8.92}}
        result_str = search_tool.forward(file_path=self.temp_file.name, properties=props)
        results = ast.literal_eval(result_str)
        self.assertEqual(results, ["Copper"])  # Only Copper should match

    def test_property_search_no_match(self):
        """
        Ensure it reports no match if ranges exclude all rows.
        """
        search_tool = SearchByProperty()
        properties = {
            "Density": {"min": 4.5, "max": 5.0},
            "Conductivity": {"min": 300, "max": 400}
        }
        result_str = search_tool.forward(
            file_path=self.temp_file.name, properties=properties
        )
        # Expect the fallback message when no materials match
        self.assertEqual(result_str, "No materials found matching the criteria.")


if __name__ == "__main__":
    unittest.main()