import threading
import random
import traceback
from datetime import datetime
from pytz import timezone
import pymysql
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import os
import time

# ------------- [ CONNECT TO VK ] -----------
token=str(os.environ.get("VK-TOKEN"))
group_id=str(os.environ.get("VK-GROUP"))
vk_session=vk_api.VkApi(token=token)  # Обработка access_token
longpoll=VkBotLongPoll(vk_session, group_id)  # Данные для работы в сообществе
vk=vk_session.get_api( )  # For api requests
# ------------- [ DATA FOR CONN TO DB ] -----------
user=str(os.environ.get("SQL-USER"))
passw=str(os.environ.get("SQL-PASS"))


# ----------------[ ENIGNE ]-----------------
def updateAndRegidstrationConv( ):
	"""
	РЕГИСТРАЦИЯ БЕСЕДЫ
	"""
	adms=[305284615, 547409675, 553069569, 337138653]
	race_adms=[553069569, 337138653, 558115430, 621502596, 430596606, 452962971, 587655226, 527338679]
	try:
		while True:
			for event in longpoll.listen( ):
				if event.type==VkBotEventType.MESSAGE_NEW:
					if event.object.message['peer_id']!=event.object.message['from_id'] and event.object.message[
						'from_id'] > 0:
						peer_id=event.object.message["peer_id"]
						conn=pymysql.connect(
							host="triniti.ru-hoster.com",
							user=user,
							password=passw,
							db='demkaXvl',
							charset='utf8', init_command='SET NAMES UTF8'
							)
						curs=conn.cursor( )
						res=curs.execute("SELECT peer_id FROM conversations WHERE peer_id = %s", (peer_id,))
						if res==0:
							try:
								chat=vk.messages.getConversationsById(peer_ids=peer_id)['items'][0]["chat_settings"]
								user_count=chat["members_count"]
								admin_id=chat["owner_id"]
								if admin_id in race_adms or admin_id in adms:
									curs.execute(
										"INSERT INTO conversations (peer_id,user_count,admin_id, verif) VALUES (%s,%s,%s, 1)",
										(peer_id, user_count, admin_id)
										)
									conn.commit( )
								else:
									curs.execute(
										"INSERT INTO conversations (peer_id,user_count,admin_id, verif) VALUES (%s,%s,%s, 0)",
										(peer_id, user_count, admin_id)
										)
									conn.commit( )
							except:
								curs.execute(
									"INSERT INTO conversations (peer_id,user_count,admin_id, verif) VALUES (%s,%s,%s,0)",
									(peer_id, 0, 0)
									)
								conn.commit( )
						else:
							try:
								curs.execute("SELECT admin_id FROM conversations WHERE peer_id = %s", (peer_id,))
								if curs.fetchone( )[0]==0:
									chat=vk.messages.getConversationsById(peer_ids=peer_id)['items'][0][
										"chat_settings"]
									admin_id=chat["owner_id"]
									user_count=chat["members_count"]
									curs.execute(
										f"UPDATE conversations SET admin_id = {admin_id}, user_count = {user_count} WHERE peer_id = %s",
										(peer_id,)
										)
									conn.commit( )
								else:
									chat=vk.messages.getConversationsById(peer_ids=peer_id)['items'][0][
										"chat_settings"]
									admin_id=chat["owner_id"]
									user_count=chat["members_count"]
									curs.execute(
										f"UPDATE conversations SET admin_id = {admin_id}, user_count = {user_count} WHERE peer_id = %s",
										(peer_id,)
										)
									conn.commit( )
							except:
								pass
	except Exception:
		print(traceback.format_exc( ))


def InflationAndDeinflation( ):
	"""
	РЕГУЛИРОВАНИЕ СТОИМОСТИ РЕСУРСОВ
	"""
	while True:
		conn=pymysql.connect(
			host="triniti.ru-hoster.com",
			user=user,
			password=passw,
			db='demkaXvl',
			charset='utf8', init_command='SET NAMES UTF8; SET time_zone="+03:00"'
			)
		curs=conn.cursor( )
		curs.execute(
			"SELECT res_id AS cnt FROM market WHERE DATE(time) BETWEEN DATE(NOW()) AND DATE_ADD(DATE(NOW()), INTERVAL 1 DAY) GROUP BY res_id ORDER BY COUNT(*) DESC"
			)
		res=curs.fetchall( )
		curs.execute(
			"SELECT res_id FROM personal_trans WHERE DATE(time) BETWEEN DATE(NOW()) AND DATE_ADD(DATE(NOW()), INTERVAL 1 DAY) GROUP BY res_id ORDER BY COUNT(*) DESC"
			)
		res2=curs.fetchall( )
		if res[0][0]==res2[0][0]:

			curs.execute(f"UPDATE resourses SET cost = cost + {random.randint(1, 3)} WHERE res_id = {res[0][0]}")
			conn.commit( )
		else:
			curs.execute(f"UPDATE resourses SET cost = cost + {random.randint(1, 3)} WHERE res_id = {res2[0][0]}")
			conn.commit( )
		cost=random.randint(1, 3)
		curs.execute(f"SELECT cost FROM resourses WHERE res_id = {res[len(res) - 1][0]}")
		a=curs.fetchone( )[0]
		if res[len(res) - 1][0]!=res[0][0]:
			if cost < a:
				curs.execute(f"UPDATE resourses SET cost = cost - {cost} WHERE res_id = {res[len(res) - 1][0]}")
				conn.commit( )
		time.sleep(86400)


