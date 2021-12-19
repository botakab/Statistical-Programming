import csv
import time
import random
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_uni_data(uni_items):
    # each row of the table is a university
    unis = []
    for uni in uni_items:
        try:
            # we go to the page of the university
            link = URL + uni.find('a', class_="title")['href']
            driver.get(link)
            time.sleep(2)
            uni_page = driver.page_source
            uni_soup = BeautifulSoup(uni_page, 'html.parser')

            # get data from the university page
            uni_name = uni_soup.find('div', class_="title_info").find('h1').text
            university = {'Name': uni_name}
            uni_country = uni_soup.find('div', class_='con-map')
            if uni_country:
                university['Country'] = uni_country.text.replace(' View map', '')
            else:
                continue

            # general stats
            uni_stats = uni_soup.find('div', class_="uni_stats")
            stats_labels = uni_stats.find_all('label')
            stats_vals = uni_stats.find_all('div', class_='val')

            for label, val in zip(stats_labels, stats_vals):
                university[label.text] = val.text

            # detailed stats
            criteria = uni_soup.find('div', class_="ranks-wrapper").find_all('div', class_="criteria")
            for criterium in criteria:
                word = criterium.text.strip().split(':')
                university[word[0]] = word[1]

            int_students = uni_soup.find('div', class_="student line").find_all('h4')[1].text
            university['Number of International Students'] = int_students.split('-')[1].strip()
            if university['Number of International Students'] == '':
                continue

            int_faculty = uni_soup.find('div', class_="faculty").find('div', class_='gr').find('div').text
            university['Number of International Faculty'] = int_faculty.strip()
            if university['Number of International Faculty'] == '':
                continue

            print(uni_name)
            print(len(unis))

            # add if the number of features is equal or more than 16
            unis.append(university)  # add this university to the list
        except:
            continue
    return unis


# links
URL = "https://www.topuniversities.com/"
rank21 = "university-rankings/world-university-rankings/2021"
link = URL + rank21
driver = webdriver.Safari()
universities = []


def get_page(n):
    driver.get(link)
    time.sleep(2)
    try:
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="qs-rankings_length"]/label/span[2]/span[2]'))).click()
        time.sleep(2)
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="qs-rankings_length"]/label/span[2]/div/div/span/span/ul/li[4]'))).click()
        for j in range(n):
            WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="qs-rankings_next"]'))).click()
            time.sleep(2)
    except:
        get_page(n)


# we iterate 5 times, each page contains 200 unis and overall 1000 unis
for i in range(5):
    get_page(i)
    # get html of the page
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')

    # finding table of ranking from the html
    table = soup.find('table', id='qs-rankings').find('tbody')
    items = table.find_all('tr')

    # random sampling
    items = random.sample(items, 50)

    # iterating through all the universities and storing their data the in the list
    universities.extend(get_uni_data(items))


# write to csv
fields = universities[0].keys()
with open('data.csv', 'w', newline='') as file:
    dict_writer = csv.DictWriter(file, fields, extrasaction='ignore')
    dict_writer.writeheader()
    dict_writer.writerows(universities)

