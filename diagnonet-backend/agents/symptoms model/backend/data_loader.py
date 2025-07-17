"""
Demo Data Loader - Uses mock dataset
"""
import pandas as pd
import os

class DatasetLoader:
    def __init__(self):
        self.dataset_path = "mock_dataset.csv"
        self.data = None
        
    def download_dataset(self):
        """Mock download - uses local mock dataset"""
        return os.path.join(os.path.dirname(__file__), self.dataset_path)
    
    def load_data(self):
        """Load the mock dataset"""
        try:
            csv_path = os.path.join(os.path.dirname(__file__), "mock_dataset.csv")
            self.data = pd.read_csv(csv_path)
            print(f"Mock dataset loaded. Shape: {self.data.shape}")
            return self.data
        except Exception as e:
            print(f"Error loading mock dataset: {e}")
            return None
    
    def get_data_info(self):
        """Get basic information about the dataset"""
        if self.data is None:
            self.load_data()
        
        if self.data is not None:
            info = {
                'shape': self.data.shape,
                'columns': list(self.data.columns),
                'diseases': self.data.iloc[:, 0].unique(),
                'sample_data': self.data.head().to_dict('records')
            }
            return info
        return None
