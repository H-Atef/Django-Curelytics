import med_scraper.scraper_helper.drugeye_scraper as de
import med_scraper.scraper_helper.drugtitan_scraper as det
import med_scraper.scraper_helper.data_handling as pro
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

    def scrape_and_process(self,drug_names)->pd.DataFrame:
        data=self.scraper.scrape_multiple_data(drug_names)
        df=self.collect_and_process_data(data)
        return df
    
    def collect_and_process_data(self,data)->pd.DataFrame:

        if not os.path.exists('./med_scraper/scraper_helper/json_outputs'):
            os.makedirs('./med_scraper/scraper_helper/json_outputs')

        pro.DataSerializer.serialize_data(data
                                          ,f'./med_scraper/scraper_helper/json_outputs/tmp_{self.scraper.scraper_name}.json')

        

        if not os.path.exists('./med_scraper/scraper_helper/csv_outputs'):
            os.makedirs('./med_scraper/scraper_helper/csv_outputs')

        df=pro.DataProcessor().process_multiple_data(data)

        if not df.empty:
            df.to_csv(f'./med_scraper/scraper_helper/csv_outputs/tmp_{self.scraper.scraper_name}.csv'
                                            ,index=False)
        
        return df
          









# if __name__ == "__main__":

#     scraper= ScraperContext(SCRAPER_MAPPING["DrugEyeTitan"])
#     scraper.scrape_and_cache(["panadol","ketofan"])


   
    
    


