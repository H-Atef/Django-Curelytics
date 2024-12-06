from typing import List, Dict
from groq import Groq
import importlib
import time

module1 = 'med_advisor.classes.active_ingredients_mapper.ai_model_auth'

class GroqActvIngMapper:
    def __init__(self):
        self.groq_client = Groq(api_key=importlib.import_module(module1).API_KEY)

    def map_diseases(self, diseases_list: List) -> Dict:
        attempt = 0
        max_attempts = 7
        while attempt < max_attempts:
            try:
                # Make API request for mapping diseases with active ingredients
                chat_completion = self.groq_client.chat.completions.create(
                    messages=[{
                        "role": "user",
                        "content": f"""
                            For the following list of diseases: {diseases_list}, I would like the following information:

                            1. Map each disease to its appropriate active ingredients.
                            1. Map each disease to its appropriate active ingredients.
                            1. Map each disease to its appropriate active ingredients.
                            1. Map each disease to its appropriate active ingredients.
                            2. For each disease, return the first-line treatment (primary), second-line, and third-line active ingredients, in that order.
                            2. For each disease, return the first-line treatment (primary), second-line, and third-line active ingredients, in that order.
                            2. For each disease, return the first-line treatment (primary), second-line, and third-line active ingredients, in that order.
                            3. For each active ingredient, include the generic name. If the active ingredient has a different commonly used name, provide it in parentheses.
                            3. For each active ingredient, include the generic name. If the active ingredient has a different commonly used name, provide it in parentheses.
                            3. For each active ingredient, include the generic name. If the active ingredient has a different commonly used name, provide it in parentheses.
                            4. Format the output as a Python dictionary where the keys are disease names and the values are lists of 3 active ingredients.
                            4. Format the output as a Python dictionary where the keys are disease names and the values are lists of 3 active ingredients.
                            4. Format the output as a Python dictionary where the keys are disease names and the values are lists of 3 active ingredients.
                            5. The list for each disease should contain exactly 3 active ingredients: the first-line treatment (primary), second-line treatment, and third-line treatment (alternatives).
                            5. The list for each disease should contain exactly 3 active ingredients: the first-line treatment (primary), second-line treatment, and third-line treatment (alternatives).
                            5. The list for each disease should contain exactly 3 active ingredients: the first-line treatment (primary), second-line treatment, and third-line treatment (alternatives).
                            6. Ensure the active ingredients are ordered from primary to alternatives.
                            6. Ensure the active ingredients are ordered from primary to alternatives.
                            6. Ensure the active ingredients are ordered from primary to alternatives.
                            7. I want the output dict like the following example: 'disease':['primary first line active ingredient','second line alternative1','third line alternative2']
                            7. I want the output dict like the following example: 'disease':['primary first line active ingredient','second line alternative1','third line alternative2']
                            7. I want the output dict like the following example: 'disease':['primary first line active ingredient','second line alternative1','third line alternative2']
                            8. the output is dict include disease as a key and values are lists of strings data type don't change this format
                            8. the output is dict include disease as a key and values are lists of strings data type don't change this format
                            8. the output is dict include disease as a key and values are lists of strings data type don't change this format
                            9. don't mention any drug name just the active ingredient
                            9. don't mention any drug name just the active ingredient
                            9. don't mention any drug name just the active ingredient
                            10. If there is any invalid disease or if input disease not found just remove it from the dictionary 
                            10. If there is any invalid disease or if input disease not found just remove it from the dictionary 
                            10. If there is any invalid disease or if input disease not found just remove it from the dictionary 
                            11. Provide the dictionary output only between ``` ``` not the code just the dictionary, with no additional explanations or clarifications.
                            11. Provide the dictionary output only between ``` ``` not the code just the dictionary, with no additional explanations or clarifications.
                            11. Provide the dictionary output only between ``` ``` not the code just the dictionary, with no additional explanations or clarifications.

                        """
                    }],
                    model="llama3-8b-8192",  # Assuming Groq uses Llama3 model
                )

                # Parse the result from the API (assuming it's a string representation of a list of tuples)
                predictions = chat_completion.choices[0].message.content

                # Return the result after splitting the dictionary content
                return eval(predictions.split('```')[1])

            except Exception as e:
                attempt += 1
                if attempt < max_attempts:
                    print(f"Attempt {attempt} failed. Retrying...")
                    time.sleep(2)  # Wait for 2 seconds before retrying
                else:
                    print(f"Max attempts reached.")
                    return {}

