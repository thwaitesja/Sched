# Pulls any Excel sheet from sched: for mentors, sponsors, or speakers and also can push a spreadsheet to sched called
# as the second argument or when asked for input

import lxml.html
import sys
import os
import subprocess
try:
    from requests import Session
except:
    subprocess.call(["pip", "install", 'requests'])
    from requests import Session

user="sched username"
password="sched password"

Site = "https://stampede2020.sched.com"
Login_URL= Site+"/editor/login"
get_URL = {
    "mentors": Site+"/editor/exports/endpoint?action=artists",
    "sponsors": Site+"/editor/exports/endpoint?action=sponsors",
    "speakers": Site+"/editor/exports/endpoint?action=speakers",
}

post_URL = {
    "mentors": Site+"/editor/artists#people-artists",
    "sponsors": Site+"/editor/artists#people-sponsors",
    "speakers": Site+"/editor/artists#add",
}

post_Filename = {
    "mentors": 'Stampede_Loaded_Mentors.xlsx',
    "sponsors": 'Stampede_Loaded_Sponsors.xlsx',
    "speakers": 'Stampede_Loaded_Speakers.xlsx',
}

Folder= "copy/"
get_Filename= {key: Folder + post_Filename[key] for key in post_Filename}


class Sched():
    def __init__(self):
        self.session = Session()
        login = self.session.get(Login_URL)
        login_html = lxml.html.fromstring(login.text)
        hidden_inputs = login_html.xpath(r'//form//input[@type="hidden"]')
        form = {x.attrib["name"]: x.attrib["value"] for x in hidden_inputs}
        form['l[password]'] = password
        form['l[username]'] = user
        self.session.post(Login_URL, data=form, allow_redirects=True)

    def pull_xlsx(self, filename, url):
        if not os.path.exists(Folder):
            os.makedirs(Folder)
        with open(filename, 'wb') as my_file:
            response = self.session.get(url)
            my_file.write(response.content)

    def push_xlsx(self, filename, url):
        with open(filename, 'rb')as f:
            files = {'users': (filename, f, 'application/vnd.ms-excel')}
            form = {'what': "importPeople", "data[commit]": "false", "data[sendinvites]": "false"}
            self.session.post(url, data=form, files=files)

            files = {'users': (filename, f, 'application/vnd.ms-excel')}
            form = {'what': "importPeople", "data[commit]": "true", "data[sendinvites]": "false"}
            self.session.post(url, data=form, files=files)

    def update(self, group):
        if group in post_URL:
            self.push_xlsx(post_Filename[group], post_URL[group])
        else:
            print(f"{group} is not a valid input. Input must be one of: {[item for item in post_URL]}")

    def get_copy(self, group):
        if group in get_URL:
            self.pull_xlsx(get_Filename[group], get_URL[group])
        else:
            print(f"{group} is not a valid input. Input must be one of: {[item for item in get_URL]}")


def main(argv):
    my_schedule = Sched()
    if not argv:
        argv = input(f"What command(s): {[item for item in get_URL]}? Include -w (no space before) for push commands\n").split()
    for command in argv:
        if command[-2:]== "-w":
            my_schedule.update(command[:-2].lower())
        else:
            my_schedule.get_copy(command.lower())



if __name__ == "__main__":
   main(sys.argv[1:])