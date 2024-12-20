# Django Curelytics (Medicine Data Hub)

## Project Overview

**Curelytics** is a powerful, data-driven Django web application designed to deliver comprehensive insights into the pharmaceutical industry, focusing on medicine data, price tracking, and AI/ML-driven disease prediction. The project integrates three specialized apps that work together to provide users with valuable tools for understanding medicines, tracking their prices, and predicting potential diseases based on symptoms. 💊📊🤖

The three core apps in **Django Curelytics** are:

### 1. Medicine Web Scraper 🕸️

This application scrapes data from various online sources, gathering key details about medicines. This includes drug names, active ingredients, and other relevant product specifications. The scraper ensures that the data is up-to-date, offering users the latest available information about medications in the market.

### 2. Medicine Price Tracker 💵

This app focuses on tracking the prices of medicines across multiple pharmacies. It enables users to compare the prices of different drugs, check price fluctuations, and review the number of registrations for specific medicines. It includes CRUD (Create, Read, Update, Delete) operations, allowing users to manage and search through medicine price data efficiently.

### 3. Medicine Advisor (AI/ML Model) 🤖💡

This app uses (AI/ML) models to predict diseases based on user-inputted symptoms. Leveraging advanced algorithms, such as the Groq AI model or custom-built model, the **Medicine Advisor** maps predicted diseases to active ingredients and then links them to available medicines in the market. This feature empowers users to find relevant treatment options based on the diseases predicted by the system.

## Project Aims 🎯

The primary aim of **Django Curelytics** is to serve as an all-in-one platform that combines **medicine data, price tracking, and disease prediction**. The key objectives include:

- **Providing comprehensive medicine information**: Offering users accurate details on medicines, including active ingredients and product specifications. 🧴
- **Tracking medicine prices**: Helping users compare prices for medicines across different pharmacies and track the number of registrations for specific drugs in various locations. 💸
- **Predicting diseases based on symptoms**: Utilizing AI and machine learning models to predict possible diseases from the user’s symptoms and suggest potential medicines based on active ingredients linked to the predicted disease. 🧠
- **Mapping active ingredients to available medicines**: Providing a comprehensive mapping of diseases to active ingredients and subsequently mapping those ingredients to available medicines, making it easier for users to find treatments. 🏥

Overall, **Django Curelytics** aims to offer a **multifaceted solution** for healthcare and pharmaceutical information, empowering users with the knowledge they need to make informed decisions about medicines and potential health issues. 🌍💡

## Main Concepts & Technologies  🛠️

- **Object-Oriented Programming (OOP):** The project utilizes **OOP principles** to organize the codebase, ensuring that the application remains modular, maintainable, and scalable. This paradigm allows for better code reuse, making it easier to extend and manage the project. 🖥️
- **Threading Techniques:** To optimize the performance of the **Medicine Web Scraper**, **threading techniques** are employed. These allow the scraper to work concurrently, which speeds up the process of collecting data from multiple sources and improves the efficiency of data gathering. ⏱️
- **Pandas:** **Pandas** is used extensively for data manipulation, cleaning, and analysis. It simplifies handling large datasets, transforming raw data into meaningful information that can be processed, analyzed, and integrated into other parts of the application. 📊
- **Scikit-learn (sklearn):** For the **AI/ML model**, **Scikit-learn** is used to build disease prediction models. These models predict diseases based on user-input symptoms and then map those predictions to active ingredients and medicines, helping users find relevant treatments. 🧬

## Disclaimer ⚠️

**Django Curelytics** is developed **for educational purposes only**. While the **Medicine Advisor** app provides disease predictions and medicine recommendations based on AI/ML models, these predictions should **never be treated as professional medical advice**. Users should consult healthcare professionals or licensed medical experts for diagnosis, treatment, and medication decisions. The information provided by this platform is meant to assist in general understanding and should not replace professional healthcare guidance. Always prioritize medical professionals when making health-related decisions.🩺
