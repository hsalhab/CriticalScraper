from constants import DEPARTMENTS, COOKIES, CRITICAL_REVIEW, MODES
import requests
from bs4 import BeautifulSoup
import pandas as pd

requests.packages.urllib3.disable_warnings() 

def get_courses():
    course_list = []
    for dept in DEPARTMENTS:
        url = CRITICAL_REVIEW + "/search/" + dept
        try:
            page = requests.get(url, cookies=COOKIES, verify=False)
            soup = BeautifulSoup(page.text, 'html.parser')
            semester_html = soup.select("td[class=semester]")
            course_html = soup.select("a[class=course_code_link]")
            prof_html = soup.select("td[class=professor]")
            for i in range(len(semester_html)):
                semester = semester_html[i].text.split(" ")
                year = int(semester[0])
                season = semester[1]
                prof = prof_html[i].text.strip()
                course_url = course_html[i]["href"]
                title = course_html[i].text.strip()
                if year > 2010 and season == "Fall":
                    course_list.append([title, year, course_url, prof])
                
        except Exception as e:
            print(e)
            return
    return course_list

def get_rated_courses():
    course_list = get_courses()
    elite_list = []
    for course in course_list:
        url = CRITICAL_REVIEW + course[2]
        try:
            page = requests.get(url, cookies=COOKIES, verify=False)
            soup = BeautifulSoup(page.text, 'html.parser')
            max_hours = float(soup.select("table[class=right_float_table] td")[3].select("div[class=value]")[0].text.strip())
            avg_hours = float(soup.select("table[class=right_float_table] td")[2].select("div[class=value]")[0].text.strip())
            if avg_hours < 2.2 or max_hours < 5.8:
                print([course[0], course[1], avg_hours, max_hours, course[3], url])
                elite_list.append([course[0], course[1], avg_hours, max_hours, course[3], url])
        except Exception as e:
            print(e)
            return
    
    df = pd.DataFrame(elite_list, columns=["Title", "Rating Year", "Average Hours", "Max Hours", "Professor", "Link"])
    df = df.sort_values("Max Hours", ascending=True)
    df.to_csv('result.csv')

get_rated_courses()