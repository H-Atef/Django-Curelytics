import drugeye_scraper as de
import drugtitan_scraper as det
import data_handling as pro
import med_db as db
import pandas as pd
import datetime 
import glob
import os


SCRAPER_MAPPING = {
        'DrugEye': de.DrugEyeScraper(),
        'DrugEyeTitan': det.DrugEyeTitanScraper()
    }


class ScraperContext:
    def __init__(self, scraper):
        self.scraper = scraper

    def scrape_data(self, drug_name):
        return self.scraper.scrape_data(drug_name)

    def scrape_multiple_data(self, drug_names):
        return self.scraper.scrape_multiple_data(drug_names)

    def scrape_and_cache(self,drug_names):
        data=self.scraper.scrape_multiple_data(drug_names)

        if not os.path.exists('json_outputs'):
            os.makedirs('json_outputs')

        pro.DataSerializer.serialize_data(data
                                          ,'json_outputs/tmp_'+self.scraper.scraper_name+'_'+
                                          datetime.datetime.now().strftime("%Y%m%d%H%M")+'.json')
        self.collect_and_cache_data()
    
    def collect_and_cache_data(self):
        json_files = glob.glob('json_outputs/tmp_'+self.scraper.scraper_name+'_*.json')
        all_data = {}
        for file in json_files:
            data=pro.DataSerializer.deserialize_data(file)
            all_data.update(data)

        if not os.path.exists('csv_outputs'):
            os.makedirs('csv_outputs')

        df=pro.DataProcessor().process_multiple_data(data)

        if not df.empty:
            df.to_csv('csv_outputs/tmp_'+self.scraper.scraper_name+'_'+
                                            datetime.datetime.now().strftime("%Y%m%d%H%M")+'.csv'
                                            ,index=False)
        
        db.MedDrugsDB().medDrug_df_db_operations(df
                                                ,mode="cache"
                                                ,collection=self.scraper.scraper_name+"_cache"
                                                ,scraper_name=self.scraper.scraper_name
                                                )

        pro.DataSerializer.append_to_main(data,self.scraper.scraper_name)
        
        return all_data
          









if __name__ == "__main__":

    scraper= ScraperContext(SCRAPER_MAPPING["DrugEye"])
    scraper.scrape_and_cache(["panadol"])


   
    
    


