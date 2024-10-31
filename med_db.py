import pandas as pd
from pymongo import MongoClient
import data_handling as pro

class MedDrugsDB:
    

    def medDrug_df_db_operations(self, df: pd.DataFrame=pd.DataFrame(),
                                  mode="get", 
                                  collection="drugeye_cache",
                                  scraper_name='drugeye'
                                  ):
        client = MongoClient('localhost', 27017)
        db = client['MedDrug']
        collection = db[collection]

        if mode == 'cache':
            try:
                if not df.empty:

                    

                    if scraper_name!='drugeye':
                        df=pro.DataProcessor().filter_de_titan_data(df).head(50)
                        records = df.to_dict(orient='records')
                        collection.insert_many(records)
                        return "New DataFrame Data cached successfully!"

                    records = df.to_dict(orient='records')
                    

                    existing_records = []
                    new_records = []
                    for record in records:
                        existing_data_count = collection.count_documents(record)
                        if existing_data_count == 0:
                            new_records.append(record)
                        else:
                            existing_records.append(record)

                    if new_records:
                        collection.insert_many(new_records)
                        return "New DataFrame Data cached successfully!"
                    else:
                        return "All records already exist in the collection"
            except Exception as e:
                return None

        elif mode == 'get':
            try:
                data = list(collection.find())
                df = pd.DataFrame(data)
                return df
            except Exception as e:
                return None

        elif mode == "truncate":
            try:
                collection.delete_many({})
                return "Collection Data Deleted successfully!"
            except Exception as e:
                return None
            
    def search_by_brand_name(self, brand_name, collection="drugeye_cache")->pd.DataFrame:
        
        client = MongoClient('localhost', 27017)
        db = client['MedDrug']
        collection = db[collection]
        
        try:
            data = list(collection.find({'Drug Name': {"$regex": brand_name, "$options": "i"}}))
            df = pd.DataFrame(data)
             # Drop the '_id' column from the DataFrame
            df = df.drop('_id', axis=1, errors='ignore')
            return df
        except Exception as e:
            return None