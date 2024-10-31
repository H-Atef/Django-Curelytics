from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import threading
import time
import pandas as pd

import web_scraping_resources as wb
import abstract_med_scraper as md
import med_db as db

class DrugEyeScraper(md.Scraper):
    def __init__(self):
        self.url = "http://www.drugeye.pharorg.com/drugeyeapp/android-search/drugeye-android-live-go.aspx"
        self.scraper_name='drugeye'
       
    def scrape_data(self, drug_name):
        try:
            drv_flag=[True]
            cache=db.MedDrugsDB().search_by_brand_name(drug_name)

            #check if drug name found in cache
            if cache is not None and not cache.empty:
                #print("found")
                drv_flag[0]=False
                return cache.to_dict(orient="list")
             
            driver=wb.WebScarpingToolInit().initialize_driver("google")
            driver.get(self.url)
            time.sleep(1)
            #print(driver.current_url,drug_name)
            input_field = driver.find_element(By.NAME, "ttt")
            input_field.send_keys(drug_name)
            driver.find_element(By.ID, "b1").click()
            table = driver.find_element(By.ID, "MyTable")
            table.location_once_scrolled_into_view
            table_html = table.get_attribute('outerHTML')
            data = self._extract_data(table_html)
            driver.close()

            return data
        
        except Exception as e:
            if drv_flag:
                driver.close()
            print(f"An error occurred while scraping data for {drug_name}: {e}")
            return {}

    def scrape_multiple_data(self, drug_names):
        results = {}
        threads = []
        for drug_name in drug_names:
            thread = threading.Thread(target=lambda name=drug_name:
                                       results.update({name: self.scrape_data(name)}))
            threads.append(thread)
            thread.start()
            

        for thread in threads:
            thread.join()

        return results
       
    def _extract_data(self, table_html):

        soup = BeautifulSoup(table_html, 'lxml')
        drug_names = []
        generic_names = []
        drug_classes = []
        similars=[]
        alternatives=[]

        rows = soup.find_all('tr')



        for i in range(len(rows)-1):
            first_cell = rows[i].find('td')
            next_cell=rows[i+1].find('td')

            if first_cell.has_attr("title"):
                q=first_cell.get('title')
                similars.append(self.url+"?gname="+q+"geno")
                alternatives.append(self.url+"?gname="+q+"alto")

                

                

            if next_cell.has_attr("style"):
                next_cell_style = next_cell.get('style')
                next_cell_style=next_cell_style[:next_cell_style.index(";")]

            if first_cell.has_attr("style"):
                cell_style = first_cell.get('style')
                cell_style=cell_style[:cell_style.index(";")]
               

                if 'color:Blue' == cell_style:
                    drug_names.append(first_cell.text)  

                if 'color:Green' == cell_style:
                    drug_classes.append(first_cell.text)    

                if 'color:Black' == cell_style:
                    generic_names.append(first_cell.text)   

                if 'color:Blue' == cell_style and next_cell_style=='color:Green':
                    generic_names.append("-")  

                if 'color:Black' == cell_style and next_cell_style=='color:BlueViolet':
                    drug_classes.append("-")  

        last_cell = rows[-1].find('td')
        if last_cell.has_attr("title"):
            q = last_cell.get('title')
            similars.append(self.url + "?gname=" + q + "geno")
            alternatives.append(self.url + "?gname=" + q + "alto")
                    
         


        number_of_drugs=len(drug_names)
        color_ref=["color:Blue", "color:Black", 
                   "color:Green", "color:BlueViolet", "color:Navy"]*number_of_drugs
        

       

    
        data = {
            'Drug Name': drug_names,
            'Generic Name': generic_names,
            'Drug Class': drug_classes,
            'Similars':similars,
            'Alternatives':alternatives
        }

        return data
