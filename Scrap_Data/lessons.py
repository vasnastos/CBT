import requests
from bs4 import BeautifulSoup
import os
import json
import re

# <tr>
# <td style="text-align: center;"  width="2%">101</td>
# <td style="text-align: center;"  colspan="2" width="18%">Υ</td>
# <td style="text-align: center;"  width="54%"><a class="one" href="http://83.212.170.184/lessons.php?id=1" target="_blank"><b>ΓΡΑΜΜΙΚΗ ΑΛΓΕΒΡΑ</b></a></td>
# <td style="text-align: center;"  width="2%">4</td>
# <td style="text-align: center;"  width="3%">3</td>
# <td style="text-align: center;"  width="4%">1</td>
# <td style="text-align: center;"  width="2%">-</td>
# <td style="text-align: center;"  width="4%">5</td>
# </tr>

class dit_data:
    def __init__(self):
        self.semesters=dict()
        self.courses=list()
        self.semester=''
    
    def add_data(self,row:list):
        row=[element for element in row if element!='']
        if re.search(".*\d+.*",row[0])==None: return
        elif row[0].strip().startswith("ΡΟΕΣ"): 
            self.semester="7" 
            self.semesters[self.semester]=list()
        elif len(row)==1:
            s=row[0]
            if s not in self.semesters:
                sub=s
                if s.find("ΡΟΗ"):
                    sub=s.split()[0]+" "+s.split()[1]               
                self.semester=sub
                self.semesters[sub]=list()
        elif len(row)==2: return
        elif re.search("\d",row[3])==None: return
        elif row[2]=='Σύνολο': return
        elif row[0]=='Σύνολο:': return
        else:
            self.semesters[self.semester].append((row[0].strip(),row[2].strip(),row[7].strip()))
            semester_real_value=int(self.semester.replace('ο','').split()[0])
            self.courses.append((row[0].strip(),semester_real_value,row[2].strip(),row[7].strip()))

    def export_data(self):
        y=input("Give filename(no file extension etc-> .txt):")
        with open(y+".txt",'w') as WF:
            WF.write("ΚΩΔΙΚΟΣ,ΕΞΑΜΗΝΟ,ΜΑΘΗΜΑ,ΔΙΔΑΚΤΙΚΕΣ ΜΟΝΑΔΕΣ\n")
            for course in self.courses:
                WF.write(f"{course[0]},{course[1]},{course[2]},{course[3]}\n")

def lessons_txt():
    file="https://www.dit.uoi.gr/education.php?id=8"
    dit=dit_data()
    resp=requests.get(file,verify=False)
    bs=BeautifulSoup(resp.text,features="lxml")
    data=bs.find_all("table")
    start_table_organized_data=2
    for tr in data:
        if start_table_organized_data>0:
                start_table_organized_data-=1
                continue

        for row in tr.find_all("tr"):
            td=row.find_all("td")
            dit.add_data([a.text for a in td])
    dit.export_data()

lessons_txt()