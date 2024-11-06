import pandas as pd


# POR COMPLETAR
class DataProcessor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = None

    def load_data(self):
        self.data = pd.read_csv(self.file_path)

    def display_head(self, n=5):
        if self.data is not None:
            print(self.data.head(n))
        else:
            print("Data not loaded. Please load the data first.")

    def clean_data(self):
        if self.data is not None:
            # Example cleaning steps
            self.data.dropna(inplace=True)  # Drop rows with missing values
            self.data.drop_duplicates(inplace=True)  # Drop duplicate rows
        else:
            print("Data not loaded. Please load the data first.")

    def preprocess_data(self):
        if self.data is not None:
            # Example preprocessing steps
            self.data['text'] = self.data['text'].str.lower()  # Convert text to lowercase
            self.data['duration'] = self.data['duration'].astype(int)  # Ensure duration is an integer
        else:
            print("Data not loaded. Please load the data first.")

if __name__ == "__main__":
    file_path = 'cupcakeslovers.csv'
    data_processor = DataProcessor(file_path)
    data_processor.load_data()
    data_processor.clean_data()
    data_processor.preprocess_data()
    data_processor.display_head()