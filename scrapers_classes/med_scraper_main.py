import scrapers_classes.drugeye_scraper as de
import scrapers_classes.drugtitan_scraper as det
import scrapers_classes.data_handling as pro
import pandas as pd
import os


SCRAPER_MAPPING = {
        'DrugEye': de.DrugEyeScraper(),
        'DrugEyeTitan': det.DrugEyeTitanScraper()
    }

PATH="./scrapers_classes/"


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

        if not os.path.exists(f'{PATH}json_outputs'):
            os.makedirs(f'{PATH}json_outputs')

        pro.DataSerializer.serialize_data(data
                                          ,f'{PATH}json_outputs/tmp_{self.scraper.scraper_name}.json')

        

        if not os.path.exists(f'{PATH}csv_outputs'):
            os.makedirs(f'{PATH}csv_outputs')

        df=pro.DataProcessor().process_multiple_data(data)
	
        if df is None:
            return pd.DataFrame({})

        if not df.empty:
            df.to_csv(f'{PATH}csv_outputs/tmp_{self.scraper.scraper_name}.csv'
                                            ,index=False)
        
        return df
          









# if __name__ == "__main__":

#     scraper= ScraperContext(SCRAPER_MAPPING["DrugEyeTitan"])
#     scraper.scrape_and_cache(["panadol","ketofan"])


   
    
    


