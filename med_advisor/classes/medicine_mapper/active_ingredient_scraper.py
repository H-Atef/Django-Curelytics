from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import threading
import pandas as pd
from typing import Dict
import queue

import importlib

module1='med_advisor.classes.medicine_mapper.web_scraping_resources'
module2='med_advisor.classes.medicine_mapper.med_serializer'

wb=importlib.import_module(module1)
json_handler=importlib.import_module(module2)


from med_advisor import models,serializers




class DrugEyeActvIngScraper():
    def __init__(self):
        self.url = "http://www.drugeye.pharorg.com/drugeyeapp/android-search/drugeye-android-live-go.aspx"
        self.data={}

    def process_input(self, active_ingredients_dict: Dict):
        active_ingredients = [values[:4] for keys, values in active_ingredients_dict.items()]
        diseases = list(active_ingredients_dict.keys())
        return active_ingredients, diseases
    
    def search_medicines(self, inputs_list, input_type='By Active Ingredient'):
        
        def thread_function(input:str, results_list:list):
            try:
                data = self.scrape_page(input=input, input_type=input_type)
                results_list.extend(data)  # Store the result for the specific input
            except Exception as e:
                print(e)
                results_list.append({"actv_ing":"","drug_name":"","generic_name":"","drug_class":""}) # In case of error, store empty data

        threads = []
        results_list= []

        try:
            # Create a thread for each input in the inputs_list
            for input in inputs_list:
                thread = threading.Thread(target=thread_function, args=(input, results_list))
                threads.append(thread)
                thread.start()

            # Wait for all threads to complete
            for thread in threads:
                thread.join()


            return results_list

        except Exception as e:
            # Handle any exceptions that might occur
            return {}
        

    def scrape_page(self, input, input_type='By Active Ingredient'):
        try:
            # Check if the drug exists in the database
            medicine_info = models.ActvIngredientsMedInfo.objects.filter(actv_ing__icontains=input)
            if medicine_info.exists():
                serializer = serializers.ActvIngMedSerializer(medicine_info, many=True)
                return serializer.data
            
            # Initialize WebDriver and load the page
            driver = wb.WebScarpingToolInit().initialize_driver("google")
            driver.get(self.url)
            
            # Wait for input field and enter the search term
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "ttt"))).send_keys(input)

            # Click the relevant button based on input type
            if input_type == 'By Active Ingredient':
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "BG"))).click()
            else:
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "b1"))).click()

            # Extract table data
            table = driver.find_element(By.ID, "MyTable")
            table_html = table.get_attribute('outerHTML')
            data = self._extract_data(table_html)

            # Close driver
            driver.close()

            # Reconstruct and save data
            result_dict = {input: data}
            reconstructed_data = []
            
            for actv_ing, details in result_dict.items():
                df = pd.DataFrame(details)
                df['drug_name'] = df['drug_name'].str.strip()
                df['generic_name'] = df['generic_name'].str.strip()
                df['drug_class'] = df['drug_class'].str.strip()
                df['actv_ing'] = actv_ing
                reconstructed_data.extend(df.to_dict(orient="records"))

            # Bulk save to database
            instances = [models.ActvIngredientsMedInfo(**data) for data in reconstructed_data]
            models.ActvIngredientsMedInfo.objects.bulk_create(instances)

            return reconstructed_data

        except Exception as e:
            #print(f"Error during scraping: {e}")
            return []  # Return an empty list or handle as needed



    def scrape_data_by_actv_ing(self, active_ingredient):
        driver=None
        try:

            data_store = json_handler.JsonFileHandler().deserialize()

            self.data.update(data_store)

            # Check if the data for the active ingredient already exists
            if active_ingredient.strip(" ").lower() in [x.lower().strip(" ") for x in data_store.keys()]:
                return data_store[active_ingredient]

            driver = wb.WebScarpingToolInit().initialize_driver("google")
            driver.get(self.url)


            data=self.scrape_page(driver=driver,input=active_ingredient)

 
            self.data.update({active_ingredient:data})

            return data
        
        except Exception as e:
            #print(e)
            return {}
        finally:
            if driver:
                driver.close()

    def scrape_multiple_data(self, active_ingredients_dict):
        results = {}
        threads = []
        result_queue = queue.Queue()  # Thread-safe queue to collect results

        def thread_function(disease, active_ingredient):
            # Scrape data for this active ingredient and store in the result queue
            data = self.scrape_data_by_actv_ing(active_ingredient)
            result_queue.put((disease, active_ingredient, data))

        for disease, active_ingredients in active_ingredients_dict.items():
            for active_ingredient in active_ingredients[:4]:  # Only first 4 active ingredients
                thread = threading.Thread(target=thread_function, args=(disease, active_ingredient))
                threads.append(thread)
                thread.start()

        for thread in threads:
            thread.join()

        # Collect results from the queue
        while not result_queue.empty():
            disease, active_ingredient, data = result_queue.get()
            if disease not in results:
                results[disease] = {}
            results[disease][active_ingredient] = data

        # Serialize the updated data back to the file (append)
        json_handler.JsonFileHandler().serialize(self.data)

        return results

    def _extract_data(self, table_html):
        soup = BeautifulSoup(table_html, 'lxml')
        drug_names = []
        generic_names = []
        drug_classes = []

        rows = soup.find_all('tr')
        

        if rows!=[]:

            for i in range(len(rows) - 1):
                first_cell = rows[i].find('td')
                next_cell = rows[i + 1].find('td')


                if next_cell.has_attr("style"):
                    next_cell_style = next_cell.get('style')
                    next_cell_style = next_cell_style[:next_cell_style.index(";")]

                if first_cell.has_attr("style"):
                    cell_style = first_cell.get('style')
                    cell_style = cell_style[:cell_style.index(";")]

                    if 'color:Blue' == cell_style:
                        drug_names.append(first_cell.text)

                    if 'color:Green' == cell_style:
                        drug_classes.append(first_cell.text)

                    if 'color:Black' == cell_style:
                        generic_names.append(first_cell.text)

                    if 'color:Blue' == cell_style and next_cell_style == 'color:Green':
                        generic_names.append("-")

                    if 'color:Black' == cell_style and next_cell_style == 'color:BlueViolet':
                        drug_classes.append("-")

          
            
                

        data = {
                'drug_name': drug_names,
                'generic_name': generic_names,
                'drug_class': drug_classes
            }

        



        return data

# # Test the scraper with sample input
# scraper = DrugEyeActvIngScraper()

# output_example = {'common cold': ['Echinacea', 'Paracetamol (Acetaminophen)', 'Zinc Supplements', 'Ibuprofen', 'Vitamin C', 'Diphenhydramine']}

# json11 = scraper.scrape_multiple_data(output_example)

# import json
# with open('ex.json', 'w+') as file:
#     json.dump(json11, file)
