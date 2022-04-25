import requests
from urllib.request import urlopen
from bs4 import BeautifulSoup
from prettytable import PrettyTable
import os
import ssl
import json

# Requirments
# pip install requests
# pip install html5lib
# pip install bs4


def teachers_to_csv():
    urls={"https://www.dit.uoi.gr/members.php":1,"https://www.dit.uoi.gr/phdstudents_show.php":2}
    teachers=list()
    for url,state in urls.items():
        resp=requests.get(url,verify=False)
        soup=BeautifulSoup(resp.text,features="lxml")
        data=soup.find_all("table")
        if state==1:            
            for row in data:
                for tr in row.findAll("tr"):
                    cols=tr.findAll("td")
                    name=cols[0].text.strip()
                    rank_cell=cols[1].findAll("center")
                    rank_reduced=str(rank_cell[0]).replace("<center>","").replace("</center>","").replace("/","")
                    if len(rank_reduced.split("<br>"))==2:
                        rank=rank_reduced.split("<br>")[0]+"_"+rank_reduced.split("<br>")[1]
                    else:
                        rank=rank_reduced.split("<br>")[0]
                    mail_cell=cols[2].findAll("a")
                    mail=mail_cell[0].text.strip()
                    teachers.append((name,rank,mail))
        else:
            for row in data:
                for tr in row.findAll("tr"):
                    cols=tr.findAll("td")
                    name=cols[0].text.strip()
                    mail=cols[1].text.strip()
                    teachers.append((name,"ΥΠΟΨΗΦΙΟΣ ΔΙΔΑΚΤΟΡΑΣ",mail))
    table=PrettyTable()
    table.field_names=['ΟΝ/ΜΟ','ΒΑΘΜΙΔΑ','ΗΛΕΚΤΡΟΝΙΚΗ ΔΙΕΥΘΥΝΣΗ']
    for record in teachers:
        table.add_row(list(record))
    print(table)
    data_path=os.path.join("..","Data","teachers.csv")
    with open(data_path,'w') as WF:
        WF.write("ΟΝΟΜΑ,ΒΑΘΜΙΔΑ,ΗΛΕΚΤΡΟΝΙΚΗ ΔΙΕΥΘΥΝΣΗ\n")
        for name,rank,mail in teachers:
            WF.write(f"{name},{rank},{mail}\n")
    print("File saved as {}".format(data_path))
    return teachers
       
def convert_to_js_format(teachers):
    json_teachers=list()
    for name,rank,mail in teachers:
        json_teachers.append({name:{
            "ΒΑΘΜΙΔΑ":rank,
            "ΗΛΕΚΤΡΟΝΙΚΗ_ΔΙΕΥΘΥΝΣΗ":mail
        }})
    return json_teachers

if __name__=='__main__':
    teachers=teachers_to_csv()
    path=os.path.join("..","Data","dit_uoi.json")
    teachers_json=convert_to_js_format(teachers)
    with open(path,'w',encoding="utf16") as WF:
        json.dump(teachers_json,WF,ensure_ascii=False)


