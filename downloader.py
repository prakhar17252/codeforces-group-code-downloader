'''
	Needs Google Chrome and chromedriver to work. 
	If you don't have chromedriver, download it from http://chromedriver.chromium.org/downloads, making sure that it is the right one for your chrome verison.
	Keep chromedriver in the same folder as this file.

	Domain Name is the group name used in the url.
	Example: If the group url is abc.contest.codeforces.com, the domain name is abc.
	If your group doesn't have a domain name, create one in the group settings.

	Contest Number is the number that appears in the URL of the contest page.
	Example: In the contest with URL http://abc.contest.codeforces.com/group/0U62CQraSv/contest/227731, the contest number is 227731.

	Use only IDs with manager access to the group.
'''

__author__ = "Prakhar Gupta(prakhar17252)"

import os, time, getpass, io
from selenium import webdriver
path = os.path.join(os.getcwd(), 'chromedriver')
driver = webdriver.Chrome(path)
login_url = 'http://{domain}.contest.codeforces.com/enter'
url = ''
contest_url = ''
contest_num = ''
wait = 2

done = set()

def print_table(table):
	data = ''
	for row in table:
		for col in row:
			data += col + ' '
		data += '\n'
	return data

def login():
	global url
	print ('Domain Name: ', end = '')
	domain = input()
	driver.get(login_url.format(domain = domain))
	print ('Handle/Email: ', end = '')
	han = input()
	pwd = getpass.getpass()

	try:
		username = driver.find_element_by_name('handleOrEmail')
		password = driver.find_element_by_name('password')
	except:
		print ('Incorrect Domain Name')
		driver.quit()
		exit(0)

	username.send_keys(han)
	password.send_keys(pwd)

	driver.find_element_by_class_name('submit').click()
	time.sleep(wait)
	url = driver.current_url

	if url.find('/blog') == -1 and url.find('/contests') == -1:
		print ('Incorrect Handle/Email/Password')
		driver.quit()
		exit(0)

	url = url.replace('/contests', '/')
	url = url.replace('/blog', '/')

def open_contest_page():
	global contest_url, contest_num
	print ('Contest Number: ', end = '')
	contest_num = input()
	contest_url = url + 'contest/' + contest_num + '/'
	driver.get(contest_url)

def get_standings():
	driver.get(contest_url + 'standings/')
	
	if contest_num not in driver.current_url:
		print ('Incorrect Contest ID')
		driver.quit()
		exit(0)

	try:
		standings = driver.find_element_by_class_name('datatable').text
	except:
		time.sleep(5)
		print ('Incorrect Contest ID')
		driver.quit()
		exit(0)		

	buf = io.StringIO(standings)

	f = open('standings.txt', 'w+')
	A = [['Rank', 'Name', 'Solved', 'Penalty']]

	while True:
		curr = buf.readline().split()
		if curr[0] == 'Tried':
			break
		try:
			rank, name, solved, penalty = int(curr[0]), curr[1], int(curr[2]), int(curr[3])
			A.append(curr[ : 4])
		except:
			pass

	f.write(print_table(A))
	f.close()

def parse_submission(sub_id):
	driver.get(contest_url + 'submission/' + sub_id)
	try:
		code = driver.find_element_by_id('program-source-text').text
	except:
		print ('You don\'t have access to submission ' + sub_id)
		driver.quit()
		exit(0)
	if sub_id not in driver.current_url:
		print ('You don\'t have access to submission ' + sub_id)
		driver.quit()
		exit(0)
	return code

def get_ext(data):
	langs = {'C++': 'cpp', 'Java': 'java', 'Python': 'py', 'PyPy' : 'py', 'FPC': 'pas', 'C#': 'cs', 'C': 'c'}
	for lang in langs.keys():
		for x in data:
			if lang in x:
				return '.' + langs[lang]
	return '.txt'

def get_submissions():
	page = 2
	prev_url = contest_url + 'status/page/1?order=BY_ARRIVED_ASC'
	driver.get(prev_url)
	while True:
		submissions = driver.find_element_by_class_name('datatable').text
		buf = io.StringIO(submissions[2:] + '\nend')
		while True:
			data = buf.readline().split()
			if len(data) == 0 or data[0] == 'end':
				break
			if 'Accepted' not in data:
				continue
			sub_id, name, prob = data[0], data[3], data[data.index('-') - 1]
			if name[-1] == ':': name = name[:-1]

			filebasename = name + '-' + prob
			
			if filebasename in done:
				continue

			done.add(filebasename)

			code = parse_submission(sub_id)
			extension = get_ext(data)

			if not os.path.exists(prob):
				os.mkdir(prob)
			
			filename = os.getcwd() + '\\' + prob + '\\' + filebasename + extension

			f = open(filename, 'w+')
			f.write(code)
			f.close()
		try:
			driver.get(prev_url)
			driver.find_element_by_link_text(str(page)).click()
			time.sleep(wait)
			prev_url = driver.current_url
			page += 1
		except:
			break
		
if __name__ == '__main__':
	login()
	open_contest_page()
	start_time = time.time()
	get_standings()
	get_submissions()
	end_time = time.time()
	driver.quit()
	print ('Execution Successful! :D')
	print ('Execution time %d seconds' % int(end_time - start_time))
