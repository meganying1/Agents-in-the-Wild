import os
import pandas as pd
import unittest
import tempfile

from matvisor.tools.add_material import AddMaterial
from matvisor.database import example_dataframe


class TestAddMaterial(unittest.TestCase):

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

    def test_add_material(self):
        """
        Add materials in the database with a mildly different input.
        """
        tool = AddMaterial()
        res = tool.forward(
            file_path=self.temp_file.name,
            material="Testium",
            melting="150",
            density="10.0",
            young_modulus="205",
        )
        self.assertIn("successfully", res.lower())

        df = pd.read_csv(self.temp_file.name)

        # Expected columns exist
        for col in ["material", "melting", "density", "young_modulus"]:
            self.assertIn(col, df.columns)

        # No accidental tuple-named columns like ("Melting", 100)
        bad_cols = [c for c in df.columns if isinstance(c, tuple) or (isinstance(c, str) and c.startswith("("))]
        self.assertEqual(bad_cols, [])

        # Last row should be our inserted material with correct values
        last = df.iloc[-1]
        self.assertEqual(last["material"], "Testium")
        self.assertAlmostEqual(float(last["melting"]), 150.0, places=6)
        self.assertAlmostEqual(float(last["density"]), 10.0, places=6)
        self.assertAlmostEqual(float(last["young_modulus"]), 205.0, places=6)

    def test_add_material_accepts_none_values(self):
        """
        Add a material with missing properties (None) and verify NaNs are written.
        """
        tool = AddMaterial()
        res = tool.forward(
            file_path=self.temp_file.name,
            material="Nullium",
            melting=None,     # explicit None
            density="None",       # case-insensitive string
            young_modulus="",
        )
        self.assertIn("successfully", res.lower())

        df = pd.read_csv(self.temp_file.name)
        last = df.iloc[-1]
        self.assertEqual(last["material"], "Nullium")
        # pandas reads missing values as NaN
        self.assertTrue(pd.isna(last["melting"]))
        self.assertTrue(pd.isna(last["density"]))
        self.assertTrue(pd.isna(last["young_modulus"]))


if __name__ == "__main__":
    unittest.main()