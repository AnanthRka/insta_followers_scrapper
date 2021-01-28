from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from getpass import getpass
from time import sleep

def login_choice(driver):
    try:
        f = open('usernames.txt','r+')
        usernames = [i.strip('\n') for i in f.readlines()]
        if len(usernames) >0 :
            print('List of previous users: ')
            count = 0
            for user in usernames:
                print(f"{usernames.index(user)+1}. {user.split(' ')[0]}")
            choose_username = input('Choose a number (If new user press Enter): ')
            if choose_username != '':
                login(driver, usernames[int(choose_username)-1].split(' '))
            else:
                login(driver)
        else:
            login(driver)
    except FileNotFoundError:
        f = open('usernames.txt','x')
        login(driver)

def login(driver, user_details = []):
    
    login_method = False

    driver.get('https://instagram.com')
    driver.maximize_window()

    if user_details == []:    
        method = input('Do you want to login through Facebook(y) or use Instagram(n)')
        if method == 'y':
            login_method = True
        username = input('Enter Phone number, username, or email: ')
        password = getpass('Enter password: ')
    else :
        if user_details[1] == 'f':
            login_method = True
        username = user_details[0]
        password = getpass(f'Enter password for {username}: ')

    if not login_method:
        
        driver.find_element_by_xpath('//*[@id="loginForm"]/div/div[1]/div/label/input').send_keys(username)
        driver.find_element_by_xpath('//*[@id="loginForm"]/div/div[2]/div/label/input').send_keys(password)
        driver.find_element_by_xpath('//*[@id="loginForm"]/div/div[3]/button/div').click()
        store_username(username, ' i')
    else:
        driver.find_element_by_xpath('//*[@id="loginForm"]/div/div[5]/button/span[2]').click()
        sleep(2)
        driver.find_element_by_xpath('//*[@id="email"]').send_keys(username)
        driver.find_element_by_xpath('//*[@id="pass"]').send_keys(password)
        driver.find_element_by_xpath('//*[@id="loginbutton"]').click()
        store_username(username, ' f')

    sleep(8)
    start_scrapping(driver)

def start_scrapping(driver):
    pass

def store_username(user, where):
    with open('usernames.txt','r+') as f:
        # if len(f.readlines())>0:
        #     f.seek(0)
        if user not in f.read():
            f.write(user + where)
        # else:
            # f.seek(0)
            # f.write(user + where)

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
