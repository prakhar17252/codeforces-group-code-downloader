import os, time, getpass, sys, io
from selenium import webdriver
path = os.path.join(os.getcwd(), "chromedriver")
driver = webdriver.Chrome(path)
login_url = 'http://{domain}.contest.codeforces.com/enter'
url = ''
con_url = ''
con_num = ''
wait = 3

def print_table(table):
    s = ''
    for row in table:
        for col in row:
            s += col + ' '
        s += '\n'
    return s

def login():
    global url
    print("Domain Name: ", end = '')
    domain = input()
    driver.get(login_url.format(domain = domain))
    print("Handle/Email: ", end = '')
    han = input()
    pwd = getpass.getpass()

    try:
        username = driver.find_element_by_name("handleOrEmail")
        password = driver.find_element_by_name("password")
    except:
        print ("Incorrect Domain Name")
        driver.quit()
        exit(0)

    username.send_keys(han)
    password.send_keys(pwd)

    driver.find_element_by_class_name("submit").click()
    time.sleep(wait)
    url = driver.current_url

    if url.find('/blog') == -1:
        print ("Incorrect Handle/Email/Password")
        driver.quit()
        exit(0)

    url = url[:-5] + '/'

def open_contest_page():
    global con_url, con_num
    print("Contest Number: ", end = '')
    con_num = input()
    con_url = url + 'contest/' + con_num + '/'
    driver.get(con_url)

def get_standings():
    driver.get(con_url + 'standings')
    
    if con_num not in driver.current_url:
        print("Incorrect Contest ID")
        driver.quit()
        exit(0)

    standings = driver.find_element_by_class_name("datatable").text

    buf = io.StringIO(standings)

    f = open('standings.txt', 'w+')
    A = [['Rank', 'Name', 'Solved', 'Penalty']]

    while True:
        curr = buf.readline().split()
        if curr[0] == 'Tried':
            break
        try:
            rank = int(curr[0])
            name = curr[1]
            solved = int(curr[2])
            penalty = int(curr[3])
            A.append(curr[ : 4])
        except:
            pass

    f.write(print_table(A))
    f.close()

def parse_submission(sub_id):
    driver.get(con_url + 'submission/' + sub_id)
    code = driver.find_element_by_xpath("//*[@id=\"pageContent\"]/div[3]/pre").text
    code.replace('&amp;', '&')        
    code.replace('&lt;', '<')        
    code.replace('&gt;', '>')        
    code.replace('&quot;', '\"')        
    code.replace('&apos;', "'")        
    code.replace('\r', '')
    if sub_id not in driver.current_url:
        print("You don't have access to submission " + sub_id)
        driver.quit()
        exit(0)
    return code

def get_ext(data):
    langs = {'C++': 'cpp', 'Java': 'java', 'Python': 'py', 'PyPy' : 'py', 'FPC': 'pas', 'C#': 'cs', 'C': 'c',}
    for lang in langs.keys():
        for x in data:
            if lang in x:
                return '.' + langs[lang]
    return '.txt'

def get_submissions():
    page = 2
    prev_url = con_url + 'status/'
    while True:
        driver.get(prev_url)
        submissions = driver.find_element_by_class_name("datatable").text
        buf = io.StringIO(submissions[2:] + '\nend')
        while True:
            data = buf.readline().split()
            if len(data) == 0 or data[0] == 'end':
                break
            if 'Accepted' not in data:
                continue
            sub_id = data[0]
            name = data[3]
            prob = data[data.index('-') - 1]
            code = parse_submission(sub_id)
            extension = get_ext(data)

            if not os.path.exists(prob):
                os.mkdir(prob)
            
            filename = os.getcwd() + '\\' + prob + '\\' + name + extension

            f = open(filename, 'w+')
            f.write(code)
            f.close()
        try:
            driver.find_element_by_link_text(str(page)).click()
            time.sleep(wait)
            prev_url = driver.current_url
            page += 1
        except:
            break
        
if __name__ == "__main__":
    login()
    open_contest_page()
    get_standings()
    get_submissions()
    driver.quit()
    print ("Execution Successful! :D")
