import requests
import re
from bs4 import BeautifulSoup


def extract_average_number(ss):
    num_list = []
    start = 0
    number_started = False
    for i, char in enumerate(ss):
        if not number_started and char in '1234567890':
            number_started = True
            start = i
        # chr(160) is not default space (not recognised as ' ')
        elif number_started and char not in '1234567890,. ' + chr(160):
            number_started = False
            raw_num = ss[start:i].replace(" ", "").replace(",", ".").replace(chr(160), '')
            if len(raw_num) >= 5:
                if raw_num[-3] == '.':
                    raw_num = raw_num[:-3]
                num_list.append(int(float(raw_num.replace(".", ''))))

    if not num_list:
        return "No info"
    else:
        return max(num_list)


full_data = []

url = 'https://hr.spbu.ru/konkursy.html'

file = open("Data", "w")
k = 0


print("Started parsing\n0%", end='')
while k <= 1830:
    k += 30
    if k == 900:
        k += 60
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    for form in soup.find_all('form', id="adminForm"):
        for link in form.find_all('a'):
            s = 'https://hr.spbu.ru' + link.get('href')
            if len(s) > 20 and s != 'https://hr.spbu.ru/konkursy.html' and '?' not in s:
                ans = requests.get(s)
                code = BeautifulSoup(ans.text, 'html.parser')
                name = code.find('h1', class_='title')
                file.write(name.text + "\n")
                requirements = code.article.ul
                requirements = requirements.text.replace('\n', '')
                file.write(requirements + "\n")
                salary = code.article
                for s in salary.text.split('\n'):
                    if 'Средняя заработная' in s or 'Размер средней' in s:
                        file.write(s)
                        file.write("\n "
                                   "-------------------------------------------------------------------------------- "
                                   "\n")
            elif len(s) > 20 and ('start=' + str(k)) in s:
                url = s
                break
    print(f'\r{round((k / 1830) * 100)}%', end='')

with open("Data", "r") as file:
    text = file.read().split("\n")
    del text[32:38]
    del text[392:404]
    del text[788:796]
    del text[4380:4392]


data = []

for index in range(len(text)):
    if text[index] != '':
        if index % 4 == 0:
            sep = text[index].split('(')
            data.append(sep[0].strip().capitalize())
            data.append(sep[-1].replace(')', '').strip().capitalize())

        if index % 4 == 1:
            data.append(text[index])

        if index % 4 == 2:
            data.append(extract_average_number(text[index]))
            full_data.append(data)

        if index % 4 == 3:
            data = []


for part in full_data:
    if part[3] == 'No info' or part[1] == '0,25+0,25':
        full_data.remove(part)
    else:
        if part[0] == 'Старший преподаватель-практик':
            part[0] = 'Старший преподаватель – практик'
        if part[1] == 'Прикладная математика - процессы управления':
            part[1] = 'Прикладная математика – процессы управления'

dataset = {
    re.sub(r'[^|\w\s]', ' ',
           '|'.join(map(str, entry)).lower())
    for entry in full_data}
with open('dataset_backup.txt', 'w') as f:
    f.write('\n'.join(dataset))

dataset = {
    re.sub(r'[^|\w\s]', ' ',
           '|'.join([' '.join(entry[:3]), str(entry[3])]).lower())
    for entry in full_data}
with open('dataset_backup3in1.txt', 'w') as f:
    f.write('\n'.join(dataset))
