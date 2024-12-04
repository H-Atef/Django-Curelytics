from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import threading
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import scrapers_classes.web_scraping_resources as wb
import scrapers_classes.abstract_med_scraper as md

from med_price_tracker import models,serializers




class DrugEyeTitanScraper(md.Scraper):
    def __init__(self):
        self.url = "http://www.drugeye.pharorg.com/drugeyeapp/android-search/drugeye-titan.aspx"
        self.scraper_name='drugeye_titan'
        
       
    def scrape_data(self, drug_name):
        # First, check if the drug exists in the database
        medicine_price_info = models.MedicinePriceInfo.objects.filter(drug_name__icontains=drug_name)
        if medicine_price_info.exists():
            serializer = serializers.MedicinePriceSerializer(medicine_price_info,many=True)
            return pd.DataFrame(serializer.data).to_dict(orient="list") 
        
        else:
            try:
                drv_flag=[True]

                driver = wb.WebScarpingToolInit().initialize_driver("google")
                driver.get(self.url)
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "ttt"))).send_keys(drug_name)
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "BtnCounting"))).click()
                table = driver.find_element(By.CSS_SELECTOR, "#ctl00 > div.l-container > table:nth-child(3)")
                table.location_once_scrolled_into_view
                table_html = table.get_attribute('outerHTML')
                data = self._extract_data(table_html)

                if data:
                    data["search_q"]=[drug_name.upper() for x in range(len(data["drug_name"]))]

                medicine_instances = []

                data_to_itterows=pd.DataFrame(data).iterrows()


                for index,row in data_to_itterows:

                    if index == 15:
                        break

                    medicine_data = row.to_dict()

                    # Create an instance of the model but don't save yet
                    medicine_instance = models.MedicinePriceInfo(**medicine_data)
                    
                    # Append to the list of instances
                    medicine_instances.append(medicine_instance)

                if medicine_instances:
                    # Use bulk_create to save all the instances in one query
                    models.MedicinePriceInfo.objects.bulk_create(medicine_instances)

                return data
            
            except Exception as e:
                #print(f"An error occurred: {e}")
                return {}
            finally:
                if drv_flag[0]:
                    driver.close()

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
        elements = [x.find_all("td") for x in soup.find_all("tr")][1:]

        data = {
            'drug_name': [],
            'repeat': [],
            'price': []
        }


        max_repeat=0



        for tr in elements:
            tds = [td.text for td in tr]
            data['drug_name'].append(tds[0])
            data['repeat'].append(str(tds[1]) if tds[1] is not None else "-")
            data['price'].append(str(tds[2]) if tds[2] is not None else "-")

        return data



