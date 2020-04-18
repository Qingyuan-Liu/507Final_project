import requests
from bs4 import BeautifulSoup
import sqlite3
import pandas as pd
import os
import webbrowser
import json

CACHE_FILENAME = "cache.json"
DBNAME = 'nba.sqlite'


def open_cache():
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict

def save_cache(cache_dict):
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close() 


def construct_unique_key(baseurl, params):  
    param_strings = []
    connector = '_'
    for k in params.keys():
        param_strings.append(f'{k}_{params[k]}')
    unique_key = baseurl + connector + connector.join(param_strings)
    return unique_key


def make_url_request_using_cache(url, params, c_type="text"):
    unique_key = construct_unique_key(url, params)
    cache = open_cache()
    if (unique_key in cache.keys()):
        print("Using cache")
    else:
        print("Fetching")
        response = requests.get(url, params=params)
        if c_type == "json":
            cache[unique_key] = response.json()
        else:
            cache[unique_key] = response.text
        save_cache(cache)

    return cache[unique_key]


def player_stats(year):
	url = "https://www.basketball-reference.com/leagues/NBA_{}_per_game.html".format(year)
	response = make_url_request_using_cache(url, {})
	soup=BeautifulSoup(response,'html.parser')
	#print(soup.findAll('tr', limit=2))
	if soup.findAll('tr', limit=2)!=[]:
		header_parent=soup.findAll('tr', limit=2)[0].findAll('th')
		header=[]
		for th in header_parent:
		    header.append(th.text)
		colLen = len(header)
		# header=header[1:]
		#print(colLen)
		res=[]
		rows = soup.findAll('tr')[1:]
		#print(rows)
		for i in rows:
		    row=[]
		    for th in i.findAll('th'):
		        row.append(th.text)
		    for td in i.findAll('td'):
		        row.append(td.text)
		    if len(row) == colLen:
		        res.append(row)
		table=pd.DataFrame(res, columns = header)
		table.head(10)
		html = table.to_html()
		text_file = open("index.html", "w")
		text_file.write(html)
		text_file.close()

		cwd = os.getcwd()
		url='file://'+cwd+'/index.html'
		print(url)
		webbrowser.open(url)
	else:
		print("There is no records for this year.")


def search_team():
	# NBA season we will be analyzing
	# URL page we will scraping (see image above)
	url = "https://www.basketball-reference.com/teams/"
	# this is the HTML from the given URL
	response = make_url_request_using_cache(url, {})
	soup=BeautifulSoup(response,'html.parser')
	a=soup.findAll('tr', limit=2)
	# #print(a)
	# for th in a[0].find_all('th'):
		#print(th.text)
	#find all the team information
	rows=soup.find_all('tr',class_='full_table')
	team_list=[]
	count=0
	for i in range(len(rows)):
		count=count+1
		if count<31:
			for th in rows[i].find_all('th'):
				team=[]
				franchise=th.text
				#print(franchise)
				team.append(franchise)
				url="https://www.basketball-reference.com"+th.find('a')['href']
				team.append(url)
				#print(url)
				league=rows[i].find_all('td')[0].text
				team.append(league)
				#print(league)
				first_year=rows[i].find_all('td')[1].text
				team.append(first_year)
				#print(first_year)
				last_year=rows[i].find_all('td')[2].text
				team.append(last_year)
				#print(last_year)
				year=rows[i].find_all('td')[3].text
				team.append(year)
				#print(year)
				games=rows[i].find_all('td')[4].text
				team.append(games)
				#print(games)
				wins=rows[i].find_all('td')[5].text
				team.append(wins)
				#print(wins)
				loses=rows[i].find_all('td')[6].text
				team.append(loses)
				#print(loses)
				wl_per=rows[i].find_all('td')[7].text
				team.append(wl_per)
				#print(wl_per)
				plyfs=rows[i].find_all('td')[8].text
				team.append(plyfs)
				#print(plyfs)
				div=rows[i].find_all('td')[9].text
				team.append(div)
				#print(div)
				conf=rows[i].find_all('td')[10].text
				team.append(conf)
				#print(conf)
				champ=rows[i].find_all('td')[11].text
				team.append(champ)
				#print(champ)
				team_list.append(team)
		else:
			break
	return team_list

def url_inlatest(url_dic):
	dic={}
	for key in url_dic:
		# response=requests.get(url_dic[key])
		response = make_url_request_using_cache(url_dic[key], {})
		soup=BeautifulSoup(response,'html.parser')
		rows=soup.find_all('tr')
		# print(rows)
		th=rows[1].find('th',class_='left')
		url="https://www.basketball-reference.com"+th.find('a')['href']
		#print(url)
		dic[key]=url
	return dic

