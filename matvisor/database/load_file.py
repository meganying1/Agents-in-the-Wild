import pandas as pd


def load_materials_from_file(filepath: str) -> pd.DataFrame:
    """
    Loads a CSV file into a pandas DataFrame and normalizes columns.
    """    
    df = pd.read_csv(filepath)
    return df


if __name__ == "__main__":
    
    import os

    path = os.path.dirname(os.path.abspath(__file__))
    filename = "database_test.csv"
    filepath = os.path.join(path, filename)
    df = load_materials_from_file(filepath)
    print(df.head())