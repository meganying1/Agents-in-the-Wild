import os
import csv


class ResultRecorder:

    def __init__(self, filepath):
        self.filepath = filepath

        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        # Create CSV file with header if it doesn’t exist
        if not os.path.exists(filepath):
            with open(filepath, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["modelsize", "result"])

    def add(self, modelsize: str, result: str):
        with open(self.filepath, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([modelsize, result])
        
    def show(self):
        with open(self.filepath, mode="r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                print(row)

    def remove(self):
        if os.path.exists(self.filepath):
            os.remove(self.filepath)


if __name__ == "__main__":
    path = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(path, "test_results.csv")
    result_recorder = ResultRecorder(filepath=filepath)
    result_recorder.add("3", "Metal")
    result_recorder.add("7", "Plastic")
    result_recorder.show()
    result_recorder.remove()

        
