from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import threading
import time
import pandas as pd

import med_scraper.scraper_helper.web_scraping_resources as wb
import med_scraper.scraper_helper.abstract_med_scraper as md
from med_scraper import models,serializers


class DrugEyeScraper(md.Scraper):
    def __init__(self):
        self.url = "http://www.drugeye.pharorg.com/drugeyeapp/android-search/drugeye-android-live-go.aspx"
        self.scraper_name='drugeye'
    from rest_framework.exceptions import NotFound


    def scrape_data(self, drug_name):
        # First, check if the drug exists in the database
        medicine_info = models.MedicineInfo.objects.filter(drug_name__icontains=drug_name)
        if medicine_info.exists():
            serializer = serializers.MedicineSerializer(medicine_info,many=True)
            return pd.DataFrame(serializer.data).to_dict(orient="list")  

        else:
            # Drug not found in the database, proceed to scrape
            try:
                driver = wb.WebScarpingToolInit().initialize_driver("google")
                driver.get(self.url)

                input_field = driver.find_element(By.NAME, "ttt")
                input_field.send_keys(drug_name)
                driver.find_element(By.ID, "b1").click()

                table = driver.find_element(By.ID, "MyTable")
                table.location_once_scrolled_into_view
                table_html = table.get_attribute('outerHTML')

                # Extract data from the table
                data = self._extract_data(table_html)

                # Iterate over each row in the DataFrame and save it
                for index, row in pd.DataFrame(data).iterrows():
                    serializer = serializers.MedicineSerializer(data=row.to_dict())  # Convert row to dict
                    if serializer.is_valid():
                        serializer.save()
                
                return data

            except Exception as e:
                # Handle any scraping or saving exceptions
                print(f"Error occurred: {e}")
                return None

            finally:
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
                    
        

       

    
        data = {
            'drug_name': drug_names,
            'generic_name': generic_names,
            'drug_class': drug_classes,
            'similars':similars,
            'alternatives':alternatives
        }

        return data
