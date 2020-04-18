import requests
from bs4 import BeautifulSoup
import sqlite3
import pandas as pd
import os
import webbrowser
from flask import Flask, render_template, request
import plotly.graph_objs as go 
import json

app = Flask(__name__)

DBNAME = 'nba.sqlite'
CACHE_FILENAME = "cache.json"


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
		text_file = open("templates/season.html", "w")
		text_file.write(html)
		text_file.close()

		# cwd = os.getcwd()
		# url='file://'+cwd+'/index.html'
		# print(url)
		# webbrowser.open(url)
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
		# print(play_list)
	return t_p_list


def db_insert():
	team_list=search_team()
	#print(team_list)
	dic={}
	for t in team_list:
		dic[t[0]]=t[1]
	#print(dic)
	u_dic=url_inlatest(dic)
	t_p_list=player_inlatest(u_dic)
	#print(player_list)

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
	        "Leage" TEXT NOT NULL,
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

def get_results_team(sort_by,sort_order,select_result):
	conn = sqlite3.connect(DBNAME)
	cur = conn.cursor()
	print(select_result)
	attributes=''
	if select_result:
		attributes='Team_name,'
		for i in range(len(select_result)):
			if i < len(select_result)-1:
				attributes=attributes+select_result[i]+','
			else:
				attributes=attributes+select_result[i]
	else:
		attributes='Team_name'

	query=f'''
		SELECT {attributes}
		From Teams
		ORDER by {sort_by} {sort_order}
		'''

	print(query)

	results = cur.execute(query).fetchall()
	conn.close()
	return results

def position_height():
	conn = sqlite3.connect(DBNAME)
	cur = conn.cursor()
	query=f'''
		SELECT DISTINCT(Position), avg(Height)
		FROM Players
		GROUP by Position
		'''
	results = cur.execute(query).fetchall()
	conn.close()
	return results

def show_player(team,player_id):
	conn = sqlite3.connect(DBNAME)
	cur = conn.cursor()
	print('team'+team)
	print('playerid'+str(player_id))
	if player_id:
		query=f'''
			SELECT Teams.Team_name, Players.Player_id, Players.Name, Players.Position, Players.Height,
			Players.Weight, Players.Birthday, Players.Year_of_experience, Players.College
			FROM Players, Teams
			WHERE Players.Team_id=Teams.Id and Teams.Team_name='{team}' and Players.Player_id={player_id}
			'''
		print(query)
		results = cur.execute(query).fetchall()
	else:
		query=f'''
			SELECT Teams.Team_name, Players.Player_id, Players.Name, Players.Position, Players.Height,
			Players.Weight, Players.Birthday, Players.Year_of_experience, Players.College
			FROM Players, Teams
			WHERE Players.Team_id=Teams.Id and Teams.Team_name='{team}'
			'''
		print(query)
		results = cur.execute(query).fetchall()
	conn.close()

	return results


@app.route('/')
def index():
	return render_template('index.html')

@app.route('/results_team', methods=['POST'])
def results():
    sort_by = request.form['sort']
    sort_order = request.form['dir']
    select_result= request.form.getlist('attribute')

    results = get_results_team(sort_by, sort_order,select_result)
    return render_template('results_team.html', 
       results=results,attributes=select_result,length=len(select_result)+1)


@app.route('/position',methods=['POST'])
def plot():
    x_vals = ['C','PF','PG','SF','SG']
    results=position_height()
    y_vals=[]
    for i in results:
    	y_vals.append(i[1])
    print(results)
    bars_data = go.Bar(
        x=x_vals,
        y=y_vals
    )
    fig = go.Figure(data=bars_data)
    div = fig.to_html(full_html=False)
    return render_template("position.html", plot_div=div)


@app.route('/player',methods=['POST'])
def player():
	team=request.form['team']
	player_id=request.form['player_id']
	# if not player_id.isnumeric():
	# 	return render_template("err_msg.html")
	# else:
	# 	result=show_player(team,player_id)
	if player_id.isnumeric() or player_id=='':
		result=show_player(team,player_id)
		if result:
			return render_template("player.html",result=result)
		else:
			return render_template("err_msg.html")
	else:
		return render_template("err_msg.html")


@app.route('/college',methods=['POST'])
def college():
	conn = sqlite3.connect(DBNAME)
	cur = conn.cursor()
	query1=f'''
		SELECT College
		FROM Players
		WHERE College!=''
		GROUP by College
		ORDER by count(*) DESC
		limit 10
		'''
	results1 = cur.execute(query1).fetchall()
	query2=f'''
		SELECT count(*)
		FROM Players
		WHERE College!=''
		GROUP by College
		ORDER by count(*) DESC
		limit 10
	'''
	results2=cur.execute(query2).fetchall()
	conn.close()
	print(results1)
	print(results2)
	res1 = [item for t in results1 for item in t]
	res2 = [item for t in results2 for item in t]
	print(res1)
	print(res2)
	x_vals = res1
	y_vals = res2
	bars_data = go.Bar(
		x=x_vals,
		y=y_vals
	)
	fig = go.Figure(data=bars_data)
	div = fig.to_html(full_html=False)
	return render_template("college.html", plot_div=div)


@app.route('/height',methods=['POST'])
def height():
	conn = sqlite3.connect(DBNAME)
	cur = conn.cursor()
	query1=f'''
		SELECT Teams.Team_name
		FROM Players,Teams
		WHERE Teams.Id=Players.Team_id
		GROUP by Players.Team_id
		'''
	results1 = cur.execute(query1).fetchall()
	query2=f'''
		SELECT avg(Players.Height)
		FROM Players,Teams
		WHERE Teams.Id=Players.Team_id
		GROUP by Players.Team_id
	'''
	results2=cur.execute(query2).fetchall()
	conn.close()
	res1 = [item for t in results1 for item in t]
	res2 = [item for t in results2 for item in t]
	x_vals = res1
	y_vals = res2
	bars_data = go.Bar(
		x=x_vals,
		y=y_vals
	)
	fig = go.Figure(data=bars_data)
	div = fig.to_html(full_html=False)
	return render_template("height.html", plot_div=div)

@app.route('/season',methods=['POST'])
def search_season():
	year=request.form['year']
	player_stats(year)
	return render_template('season.html')




if __name__ == '__main__':
	# db_insert()
	app.run(debug=True)