def player_inlatest(dic):
	t_p_list=[]
	for key in dic:
		url=dic[key]
		# response=requests.get(url)
		response = make_url_request_using_cache(url, {})
		soup=BeautifulSoup(response,'html.parser')
		#a=soup.findAll('tr', limit=2)
		#print(a)
		# for th in a[0].findAll('th'):
		# 	print(th.text)
		table=soup.find('table',id='roster')
		#print(table)
		player_par=table.find('tbody')
		#print(player_par)
		player=player_par.find_all('tr')
		#print(player)
		play_list=[]
		for p in player:
			p_number=p.find('th').text
			play=[]
			if p_number:
				#print(p_number)
				play.append(p_number)
				link='https://www.basketball-reference.com'+p.find('td').find('a')['href']
				#print(link)
				play.append(link)
				name=p.find_all('td')[0].find('a').text
				#print(name)
				play.append(name)
				pos=p.find_all('td')[1].text
				#print(pos)
				play.append(pos)
				height=p.find_all('td')[2].text
				#print(height)
				play.append(height)
				weight=p.find_all('td')[3].text
				#print(weight)
				play.append(weight)
				birth_date=p.find_all('td')[4].text
				#print(birth_date)
				play.append(birth_date)
				year_exp=p.find_all('td')[6].text
				#print(year_exp)
				play.append(year_exp)
				college=p.find_all('td')[7].text
				play.append(college)
				#print(play)
				play_list.append(play)
		t_p_list.append(play_list)
		print(t_p_list)
	return t_p_list


def db_insert(t_p_list,team_list):
	conn = sqlite3.connect(DBNAME)
	cur = conn.cursor()

	drop_players = '''
	    DROP TABLE IF EXISTS "Players";
	'''

	create_players = '''
	    CREATE TABLE IF NOT EXISTS "Players" (
	        "Id"        INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
	        "Team_id" INTEGER NOT NULL,
	        "Player_id"  TEXT NOT NULL,
	        "Intro_url" TEXT,
	        "Name" 		TEXT NOT NULL,
	        "Position" TEXT,
	        "Height" TEXT,
	        "Weight" INTEGER,
	        "Birthday" TEXT,
	        "Year_of_experience" TEXT,
	        "College" TEXT,
	        FOREIGN KEY(Team_id) REFERENCES Team(Id)
	    );
	'''

	drop_teams = '''
	    DROP TABLE IF EXISTS "Teams";
	'''

	create_teams='''
	    CREATE TABLE IF NOT EXISTS "Teams" (
	    	"Id" INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
	        "Team_name" TEXT NOT NULL,
	        "Intro_url" TEXT,
	        "League" TEXT NOT NULL,
	        "Since"  TEXT NOT NULL,
	        "Until" TEXT NOT NULL,
	        "Year" INTEGER NOT NULL,
	        "Games" INTEGER NOT NULL,
	        "Wins" INTEGER NOT NULL,
	        "Losts" INTEGER NOT NULL,
	        "Win_lose_percentage" REAL NOT NULL,
	        "Playoffs" INTEGER NOT NULL,
	        "Divisions" INTEGER NOT NULL,
	        "Conference_champ" INTEGER NOT NULL,
	        "Championship" INTEGER NOT NULL
	    );
	'''

	cur.execute(drop_teams)
	cur.execute(create_teams)
	cur.execute(drop_players)
	cur.execute(create_players)

	conn.commit()

	insert_teams = '''
    INSERT INTO Teams
    VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
	'''

	for team in team_list:
		cur.execute(insert_teams, team)


	insert_players='''
    INSERT INTO Players
    VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
	'''

	team_id=0
	for t in t_p_list:
		team_id=team_id+1
		for p in t:
			p.insert(0,team_id)
			cur.execute(insert_players,p)

	conn.commit()


def db_query(sql_phrase):
    connection = sqlite3.connect(DBNAME)
    cursor = connection.cursor()
    result = cursor.execute(sql_phrase).fetchall()
    connection.close()
    return result

if __name__ == '__main__':
	team_list=search_team()
	#print(team_list)
	dic={}
	for t in team_list:
		dic[t[0]]=t[1]
	#print(dic)
	u_dic=url_inlatest(dic)
	t_p_list=player_inlatest(u_dic)
	#print(player_list)
	
	db_insert(t_p_list,team_list)

	# year=input("Please enter the season you want to search:")
	# player_stats(year)
	print("1.Enter the player number(or name) and specify his team to obtain his information.")
	print("2.Enter the team name to see all the players on this team in the current season.")
	print("3.See the top 10 teams won the most championships and the players’ average height in a bar plot.")
	print("4.See the top 10 universities with the most drafted players in a bar plot.")
	print("5.Check the NBA player stats for the season you indicate")
	choice=input("Please enter the option:")
	if choice=='1':
		while True:
			info=input("Please indicate the player's number(or name) and specify his team,\
			 (eg: Atlanta Hawks/12 or Atlanta Hawks/De'Andre Hunter):")
			info_list=info.split('/')
			query=""
			if len(info_list)!=2:
				print("Please check your input format!")
				continue
			elif info_list[1].isnumeric():
				query="SELECT * From Players, Teams WHERE Players.Team_id=Teams.Id and Team_name='"+info_list[0]+"' and Player_id="+info_list[1]
			elif not info_list[1].isnumeric():
				query='SELECT * From Players, Teams WHERE Players.Team_id=Teams.Id and Team_name="'+info_list[0]+'" and Name='+'"'+info_list[1]+'"'
			print(db_query(query))







