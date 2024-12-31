nfl_teams = [
  bills,
  cards,
  eagles
]

def read_folder(folder_path):
        """
        Function to read all CSV files in a folder and combine them into a single DataFrame.
        Args:
            folder_path (str): Path to the folder containing the CSV files.
        Returns:
            combined_df (DataFrame): A pandas DataFrame containing the combined data from all CSV files.
        """
        all_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.csv')]
        df_list = [pd.read_csv(file) for file in all_files]
        combined_df = pd.concat(df_list, ignore_index=True)
        return combined_df
read_folder(nfl_teams)
