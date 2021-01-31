from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from getpass import getpass
from time import sleep
import csv
import sys

def login_choice(driver):
    try:
        f = open('usernames.txt','r+')
        usernames = [i.strip('\n') for i in f.readlines()]
        
        driver.get('https://instagram.com')
        driver.maximize_window()

        if len(usernames) >0 :
            print('List of previous users: ')
            count = 0
            for user in usernames:
                print(f"{usernames.index(user)+1}. {user.split(' ')[0]}")
            print()
            choose_username = input('Choose a number if you are in the above list (If new user press Enter): ')

            if choose_username != '':
                login(driver, usernames[int(choose_username)-1].split(' '))
            else:
                login(driver)
        else:
            login(driver)

    except FileNotFoundError:
        f = open('usernames.txt','x')
        login(driver)

def login(driver, user_details = [],login_method=False, retry = False,count =1):
    
    if user_details == []:    
        if not retry:
            method = input('Do you want to login through Facebook(y) or use Instagram(n)')
            if method == 'y':
                login_method = True
        username = input('Enter Phone number, username, or email: ')
        password = getpass(f'Enter password for {username}: ')
    
    else :
        if not retry:
            if user_details[1] == 'f':
                login_method = True
        username = user_details[0]
        password = getpass(f'Enter password for {username}: ')
    
    try:
        if not login_method:

            driver.find_element_by_xpath('//*[@id="loginForm"]/div/div[1]/div/label/input').send_keys(username)
            driver.find_element_by_xpath('//*[@id="loginForm"]/div/div[2]/div/label/input').send_keys(password)
            driver.find_element_by_xpath('//*[@id="loginForm"]/div/div[3]/button/div').click()
            store_username(username, ' i')
        
        else:

            if not retry:
                driver.find_element_by_xpath('//*[@id="loginForm"]/div/div[5]/button/span[2]').click()
                sleep(2)
            driver.find_element_by_xpath('//*[@id="email"]').send_keys(username)
            driver.find_element_by_xpath('//*[@id="pass"]').send_keys(password)
            driver.find_element_by_xpath('//*[@id="loginbutton"]').click()
            store_username(username, ' f')
        sleep(8)

        if driver.current_url != 'https://www.instagram.com/':
            driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div[2]/div/div/div/div/div[3]/button').click()
            sleep(2)
            driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div/div/div/div[2]/button/div/div').click()
            sleep(2)
        driver.find_element_by_class_name('gmFkV').click()
        sleep(2)

        start_scrapping(driver)
    
    except NoSuchElementException:
        count+=1
        if count == 4:
            print('You have made 3 unsuccessful login attempts, relax yourself and come again when you are sure.')
            driver.quit()
            sys.exit()
        if count == 2:
            print()
            print('Two more login attempts remaining, choose wisely.')
        print()
        if user_details != []:
            print('Incorrect password')
        else:
            print('Incorrect username or password')
        
        print()
        login(driver,user_details, login_method, True, count )

def start_scrapping(driver):

    driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/header/section/ul/li[2]/a').click()
    sleep(2)
    
    popup_body  = driver.find_element_by_xpath("//div[@class='isgrP']")

    # Get scroll height.
    last_height = driver.execute_script("return arguments[0].scrollHeight",popup_body)

    while True:

        # Scroll down to the bottom.
        driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);",popup_body)
        sleep(1)

        # Calculate new scroll height and compare with last scroll height.
        new_height = driver.execute_script("return arguments[0].scrollHeight",popup_body)

        if new_height == last_height:
            sleep(2)
            break

        last_height = new_height

    page = driver.page_source
    soup = BeautifulSoup(page, 'lxml')
    driver.close()

    li_tags_data =[i.text[:len(i.text)-6] for i in soup.find_all('li') if 'Remove' in i.text]
    
    store_followers_details(li_tags_data)
    


def store_username(user, where):
    with open('usernames.txt','r+') as f:
        if user not in f.read():
            f.write(user + where)


def store_followers_details(list_followers):
    
    followers = []
    try:
        for i in list_followers:
            if 'Follow' in i:
               a =i.split('Follow')
               a.append('Follow')
               followers.append(a)
            else:
                followers.append(i.split(' ',1))
        headers = ['Username', 'Name', 'Follow']
        with open('followers.csv','w',encoding="utf-8") as f:
            csv_writer = csv.writer(f)

            csv_writer.writerow(headers)
            csv_writer.writerows(followers)

    except FileNotFoundError:
        f = open('followers.csv','x')
        f.close()
        store_followers_details(list_followers)



if __name__ == '__main__':
    option = webdriver.ChromeOptions()
    # option.add_argument('--headless')
    option.add_argument("--log-level=3")
    option.add_experimental_option('excludeSwitches', ['enable-logging'])
    prefs = {"profile.default_content_setting_values.notifications" : 2}
    option.add_experimental_option("prefs",prefs)
    CDM = ChromeDriverManager(log_level='0')
    driver = webdriver.Chrome(CDM.install(), options=option)
    
    login_choice(driver)

    driver.quit()
