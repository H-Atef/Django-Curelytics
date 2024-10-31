

from fuzzywuzzy import fuzz
import pandas as pd
import json







class DataProcessor:

    
    def process_data(self,data):
        df = pd.DataFrame(data)
        return df
    
    def process_multiple_data(self, scraped_data):
         
        if scraped_data:
         
            dict_keys_list=list(scraped_data.keys())
            df=pd.DataFrame(scraped_data[dict_keys_list[0]])
            for key in dict_keys_list[1:]:
                if scraped_data[key]!={}:
                    df= pd.concat([df,pd.DataFrame(scraped_data[key])],ignore_index=True)
                
            return df
            
    def filter_de_titan_data(self, df):
        # Convert "Repeat" column to numeric with handling errors
        df["Repeat"] = pd.to_numeric(df["Repeat"], errors='coerce')

        # Get top 10 maximum repeat values
        top_10_max_repeats = df["Repeat"].nlargest(10)

        # Define function to filter based on drug name similarity and top 10 max repeats
        def filter_similar_names(row):
            brand_name = row["Drug Name"]
            similar_names = df[(df["Drug Name"] != brand_name) &
                                (df["Drug Name"].apply(lambda x: fuzz.ratio(x, brand_name)) > 82)]
            if len(similar_names) > 0:
                if row["Repeat"] in top_10_max_repeats.values:
                    return True
                return False
            return True
        
        # Filter the DataFrame based on the defined function
        df = df[df.apply(filter_similar_names, axis=1)]
        
        # Sort by "Repeat" column in descending order
        df = df.sort_values(by="Repeat", ascending=False)
        
        # Return the filtered and sorted DataFrame
        return df
            

    

class DataSerializer:
    
    @staticmethod
    def serialize_data(data, file_path):
     # Serialize data to JSON and save in a file
     json_table = json.dumps(data,ensure_ascii=False)
     with open(file_path, 'w', encoding='utf-8') as file:
          file.write(json_table)

    @staticmethod
    def append_to_main(data, file_path):
        main_file_path = "json_outputs/main_" + file_path + ".json"
        
        try:
            with open(main_file_path, 'r', encoding='utf-8') as file:
                main_data = json.load(file)
        except FileNotFoundError:
            main_data = {}
        
        if isinstance(main_data, dict) and isinstance(data, dict):
            main_data.update(data)
        else:
            print("Data or main_data is not a dictionary. Cannot append.")
        
        with open(main_file_path, 'w', encoding='utf-8') as file:
            json.dump(main_data, file, ensure_ascii=False)

    
     
    @staticmethod
    def deserialize_data(file_path):
     # Deserialize data from a JSON file
     with open(file_path, 'r', encoding='utf-8') as file:
          data = json.load(file)
     return data
