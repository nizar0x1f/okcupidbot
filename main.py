from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.support import expected_conditions as EC
import json
import time
import os


DRIVER_PATH = './chromedriver.exe'
def init_driver():
    """ save browser cookies and session to avoid login everytime """
    options = webdriver.ChromeOptions()
    options.add_argument("user-data-dir=./chrome_profile")
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    options.add_argument('--remote-debugging-port=3332')
    options.add_argument('--blink-settings=imagesEnabled=false')
    try:
        driver = webdriver.Chrome(executable_path=DRIVER_PATH, options=options)
    except Exception as e:
        print(e)
    return driver

def login_get_cookies(driver):
    user_name = os.environ.get("OKCUPID_USERNAME")
    password = os.environ.get("OKCUPID_PASSWORD")
    driver.get("https://www.okcupid.com/login")
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "login-header-title-LOGIN")))
        driver.find_element(By.ID, "username").send_keys(user_name)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.CLASS_NAME, "login-actions-button").click()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "login-header-title-SMS_CODE_INPUT")))
        time.sleep(3)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "upgrade-link-premium")))

        cookies = driver.get_cookies()
        with open('cookies.json', 'w') as fp:
            json.dump(cookies, fp)

        
        return driver
    
    except Exception as e:
        print(e)
        return driver
    
def go_to_question_page(driver, question_page):
    driver.get(question_page)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "profile-questions-userinfo-photos"))) 
    time.sleep(3)
    return driver

def respond_to_questions(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    wait = WebDriverWait(driver, 10)
    questions = driver.find_elements(By.XPATH, "//li[contains(@class, 'profile-question')]") 
    try:
        for question in questions:  
            time.sleep(2)
            driver.execute_script("arguments[0].scrollIntoView();", question)
            if question.find_element(By.CLASS_NAME, "profile-question-action").text == "ANSWER":   
                question.find_element(By.CLASS_NAME, "profile-question-action").click()
                time.sleep(2)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "profile-questions-answer-modal")))
                driver.find_element(By.CLASS_NAME, "oknf-radio-decoration").click()
                driver.find_elements(By.CLASS_NAME, "oknf-checkbox-decoration")[0].click()       
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                driver.find_element(By.CLASS_NAME, "questionspage-buttons-button--answer").click()
                questions = driver.find_elements(By.XPATH, "//li[contains(@class, 'profile-question')]")
    except Exception as e:
        print(e)
        return driver

def match_answers(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    wait = WebDriverWait(driver, 10)
    questions = driver.find_elements(By.XPATH, "//li[contains(@class, 'profile-question')]")
    try:
        for question in questions:
            time.sleep(2)
            driver.execute_script("arguments[0].scrollIntoView();", question)
            other_user_answer = question.find_element(By.CLASS_NAME, "profile-question-answer").text
            print(other_user_answer)
            if question.find_element(By.CLASS_NAME, "profile-question-action").text == "RE-ANSWER":   
                question.find_element(By.CLASS_NAME, "profile-question-action").click()
                time.sleep(2)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "profile-questions-answer-modal")))
                driver.find_element(By.CLASS_NAME, "oknf-radio-decoration").click()
                
                available_answers = driver.find_elements(By.XPATH, "//label[contains(@class, 'oknf-radio oknf-radio--has-label')]")
                for answer in available_answers:
                    if answer.text == other_user_answer:
                        answer.click()
                        break
                accpeted_answers = driver.find_elements(By.XPATH, "//label[contains(@class, 'oknf-checkbox oknf-checkbox--has-label')]")
                for ac_answer in accpeted_answers:
                    if ac_answer.get_attribute("aria-checked") == "true":
                        ac_answer.click()
                        break
                for ac_answer in accpeted_answers:
                    span = ac_answer.find_element(By.CLASS_NAME, "oknf-checkbox-decoration")
                    print(ac_answer.text)
                    span.click()
                    print ("clicked accepted answer")      
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                driver.find_element(By.CLASS_NAME, "questionspage-buttons-button--answer").click()
                questions = driver.find_elements(By.XPATH, "//li[contains(@class, 'profile-question')]")
    except Exception as e:
        print(e)
        return driver
    
def main():
    user_id = input("Enter user id: ")
    action = input("Enter 0 to login, 1 to fill or 2 to match: ")

    if action == "1":
        action = "fill"
    elif action == "2":
        action = "match"
    elif action == "0":
        driver = init_driver()
        driver = login_get_cookies(driver)
        driver.close()
        return 0
    else:
        print("invalid input")
        return 0

    if action == "fill":
        question_page=f"https://www.okcupid.com/profile/{user_id}/questions?cf=profile+match+score&filter_id=11"
    elif action == "match":
        question_page= f"https://www.okcupid.com/profile/{user_id}/questions?cf=profile%2Bmatch%2Bscore&filter_id=10"
    while True:
        try:
            driver = init_driver()         
            driver = go_to_question_page(driver, question_page)
            try:    
                if action == "fill":
                    driver = respond_to_questions(driver)
                elif action == "match":
                    driver = match_answers(driver)
            except Exception as e:
                    pass
        except Exception as e:
            pass

if __name__ == "__main__":
    main()



 