def checkPayForCitysAndVlgs( ):
	"""
	АВТОМАТИЧЕСКОЕ СПИСАНИЕ ЕДЫ ЗА ГОРОДА/СЕЛА
	"""
	while True:
		conn=pymysql.connect(
			host="triniti.ru-hoster.com",
			user=user,
			password=passw,
			db='demkaXvl',
			charset='utf8', init_command='SET NAMES UTF8; SET time_zone="+03:00"'
			)
		curs=conn.cursor( )
		curs.execute("SELECT user_id, vlg*150 + city*500 FROM users WHERE food >= vlg*150 + city*500")
		payers=curs.fetchall( )
		curs.execute("SELECT user_id, vlg*150 + city*500 FROM users WHERE food < vlg*150 + city*500")
		dfc=curs.fetchall( )
		now_utc=datetime.now(timezone('UTC'))
		tim=now_utc.astimezone(timezone('Europe/Moscow'))
		now=int(tim.timestamp( ))
		txt=""
		for i in payers:
			curs.execute(f"SELECT last_pay FROM forts WHERE user_id = {i[0]}")
			if now - curs.fetchone( )[0] >= 86400:
				curs.execute(f"UPDATE users SET food = food - {i[1]} WHERE user_id = {i[0]}")
				conn.commit( )
				curs.execute(f"SELECT hps, plt FROM forts WHERE user_id = {i[0]}")
				fort=curs.fetchone( )
				if fort[0] < 100:
					b=100 - fort[0]
					if b >= 10:
						curs.execute(
							f"UPDATE forts SET last_check = {tim}, last_pay = {now}, hps = hps + 10, dfc = 2 WHERE user_id = {i[0]}"
							)
						conn.commit( )
					else:
						curs.execute(
							f"UPDATE forts SET last_check = {tim}, last_pay = {now}, hps = hps + {b}, dfc = 2 WHERE user_id = {i[0]}"
							)
						conn.commit( )
				else:
					curs.execute(
						f"UPDATE forts SET last_check = {tim}, last_pay = {now} WHERE user_id = {i[0]}"
						)
					conn.commit( )
				txt+=f"\n@id{i[0]} выдал {i[1]} ед. Продовольствия жителям своего Форта."
		vk.messages.send(
			peer_id=2e9 + 20,
			random_id=random.randint(0, 10000000000),
			message=txt
			)
		txt=""
		for i in dfc:
			curs.execute(f"SELECT hps, plt FROM forts WHERE user_id = {i[0]}")
			fort=curs.fetchone( )
			curs.execute(f"SELECT {i[1]} - food, hps FROM users WHERE user_id = {i[0]}")
			cr=curs.fetchone( )[0]
			b=100 - fort[0]
			c=random.randint(1,3)
			if b >= 10:
				curs.execute(f"UPDATE forts SET dfc = 1, last_check = {tim}, hps = hps - 10, plt = plt - plt/100*{c} WHERE user_id = {i[0]}")
				conn.commit( )
			else:
				curs.execute(f"UPDATE forts SET dfc = 1, last_check = {tim}, plt = plt - plt/100*{c} WHERE user_id = {i[0]}")
				conn.commit( )
			txt+=f"\n@id{i[0]} не хватает {i[1]} ед. Продовольствия, чтобы прокормить жителей Форта. Погибло {c}% жителей форта.\n"
		vk.messages.send(
			peer_id=2e9 + 20,
			random_id=random.randint(0, 10000000000),
			message=txt
			)
		time.sleep(86400)

def checkAndPayForMilitary( ):
	while True:
		conn=pymysql.connect(
			host="triniti.ru-hoster.com",
			user=user,
			password=passw,
			db='demkaXvl',
			charset='utf8', init_command='SET NAMES UTF8; SET time_zone="+03:00"'
			)
		curs=conn.cursor( )
		army = ['clvr', 'inf', 'arch', 'bllsts', 'ctpl', 'plds', 'mag']
		curs.execute("SELECT user_id FROM users")
		payers = curs.fetchall()
		txt1 = ""
		txt2 = ""
		for i in payers:
			now_utc=datetime.now(timezone('UTC'))
			time=int(now_utc.astimezone(timezone('Europe/Moscow')).timestamp( ))
			for c in army:
				curs.execute(f"SELECT expns, res_id, count, name FROM military WHERE bd_name = {c}")
				mil = curs.fetchone()
				curs.execute(f"SELECT bd_name FROM resourses WHERE res_id = {mil[1]}")
				res = curs.fetchone()[0]
				curs.execute(f"SELECT {res}, {c}/count*{mil[0]} FROM users WHERE user_id = {i[0]}")
				user = curs.fetchone()
				if user[0] >= user[1]:
					curs.execute(f"UPDATE {res} = {res} - {user[1]}, last_pay_mil = {time} WHERE user_id = {i[0]}")
					conn.commit()
					txt1+=f"\n@id{i[0]} оплатил все за {mil[3]}"
				else:
					r = random.randint(1, 3)
					curs.execute(f"UPDATE {c} = c - c/100*{r} WHERE user_id = {i[0]}")
					conn.commit( )
					break
		time.sleep(86400)

th1=threading.Thread(target=updateAndRegidstrationConv( ))
th2=threading.Thread(target=InflationAndDeinflation( ))
th3=threading.Thread(target=checkPayForCitysAndVlgs( ))
th4=threading.Thread(target=checkAndPayForMilitary())

th4.start( )
th3.start( )
th1.start( )
th2.start( )
