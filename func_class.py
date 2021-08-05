import datetime
import random
from datetime import datetime
from PIL import Image, ImageFont, ImageDraw
import vk_api
import pymorphy2
import pymysql
from pytz import timezone
import os
import traceback
from pytils import numeral
import urllib.request # Загрузить модуль и добавить в req.txt

class Main(object):
	def __init__(self, vk, event, vk_session):
		self.vk = vk
		self.event = event
		self.user_id = event.object.message["from_id"]
		self.peer_id = event.object.message["peer_id"]
		self.command = event.obj.message["text"].lower( )
		self.txt = event.obj.message["text"]
		self.vk_session = vk_session
		self.adms_chat = 2000000004
		self.user = str(os.environ.get("SQL-USER"))
		self.passw = str(os.environ.get("SQL-PASS"))
		self.adms = [305284615, 547409675, 553069569, 337138653]
		self.race_adms = [553069569, 337138653, 558115430, 621502596, 430596606, 452962971, 587655226, 527338679]
		self.map_types = ['g']
	
	def registrationConv(self):
		conn = pymysql.connect(
				host="triniti.ru-hoster.com",
				user=self.user,
				password=self.passw,
				db='demkaXvl',
				charset='utf8', init_command='SET NAMES UTF8'
				)
		curs = conn.cursor( )
		res = curs.execute("SELECT peer_id FROM conversations WHERE peer_id = %s", (self.peer_id,))
		if res == 0:
			try:
				chat = self.vk.messages.getConversationsById(peer_ids=self.peer_id)['items'][0]["chat_settings"]
				user_count = chat["members_count"]
				admin_id = chat["owner_id"]
				if admin_id in self.race_adms or admin_id in self.adms:
					curs.execute(
							"INSERT INTO conversations (peer_id,user_count,admin_id, verif) VALUES (%s,%s,%s, 1)",
							(self.peer_id, user_count, admin_id)
							)
					conn.commit( )
				else:
					curs.execute(
							"INSERT INTO conversations (peer_id,user_count,admin_id, verif) VALUES (%s,%s,%s, 0)",
							(self.peer_id, user_count, admin_id)
							)
					conn.commit( )
			except:
				curs.execute(
						"INSERT INTO conversations (peer_id,user_count,admin_id, verif) VALUES (%s,%s,%s,0)",
						(self.peer_id, 0, 0)
						)
				conn.commit( )
		else:
			try:
				curs.execute("SELECT admin_id FROM conversations WHERE peer_id = %s", (self.peer_id,))
				if curs.fetchone()[0] == 0:
					chat = self.vk.messages.getConversationsById(peer_ids=self.peer_id)['items'][0]["chat_settings"]
					admin_id = chat["owner_id"]
					user_count = chat["members_count"]
					curs.execute(f"UPDATE conversations SET admin_id = {admin_id}, user_count = {user_count} WHERE peer_id = %s", (self.peer_id,))
					conn.commit()
				else:
					chat = self.vk.messages.getConversationsById(peer_ids=self.peer_id)['items'][0]["chat_settings"]
					admin_id = chat["owner_id"]
					user_count = chat["members_count"]
					curs.execute(f"UPDATE conversations SET admin_id = {admin_id}, user_count = {user_count} WHERE peer_id = %s", (self.peer_id,))
					conn.commit()
			except:
				pass
	def registrarionUser(self):
		conn = pymysql.connect(
				host="triniti.ru-hoster.com",
				user=self.user,
				password=self.passw,
				db='demkaXvl',
				charset='utf8', init_command='SET NAMES UTF8'
				)
		curs = conn.cursor( )
		res = curs.execute("SELECT user_id FROM users WHERE user_id = %s", (self.user_id,))
		if res == 0:
			user = self.vk.users.get(user_ids=self.user_id)
			user_name = f"{user[0]['first_name']}"
			curs.execute(
					"INSERT INTO users(user_id,peer_id,anders,nickname,food) VALUES (%s,%s,%s,%s,%s)",
					(self.user_id, self.peer_id, 0, user_name, 10)
					)
			conn.commit( )
	
	def addResourse(self):
		"""
		/addres
		[NAME]
		[МИНИМАЛЬНАЯ СТОИМОСТЬ ЗА УДИНИЦУ]
		NAME - с большой буквы
		
		!! ПОСЛЕ ДОБАВЛЕНИЯ НОВОГО РЕСУРСА НУЖНО СРОЧНО НАПИСАТЬ @n.i4oo6 !!
		"""
		if self.user_id in self.adms:
			res_cost = self.txt.split("\n")[2].strip( )
			res_name = self.txt.split("\n")[1].strip( )
			if res_cost.isdigit( ):
				conn = pymysql.connect(
						host="triniti.ru-hoster.com",
						user=self.user,
						password=self.passw,
						db='demkaXvl',
						charset='utf8', init_command='SET NAMES UTF8'
						)
				curs = conn.cursor( )
				res = curs.execute("SELECT * FROM resourses WHERE name = %s", (res_name,))
				if res == 0:
					curs.execute(
							"INSERT INTO resourses (name,cost) VALUES (%s, %s)",
							(res_name, res_cost)
							)
					conn.commit( )
					
					self.vk.messages.send(
							peer_id=self.peer_id,
							random_id=random.randint(0, 10000000000),
							message="Ресурс успешно добавлен в базу данных."
							)
				else:
					self.vk.messages.send(
							peer_id=self.peer_id,
							random_id=random.randint(0, 10000000000),
							message="Данный ресурс уже есть в базе данных."
							)
			else:
				self.vk.messages.send(
						peer_id=self.peer_id,
						random_id=random.randint(0, 10000000000),
						message="Один из аргументов указан неверно."
						)
	
	def addMilitary(self):
		"""
		/addmil
		[NAME]
		[СТОИМОСТЬ ЗА УКАЗАННОЕ КОЛ-ВО]
		[КОЛ-ВО ПРИ ПОКУПКЕ]
		NAME - с большой буквы
		
		!! ПОСЛЕ ДОБАВЛЕНИЯ НОВОГО ВИДА ВОЙСК НУЖНО СРОЧНО НАПИСАТЬ @n.i4oo6 !!
		"""
		if self.user_id in self.adms:
			mil_name = self.txt.split("\n")[1].strip( )
			mil_cost = self.txt.split("\n")[2].strip( )
			mil_count = self.txt.split("\n")[3].strip( )
			# mil_expn = self.txt.split("\n")[4].strip( ) - затраты не требуются по ТЗ
			if mil_cost.isdigit( ) and mil_count.isdigit( ):
				conn = pymysql.connect(
						host="triniti.ru-hoster.com",
						user=self.user,
						password=self.passw,
						db='demkaXvl',
						charset='utf8', init_command='SET NAMES UTF8'
						)
				curs = conn.cursor( )
				mil_check = curs.execute("SELECT * FROM military WHERE name = %s", (mil_name,))
				if mil_check == 0:
					curs.execute(
							"INSERT INTO military (name, count, cost) VALUES (%s, %s, %s)",
							(mil_name, mil_count, mil_cost)
							)
					conn.commit( )
					
					self.vk.messages.send(
							peer_id=self.peer_id,
							random_id=random.randint(0, 10000000000),
							message="Вид войска успешно добавлен в базу данных."
							)
				else:
					self.vk.messages.send(
							peer_id=self.peer_id,
							random_id=random.randint(0, 10000000000),
							message="Данный вид войска уже есть в базе данных."
							)
			else:
				self.vk.messages.send(
						peer_id=self.peer_id,
						random_id=random.randint(0, 10000000000),
						message="Один из аргументов указан неверно."
						)
	
	def addBuild(self):
		"""
		/addbld
		[NAME]
		[КОЛ-ВО ПРИНОСИМОГО РЕСУРСА РАЗ В 24Ч.]
		[ID РЕСУРСА ПРИНОСИМОГО РАЗ В 24Ч.]
		NAME - с большой буквы
		
		!! ПОСЛЕ ДОБАВЛЕНИЯ НОВОГО ВИДА ПОСТРОЕК НУЖНО СРОЧНО НАПИСАТЬ @n.i4oo6 !!
		"""
		if self.user_id in self.adms:
			name = self.txt.split("\n")[1]
			cost = self.txt.split("\n")[2]
			prof = self.txt.split("\n")[3]
			res_id = self.txt.split("\n")[4]
			if cost.isdigit( ) and res_id.isdigit( ) and prof.isdigit( ):
				conn = pymysql.connect(
						host="triniti.ru-hoster.com",
						user=self.user,
						password=self.passw,
						db='demkaXvl',
						charset='utf8', init_command='SET NAMES UTF8'
						)
				curs = conn.cursor( )
				build_check = curs.execute("SELECT * FROM builds WHERE name = %s", (name,))
				if build_check == 0:
					res_check = curs.execute("SELECT * FROM resourses WHERE res_id = %s", (res_id,))
					if res_check == 0:
						self.vk.messages.send(
								peer_id=self.peer_id,
								random_id=random.randint(0, 10000000000),
								message="В базе данных не существует указанного ID ресурса."
								)
					else:
						curs.execute(
								"INSERT INTO builds (name, cost, profit, res_id) VALUES (%s, %s, %s, %s)",
								(name, cost, prof, res_id)
								)
						conn.commit( )
						
						self.vk.messages.send(
								peer_id=self.peer_id,
								random_id=random.randint(0, 10000000000),
								message="Постройка успешно добавлена в базу данных."
								)
				else:
					self.vk.messages.send(
							peer_id=self.peer_id,
							random_id=random.randint(0, 10000000000),
							message="Данная постройка уже есть в базе данных."
							)
			
			else:
				self.vk.messages.send(
						peer_id=self.peer_id,
						random_id=random.randint(0, 10000000000),
						message="Один из аргументов указан неверно."
						)
	
	def collectResourses(self):
		now_utc = datetime.now(timezone('UTC'))
		time = now_utc.astimezone(timezone('Europe/Moscow'))
		conn = pymysql.connect(
				host="triniti.ru-hoster.com",
				user=self.user,
				password=self.passw,
				db='demkaXvl',
				charset='utf8', init_command='SET NAMES UTF8'
				)
		curs = conn.cursor( )
		curs.execute(f'SELECT verif FROM conversations WHERE peer_id = {self.peer_id}')
		ch = int(curs.fetchone( )[0])
		if ch == 1:
			now = int(time.timestamp( ))
			curs.execute("SELECT last_res_coll FROM users WHERE user_id = %s", (self.user_id,))
			resp = int(curs.fetchone( )[0])
			if resp == 0 or now - resp >= 86400:
				curs.execute(
						"SELECT mine, vlg, farm, city, tmpl, altr, swml FROM users WHERE user_id = %s", (self.user_id,)
						)
				data = curs.fetchone( )
				curs.execute("SELECT build_id FROM builds ORDER BY build_id DESC")
				count = curs.fetchone( )[0]
				curs.execute("SELECT profit FROM builds")
				prof = curs.fetchall( )
				res = []
				for i in range(count):
					mine = data[i] * prof[i][0]
					res.append(mine)
				curs.execute(
						f"UPDATE users SET steel = steel + {res[0]}, anders = anders +{res[1] + res[3]}, food = food + {res[2]}, w_cris = w_cris + {res[4]}, b_cris = b_cris + {res[5]}, wood = wood + {res[6]}, last_res_coll = {now} WHERE user_id = %s",
						(self.user_id,)
						)
				conn.commit( )
				curs.execute(
						f"INSERT INTO res_collect (steel, anders, food, w_cris, b_cris, wood, time, user_id) VALUES ({res[0]}, {res[1] + res[3]}, {res[2]},{res[4]}, {res[5]}, {res[6]}, {now}, {self.user_id})"
						)
				conn.commit( )
				stats_pic = Image.open("res.png")
				stats_pic_draw = ImageDraw.Draw(stats_pic)
				font = ImageFont.truetype("Aqum.ttf", size=23)
				stats_pic_draw.text(xy=(165, 179), text=str(res[2]), fill="black", font=font)
				stats_pic_draw.text(xy=(165, 279), text=str(res[6]), fill="black", font=font)
				stats_pic_draw.text(xy=(165, 376), text=str(res[0]), fill="black", font=font)
				stats_pic_draw.text(xy=(165, 475), text=str(res[5]), fill="black", font=font)
				stats_pic_draw.text(xy=(165, 572), text=str(res[4]), fill="black", font=font)
				stats_pic_draw.text(xy=(165, 670), text=str(res[1] + res[3]), fill="black", font=font)
				
				stats_pic.save('r.png')
				
				vk_upload = vk_api.VkUpload(self.vk_session)
				photo = vk_upload.photo_messages(photos="r.png")
				photo = f'photo{photo[0]["owner_id"]}_{photo[0]["id"]}'
				self.vk.messages.send(
						peer_id=self.peer_id, random_id=random.randint(0, 10000000000), attachment=photo
						)
			else:
				self.vk.messages.send(
						peer_id=self.peer_id,
						random_id=random.randint(0, 10000000000),
						message=f"&#128339; [id{self.user_id}|Вы] уже собирали ресурсы.\n Повторно вы сможете их собрать только {datetime.fromtimestamp(resp + 86400).astimezone(timezone('Europe/Moscow')).strftime('%Y-%m-%d %H:%M:%S')} (По Московскому времени)",
						disable_mentions=1
						)
	
	def collectExpirience(self):
		now_utc = datetime.now(timezone('UTC'))
		time = now_utc.astimezone(timezone('Europe/Moscow'))
		conn = pymysql.connect(
				host="triniti.ru-hoster.com",
				user=self.user,
				password=self.passw,
				db='demkaXvl',
				charset='utf8', init_command='SET NAMES UTF8'
				)
		curs = conn.cursor( )
		curs.execute(f'SELECT verif FROM conversations WHERE peer_id = {self.peer_id}')
		ch = int(curs.fetchone( )[0])
		if ch == 1:
			now = int(time.timestamp( ))
			curs.execute("SELECT last_exp_coll FROM users WHERE user_id = %s", (self.user_id,))
			resp = int(curs.fetchone( )[0])
			if resp == 0 or now - resp >= 259200:
				curs.execute(
						"SELECT inf, arch, clvr, plds, mag, ctpl, bllsts FROM users WHERE user_id = %s", (self.user_id,)
						)
				data = curs.fetchone( )
				mil = 0
				for i in data:
					mil = i + mil
				res = mil * 0.1
				if res == 0:
					self.vk.messages.send(
							peer_id=self.peer_id,
							random_id=random.randint(0, 10000000000),
							message=f"&#128339; [id{self.user_id}|Вы] сейчас можете собрать только 0 ед. Опыта. Лучше увеличьте численность армии и попробуйте вновь собрать опыт.",
							disable_mentions=1
							)
				else:
					curs.execute(
							f"UPDATE users SET exp = exp + {res}, last_exp_coll = {now} WHERE user_id = {self.user_id}"
							)
					conn.commit( )
					curs.execute(f"INSERT INTO exp_collect (exp, time, user_id) VALUES ({res}, {now}, {self.user_id})")
					conn.commit( )
					
					stats_pic = Image.open("exp.png")
					stats_pic_draw = ImageDraw.Draw(stats_pic)
					font = ImageFont.truetype("Aqum.ttf", size=23)
					stats_pic_draw.text(xy=(165, 179), text=str(res), fill="black", font=font)
					
					stats_pic.save('ex.png')
					
					vk_upload = vk_api.VkUpload(self.vk_session)
					photo = vk_upload.photo_messages(photos="ex.png")
					photo = f'photo{photo[0]["owner_id"]}_{photo[0]["id"]}'
					self.vk.messages.send(
							peer_id=self.peer_id, random_id=random.randint(0, 10000000000), attachment=photo
							)
			else:
				self.vk.messages.send(
						peer_id=self.peer_id,
						random_id=random.randint(0, 10000000000),
						message=f"&#128339; [id{self.user_id}|Вы] уже собирали опыт. Повторно вы сможете его собрать только {datetime.fromtimestamp(resp + 259200).astimezone(timezone('Europe/Moscow')).strftime('%Y-%m-%d %H:%M:%S')} (По Московскому времени)",
						disable_mentions=1
						)
	
	def listOfMillitaryObj(self):
		conn = pymysql.connect(
				host="triniti.ru-hoster.com",
				user=self.user,
				password=self.passw,
				db='demkaXvl',
				charset='utf8', init_command='SET NAMES UTF8'
				)
		curs = conn.cursor( )
		curs.execute(f'SELECT verif FROM conversations WHERE peer_id = {self.peer_id}')
		ch = int(curs.fetchone( )[0])
		if ch == 1:
			curs.execute("SELECT anders FROM users WHERE user_id = %s", (self.user_id,))
			
			builds = curs.fetchone( )
			stats_pic = Image.open("voyska_v2.png")
			stats_pic_draw = ImageDraw.Draw(stats_pic)
			font = ImageFont.truetype("Aqum.ttf", size=23)
			stats_pic_draw.text(xy=(365, 180), text=str(builds[0]), fill="white", font=font)
			
			stats_pic.save('mil.png')
			
			vk_upload = vk_api.VkUpload(self.vk_session)
			photo = vk_upload.photo_messages(photos="mil.png")
			photo = f'photo{photo[0]["owner_id"]}_{photo[0]["id"]}'
			self.vk.messages.send(
					peer_id=self.peer_id, random_id=random.randint(0, 10000000000), attachment=photo
					)
	
	def listOfBuilds(self):
		conn = pymysql.connect(
				host="triniti.ru-hoster.com",
				user=self.user,
				password=self.passw,
				db='demkaXvl',
				charset='utf8', init_command='SET NAMES UTF8'
				)
		curs = conn.cursor( )
		curs.execute(f'SELECT verif FROM conversations WHERE peer_id = {self.peer_id}')
		ch = int(curs.fetchone( )[0])
		if ch == 1:
			curs.execute("SELECT anders FROM users WHERE user_id = %s", (self.user_id,))
			
			builds = curs.fetchone( )
			stats_pic = Image.open("stroenia_v2.png")
			stats_pic_draw = ImageDraw.Draw(stats_pic)
			font = ImageFont.truetype("Aqum.ttf", size=23)
			stats_pic_draw.text(xy=(365, 180), text=str(builds[0]), fill="white", font=font)
			
			stats_pic.save('build.png')
			
			vk_upload = vk_api.VkUpload(self.vk_session)
			photo = vk_upload.photo_messages(photos="build.png")
			photo = f'photo{photo[0]["owner_id"]}_{photo[0]["id"]}'
			self.vk.messages.send(
					peer_id=self.peer_id, random_id=random.randint(0, 10000000000), attachment=photo
					)
	
	def buyMilitaryObj(self):
		if len(self.command.split(" ")) == 2:
			conn = pymysql.connect(
					host="triniti.ru-hoster.com",
					user=self.user,
					password=self.passw,
					db='demkaXvl',
					charset='utf8', init_command='SET NAMES UTF8'
					)
			curs = conn.cursor( )
			curs.execute(f'SELECT verif FROM conversations WHERE peer_id = {self.peer_id}')
			if curs.fetchone( )[0] == 1:
				mil_id = self.command.split(" ")[1]
				if mil_id.isdigit( ):
					curs.execute("SELECT cost, count, bd_name, name, bld_id FROM military WHERE mil_id = %s", (mil_id,))
					mil=curs.fetchone( )
					if mil is not None:
						curs.execute(f"SELECT bd_name, count FROM builds WHERE build_id = {mil[4]}")
						bld = curs.fetchone( )
						if bld is None:
							curs.execute(
								f"SELECT anders FROM users WHERE user_id = %s",
								(self.user_id,)
								)
							user_profile=curs.fetchone( )
							if user_profile[0] >= mil[0]:
								curs.execute(
										f"UPDATE users SET {mil[2]} = {mil[2]} + {mil[1]}, anders = anders - {mil[0]} WHERE user_id = {self.user_id}"
										)
								conn.commit( )

								morph = pymorphy2.MorphAnalyzer( )
								mil_name = morph.parse(mil[3])[0]
								mil_name = mil_name.inflect({'gent'}).word.capitalize( )
								self.vk.messages.send(
										peer_id=self.peer_id,
										random_id=random.randint(0, 10000000000),
										message=f"&#9989; Поздравляем!\nВы приобрели {mil[1]} {mil_name}!"
										)
							else:
								self.vk.messages.send(
										peer_id=self.peer_id,
										random_id=random.randint(0, 10000000000),
										message=f"&#10062; Вам нужно еще %s" % (
												numeral.get_plural(
														mil[0] - user_profile[0], ("Андер", "Андеров", "Андера")
														))
										)
						else:
							curs.execute(f"SELECT anders, {bld[0]}*{bld[1]}, {mil[2]} FROM users WHERE user_id = %s", (self.user_id,))
							user_profile=curs.fetchone( )
							if user_profile[1] >= user_profile[2]:
								if user_profile[0] >= mil[0]:
									curs.execute(
											f"UPDATE users SET {mil[2]} = {mil[2]} + {mil[1]}, anders = anders - {mil[0]} WHERE user_id = {self.user_id}"
											)
									conn.commit( )

									morph = pymorphy2.MorphAnalyzer( )
									mil_name = morph.parse(mil[3])[0]
									mil_name = mil_name.inflect({'gent'}).word.capitalize( )
									self.vk.messages.send(
											peer_id=self.peer_id,
											random_id=random.randint(0, 10000000000),
											message=f"&#9989; Поздравляем!\nВы приобрели {mil[1]} {mil_name}!"
											)
								else:
									self.vk.messages.send(
											peer_id=self.peer_id,
										random_id=random.randint(0, 10000000000),
										message=f"&#10062; Вам нужно еще %s" % (
												numeral.get_plural(
														mil[0] - user_profile[0], ("Андер", "Андеров", "Андера")
														))
									)
							else:
								self.vk.messages.send(
									peer_id=self.peer_id,
									random_id=random.randint(0, 10000000000),
									message="&#10062; У вас недостаточно построек, для расположения такого количества данного вида войск."
									)
					else:
						self.vk.messages.send(
								peer_id=self.peer_id,
								random_id=random.randint(0, 10000000000),
								message="&#10062; Войска с таким ID не существует. Чтобы узнать все виды войск, напишите: '/listmil' (Без кавычек)"
								)
				else:
					curs.execute("SELECT cost, count, bd_name, name, bld_id FROM military WHERE name = %s", (mil_id.capitalize(),))
					mil = curs.fetchone( )
					if mil is not None:
						curs.execute(f"SELECT bd_name, count FROM builds WHERE build_id = {mil[4]}")
						bld=curs.fetchone( )
						if bld is None:
							curs.execute(
								f"SELECT anders FROM users WHERE user_id = %s",
								(self.user_id,)
								)
							user_profile=curs.fetchone( )
							if user_profile[0] >= mil[0]:
								curs.execute(
										f"UPDATE users SET {mil[2]} = {mil[2]} + {mil[1]}, anders = anders - {mil[0]} WHERE user_id = {self.user_id}"
										)
								conn.commit( )

								morph = pymorphy2.MorphAnalyzer( )
								mil_name = morph.parse(mil[3])[0]
								mil_name = mil_name.inflect({'gent'}).word.capitalize( )
								self.vk.messages.send(
										peer_id=self.peer_id,
										random_id=random.randint(0, 10000000000),
										message=f"&#9989; Поздравляем!\nВы приобрели {mil[1]} {mil_name}!"
										)
							else:
								self.vk.messages.send(
										peer_id=self.peer_id,
										random_id=random.randint(0, 10000000000),
										message=f"&#10062; Вам нужно еще %s" % (
												numeral.get_plural(
														mil[0] - user_profile[0], ("Андер", "Андеров", "Андера")
														))
										)
						else:
							curs.execute(
								f"SELECT anders, {bld[0]}*{bld[1]}, {mil[2]} FROM users WHERE user_id = %s", (self.user_id,)
								)
							user_profile=curs.fetchone( )
							if user_profile[1] >= user_profile[2]:
								if user_profile[0] >= mil[0]:
									curs.execute(
											f"UPDATE users SET {mil[2]} = {mil[2]} + {mil[1]}, anders = anders - {mil[0]} WHERE user_id = {self.user_id}"
											)
									conn.commit( )

									morph = pymorphy2.MorphAnalyzer( )
									mil_name = morph.parse(mil[3])[0]
									mil_name = mil_name.inflect({'gent'}).word.capitalize( )
									self.vk.messages.send(
											peer_id=self.peer_id,
											random_id=random.randint(0, 10000000000),
											message=f"&#9989; Поздравляем!\nВы приобрели {mil[1]} {mil_name}!"
											)
								else:
									self.vk.messages.send(
											peer_id=self.peer_id,
											random_id=random.randint(0, 10000000000),
											message=f"&#10062; Вам нужно еще %s" % (
													numeral.get_plural(
															mil[0] - user_profile[0], ("Андер", "Андеров", "Андера")
															))
											)
							else:
								self.vk.messages.send(
									peer_id=self.peer_id,
									random_id=random.randint(0, 10000000000),
									message="&#10062; У вас недостаточно построек, для расположения такого количества данного вида войск."
									)

					else:
						self.vk.messages.send(
								peer_id=self.peer_id,
								random_id=random.randint(0, 10000000000),
								message="&#10062; Войска с таким названием не существует. Чтобы узнать все виды войск, напишите: '/listmil' (Без кавычек)"
								)
		elif len(self.command.split(" ")) >= 3:
			conn=pymysql.connect(
				host="triniti.ru-hoster.com",
				user=self.user,
				password=self.passw,
				db='demkaXvl',
				charset='utf8', init_command='SET NAMES UTF8'
				)
			curs=conn.cursor( )
			curs.execute(f'SELECT verif FROM conversations WHERE peer_id = {self.peer_id}')
			if curs.fetchone( )[0]==1:
				mil_id=self.command.split(" ")[1]
				count=self.command.split(" ")[2]
				if mil_id.isdigit( ):
					if count.isdigit( ):
						count=int(count)
						if count > 0:
							curs.execute(
								f"SELECT cost*{count}, count*{count}, bd_name, name, bld_id FROM military WHERE mil_id = %s", (mil_id,)
								)
							mil=curs.fetchone( )
							if mil is not None:
								curs.execute(f"SELECT bd_name, count FROM builds WHERE build_id = {mil[4]}")
								bld=curs.fetchone( )
								if bld is None:
									curs.execute(
										f"SELECT anders FROM users WHERE user_id = %s",
										(self.user_id,)
										)
									user_profile=curs.fetchone( )
									if user_profile[0] >= mil[0]:
										curs.execute(
											f"UPDATE users SET {mil[2]} = {mil[2]} + {mil[1]}, anders = anders - {mil[0]} WHERE user_id = {self.user_id}"
											)
										conn.commit( )

										morph=pymorphy2.MorphAnalyzer( )
										mil_name=morph.parse(mil[3])[0]
										mil_name=mil_name.inflect({'gent'}).word.capitalize( )
										self.vk.messages.send(
											peer_id=self.peer_id,
											random_id=random.randint(0, 10000000000),
											message=f"&#9989; Поздравляем!\nВы приобрели {mil[1]} {mil_name}!"
											)
									else:
										self.vk.messages.send(
											peer_id=self.peer_id,
											random_id=random.randint(0, 10000000000),
											message=f"&#10062; Вам нужно еще %s" % (
												numeral.get_plural(
													mil[0] - user_profile[0], ("Андер", "Андеров", "Андера")
													))
											)
								else:
									curs.execute(
										f"SELECT anders, {bld[0]}*{bld[1]}, {mil[2]} FROM users WHERE user_id = %s",
										(self.user_id,)
										)
									user_profile=curs.fetchone( )
									if user_profile[1] >= user_profile[2]:
										if user_profile[0] >= mil[0]:
											curs.execute(
												f"UPDATE users SET {mil[2]} = {mil[2]} + {mil[1]}, anders = anders - {mil[0]} WHERE user_id = {self.user_id}"
												)
											conn.commit( )

											morph=pymorphy2.MorphAnalyzer( )
											mil_name=morph.parse(mil[3])[0]
											mil_name=mil_name.inflect({'gent'}).word.capitalize( )
											self.vk.messages.send(
												peer_id=self.peer_id,
												random_id=random.randint(0, 10000000000),
												message=f"&#9989; Поздравляем!\nВы приобрели {mil[1]} {mil_name}!"
												)
										else:
											self.vk.messages.send(
												peer_id=self.peer_id,
												random_id=random.randint(0, 10000000000),
												message=f"&#10062; Вам нужно еще %s" % (
													numeral.get_plural(
														mil[0] - user_profile[0], ("Андер", "Андеров", "Андера")
														))
												)
									else:
										self.vk.messages.send(
											peer_id=self.peer_id,
											random_id=random.randint(0, 10000000000),
											message="&#10062; У вас недостаточно построек, для расположения такого количества данного вида войск."
											)
							else:
								self.vk.messages.send(
									peer_id=self.peer_id,
									random_id=random.randint(0, 10000000000),
									message="&#10062; Войска с таким ID не существует. Чтобы узнать все виды войск, напишите: '/listmil' (Без кавычек)"
									)
						else:
							self.vk.messages.send(
								peer_id=self.peer_id,
								random_id=random.randint(0, 10000000000),
								message="&#10062; Вы неверно указали кол-во закупок."
								)
					else:
						self.vk.messages.send(
							peer_id=self.peer_id,
							random_id=random.randint(0, 10000000000),
							message="&#10062; Вы неверно указали кол-во закупок."
							)
				else:
					if count.isdigit( ):
						count=int(count)
						if count > 0:
							curs.execute(
								f"SELECT cost*{count}, count*{count}, bd_name, name, bld_id FROM military WHERE name = %s", (mil_id.capitalize( ),)
								)
							mil=curs.fetchone( )
							if mil is not None:
								curs.execute(f"SELECT bd_name, count FROM builds WHERE build_id = {mil[4]}")
								bld=curs.fetchone( )
								if bld is None:
									curs.execute(
										f"SELECT anders FROM users WHERE user_id = %s",
										(self.user_id,)
										)
									user_profile=curs.fetchone( )
									if user_profile[0] >= mil[0]:
										curs.execute(
											f"UPDATE users SET {mil[2]} = {mil[2]} + {mil[1]}, anders = anders - {mil[0]} WHERE user_id = {self.user_id}"
											)
										conn.commit( )

										morph=pymorphy2.MorphAnalyzer( )
										mil_name=morph.parse(mil[3])[0]
										mil_name=mil_name.inflect({'gent'}).word.capitalize( )
										self.vk.messages.send(
											peer_id=self.peer_id,
											random_id=random.randint(0, 10000000000),
											message=f"&#9989; Поздравляем!\nВы приобрели {mil[1]} {mil_name}!"
											)
									else:
										self.vk.messages.send(
											peer_id=self.peer_id,
											random_id=random.randint(0, 10000000000),
											message=f"&#10062; Вам нужно еще %s" % (
												numeral.get_plural(
													mil[0] - user_profile[0], ("Андер", "Андеров", "Андера")
													))
											)
								else:
									curs.execute(
										f"SELECT anders, {bld[0]}*{bld[1]}, {mil[2]} FROM users WHERE user_id = %s",
										(self.user_id,)
										)
									user_profile=curs.fetchone( )
									if user_profile[1] >= user_profile[2]:
										if user_profile[0] >= mil[0]:
											curs.execute(
												f"UPDATE users SET {mil[2]} = {mil[2]} + {mil[1]}, anders = anders - {mil[0]} WHERE user_id = {self.user_id}"
												)
											conn.commit( )

											morph=pymorphy2.MorphAnalyzer( )
											mil_name=morph.parse(mil[3])[0]
											mil_name=mil_name.inflect({'gent'}).word.capitalize( )
											self.vk.messages.send(
												peer_id=self.peer_id,
												random_id=random.randint(0, 10000000000),
												message=f"&#9989; Поздравляем!\nВы приобрели {mil[1]} {mil_name}!"
												)
										else:
											self.vk.messages.send(
												peer_id=self.peer_id,
												random_id=random.randint(0, 10000000000),
												message=f"&#10062; Вам нужно еще %s" % (
													numeral.get_plural(
														mil[0] - user_profile[0], ("Андер", "Андеров", "Андера")
														))
												)
									else:
										self.vk.messages.send(
											peer_id=self.peer_id,
											random_id=random.randint(0, 10000000000),
											message="&#10062; У вас недостаточно построек, для расположения такого количества данного вида войск."
											)
							else:
								self.vk.messages.send(
									peer_id=self.peer_id,
									random_id=random.randint(0, 10000000000),
									message="&#10062; Войска с таким названием не существует. Чтобы узнать все виды войск, напишите: '/listmil' (Без кавычек)"
									)
						else:
							self.vk.messages.send(
								peer_id=self.peer_id,
								random_id=random.randint(0, 10000000000),
								message="&#10062; Вы неверно указали кол-во закупок."
								)
					else:
						self.vk.messages.send(
							peer_id=self.peer_id,
							random_id=random.randint(0, 10000000000),
							message="&#10062; Вы неверно указали кол-во закупок."
							)
		else:
			self.vk.messages.send(
					peer_id=self.peer_id,
					random_id=random.randint(0, 10000000000),
					message=f"&#10062; Указано недостаточно аргументов."
					)
	
	def buyBuild(self):
		if len(self.command.split(" ")) == 2:
			conn = pymysql.connect(
					host="triniti.ru-hoster.com",
					user=self.user,
					password=self.passw,
					db='demkaXvl',
					charset='utf8', init_command='SET NAMES UTF8'
					)
			curs = conn.cursor( )
			curs.execute(f'SELECT verif FROM conversations WHERE peer_id = {self.peer_id}')
			if curs.fetchone( )[0] == 1:
				curs.execute("SELECT steel, wood, food, w_cris, b_cris, stone, vlg*5+city*20, swml+farm+mine+altr+tmpl FROM users WHERE user_id = %s", (self.user_id,))
				user_profile = curs.fetchone( )
				build_id = self.command.split(" ")[1]
				if build_id.isdigit( ):

					# По ID
					curs.execute(
							"SELECT food, steel, wood, b_cris, w_cris, bd_name, name, stone FROM builds WHERE build_id = %s",
							(build_id,)
							)
					build = curs.fetchone( )
					if build is None:
						self.vk.messages.send(
								peer_id=self.peer_id,
								random_id=random.randint(0, 10000000000),
								message="&#10062;Здания с таким ID не существует. Чтобы узнать все о Зданиях, напишите '/listbld' (Без кавычек)"
								)
					else:
						if user_profile[6] > user_profile[7] or build[5] in ["city","vlg"]:
							if user_profile[2] >= build[0]:
								if user_profile[0] >= build[1]:
									if user_profile[1] >= build[2]:
										if user_profile[3] >= build[4]:
											if user_profile[4] >= build[3]:
												if user_profile[5] >= build[7]:
													curs.execute(
														f"UPDATE users SET {build[5]} = {build[5]} + 1, wood = wood - {build[2]}, steel = steel - {build[1]}, food = food - {build[0]}, b_cris = b_cris - {build[3]}, w_cris = w_cris - {build[4]}, stone = stone - {build[7]} WHERE user_id = {self.user_id}"
														)
													conn.commit( )

													morph=pymorphy2.MorphAnalyzer( )
													build_name=morph.parse(build[6])[0]
													build_name=build_name.inflect({'gent'}).word.capitalize( )
													self.vk.messages.send(
														peer_id=self.peer_id,
														random_id=random.randint(0, 10000000000),
														message=f"&#9989; Поздравляем вас с покупкой {build_name}!"
														)
												else:
													self.vk.messages.send(
														peer_id=self.peer_id,
														random_id=random.randint(0, 10000000000),
														message=f"&#10062; У вас не хватает %s Тьмы." % (
															numeral.get_plural(
																build[7] - user_profile[5],
																("Камня", "Камней")
																))
														)
											else:
												self.vk.messages.send(
														peer_id=self.peer_id,
														random_id=random.randint(0, 10000000000),
														message=f"&#10062; У вас не хватает %s Тьмы." % (
																numeral.get_plural(
																		build[4] - user_profile[3],
																		("Кристалла", "Кристаллов")
																		))
														)
										else:
											self.vk.messages.send(
													peer_id=self.peer_id,
													random_id=random.randint(0, 10000000000),
													message=f"&#10062; У вас не хватает %s Cвета." % (
															numeral.get_plural(
																	build[4] - user_profile[3], ("Кристалла", "Кристаллов")
																	))
													)
									else:
										self.vk.messages.send(
												peer_id=self.peer_id,
												random_id=random.randint(0, 10000000000),
												message=f"&#10062; У вас не хватает {build[2] - user_profile[1]} ед. Дерева."
												)
								else:
									self.vk.messages.send(
											peer_id=self.peer_id,
											random_id=random.randint(0, 10000000000),
											message=f"&#10062; У вас не хватает {build[1] - user_profile[0]} ед. Металлов."
											)
							else:
								self.vk.messages.send(
										peer_id=self.peer_id,
										random_id=random.randint(0, 10000000000),
										message=f"&#10062; У вас не хватает {build[0] - user_profile[2]} ед. Продовольствия."
										)
						else:
							self.vk.messages.send(
								peer_id=self.peer_id,
								random_id=random.randint(0, 10000000000),
								message=f"&#10062; Возле ваших поселение слишком много предприятий. Чтобы построить еще предприятие нужно построить и город."
								)
				else:
					# По названию
					curs.execute(
							"SELECT food, steel, wood, b_cris, w_cris, bd_name, name, stone FROM builds WHERE name = %s",
							(build_id.capitalize( ),)
							)
					build = curs.fetchone( )
					if build is None:
						self.vk.messages.send(
								peer_id=self.peer_id,
								random_id=random.randint(0, 10000000000),
								message="&#10062; Здания с таким Названием не существует. Чтобы узнать все о Зданиях, напишите '/listbld' (Без кавычек)"
								)
					else:
						if user_profile[6] > user_profile[7] or build[5] in ["city", "vlg"]:
							if user_profile[2] >= build[0]:
								if user_profile[0] >= build[1]:
									if user_profile[1] >= build[2]:
										if user_profile[3] >= build[4]:
											if user_profile[4] >= build[3]:
												if user_profile[5] >= build[7]:
													curs.execute(
														f"UPDATE users SET {build[5]} = {build[5]} + 1, wood = wood - {build[2]}, steel = steel - {build[1]}, food = food - {build[0]}, b_cris = b_cris - {build[3]}, w_cris = w_cris - {build[4]}, stone = stone - {build[7]} WHERE user_id = {self.user_id}"
														)
													conn.commit( )

													morph=pymorphy2.MorphAnalyzer( )
													build_name=morph.parse(build[6])[0]
													build_name=build_name.inflect({'gent'}).word.capitalize( )
													self.vk.messages.send(
														peer_id=self.peer_id,
														random_id=random.randint(0, 10000000000),
														message=f"&#9989; Поздравляем вас с покупкой {build_name}!"
														)
												else:
													self.vk.messages.send(
														peer_id=self.peer_id,
														random_id=random.randint(0, 10000000000),
														message=f"&#10062; У вас не хватает %s Тьмы." % (
															numeral.get_plural(
																build[7] - user_profile[5],
																("Камня", "Камней")
																))
														)
											else:
												self.vk.messages.send(
														peer_id=self.peer_id,
														random_id=random.randint(0, 10000000000),
														message=f"&#10062; У вас не хватает %s Тьмы." % (
																numeral.get_plural(
																		build[4] - user_profile[3],
																		("Кристалла", "Кристаллов")
																		))
														)
										else:
											self.vk.messages.send(
													peer_id=self.peer_id,
													random_id=random.randint(0, 10000000000),
													message=f"&#10062; У вас не хватает %s Cвета." % (
															numeral.get_plural(
																	build[4] - user_profile[3], ("Кристалла", "Кристаллов")
																	))
													)
									else:
										self.vk.messages.send(
												peer_id=self.peer_id,
												random_id=random.randint(0, 10000000000),
												message=f"&#10062; У вас не хватает {build[2] - user_profile[1]} ед. Дерева."
												)
								else:
									self.vk.messages.send(
											peer_id=self.peer_id,
											random_id=random.randint(0, 10000000000),
											message=f"&#10062; У вас не хватает {build[1] - user_profile[0]} ед. Металлов."
											)
							else:
								self.vk.messages.send(
										peer_id=self.peer_id,
										random_id=random.randint(0, 10000000000),
										message=f"&#10062; У вас не хватает {build[0] - user_profile[2]} ед. Продовольствия."
										)
						else:
							self.vk.messages.send(
								peer_id=self.peer_id,
								random_id=random.randint(0, 10000000000),
								message=f"&#10062; Возле ваших поселение слишком много предприятий. Чтобы построить еще предприятие нужно построить и город."
								)
		elif len(self.command.split(" ")) >= 3:
			conn=pymysql.connect(
				host="triniti.ru-hoster.com",
				user=self.user,
				password=self.passw,
				db='demkaXvl',
				charset='utf8', init_command='SET NAMES UTF8'
				)
			curs=conn.cursor( )
			curs.execute(f'SELECT verif FROM conversations WHERE peer_id = {self.peer_id}')
			if curs.fetchone( )[0]==1:
				curs.execute("SELECT steel, wood, food, w_cris, b_cris, stone, vlg*5+city*20, swml+farm+mine+altr+tmpl  FROM users WHERE user_id = %s", (self.user_id,))
				user_profile=curs.fetchone( )
				build_id=self.command.split(" ")[1]
				count=self.command.split(" ")[2]
				if build_id.isdigit( ):
					# По ID
					if count.isdigit( ):
						count=int(count)
						if count > 0:
							curs.execute(
								f"SELECT food*{count}, steel*{count}, wood*{count}, b_cris*{count}, w_cris*{count}, bd_name, name, stone*{count} FROM builds WHERE build_id = %s",
								(build_id,)
								)
							build=curs.fetchone( )
							if build is None:
								self.vk.messages.send(
									peer_id=self.peer_id,
									random_id=random.randint(0, 10000000000),
									message="&#10062;Здания с таким ID не существует. Чтобы узнать все о Зданиях, напишите '/listbld' (Без кавычек)"
									)
							else:
								if user_profile[6] > user_profile[7] or build[5] in ["city", "vlg"]:
									if user_profile[2] >= build[0]:
										if user_profile[0] >= build[1]:
											if user_profile[1] >= build[2]:
												if user_profile[3] >= build[4]:
													if user_profile[4] >= build[3]:
														if user_profile[5] >= build[7]:
															curs.execute(
																f"UPDATE users SET {build[5]} = {build[5]} + {count}, wood = wood - {build[2]}, steel = steel - {build[1]}, food = food - {build[0]}, b_cris = b_cris - {build[3]}, w_cris = w_cris - {build[4]}, stone = stone - {build[7]} WHERE user_id = {self.user_id}"
																)
															conn.commit( )

															morph=pymorphy2.MorphAnalyzer( )
															build_name=morph.parse(build[6])[0]
															build_name=build_name.inflect({'gent'}).word.capitalize( )
															self.vk.messages.send(
																peer_id=self.peer_id,
																random_id=random.randint(0, 10000000000),
																message=f"&#9989; Поздравляем вас с покупкой {build_name}!"
																)
														else:
															self.vk.messages.send(
																peer_id=self.peer_id,
																random_id=random.randint(0, 10000000000),
																message=f"&#10062; У вас не хватает %s Тьмы." % (
																	numeral.get_plural(
																		build[7] - user_profile[5],
																		("Камня", "Камней")
																		))
																)
													else:
														self.vk.messages.send(
															peer_id=self.peer_id,
															random_id=random.randint(0, 10000000000),
															message=f"&#10062; У вас не хватает %s Тьмы." % (
																numeral.get_plural(
																	build[4] - user_profile[3],
																	("Кристалла", "Кристаллов")
																	))
															)
												else:
													self.vk.messages.send(
														peer_id=self.peer_id,
														random_id=random.randint(0, 10000000000),
														message=f"&#10062; У вас не хватает %s Cвета." % (
															numeral.get_plural(
																build[4] - user_profile[3], ("Кристалла", "Кристаллов")
																))
														)
											else:
												self.vk.messages.send(
													peer_id=self.peer_id,
													random_id=random.randint(0, 10000000000),
													message=f"&#10062; У вас не хватает {build[2] - user_profile[1]} ед. Дерева."
													)
										else:
											self.vk.messages.send(
												peer_id=self.peer_id,
												random_id=random.randint(0, 10000000000),
												message=f"&#10062; У вас не хватает {build[1] - user_profile[0]} ед. Металлов."
												)
									else:
										self.vk.messages.send(
											peer_id=self.peer_id,
											random_id=random.randint(0, 10000000000),
											message=f"&#10062; У вас не хватает {build[0] - user_profile[2]} ед. Продовольствия."
											)
								else:
									self.vk.messages.send(
										peer_id=self.peer_id,
										random_id=random.randint(0, 10000000000),
										message=f"&#10062; Возле ваших поселение слишком много предприятий. Чтобы построить еще предприятие нужно построить и город."
										)
						else:
							self.vk.messages.send(
								peer_id=self.peer_id,
								random_id=random.randint(0, 10000000000),
								message=f"&#10062; Вы неверно указали кол-во зданий."
								)
					else:
						self.vk.messages.send(
							peer_id=self.peer_id,
							random_id=random.randint(0, 10000000000),
							message=f"&#10062; Вы неверно указали кол-во зданий."
							)
				else:
					# По названию
					if count.isdigit( ):
						count = int(count)
						if count > 0:
							curs.execute(
								f"SELECT food*{count}, steel*{count}, wood*{count}, b_cris*{count}, w_cris*{count}, bd_name, name, stone*{count} FROM builds WHERE name = %s",
								(build_id.capitalize( ),)
								)
							build=curs.fetchone( )
							if build is None:
								self.vk.messages.send(
									peer_id=self.peer_id,
									random_id=random.randint(0, 10000000000),
									message="&#10062; Здания с таким Названием не существует. Чтобы узнать все о Зданиях, напишите '/listbld' (Без кавычек)"
									)
							else:
								if user_profile[6] > user_profile[7] or build[5] in ["city", "vlg"]:
									if user_profile[2] >= build[0]:
										if user_profile[0] >= build[1]:
											if user_profile[1] >= build[2]:
												if user_profile[3] >= build[4]:
													if user_profile[4] >= build[3]:
														if user_profile[5] >=  build[7]:
															curs.execute(
																f"UPDATE users SET {build[5]} = {build[5]} + 1, wood = wood - {build[2]}, steel = steel - {build[1]}, food = food - {build[0]}, b_cris = b_cris - {build[3]}, w_cris = w_cris - {build[4]}, stone = stone - {build[7]} WHERE user_id = {self.user_id}"
																)
															conn.commit( )

															morph=pymorphy2.MorphAnalyzer( )
															build_name=morph.parse(build[6])[0]
															build_name=build_name.inflect({'gent'}).word.capitalize( )
															self.vk.messages.send(
																peer_id=self.peer_id,
																random_id=random.randint(0, 10000000000),
																message=f"&#9989; Поздравляем вас с покупкой {build_name}!"
																)
														else:
															self.vk.messages.send(
																peer_id=self.peer_id,
																random_id=random.randint(0, 10000000000),
																message=f"&#10062; У вас не хватает %s Тьмы." % (
																	numeral.get_plural(
																		build[7] - user_profile[5],
																		("Камня", "Камней")
																		))
																)
													else:
														self.vk.messages.send(
															peer_id=self.peer_id,
															random_id=random.randint(0, 10000000000),
															message=f"&#10062; У вас не хватает %s Тьмы." % (
																numeral.get_plural(
																	build[4] - user_profile[3],
																	("Кристалла", "Кристаллов")
																	))
															)
												else:
													self.vk.messages.send(
														peer_id=self.peer_id,
														random_id=random.randint(0, 10000000000),
														message=f"&#10062; У вас не хватает %s Cвета." % (
															numeral.get_plural(
																build[4] - user_profile[3], ("Кристалла", "Кристаллов")
																))
														)
											else:
												self.vk.messages.send(
													peer_id=self.peer_id,
													random_id=random.randint(0, 10000000000),
													message=f"&#10062; У вас не хватает {build[2] - user_profile[1]} ед. Дерева."
													)
										else:
											self.vk.messages.send(
												peer_id=self.peer_id,
												random_id=random.randint(0, 10000000000),
												message=f"&#10062; У вас не хватает {build[1] - user_profile[0]} ед. Металлов."
												)
									else:
										self.vk.messages.send(
											peer_id=self.peer_id,
											random_id=random.randint(0, 10000000000),
											message=f"&#10062; У вас не хватает {build[0] - user_profile[2]} ед. Продовольствия."
											)
								else:
									self.vk.messages.send(
										peer_id=self.peer_id,
										random_id=random.randint(0, 10000000000),
										message=f"&#10062; Возле ваших поселение слишком много предприятий. Чтобы построить еще предприятие нужно построить и город."
										)
						else:
							self.vk.messages.send(
								peer_id=self.peer_id,
								random_id=random.randint(0, 10000000000),
								message=f"&#10062; Вы неверно указали кол-во зданий."
								)
					else:
						self.vk.messages.send(
							peer_id=self.peer_id,
							random_id=random.randint(0, 10000000000),
							message=f"&#10062; Вы неверно указали кол-во зданий."
							)
		else:
			self.vk.messages.send(
					peer_id=self.peer_id,
					random_id=random.randint(0, 10000000000),
					message=f"&#10062; Указано недостаточно аргументов."
					)
	
	def transaction(self):
		# /trans [кол во] [адресат]
		conn = pymysql.connect(
				host="triniti.ru-hoster.com",
				user=self.user,
				password=self.passw,
				db='demkaXvl',
				charset='utf8', init_command='SET NAMES UTF8'
				)
		curs = conn.cursor( )
		curs.execute(f'SELECT verif FROM conversations WHERE peer_id = {self.peer_id}')
		ch = int(curs.fetchone( )[0])
		if ch == 1:
			val = self.command.split(" ")[1]
			if val.isdigit( ):
				curs.execute("SELECT anders FROM users WHERE user_id = %s", (self.user_id,))
				if curs.fetchone( )[0] >= int(val):
					try:
						to_user = 0
						if len(self.command.split(" ")) >= 3:
							if self.command.split(" ")[2].startswith("http") or self.command.split(" ")[2].startswith(
									"https"
									):
								short_name = self.command.split(" ")[2].split("/")[3]
								to_user = self.vk.users.get(user_ids=short_name)[0]['id']
							
							elif self.command.split(" ")[2].startswith("[id"):
								to_user = self.command.split(" ")[2].split("|")[0].replace("[id", "")
						else:
							try:
								if 'reply_message' in self.event.object["message"].keys( ):
									if self.event.object["message"]["reply_message"]["from_id"] > 0:
										to_user = self.event.object["message"]["reply_message"]["from_id"]
									else:
										self.vk.messages.send(
												peer_id=self.peer_id,
												random_id=random.randint(0, 10000000000),
												message=f"&#10062; [club{str(self.event.object['message']['reply_message']['from_id']).replace('-', '')}|Эта страница] не является страницей пользователя."
												)
								else:
									self.vk.messages.send(
										peer_id=self.peer_id,
										random_id=random.randint(0, 10000000000),
										message=f"&#10062; Указаны не все аргументы."
										)
							except Exception:
								pass
						
						curs.execute("SELECT peer_id FROM users WHERE user_id = %s", (to_user,))
						to_chat = curs.fetchone( )
						if to_chat is None:
							self.vk.messages.send(
									peer_id=self.peer_id,
									random_id=random.randint(0, 10000000000),
									message=f"&#10062; [id{to_user}|Этот пользователь] не зарегистрирован в Боте."
									)
						else:
							if int(to_user) != self.user_id:
								now_utc = datetime.now(timezone('UTC'))
								time = str(now_utc.astimezone(timezone('Europe/Moscow'))).split(".")[0]
								curs.execute(f"UPDATE users SET anders = anders + {val} WHERE user_id = {to_user}")
								conn.commit( )
								curs.execute(f"UPDATE users SET anders = anders - {val} WHERE user_id = {self.user_id}")
								conn.commit( )
								curs.execute(
										f"INSERT INTO transactions (from_user, to_user, datetime, summ) VALUES (%s, %s, %s, %s)",
										(self.user_id, to_user, time, val)
										)
								conn.commit( )
								curs.execute("SELECT trans_id FROM transactions ORDER BY trans_id DESC LIMIT 1")
								last_post = curs.fetchone( )[0]
								
								self.vk.messages.send(
										peer_id=self.adms_chat,
										random_id=random.randint(0, 10000000000),
										message=f"Перевод:\n FROM: @id{self.user_id}\nTO: @id{to_user}\n SUMM: {val}\nTRANS_ID: {last_post}",
										disable_mentions=1
										)
								self.vk.messages.send(
										peer_id=self.peer_id,
										random_id=random.randint(0, 10000000000),
										message=f"&#9989; [id{self.user_id}|Вы] отправили {val} ед. Андеров на счет @id{to_user}"
										)
								self.vk.messages.send(
										peer_id=int(to_chat[0]),
										random_id=random.randint(0, 10000000000),
										message=f"&#9989; [id{to_user}|Вам] пришло {val} ед. Андеров от @id{self.user_id}"
										)
							else:
								self.vk.messages.send(
										peer_id=self.peer_id,
										random_id=random.randint(0, 10000000000),
										message=f"&#10062; Нельзя совершить перевод самому себе."
										)
					except Exception:
						self.vk.messages.send(
								peer_id=self.peer_id,
								random_id=random.randint(0, 10000000000),
								message=f"&#10062; Произошла ошибка. Возможно данная ссылка не ведет на страницу пользователя\n{traceback.format_exc( )}"
								)
						self.vk.messages.send(
								peer_id=2e9 + 4,
								random_id=random.randint(0, 10000000000),
								message=f"[ERROR]\n{traceback.format_exc( )}\n\nLAST_EVENT: {self.event}"
								)
				else:
					self.vk.messages.send(
							peer_id=self.peer_id,
							random_id=random.randint(0, 10000000000),
							message="&#10062; У вас недостаточно средств."
							)
			else:
				self.vk.messages.send(
						peer_id=self.peer_id,
						random_id=random.randint(0, 10000000000),
						message="&#10062; Вы неверно указали сумму перевода."
						)
	
	def transactionRejection(self):
		if self.user_id in self.adms:
			conn = pymysql.connect(
					host="triniti.ru-hoster.com",
					user=self.user,
					password=self.passw,
					db='demkaXvl',
					charset='utf8', init_command='SET NAMES UTF8'
					)
			curs = conn.cursor( )
			trans_id = self.command.split(" ")[1]
			if trans_id.isdigit( ):
				curs.execute('SELECT * FROM transactions WHERE trans_id = %s', (trans_id,))
				trans_info = curs.fetchone( )
				if trans_info is None:
					self.vk.messages.send(
							peer_id=self.peer_id,
							random_id=random.randint(0, 10000000000),
							message="Транзакции с таким ID не существует."
							)
				else:
					curs.execute(f"UPDATE users SET anders = anders - {trans_info[3]} WHERE user_id = {trans_info[2]}")
					conn.commit( )
					curs.execute(f"UPDATE users SET anders = anders + {trans_info[3]} WHERE user_id = {trans_info[1]}")
					conn.commit( )
					curs.execute(f"UPDATE transactions SET accept = 0 WHERE trans_id = %s", (trans_id,))
					conn.commit( )
					
					self.vk.messages.send(
							peer_id=self.peer_id,
							random_id=random.randint(0, 10000000000),
							message=f"Транзанкция #{trans_id} отменена."
							)
			else:
				self.vk.messages.send(
						peer_id=self.peer_id,
						random_id=random.randint(0, 10000000000),
						message="ID транзакции должно состоять только из цифр."
						)
	
	def raceInformation(self):
		# ДОБАВИТЬ ПОЛЕ С КАМНЕМ.
		conn = pymysql.connect(
				host="triniti.ru-hoster.com",
				user=self.user,
				password=self.passw,
				db='demkaXvl',
				charset='utf8', init_command='SET NAMES UTF8'
				)
		curs = conn.cursor( )
		curs.execute(f'SELECT verif FROM conversations WHERE peer_id = {self.peer_id}')
		ch = int(curs.fetchone( )[0])
		if ch == 1:
			if len(self.command.split(" ")) < 2:
				curs.execute(f"SELECT race_id FROM users WHERE user_id = {self.user_id}")
				race_id = curs.fetchone( )[0]
				curs.execute(
					"SELECT SUM(anders), SUM(food), SUM(steel), SUM(wood), SUM(w_cris), SUM(b_cris), SUM(exp), SUM(stone), COUNT(*) FROM users WHERE race_id = %s",
					(race_id,)
					)
				race_inv=curs.fetchone( )

				curs.execute(
					"SELECT SUM(inf),SUM(mag),SUM(arch),SUM(ctpl),SUM(bllsts),SUM(clvr),SUM(plds) FROM users WHERE race_id = %s",
					(race_id,)
					)
				mil_inv=curs.fetchone( )

				curs.execute(
					"SELECT SUM(farm),SUM(swml),SUM(mine),SUM(vlg),SUM(city),SUM(tmpl),SUM(altr) FROM users WHERE race_id = %s",
					(race_id,)
					)
				bld_inv=curs.fetchone( )
				curs.execute(
					"SELECT low_name, color FROM races WHERE race_id = %s",
					(race_id,)
					)
				low_name, color=curs.fetchone( )
				if race_id != 1:
					stats_pic=Image.open(f"race_profiles/{low_name}_раса.png")
					stats_pic_draw=ImageDraw.Draw(stats_pic)
					font=ImageFont.truetype("Aqum.ttf", size=20)

					stats_pic_draw.text(
							xy=(242, 208), text=race_inv[8], fill=color,
							font=ImageFont.truetype("Aqum.ttf", size=25)
							)  # RACE USERS COUNT
					stats_pic_draw.text(
						xy=(632, 227), text="V", fill="#080808",
						font=ImageFont.truetype("Aqum.ttf", size=25)
						)
					"""MILITARY"""
					stats_pic_draw.text(xy=(207, 419+36), text=str(mil_inv[0]), fill="black", font=font)
					stats_pic_draw.text(xy=(207, 518+36), text=str(mil_inv[2]), fill="black", font=font)
					stats_pic_draw.text(xy=(207, 617+36), text=str(mil_inv[5]), fill="black", font=font)
					stats_pic_draw.text(xy=(207, 716+36), text=str(mil_inv[6]), fill="black", font=font)
					stats_pic_draw.text(xy=(207, 814+36), text=str(mil_inv[1]), fill="black", font=font)
					stats_pic_draw.text(xy=(207, 912+36), text=str(mil_inv[3]), fill="black", font=font)
					stats_pic_draw.text(xy=(207, 1011+36), text=str(mil_inv[4]), fill="black", font=font)
					"""EXP"""
					stats_pic_draw.text(
							xy=(935, 121), text=str(round(race_inv[6], 3)), fill=color,
							font=ImageFont.truetype("Aqum.ttf", size=25)
							)
					"""MONEY"""
					stats_pic_draw.text(
							xy=(935, 208), text=str(race_inv[0]), fill=color,
							font=ImageFont.truetype("Aqum.ttf", size=25)
							)
					"""RESOURCES"""
					stats_pic_draw.text(xy=(631, 419+36), text=str(race_inv[1]), fill="black", font=font)
					stats_pic_draw.text(xy=(631, 518+36), text=str(race_inv[3]), fill="black", font=font)
					stats_pic_draw.text(xy=(631, 617+36), text=str(race_inv[2]), fill="black", font=font)
					stats_pic_draw.text(xy=(631, 716+36), text=str(race_inv[4]), fill="black", font=font)
					stats_pic_draw.text(xy=(631, 814+36), text=str(race_inv[5]), fill="black", font=font)
					"""BUILDS"""
					stats_pic_draw.text(xy=(1055, 419+36), text=str(bld_inv[0]), fill="black", font=font)
					stats_pic_draw.text(xy=(1055, 518+36), text=str(bld_inv[1]), fill="black", font=font)
					stats_pic_draw.text(xy=(1055, 617+36), text=str(bld_inv[2]), fill="black", font=font)
					stats_pic_draw.text(xy=(1055, 716+36), text=str(bld_inv[3]), fill="black", font=font)
					stats_pic_draw.text(xy=(1055, 814+36), text=str(bld_inv[4]), fill="black", font=font)
					stats_pic_draw.text(xy=(1055, 912+36), text=str(bld_inv[5]), fill="black", font=font)
					stats_pic_draw.text(xy=(1055, 1011+36), text=str(bld_inv[6]), fill="black", font=font)

					stats_pic.save('stats.png')
				else:
					stats_pic=Image.open(f"interfeys_dlya_bota_v3.png")
					stats_pic_draw=ImageDraw.Draw(stats_pic)
					font=ImageFont.truetype("Aqum.ttf", size=20)

					stats_pic_draw.text(
						xy=(245, 71), text=name, fill="white",
						font=ImageFont.truetype("Aqum.ttf", size=35)
						)  # RACE NAME
					"""MILITARY"""
					stats_pic_draw.text(xy=(207, 419), text=str(mil_inv[0]), fill="black", font=font)
					stats_pic_draw.text(xy=(207, 518), text=str(mil_inv[2]), fill="black", font=font)
					stats_pic_draw.text(xy=(207, 617), text=str(mil_inv[5]), fill="black", font=font)
					stats_pic_draw.text(xy=(207, 716), text=str(mil_inv[6]), fill="black", font=font)
					stats_pic_draw.text(xy=(207, 814), text=str(mil_inv[1]), fill="black", font=font)
					stats_pic_draw.text(xy=(207, 912), text=str(mil_inv[3]), fill="black", font=font)
					stats_pic_draw.text(xy=(207, 1011), text=str(mil_inv[4]), fill="black", font=font)
					"""EXP"""
					stats_pic_draw.text(
						xy=(357, 174), text=str(round(race_inv[6], 3)), fill="white",
						font=ImageFont.truetype("Aqum.ttf", size=25)
						)
					"""MONEY"""
					stats_pic_draw.text(
						xy=(835, 174), text=str(race_inv[0]), fill="white",
						font=ImageFont.truetype("Aqum.ttf", size=25)
						)
					"""RESOURCES"""
					stats_pic_draw.text(xy=(631, 419), text=str(race_inv[1]), fill="black", font=font)
					stats_pic_draw.text(xy=(631, 518), text=str(race_inv[3]), fill="black", font=font)
					stats_pic_draw.text(xy=(631, 617), text=str(race_inv[2]), fill="black", font=font)
					stats_pic_draw.text(xy=(631, 716), text=str(race_inv[4]), fill="black", font=font)
					stats_pic_draw.text(xy=(631, 814), text=str(race_inv[5]), fill="black", font=font)
					"""BUILDS"""
					stats_pic_draw.text(xy=(1055, 419), text=str(bld_inv[0]), fill="black", font=font)
					stats_pic_draw.text(xy=(1055, 518), text=str(bld_inv[1]), fill="black", font=font)
					stats_pic_draw.text(xy=(1055, 617), text=str(bld_inv[2]), fill="black", font=font)
					stats_pic_draw.text(xy=(1055, 716), text=str(bld_inv[3]), fill="black", font=font)
					stats_pic_draw.text(xy=(1055, 814), text=str(bld_inv[4]), fill="black", font=font)
					stats_pic_draw.text(xy=(1055, 912), text=str(bld_inv[5]), fill="black", font=font)
					stats_pic_draw.text(xy=(1055, 1011), text=str(bld_inv[6]), fill="black", font=font)

					stats_pic.save('stats.png')

				vk_upload=vk_api.VkUpload(self.vk_session)
				photo=vk_upload.photo_messages(photos="stats.png")
				photo=f'photo{photo[0]["owner_id"]}_{photo[0]["id"]}'

				self.vk.messages.send(peer_id=self.peer_id, random_id=random.randint(0, 10000000000), attachment=photo)
			else:
				race = self.command.split(" ", 1)[1]
				if race.isdigit( ):
					curs.execute(
							"SELECT SUM(anders), SUM(food), SUM(steel), SUM(wood), SUM(w_cris), SUM(b_cris), SUM(exp), SUM(stone), COUNT(*) FROM users WHERE race_id = %s",
							(race,)
							)
					race_inv = curs.fetchone( )
					if race_inv is None:
						self.vk.messages.send(
								peer_id=self.peer_id,
								random_id=random.randint(0, 10000000000),
								message="&#10062; Расы с таким ID не существует."
								)
					else:
						curs.execute(
								"SELECT SUM(inf),SUM(mag),SUM(arch),SUM(ctpl),SUM(bllsts),SUM(clvr),SUM(plds) FROM users WHERE race_id = %s",
								(race,)
								)
						mil_inv = curs.fetchone( )
						
						curs.execute(
								"SELECT SUM(farm),SUM(swml),SUM(mine),SUM(vlg),SUM(city),SUM(tmpl),SUM(altr) FROM users WHERE race_id = %s",
								(race,)
								)
						bld_inv = curs.fetchone( )
						curs.execute(
							"SELECT name, low_name, color FROM races WHERE race_id = %s",
							(race_id,)
							)
						name, low_name, color = curs.fetchone()
						if race != "1":
							stats_pic=Image.open(f"race_profiles/{low_name}_раса.png")
							stats_pic_draw=ImageDraw.Draw(stats_pic)
							font=ImageFont.truetype("Aqum.ttf", size=20)

							stats_pic_draw.text(
								xy=(632, 227), text="V", fill="#080808",
								font=ImageFont.truetype("Aqum.ttf", size=25)
								)

							stats_pic_draw.text(
								xy=(242, 208), text=race_inv[8], fill=color,
								font=ImageFont.truetype("Aqum.ttf", size=25)
								)  # RACE USERS COUNT
							"""MILITARY"""
							stats_pic_draw.text(xy=(207, 419 + 36), text=str(mil_inv[0]), fill="black", font=font)
							stats_pic_draw.text(xy=(207, 518 + 36), text=str(mil_inv[2]), fill="black", font=font)
							stats_pic_draw.text(xy=(207, 617 + 36), text=str(mil_inv[5]), fill="black", font=font)
							stats_pic_draw.text(xy=(207, 716 + 36), text=str(mil_inv[6]), fill="black", font=font)
							stats_pic_draw.text(xy=(207, 814 + 36), text=str(mil_inv[1]), fill="black", font=font)
							stats_pic_draw.text(xy=(207, 912 + 36), text=str(mil_inv[3]), fill="black", font=font)
							stats_pic_draw.text(xy=(207, 1011 + 36), text=str(mil_inv[4]), fill="black", font=font)
							"""EXP"""
							stats_pic_draw.text(
								xy=(935, 121), text=str(round(race_inv[6], 3)), fill=color,
								font=ImageFont.truetype("Aqum.ttf", size=25)
								)
							"""MONEY"""
							stats_pic_draw.text(
								xy=(935, 208), text=str(race_inv[0]), fill=color,
								font=ImageFont.truetype("Aqum.ttf", size=25)
								)
							"""RESOURCES"""
							stats_pic_draw.text(xy=(631, 419 + 36), text=str(race_inv[1]), fill="black", font=font)
							stats_pic_draw.text(xy=(631, 518 + 36), text=str(race_inv[3]), fill="black", font=font)
							stats_pic_draw.text(xy=(631, 617 + 36), text=str(race_inv[2]), fill="black", font=font)
							stats_pic_draw.text(xy=(631, 716 + 36), text=str(race_inv[4]), fill="black", font=font)
							stats_pic_draw.text(xy=(631, 814 + 36), text=str(race_inv[5]), fill="black", font=font)
							"""BUILDS"""
							stats_pic_draw.text(xy=(1055, 419 + 36), text=str(bld_inv[0]), fill="black", font=font)
							stats_pic_draw.text(xy=(1055, 518 + 36), text=str(bld_inv[1]), fill="black", font=font)
							stats_pic_draw.text(xy=(1055, 617 + 36), text=str(bld_inv[2]), fill="black", font=font)
							stats_pic_draw.text(xy=(1055, 716 + 36), text=str(bld_inv[3]), fill="black", font=font)
							stats_pic_draw.text(xy=(1055, 814 + 36), text=str(bld_inv[4]), fill="black", font=font)
							stats_pic_draw.text(xy=(1055, 912 + 36), text=str(bld_inv[5]), fill="black", font=font)
							stats_pic_draw.text(xy=(1055, 1011 + 36), text=str(bld_inv[6]), fill="black", font=font)

							stats_pic.save('stats.png')
						else:
							stats_pic=Image.open(f"interfeys_dlya_bota_v3.png")
							stats_pic_draw=ImageDraw.Draw(stats_pic)
							font=ImageFont.truetype("Aqum.ttf", size=20)

							stats_pic_draw.text(
									xy=(245, 71), text=name, fill="white",
									font=ImageFont.truetype("Aqum.ttf", size=35)
									)  # RACE NAME
							"""MILITARY"""
							stats_pic_draw.text(xy=(207, 419), text=str(mil_inv[0]), fill="black", font=font)
							stats_pic_draw.text(xy=(207, 518), text=str(mil_inv[2]), fill="black", font=font)
							stats_pic_draw.text(xy=(207, 617), text=str(mil_inv[5]), fill="black", font=font)
							stats_pic_draw.text(xy=(207, 716), text=str(mil_inv[6]), fill="black", font=font)
							stats_pic_draw.text(xy=(207, 814), text=str(mil_inv[1]), fill="black", font=font)
							stats_pic_draw.text(xy=(207, 912), text=str(mil_inv[3]), fill="black", font=font)
							stats_pic_draw.text(xy=(207, 1011), text=str(mil_inv[4]), fill="black", font=font)
							"""EXP"""
							stats_pic_draw.text(
									xy=(357, 174), text=str(round(race_inv[6], 3)), fill="white",
									font=ImageFont.truetype("Aqum.ttf", size=25)
									)
							"""MONEY"""
							stats_pic_draw.text(
									xy=(835, 174), text=str(race_inv[0]), fill="white",
									font=ImageFont.truetype("Aqum.ttf", size=25)
									)
							"""RESOURCES"""
							stats_pic_draw.text(xy=(631, 419), text=str(race_inv[1]), fill="black", font=font)
							stats_pic_draw.text(xy=(631, 518), text=str(race_inv[3]), fill="black", font=font)
							stats_pic_draw.text(xy=(631, 617), text=str(race_inv[2]), fill="black", font=font)
							stats_pic_draw.text(xy=(631, 716), text=str(race_inv[4]), fill="black", font=font)
							stats_pic_draw.text(xy=(631, 814), text=str(race_inv[5]), fill="black", font=font)
							"""BUILDS"""
							stats_pic_draw.text(xy=(1055, 419), text=str(bld_inv[0]), fill="black", font=font)
							stats_pic_draw.text(xy=(1055, 518), text=str(bld_inv[1]), fill="black", font=font)
							stats_pic_draw.text(xy=(1055, 617), text=str(bld_inv[2]), fill="black", font=font)
							stats_pic_draw.text(xy=(1055, 716), text=str(bld_inv[3]), fill="black", font=font)
							stats_pic_draw.text(xy=(1055, 814), text=str(bld_inv[4]), fill="black", font=font)
							stats_pic_draw.text(xy=(1055, 912), text=str(bld_inv[5]), fill="black", font=font)
							stats_pic_draw.text(xy=(1055, 1011), text=str(bld_inv[6]), fill="black", font=font)

							stats_pic.save('stats.png')

						vk_upload = vk_api.VkUpload(self.vk_session)
						photo = vk_upload.photo_messages(photos="stats.png")
						photo = f'photo{photo[0]["owner_id"]}_{photo[0]["id"]}'
						
						self.vk.messages.send(
								peer_id=self.peer_id, random_id=random.randint(0, 10000000000), attachment=photo
								)
				else:
					curs.execute("SELECT race_id FROM races WHERE low_name = %s", (race,))
					race_id=curs.fetchone( )
					if race_id is None:
						self.vk.messages.send(
								peer_id=self.peer_id,
								random_id=random.randint(0, 10000000000),
								message="&#10062; Расы с таким названием не существует."
								)
					else:
						curs.execute(
								"SELECT SUM(anders), SUM(food), SUM(steel), SUM(wood), SUM(w_cris), SUM(b_cris), SUM(exp), SUM(stone), COUNT(*) FROM users WHERE race_id = %s",
								(race_id[0],)
								)
						race_inv = curs.fetchone( )
						
						curs.execute(
								"SELECT SUM(inf),SUM(mag),SUM(arch),SUM(ctpl),SUM(bllsts),SUM(clvr),SUM(plds) FROM users WHERE race_id = %s",
								(race_id[0],)
								)
						mil_inv = curs.fetchone( )
						
						curs.execute(
								"SELECT SUM(farm),SUM(swml),SUM(mine),SUM(vlg),SUM(city),SUM(tmpl),SUM(altr) FROM users WHERE race_id = %s",
								(race_id[0],)
								)
						bld_inv = curs.fetchone( )
						curs.execute(
							"SELECT name, low_name, color FROM races WHERE race_id = %s",
							(race_id,)
							)
						name, low_name, color=curs.fetchone( )
						if race_id != "1":
							stats_pic=Image.open(f"race_profiles/{race}_раса.png")
							stats_pic_draw=ImageDraw.Draw(stats_pic)
							font=ImageFont.truetype("Aqum.ttf", size=20)

							stats_pic_draw.text(
								xy=(632, 227), text="V", fill="#080808",
								font=ImageFont.truetype("Aqum.ttf", size=25)
								)

							stats_pic_draw.text(
								xy=(242, 208), text=race_inv[8], fill=color,
								font=ImageFont.truetype("Aqum.ttf", size=25)
								)  # RACE USERS COUNT
							"""MILITARY"""
							stats_pic_draw.text(xy=(207, 419 + 36), text=str(mil_inv[0]), fill="black", font=font)
							stats_pic_draw.text(xy=(207, 518 + 36), text=str(mil_inv[2]), fill="black", font=font)
							stats_pic_draw.text(xy=(207, 617 + 36), text=str(mil_inv[5]), fill="black", font=font)
							stats_pic_draw.text(xy=(207, 716 + 36), text=str(mil_inv[6]), fill="black", font=font)
							stats_pic_draw.text(xy=(207, 814 + 36), text=str(mil_inv[1]), fill="black", font=font)
							stats_pic_draw.text(xy=(207, 912 + 36), text=str(mil_inv[3]), fill="black", font=font)
							stats_pic_draw.text(xy=(207, 1011 + 36), text=str(mil_inv[4]), fill="black", font=font)
							"""EXP"""
							stats_pic_draw.text(
								xy=(935, 121), text=str(round(race_inv[6], 3)), fill=color,
								font=ImageFont.truetype("Aqum.ttf", size=25)
								)
							"""MONEY"""
							stats_pic_draw.text(
								xy=(935, 208), text=str(race_inv[0]), fill=color,
								font=ImageFont.truetype("Aqum.ttf", size=25)
								)
							"""RESOURCES"""
							stats_pic_draw.text(xy=(631, 419 + 36), text=str(race_inv[1]), fill="black", font=font)
							stats_pic_draw.text(xy=(631, 518 + 36), text=str(race_inv[3]), fill="black", font=font)
							stats_pic_draw.text(xy=(631, 617 + 36), text=str(race_inv[2]), fill="black", font=font)
							stats_pic_draw.text(xy=(631, 716 + 36), text=str(race_inv[4]), fill="black", font=font)
							stats_pic_draw.text(xy=(631, 814 + 36), text=str(race_inv[5]), fill="black", font=font)
							"""BUILDS"""
							stats_pic_draw.text(xy=(1055, 419 + 36), text=str(bld_inv[0]), fill="black", font=font)
							stats_pic_draw.text(xy=(1055, 518 + 36), text=str(bld_inv[1]), fill="black", font=font)
							stats_pic_draw.text(xy=(1055, 617 + 36), text=str(bld_inv[2]), fill="black", font=font)
							stats_pic_draw.text(xy=(1055, 716 + 36), text=str(bld_inv[3]), fill="black", font=font)
							stats_pic_draw.text(xy=(1055, 814 + 36), text=str(bld_inv[4]), fill="black", font=font)
							stats_pic_draw.text(xy=(1055, 912 + 36), text=str(bld_inv[5]), fill="black", font=font)
							stats_pic_draw.text(xy=(1055, 1011 + 36), text=str(bld_inv[6]), fill="black", font=font)

							stats_pic.save('stats.png')
						else:
							stats_pic=Image.open(f"interfeys_dlya_bota_v3.png")
							stats_pic_draw=ImageDraw.Draw(stats_pic)
							font=ImageFont.truetype("Aqum.ttf", size=20)

							stats_pic_draw.text(
								xy=(245, 71), text=name, fill="white",
								font=ImageFont.truetype("Aqum.ttf", size=35)
								)  # RACE NAME
							"""MILITARY"""
							stats_pic_draw.text(xy=(207, 419), text=str(mil_inv[0]), fill="black", font=font)
							stats_pic_draw.text(xy=(207, 518), text=str(mil_inv[2]), fill="black", font=font)
							stats_pic_draw.text(xy=(207, 617), text=str(mil_inv[5]), fill="black", font=font)
							stats_pic_draw.text(xy=(207, 716), text=str(mil_inv[6]), fill="black", font=font)
							stats_pic_draw.text(xy=(207, 814), text=str(mil_inv[1]), fill="black", font=font)
							stats_pic_draw.text(xy=(207, 912), text=str(mil_inv[3]), fill="black", font=font)
							stats_pic_draw.text(xy=(207, 1011), text=str(mil_inv[4]), fill="black", font=font)
							"""EXP"""
							stats_pic_draw.text(
								xy=(357, 174), text=str(round(race_inv[6], 3)), fill="white",
								font=ImageFont.truetype("Aqum.ttf", size=25)
								)
							"""MONEY"""
							stats_pic_draw.text(
								xy=(835, 174), text=str(race_inv[0]), fill="white",
								font=ImageFont.truetype("Aqum.ttf", size=25)
								)
							"""RESOURCES"""
							stats_pic_draw.text(xy=(631, 419), text=str(race_inv[1]), fill="black", font=font)
							stats_pic_draw.text(xy=(631, 518), text=str(race_inv[3]), fill="black", font=font)
							stats_pic_draw.text(xy=(631, 617), text=str(race_inv[2]), fill="black", font=font)
							stats_pic_draw.text(xy=(631, 716), text=str(race_inv[4]), fill="black", font=font)
							stats_pic_draw.text(xy=(631, 814), text=str(race_inv[5]), fill="black", font=font)
							"""BUILDS"""
							stats_pic_draw.text(xy=(1055, 419), text=str(bld_inv[0]), fill="black", font=font)
							stats_pic_draw.text(xy=(1055, 518), text=str(bld_inv[1]), fill="black", font=font)
							stats_pic_draw.text(xy=(1055, 617), text=str(bld_inv[2]), fill="black", font=font)
							stats_pic_draw.text(xy=(1055, 716), text=str(bld_inv[3]), fill="black", font=font)
							stats_pic_draw.text(xy=(1055, 814), text=str(bld_inv[4]), fill="black", font=font)
							stats_pic_draw.text(xy=(1055, 912), text=str(bld_inv[5]), fill="black", font=font)
							stats_pic_draw.text(xy=(1055, 1011), text=str(bld_inv[6]), fill="black", font=font)

							stats_pic.save('stats.png')

						vk_upload=vk_api.VkUpload(self.vk_session)
						photo=vk_upload.photo_messages(photos="stats.png")
						photo=f'photo{photo[0]["owner_id"]}_{photo[0]["id"]}'

						self.vk.messages.send(
							peer_id=self.peer_id, random_id=random.randint(0, 10000000000), attachment=photo
							)
	
	def setRace(self):
		conn = pymysql.connect(
				host="triniti.ru-hoster.com",
				user=self.user,
				password=self.passw,
				db='demkaXvl',
				charset='utf8', init_command='SET NAMES UTF8'
				)
		curs = conn.cursor( )
		if self.user_id in self.adms or self.user_id in self.race_adms:
			if len(self.command.split(" ")) >= 3:
				user = self.command.split(" ")[1].split("|")[0]
				race = self.command.split(" ")[2]
				if race.isdigit( ):
					curs.execute("SELECT race_id FROM races WHERE race_id = %s", (race,))
					if curs.fetchone( ) is None:
						self.vk.messages.send(
								peer_id=self.peer_id,
								random_id=random.randint(0, 10000000000),
								message="&#10062; Расы с таким ID не существует."
								)
					else:
						if user.startswith("[id"):
							user = user.replace("[id", "")
							curs.execute("SELECT user_id FROM users WHERE user_id = %s", (user,))
							if curs.fetchone( ) is None:
								self.vk.messages.send(
										peer_id=self.peer_id,
										random_id=random.randint(0, 10000000000),
										message="&#10062; Данный пользователь не зарегистрирован в базе данных."
										)
							else:
								curs.execute("UPDATE users SET race_id = %s WHERE user_id = %s", (race, user))
								conn.commit( )
								
								self.vk.messages.send(
										peer_id=self.peer_id,
										random_id=random.randint(0, 10000000000),
										message="&#9989; Вы изменили расу пользователю."
										)
						else:
							self.vk.messages.send(
									peer_id=self.peer_id,
									random_id=random.randint(0, 10000000000),
									message="&#10062; Гиперссылка должна вести на страницу человека."
									)
				else:
					self.vk.messages.send(
							peer_id=self.peer_id,
							random_id=random.randint(0, 10000000000),
							message="&#10062; ID расы должно состоять только из цифр."
							)
			else:
				if len(self.command.split(" ")) >= 2:
					race = self.command.split(" ")[1]
					if race.isdigit( ):
						curs.execute("SELECT race_id FROM races ORDER BY race_id DESC LIMIT 1")
						maxi = curs.fetchone( )[0]
						if maxi >= int(race) > 1:
							curs.execute(f"UPDATE users SET race_id = {race} WHERE user_id = {self.user_id}")
							conn.commit( )
							
							self.vk.messages.send(
									peer_id=self.peer_id,
									random_id=random.randint(0, 10000000000),
									message="&#9989; Раса успешно установлена."
									)
				else:
					self.vk.messages.send(
							peer_id=self.peer_id,
							random_id=random.randint(0, 10000000000),
							message="&#10062; Указаны не все аргументы."
							)
		else:
			curs.execute(f'SELECT verif FROM conversations WHERE peer_id = {self.peer_id}')
			if curs.fetchone( )[0] == 1:
				if len(self.command.split(" ")) >= 2:
					curs.execute(f"SELECT race_id FROM users WHERE user_id = {self.user_id}")
					if curs.fetchone( )[0] == 1:
						race = self.command.split(" ")[1]
						if race.isdigit( ):
							curs.execute("SELECT race_id FROM races ORDER BY race_id DESC LIMIT 1")
							maxi = curs.fetchone( )[0]
							if maxi >= int(race) >= 1 and int(race) != 1:
								curs.execute(f"UPDATE users SET race_id = {race} WHERE user_id = {self.user_id}")
								conn.commit( )
								
								self.vk.messages.send(
										peer_id=self.peer_id,
										random_id=random.randint(0, 10000000000),
										message="&#9989; Раса успешно установлена."
										)
							else:
								self.vk.messages.send(
										peer_id=self.peer_id,
										random_id=random.randint(0, 10000000000),
										message="&#10062; Расы с таким ID не существует или вы не можете установить ID этой расы"
										)
						else:
							self.vk.messages.send(
									peer_id=self.peer_id,
									random_id=random.randint(0, 10000000000),
									message="&#10062; ID расы должно состоять только из цифр."
									)
					else:
						self.vk.messages.send(
								peer_id=self.peer_id,
								random_id=random.randint(0, 10000000000),
								message="&#10062; Вы уже выбрали свою расу. Для изменения расы требуется обратиться к Администрации."
								)
				else:
					self.vk.messages.send(
							peer_id=self.peer_id,
							random_id=random.randint(0, 10000000000),
							message="&#10062; Указаны не все аргументы."
							)
	
	def changeNickname(self):
		conn = pymysql.connect(
				host="triniti.ru-hoster.com",
				user=self.user,
				password=self.passw,
				db='demkaXvl',
				charset='utf8', init_command='SET NAMES UTF8'
				)
		curs = conn.cursor( )
		curs.execute(f'SELECT verif FROM conversations WHERE peer_id = {self.peer_id}')
		ch = int(curs.fetchone( )[0])
		if ch == 1:
			if len(self.txt.split(" ")) >= 2:
				name = self.txt.split(" ", 1)[1]
				if len(name) > 20:
					self.vk.messages.send(
							peer_id=self.peer_id,
							random_id=random.randint(0, 10000000000),
							message="&#10062; Ваш ник слишком длинный."
							)
				else:
					curs.execute("SELECT user_id FROM users WHERE nickname = %s", (name,))
					if curs.fetchone( ) is None:
						curs.execute("UPDATE users SET nickname = %s WHERE user_id = %s", (name, self.user_id))
						conn.commit( )
						# нужно переложить ответственность за ник на пользователя - ГОТОВО
						
						self.vk.messages.send(
								peer_id=self.peer_id,
								random_id=random.randint(0, 10000000000),
								message="&#9989; Ник успешно изменен."
								)
					else:
						self.vk.messages.send(
								peer_id=self.peer_id,
								random_id=random.randint(0, 10000000000),
								message="&#10062; Этот ник уже кем-то занят."
								)
			else:
				self.vk.messages.send(
						peer_id=self.peer_id,
						random_id=random.randint(0, 10000000000),
						message="&#10062; Указано недостаточно аргументов."
						)
	
	def listOfGoods(self):
		conn = pymysql.connect(
				host="triniti.ru-hoster.com",
				user=self.user,
				password=self.passw,
				db='demkaXvl',
				charset='utf8', init_command='SET NAMES UTF8'
				)
		curs = conn.cursor( )
		curs.execute(f'SELECT verif FROM conversations WHERE peer_id = {self.peer_id}')
		if int(curs.fetchone( )[0]) == 1:
			curs.execute("SELECT lot_id, from_user, res_id, count, cost FROM market WHERE purch = 0")
			goods = curs.fetchall( )
			a = ""
			for i in goods:
				curs.execute(f"SELECT name FROM resourses WHERE res_id = {i[2]}")
				a += f"ID: {i[0]}\nПродавец: @id{i[1]}\nСтоимость: {i[4]} Андеров \nРесурс: {curs.fetchone( )[0]}\nКол-во: {i[3]}\n\n"
			
			self.vk.messages.send(
					peer_id=self.peer_id,
					random_id=random.randint(0, 10000000000),
					message=f"&#128177; Список лотов:\n{a}ЧТОБЫ КУПИТЬ ЛОТ НАПИШИТЕ '/buygood [ID лота]' (без кавычек)",
					disable_mentions=1
					)  # оформление
	
	def buyGood(self):
		if len(self.command.split(" ")) >= 2:
			conn = pymysql.connect(
					host="triniti.ru-hoster.com",
					user=self.user,
					password=self.passw,
					db='demkaXvl',
					charset='utf8', init_command='SET NAMES UTF8'
					)
			curs = conn.cursor( )
			curs.execute(f'SELECT verif FROM conversations WHERE peer_id = {self.peer_id}')
			if int(curs.fetchone( )[0]) == 1:
				now_utc = datetime.now(timezone('UTC'))
				time = now_utc.astimezone(timezone('Europe/Moscow'))
				lot_id = self.command.split(" ")[1]
				if lot_id.isdigit( ):
					curs.execute(
							"SELECT count, res_id, cost, from_user, purch FROM market WHERE lot_id = %s", (lot_id,)
							)
					lot = curs.fetchone( )
					if lot is not None:
						if lot[3] == self.user_id:
							self.vk.messages.send(
								peer_id=self.peer_id,
								random_id=random.randint(0, 10000000000),
								message="&#10062; Нельзя купить свой же лот."
								)  # оформление
						else:
							if lot[4] == 1:
								self.vk.messages.send(
										peer_id=self.peer_id,
										random_id=random.randint(0, 10000000000),
										message="&#10062; Лот уже куплен."
										)  # оформление
							else:
								curs.execute("SELECT anders FROM users WHERE user_id = %s", (self.user_id,))
								money = curs.fetchone( )[0]
								if money >= lot[2]:
									curs.execute("SELECT bd_name, name FROM resourses WHERE res_id = %s", (lot[1],))
									res_name = curs.fetchone( )
									curs.execute(
											f"UPDATE users SET anders = anders - {lot[2]}, {res_name[0]} = {res_name[0]} + {lot[0]} WHERE user_id = {self.user_id}"
											)
									conn.commit( )
									curs.execute(
											f"UPDATE users SET anders = anders + {lot[2]} WHERE user_id = {lot[3]}"
											)
									conn.commit( )
									curs.execute(
											f"UPDATE market SET purch_time = %s, to_user = {self.user_id}, purch = 1 WHERE lot_id = {lot_id}",
											(time,)
											)
									conn.commit( )
									
									self.vk.messages.send(
											peer_id=self.peer_id,
											random_id=random.randint(0, 10000000000),
											message=f"&#9989; Вы купили {lot[0]} ед. {res_name[1]}!\n\n[id{lot[3]}|Лот #{lot_id}] продан!"
											)  # оформление
								
								else:
									self.vk.messages.send(
											peer_id=self.peer_id,
											random_id=random.randint(0, 10000000000),
											message="&#10062; У вас недостаточно Андеров."
											)  # оформление
					else:
						self.vk.messages.send(
								peer_id=self.peer_id,
								random_id=random.randint(0, 10000000000),
								message="&#10062; Нельзя купить свой же лот."
								)  # оформление
				else:
					self.vk.messages.send(
							peer_id=self.peer_id,
							random_id=random.randint(0, 10000000000),
							message="&#10062; ID лота должно состоять только из цифр."
							)  # оформление
		else:
			self.vk.messages.send(
					peer_id=self.peer_id,
					random_id=random.randint(0, 10000000000),
					message="&#10062; Указаны не все аргументы."
					)  # оформление
	
	def addGood(self):
		"""
		/addgood
		[ресурс]
		[кол-во]
		[стоимость за ед.]
		"""
		if len(self.command.split("\n")) >= 4:
			res_name = self.command.split("\n")[1].capitalize( ).strip( )
			res_count = self.command.split("\n")[2].strip( )
			res_cost = self.command.split("\n")[3].strip( )
			conn = pymysql.connect(
					host="triniti.ru-hoster.com",
					user=self.user,
					password=self.passw,
					db='demkaXvl',
					charset='utf8', init_command='SET NAMES UTF8'
					)
			curs = conn.cursor( )
			curs.execute(f'SELECT verif FROM conversations WHERE peer_id = {self.peer_id}')
			a = curs.fetchone( )[0]
			if int(a) == 1:
				now_utc=datetime.now(timezone('UTC'))
				time=now_utc.astimezone(timezone('Europe/Moscow'))
				curs.execute(f"SELECT COUNT(lot_id) FROM market WHERE from_user = {self.user_id} and purch = 0 and access = 0")
				if int(curs.fetchone( )[0]) < 3:
					curs.execute("SELECT cost, res_id, bd_name FROM resourses WHERE name = %s", (res_name,))
					res = curs.fetchone( )
					if res is None:
						self.vk.messages.send(
								peer_id=self.peer_id,
								random_id=random.randint(0, 10000000000),
								message="&#10062; Ресурса с таким названием не существует."
								)  # оформление
					else:
						if res_cost.isdigit( ) and res_count.isdigit( ):
							if int(res_count) == 0 or int(res_cost) == 0:
								self.vk.messages.send(
										peer_id=self.peer_id,
										random_id=random.randint(0, 10000000000),
										message="&#10062; Аргументы указаны неверно. Проверьте, чтоб стоимость и количество не были равны нулю."
										)  # оформление
							else:
								curs.execute(f"SELECT {res[2]} FROM users WHERE user_id = {self.user_id}")
								if curs.fetchone( )[0] >= int(res_count):
									if res[0] <= int(res_cost):
										cost = int(res_cost) * int(res_count)
										curs.execute(
												f"UPDATE users SET {res[2]} = {res[2]} - {res_count} WHERE user_id = {self.user_id}"
												)
										conn.commit( )
										curs.execute(
												"INSERT INTO market (from_user, cost, res_id, count, time) VALUE (%s,%s,%s,%s,%s)",
												(self.user_id, cost, res[1], res_count, time)
												)
										conn.commit( )
										curs.execute("SELECT lot_id FROM market ORDER BY lot_id DESC LIMIT 1")
										lot = curs.fetchone( )[0]
										
										self.vk.messages.send(
												peer_id=self.peer_id,
												random_id=random.randint(0, 10000000000),
												message=f"&#9989; Лот #{lot} выставлен на продажу!"
												)  # оформление
									else:
										morph = pymorphy2.MorphAnalyzer( )
										res_name = morph.parse(res_name)[0]
										res_name = res_name.inflect({'gent'}).word.capitalize( )
										self.vk.messages.send(
												peer_id=self.peer_id,
												random_id=random.randint(0, 10000000000),
												message=f"&#10062; Минимальная цена за 1 ед. {res_name}: {res[0]}."
												)  # оформление
								else:
									morph = pymorphy2.MorphAnalyzer( )
									res_name = morph.parse(res_name)[0]
									res_name = res_name.inflect({'gent'}).word.capitalize( )
									self.vk.messages.send(
											peer_id=self.peer_id,
											random_id=random.randint(0, 10000000000),
											message=f"&#10062; У вас недостаточно {res_name}."
											)  # оформление
						else:
							self.vk.messages.send(
									peer_id=self.peer_id,
									random_id=random.randint(0, 10000000000),
									message="&#10062; Аргументы указаны неверно. Проверьте, чтоб стоимость и количество были указаны числами."
									)  # оформление
				else:
					self.vk.messages.send(
							peer_id=self.peer_id,
							random_id=random.randint(0, 10000000000),
							message="&#10062; Один пользователь может одновременно продавать не более 3 товаров."
							)  # оформление
		else:
			self.vk.messages.send(
					peer_id=self.peer_id,
					random_id=random.randint(0, 10000000000),
					message="&#10062; Указаны не все аргументы."
					)  # оформление
	
	def rejectonLotForAdms(self):
		"""
		/rejlot [lot_id]
		"""
		if self.user_id in self.adms:
			lot_id = self.command.split(" ")[1]
			conn = pymysql.connect(
					host="triniti.ru-hoster.com",
					user=self.user,
					password=self.passw,
					db='demkaXvl',
					charset='utf8', init_command='SET NAMES UTF8'
					)
			curs = conn.cursor( )
			if lot_id.isdigit( ):
				curs.execute(
						"SELECT to_user, from_user, cost, res_id, count, purch FROM market WHERE lot_id = %s", (lot_id,)
						)
				lot = curs.fetchone( )
				if lot is not None:
					if lot[5] == 1:
						curs.execute(f"SELECT bd_name FROM resourses WHERE res_id = {lot[3]}")
						res_name = curs.fetchone( )[0]
						curs.execute(
								f"UPDATE users SET anders = anders + {lot[2]}, {res_name} = {res_name} - {lot[4]} WHERE user_id = {lot[0]}"
								)
						conn.commit( )
						curs.execute(
								f"UPDATE users SET anders = anders - {lot[2]}, {res_name} = {res_name} + {lot[4]} WHERE user_id = {lot[1]}"
								)
						conn.commit( )
						curs.execute(f"UPDATE market SET access = 0 WHERE lot_id = {lot_id}")
						conn.commit( )
						
						self.vk.messages.send(
								peer_id=self.peer_id,
								random_id=random.randint(0, 10000000000),
								message=f"&#9989; Лот {lot_id} заблокирован."
								)  # оформление
					else:
						self.vk.messages.send(
								peer_id=self.peer_id,
								random_id=random.randint(0, 10000000000),
								message=f"&#10062; Лот {lot_id} еще не продан."
								)  # оформление
				else:
					self.vk.messages.send(
							peer_id=self.peer_id,
							random_id=random.randint(0, 10000000000),
							message="&#10062; Лота с таким ID не существует."
							)  # оформление
			else:
				self.vk.messages.send(
						peer_id=self.peer_id,
						random_id=random.randint(0, 10000000000),
						message="&#10062; ID лота должно состоять только из цифр."
						)  # оформление
	
	def getProfile(self):
		user_id = self.user_id
		if len(self.command.split(" ")) >= 2:
			if self.command.split(" ")[1].startswith("http") or self.command.split(" ")[1].startswith("https"):
				short_name = self.command.split(" ")[1].split("/")[3]
				user_id = self.vk.users.get(user_ids=short_name)[0]['id']
			
			elif self.command.split(" ")[1].startswith("[id"):
				user_id = self.command.split(" ")[1].split("|")[0].replace("[id", "")
		else:
			try:
				if 'reply_message' in self.event.object["message"].keys( ):
					if self.event.object["message"]["reply_message"]["from_id"] > 0:
						user_id = self.event.object["message"]["reply_message"]["from_id"]
					else:
						self.vk.messages.send(
								peer_id=self.peer_id,
								random_id=random.randint(0, 10000000000),
								message=f"&#10062; [club{str(self.event.object['message']['reply_message']['from_id']).replace('-', '')}|Эта страница] не является страницей пользователя."
								)
				else:
					self.vk.messages.send(
						peer_id=self.peer_id,
						random_id=random.randint(0, 10000000000),
						message=f"&#10062; Указаны не все аргументы."
						)
			except:
				pass
		conn = pymysql.connect(
				host="triniti.ru-hoster.com",
				user=self.user,
				password=self.passw,
				db='demkaXvl',
				charset='utf8', init_command='SET NAMES UTF8'
				)
		curs = conn.cursor( )
		curs.execute(f'SELECT verif FROM conversations WHERE peer_id = {self.peer_id}')
		ch = int(curs.fetchone( )[0])
		if ch == 1:
			curs.execute(
					"SELECT race_id, exp, anders, nickname, food, wood, steel, b_cris, w_cris, vlg, city, farm, tmpl, altr, mine, inf, arch, clvr, plds, ctpl, mag, bllsts, swml, fort_name, peer_id FROM users WHERE user_id = %s",
					(user_id,)
					)
			prof = curs.fetchone( )
			if prof is None:
				self.vk.messages.send(
						peer_id=self.peer_id,
						random_id=random.randint(0, 10000000000),
						message="Этого пользователя нет в базе данных."
						)  # оформление
			else:
				curs.execute(f"SELECT verif FROM conversations WHERE peer_id = {prof[24]}")
				chat = curs.fetchone( )[0]
				curs.execute("SELECT name, low_name, color FROM races WHERE race_id = %s", (prof[0],))
				race = curs.fetchone( )
				curs.execute(f"SELECT COUNT(*) FROM users WHERE race_id = {prof[0]}")
				race_count = str(curs.fetchone( )[0])
				font = ImageFont.truetype("Aqum.ttf", size=20)
				if int(prof[0]) !=1:
					
					stats_pic = Image.open(f"{race[1]}.png")
					stats_pic_draw = ImageDraw.Draw(stats_pic)
					stats_pic_draw.text(
							xy=(164, 240), text=prof[3], fill=str(race[2]), font=ImageFont.truetype("Aqum.ttf", size=25)
							)
					if prof[23] is None:
						stats_pic_draw.text(
								xy=(164, 155), text="Не указано", fill=str(race[2]),
								font=ImageFont.truetype("Aqum.ttf", size=25)
								)
					else:
						stats_pic_draw.text(
								xy=(164, 155), text=prof[23], fill=str(race[2]),
								font=ImageFont.truetype("Aqum.ttf", size=25)
								)
					if chat == 1:
						stats_pic_draw.text(
								xy=(632, 262), text="V", fill="#080808",
								font=ImageFont.truetype("Aqum.ttf", size=25)
								)
					else:
						stats_pic_draw.text(
								xy=(632, 262), text="X", fill="#080808",
								font=ImageFont.truetype("Aqum.ttf", size=25)
								)
					stats_pic_draw.text(
							xy=(838, 155), text=str(prof[2]), fill=str(race[2]),
							font=ImageFont.truetype("Aqum.ttf", size=25)
							)
					stats_pic_draw.text(
							xy=(610, 186), text=race_count, fill=str(race[2]),
							font=ImageFont.truetype("Aqum.ttf", size=25)
							)
					stats_pic_draw.text(
							xy=(838, 240), text=str(user_id), fill=str(race[2]),
							font=ImageFont.truetype("Aqum.ttf", size=25)
							)
					stats_pic_draw.text(
							xy=(838, 68), text=str(prof[1]), fill=str(race[2]),
							font=ImageFont.truetype("Aqum.ttf", size=25)
							)
					
					stats_pic_draw.text(xy=(170, 485), text=str(prof[15]), fill="black", font=font)
					stats_pic_draw.text(xy=(170, 585), text=str(prof[16]), fill="black", font=font)
					stats_pic_draw.text(xy=(170, 683), text=str(prof[17]), fill="black", font=font)
					stats_pic_draw.text(xy=(170, 783), text=str(prof[18]), fill="black", font=font)
					stats_pic_draw.text(xy=(170, 879), text=str(prof[20]), fill="black", font=font)
					stats_pic_draw.text(xy=(170, 978), text=str(prof[19]), fill="black", font=font)
					stats_pic_draw.text(xy=(170, 1077), text=str(prof[21]), fill="black", font=font)
					
					stats_pic_draw.text(xy=(570, 485), text=str(prof[4]), fill="black", font=font)
					stats_pic_draw.text(xy=(570, 585), text=str(prof[5]), fill="black", font=font)
					stats_pic_draw.text(xy=(570, 683), text=str(prof[6]), fill="black", font=font)
					stats_pic_draw.text(xy=(570, 783), text=str(prof[8]), fill="black", font=font)
					stats_pic_draw.text(xy=(570, 879), text=str(prof[7]), fill="black", font=font)
					
					stats_pic_draw.text(xy=(970, 485), text=str(prof[11]), fill="black", font=font)
					stats_pic_draw.text(xy=(970, 585), text=str(prof[22]), fill="black", font=font)
					stats_pic_draw.text(xy=(970, 683), text=str(prof[14]), fill="black", font=font)
					stats_pic_draw.text(xy=(970, 783), text=str(prof[9]), fill="black", font=font)
					stats_pic_draw.text(xy=(970, 879), text=str(prof[10]), fill="black", font=font)
					stats_pic_draw.text(xy=(970, 978), text=str(prof[12]), fill="black", font=font)
					stats_pic_draw.text(xy=(970, 1077), text=str(prof[13]), fill="black", font=font)
					
					stats_pic.save('prof.png')
				else:
					stats_pic = Image.open("old/profil_igroka_v2.png")
					stats_pic_draw = ImageDraw.Draw(stats_pic)
					stats_pic_draw.text(
							xy=(230, 65), text=race[0], fill="white", font=ImageFont.truetype("Aqum.ttf", size=40)
							)
					stats_pic_draw.text(
							xy=(370, 158), text=prof[3], fill="white", font=ImageFont.truetype("Aqum.ttf", size=25)
							)
					stats_pic_draw.text(xy=(170, 239), text=str(self.user_id), fill="white", font=font)
					stats_pic_draw.text(xy=(552, 239), text=str(prof[1]), fill="white", font=font)
					stats_pic_draw.text(xy=(855, 239), text=str(prof[2]), fill="white", font=font)
					
					stats_pic_draw.text(xy=(170, 485), text=str(prof[15]), fill="black", font=font)
					stats_pic_draw.text(xy=(170, 585), text=str(prof[16]), fill="black", font=font)
					stats_pic_draw.text(xy=(170, 683), text=str(prof[17]), fill="black", font=font)
					stats_pic_draw.text(xy=(170, 783), text=str(prof[18]), fill="black", font=font)
					stats_pic_draw.text(xy=(170, 879), text=str(prof[20]), fill="black", font=font)
					stats_pic_draw.text(xy=(170, 978), text=str(prof[19]), fill="black", font=font)
					stats_pic_draw.text(xy=(170, 1077), text=str(prof[21]), fill="black", font=font)
					
					stats_pic_draw.text(xy=(570, 485), text=str(prof[4]), fill="black", font=font)
					stats_pic_draw.text(xy=(570, 585), text=str(prof[5]), fill="black", font=font)
					stats_pic_draw.text(xy=(570, 683), text=str(prof[6]), fill="black", font=font)
					stats_pic_draw.text(xy=(570, 783), text=str(prof[8]), fill="black", font=font)
					stats_pic_draw.text(xy=(570, 879), text=str(prof[7]), fill="black", font=font)
					
					stats_pic_draw.text(xy=(970, 485), text=str(prof[11]), fill="black", font=font)
					stats_pic_draw.text(xy=(970, 585), text=str(prof[22]), fill="black", font=font)
					stats_pic_draw.text(xy=(970, 683), text=str(prof[14]), fill="black", font=font)
					stats_pic_draw.text(xy=(970, 783), text=str(prof[9]), fill="black", font=font)
					stats_pic_draw.text(xy=(970, 879), text=str(prof[10]), fill="black", font=font)
					stats_pic_draw.text(xy=(970, 978), text=str(prof[12]), fill="black", font=font)
					stats_pic_draw.text(xy=(970, 1077), text=str(prof[13]), fill="black", font=font)
					
					stats_pic.save('prof.png')
				
				vk_upload = vk_api.VkUpload(self.vk_session)
				photo = vk_upload.photo_messages(photos="prof.png")
				photo = f'photo{photo[0]["owner_id"]}_{photo[0]["id"]}'
				self.vk.messages.send(
						peer_id=self.peer_id,
						random_id=random.randint(0, 10000000000),
						attachment=photo,
						content_resourse=self.user_id
						)
		else:
			self.vk.messages.send(
				peer_id=self.peer_id,
				random_id=random.randint(0, 10000000000),
				attachment="Пользователь не найден в Базе Данных."
				)
	def races(self):
		conn = pymysql.connect(
				host="triniti.ru-hoster.com",
				user=self.user,
				password=self.passw,
				db='demkaXvl',
				charset='utf8', init_command='SET NAMES UTF8'
				)
		curs = conn.cursor( )
		curs.execute(f'SELECT verif FROM conversations WHERE peer_id = {self.peer_id}')
		ch = int(curs.fetchone( )[0])
		if ch == 1:
			curs.execute("SELECT name, adm, race_id FROM races")
			
			a = "\n\n"
			txt = a.join(f"ID: {i[2]}\nНазвание: {i[0]}\nАдмин: @id{i[1]}" for i in curs.fetchall( ))  # оформление
			self.vk.messages.send(
					peer_id=self.peer_id,
					random_id=random.randint(0, 10000000000),
					message=txt,
					disable_mentions=1
					)
	
	def getCount(self):
		conn = pymysql.connect(
				host="triniti.ru-hoster.com",
				user=self.user,
				password=self.passw,
				db='demkaXvl',
				charset='utf8', init_command='SET NAMES UTF8'
				)
		curs = conn.cursor( )
		if self.user_id in self.adms:
			curs.execute("SELECT COUNT(*) FROM users")
			users = curs.fetchone( )[0]
			curs.execute("SELECT COUNT(*) FROM transactions")
			trans = curs.fetchone( )[0]
			curs.execute("SELECT COUNT(*) FROM market")
			market = curs.fetchone( )[0]
			curs.execute("SELECT COUNT(*) FROM personal_trans")
			personal_trans = curs.fetchone( )[0]
			curs.execute("SELECT COUNT(*) FROM conversations")
			conv = curs.fetchone( )[0]
			self.vk.messages.send(
					peer_id=self.peer_id,
					random_id=random.randint(0, 10000000000),
					message=f"Общее кол-во пользователей: {users}\nСовершено переводов: {trans}\nВсего продаж: {market}\nВсего сделок: {personal_trans}\nВсего бесед: {conv}"
					)
	
	def getLot(self):
		conn = pymysql.connect(
				host="triniti.ru-hoster.com",
				user=self.user,
				password=self.passw,
				db='demkaXvl',
				charset='utf8', init_command='SET NAMES UTF8'
				)
		curs = conn.cursor( )
		if self.user_id in self.adms:
			if len(self.command.split(" ")) >= 2:
				lot_id = self.command.split(" ")[1]
				if lot_id.isdigit( ):
					curs.execute("SELECT * FROM market WHERE lot_id = %s", (lot_id,))
					lot = curs.fetchone( )
					if lot is None:
						self.vk.messages.send(
								peer_id=self.peer_id,
								random_id=random.randint(0, 10000000000),
								message="Лота с таким ID не существует."
								)
					else:
						curs.execute(f"SELECT name FROM resourses WHERE res_id = {lot[4]}")
						self.vk.messages.send(
								peer_id=self.peer_id,
								random_id=random.randint(0, 10000000000),
								message=f"""LOT_ID:{lot_id}\nFROM_USER: {lot[1]}\nTO_USER: {lot[2]}\nCOST: {lot[3]}\nRES: {curs.fetchone( )[0]}\nACCESS: {lot[5]}\nPURCH: {lot[6]}\nTIME: {lot[7]}\nPURCH_TIME: {lot[8]}"""
								)
				else:
					self.vk.messages.send(
							peer_id=self.peer_id,
							random_id=random.randint(0, 10000000000),
							message="Аргументы указаны неверно."
							)
			else:
				self.vk.messages.send(
						peer_id=self.peer_id,
						random_id=random.randint(0, 10000000000),
						message="&#10062; Указано недостаточно аргументов."
						)
	
	def getTransaction(self):
		conn = pymysql.connect(
				host="triniti.ru-hoster.com",
				user=self.user,
				password=self.passw,
				db='demkaXvl',
				charset='utf8', init_command='SET NAMES UTF8'
				)
		curs = conn.cursor( )
		if self.user_id in self.adms:
			if len(self.command.split(" ")) >= 2:
				trans_id = self.command.split(" ")[1]
				if trans_id.isdigit( ):
					curs.execute("SELECT * FROM transactions WHERE trans_id = %s", (trans_id,))
					trans = curs.fetchone( )
					if trans is None:
						self.vk.messages.send(
								peer_id=self.peer_id,
								random_id=random.randint(0, 10000000000),
								message="Перевода с таким ID не существует."
								)
					else:
						self.vk.messages.send(
								peer_id=self.peer_id,
								random_id=random.randint(0, 10000000000),
								message=f"TRANS_ID: {trans[0]}\nFROM: @id{trans[1]}\nTO: @id{trans[2]}\nSUMM: {trans[3]}\nTIME: {trans[4]}\nACCEPT: {trans[5]}"
								)
				else:
					self.vk.messages.send(
							peer_id=self.peer_id,
							random_id=random.randint(0, 10000000000),
							message="Аргументы указаны неверно."
							)
			else:
				self.vk.messages.send(
						peer_id=self.peer_id,
						random_id=random.randint(0, 10000000000),
						message="&#10062; Указано недостаточно аргументов."
						)
	
	def changeNickForAdms(self):
		"""
		/chngn [user] [nick]
		"""
		if self.user_id in self.adms:
			conn = pymysql.connect(
					host="triniti.ru-hoster.com",
					user=self.user,
					password=self.passw,
					db='demkaXvl',
					charset='utf8', init_command='SET NAMES UTF8'
					)
			curs = conn.cursor( )
			if len(self.command.split(" ")) >= 3:
				if self.command.split(" ")[1].startswith("[id"):
					user = self.command.split(" ")[1].split("|")[0].replace("[id", "")
					curs.execute(f"SELECT user_id FROM users WHERE user_id = {user}")
					if curs.fetchone( ) is not None:
						nick = self.txt.split(" ", 2)[2]
						if len(nick) > 20:
							self.vk.messages.send(
									peer_id=self.peer_id,
									random_id=random.randint(0, 10000000000),
									message="Указанный ник слишком длинный."
									)
						else:
							curs.execute("UPDATE users SET nickname = %s WHERE user_id = %s", (nick, user))
							conn.commit( )
							self.vk.messages.send(
									peer_id=self.peer_id,
									random_id=random.randint(0, 10000000000),
									message="Ник успешно изменен."
									)
					else:
						self.vk.messages.send(
								peer_id=self.peer_id,
								random_id=random.randint(0, 10000000000),
								message=f"&#10062; [id{user}|Этот пользователь] не зарегистрирован в Боте."
								)
				
				else:
					self.vk.messages.send(
							peer_id=self.peer_id,
							random_id=random.randint(0, 10000000000),
							message="Аргументы указаны неверно."
							)
			else:
				self.vk.messages.send(
						peer_id=self.peer_id,
						random_id=random.randint(0, 10000000000),
						message="&#10062; недостаточно аргументов."
						)
	
	def showEvent(self):
		if self.user_id in self.adms:
			self.vk.messages.send(
					peer_id=self.peer_id,
					random_id=random.randint(0, 10000000000),
					message=self.event
					)
	
	def help(self):
		conn = pymysql.connect(
				host="triniti.ru-hoster.com",
				user=self.user,
				password=self.passw,
				db='demkaXvl',
				charset='utf8', init_command='SET NAMES UTF8'
				)
		curs = conn.cursor( )
		curs.execute(f'SELECT verif FROM conversations WHERE peer_id = {self.peer_id}')
		ch = int(curs.fetchone( )[0])
		if ch == 1:
			self.vk.messages.send(
					peer_id=self.peer_id,
					random_id=random.randint(0, 10000000000),
					message="&#9981; Помощь:\nvk.com/@andwb-help\n\nПравила:\nhttps://vk.com/@andwb-rule",
					attachment="article-205707057_62167_0d6cbb198060823369"
					)
	
	def giveBan(self):
		if self.user_id in self.adms:
			conn = pymysql.connect(
					host="triniti.ru-hoster.com",
					user=self.user,
					password=self.passw,
					db='demkaXvl',
					charset='utf8', init_command='SET NAMES UTF8'
					)
			curs = conn.cursor( )
			if len(self.command.split(" ")) >= 2:
				if self.command.split(" ")[1].split("|")[0].startswith("[id"):
					us = self.command.split(" ")[1].split("|")[0].replace("[id", "")
					curs.execute(f"SELECT user_id FROM users WHERE user_id = {us}")
					if curs.fetchone( ) is None:
						self.vk.messages.send(
								peer_id=self.peer_id,
								random_id=random.randint(0, 10000000000),
								message="Этого пользователя нет в базе данных."
								)
					else:
						curs.execute(f"UPDATE users SET ban = 1 WHERE user_id = {us}")
						conn.commit( )
						self.vk.messages.send(
								peer_id=self.peer_id,
								random_id=random.randint(0, 10000000000),
								message="Бан выдан."
								)
				else:
					self.vk.messages.send(
							peer_id=self.peer_id,
							random_id=random.randint(0, 10000000000),
							message="Вы указали неверную ссылку на пользователя."
							)
			else:
				self.vk.messages.send(
						peer_id=self.peer_id,
						random_id=random.randint(0, 10000000000),
						message="Указаны не все аргументы."
						)
	
	def giveUnban(self):
		if self.user_id in self.adms:
			conn = pymysql.connect(
					host="triniti.ru-hoster.com",
					user=self.user,
					password=self.passw,
					db='demkaXvl',
					charset='utf8', init_command='SET NAMES UTF8'
					)
			curs = conn.cursor( )
			if len(self.command.split(" ")) >= 2:
				if self.command.split(" ")[1].split("|")[0].startswith("[id"):
					us = self.command.split(" ")[1].split("|")[0].replace("[id", "")
					curs.execute(f"SELECT user_id FROM users WHERE user_id = {us}")
					if curs.fetchone( ) is None:
						self.vk.messages.send(
								peer_id=self.peer_id,
								random_id=random.randint(0, 10000000000),
								message="Этого пользователя нет в базе данных."
								)
					else:
						curs.execute(f"UPDATE users SET ban = 0 WHERE user_id = {us}")
						conn.commit( )
						self.vk.messages.send(
								peer_id=self.peer_id,
								random_id=random.randint(0, 10000000000),
								message="Бан снят."
								)
				else:
					self.vk.messages.send(
							peer_id=self.peer_id,
							random_id=random.randint(0, 10000000000),
							message="Вы указали неверную ссылку на пользователя."
							)
			else:
				self.vk.messages.send(
						peer_id=self.peer_id,
						random_id=random.randint(0, 10000000000),
						message="Указаны не все аргументы."
						)
	
	def addResTransactions(self):
		if len(self.command.split("\n")) >= 5:
			user = self.command.split("\n")[1].strip( )
			res = self.command.split("\n")[2].capitalize( ).strip( )
			count = self.command.split("\n")[3].strip( )
			cost = self.command.split("\n")[4].strip( )
			if self.command.split("\n")[1].startswith("http") or self.command.split("\n")[1].startswith(
					"https"
					):
				short_name = self.command.split(" ")[2].split("/")[3]
				user = self.vk.users.get(user_ids=short_name)[0]['id']
			elif self.command.split("\n")[1].startswith("[id"):
				user = self.command.split("\n")[1].split("|")[0].replace("[id", "")
			else:
				self.vk.messages.send(
					peer_id=self.peer_id,
					random_id=random.randint(0, 10000000000),
					message="&#10062; Получатель указан неверно."
					)
			if count.isdigit( ) and cost.isdigit( ):
				conn = pymysql.connect(
						host="triniti.ru-hoster.com",
						user=self.user,
						password=self.passw,
						db='demkaXvl',
						charset='utf8', init_command='SET NAMES UTF8'
						)
				curs = conn.cursor( )
				curs.execute(f'SELECT verif FROM conversations WHERE peer_id = {self.peer_id}')
				ch = int(curs.fetchone( )[0])
				if ch == 1:
					curs.execute(
							f"SELECT COUNT(trans_id) FROM personal_trans WHERE from_user = {self.user_id} and purch = 0 and rej = 0 and accept = 0"
							)
					if int(curs.fetchone( )[0]) < 3:
						curs.execute("SELECT bd_name, res_id, cost FROM resourses WHERE name = %s", (res,))
						res_info = curs.fetchone( )
						if res_info is None:
							self.vk.messages.send(
									peer_id=self.peer_id,
									random_id=random.randint(0, 10000000000),
									message="&#10062; Ресурса с таким название не существует."
									)
						else:
							curs.execute(f"SELECT ban, peer_id FROM users WHERE user_id = {user}")
							us = curs.fetchone( )
							if us is None:
								self.vk.messages.send(
										peer_id=self.peer_id,
										random_id=random.randint(0, 10000000000),
										message="&#10062; Этого пользователя нет в базе данных."
										)
							else:
								if int(us[0]) == 1:
									self.vk.messages.send(
											peer_id=self.peer_id,
											random_id=random.randint(0, 10000000000),
											message="&#10062; Этот пользователь сейчас заблокирован."
											)
								else:
									if int(cost) >= 0:
										if int(cost) == 0:
											curs.execute(f"SELECT {res_info[0]} FROM users WHERE user_id = {self.user_id}")
											if int(count) <= int(curs.fetchone()[0]):
												if int(count) > 0:
													if self.user_id != user:
														now_utc=datetime.now(timezone('UTC'))
														now=now_utc.astimezone(timezone('Europe/Moscow'))
														curs.execute(
																f"INSERT INTO personal_trans (from_user, to_user, res_id, cost, count, time) VALUES ({self.user_id}, {user}, {res_info[1]}, {cost}, {count}, %s)",
																(now,)
																)
														conn.commit( )
														curs.execute(
																f"UPDATE users SET {res_info[0]} = {res_info[0]} - %s WHERE user_id = %s",
																(int(count), self.user_id)
																)
														conn.commit( )
														curs.execute(
																"SELECT trans_id FROM personal_trans ORDER BY trans_id DESC LIMIT 1"
																)
														last_trans = curs.fetchone( )[0]
														if int(us[1]) != self.peer_id:
															self.vk.messages.send(
																	peer_id=int(us[1]),
																	random_id=random.randint(0, 10000000000),
																	message=f"[id{user}|Вам] предложили сделку!\nЕе ID: {last_trans}\n\nЧтобы посмотреть все свои сделки напишите: '/lsttrn' (Без кавычек!)"
																	)
															self.vk.messages.send(
																	peer_id=self.peer_id,
																	random_id=random.randint(0, 10000000000),
																	message=f"[id{self.user_id}|Вы] предложили сделку!\nЕе ID: {last_trans}"
																	)
														else:
															self.vk.messages.send(
																	peer_id=self.peer_id,
																	random_id=random.randint(0, 10000000000),
																	message=f"[id{self.user_id}|Вы] предложили сделку!\nЕе ID: {last_trans}\n\n[id{user}|Вам] предложили сделку!\nЕе ID: {last_trans}\n\nЧтобы посмотреть все свои сделки напишите: '/lsttrn' (Без кавычек!)"
																	)
													else:
														self.vk.messages.send(
																peer_id=self.peer_id,
																random_id=random.randint(0, 10000000000),
																message="&#10062; Нельзя предложить сделку самому себе."
																)  # оформление
												else:
													self.vk.messages.send(
															peer_id=self.peer_id,
															random_id=random.randint(0, 10000000000),
															message="&#10062; Нельзя передать 0 ед. ресурса."
															)  # оформление
											else:
												morph = pymorphy2.MorphAnalyzer( )
												res_name = morph.parse(res)[0]
												res_name = res_name.inflect({'gent'}).word.capitalize( )
												self.vk.messages.send(
														peer_id=self.peer_id,
														random_id=random.randint(0, 10000000000),
														message=f"&#10062; У вас недостаточно {res_name}."
														)  # оформление
										else:
											morph = pymorphy2.MorphAnalyzer( )
											res_name = morph.parse(res)[0]
											res_name = res_name.inflect({'gent'}).word.capitalize( )
											self.vk.messages.send(
													peer_id=self.peer_id,
													random_id=random.randint(0, 10000000000),
													message=f"&#10062; Минимальная цена за 1 ед. {res_name}: {res_info[2]}."
													)
									else:
										self.vk.messages.send(
											peer_id=self.peer_id,
											random_id=random.randint(0, 10000000000),
											message=f"&#10062; Стоимость не может быть меньше 0."
											)
					else:
						self.vk.messages.send(
								peer_id=self.peer_id,
								random_id=random.randint(0, 10000000000),
								message="&#10062; Каждый пользователь может иметь не более 3 активных сделок."
								)  # оформление
			else:
				self.vk.messages.send(
						peer_id=self.peer_id,
						random_id=random.randint(0, 10000000000),
						message="&#10062; Один из аргументов указан неверно."
						)
		else:
			self.vk.messages.send(
					peer_id=self.peer_id,
					random_id=random.randint(0, 10000000000),
					message="Указаны не все аргументы."
					)
	
	def acceptPersonalTrans(self):
		if len(self.command.split(" ")) >= 2:
			tr_id = self.command.split(" ")[1]
			if tr_id.isdigit( ):
				conn = pymysql.connect(
						host="triniti.ru-hoster.com",
						user=self.user,
						password=self.passw,
						db='demkaXvl',
						charset='utf8', init_command='SET NAMES UTF8'
						)
				curs = conn.cursor( )
				curs.execute(f'SELECT verif FROM conversations WHERE peer_id = {self.peer_id}')
				if curs.fetchone( )[0] == 1:
					curs.execute(
							f"SELECT res_id, cost, purch, rej, count, from_user, to_user FROM personal_trans WHERE trans_id = {tr_id}"
							)
					trans = curs.fetchone( )
					if trans is not None:
						if int(trans[6]) == self.user_id:
							if int(trans[2]) == 0:
								if int(trans[3]) == 0:
									curs.execute(f"SELECT anders FROM users WHERE user_id = {self.user_id}")
									if int(curs.fetchone( )[0]) >= int(trans[1]):
										now_utc=datetime.now(timezone('UTC'))
										now=now_utc.astimezone(timezone('Europe/Moscow'))
										curs.execute(f"SELECT bd_name FROM resourses WHERE res_id = {trans[0]}")
										res_name = curs.fetchone( )
										curs.execute(
												f"UPDATE users SET anders = anders - {trans[1]} WHERE user_id = {self.user_id}"
												)
										conn.commit( )
										curs.execute(
												f"UPDATE users SET {res_name[0]} = {res_name[0]} + %s WHERE user_id = {self.user_id}",
												(trans[4],)
												)
										conn.commit( )
										curs.execute(
												f"UPDATE personal_trans SET purch = 1, purch_time = %s WHERE trans_id = {tr_id}",
												(now,)
												)
										conn.commit( )
										curs.execute(
												f"UPDATE users SET anders = anders + {trans[1]} WHERE user_id = {trans[5]}"
												)
										conn.commit( )
										curs.execute(f"SELECT peer_id FROM users WHERE user_id = {trans[5]}")
										chat = int(curs.fetchone( )[0])
										if chat != self.peer_id:
											self.vk.messages.send(
													peer_id=chat,
													random_id=random.randint(0, 10000000000),
													message=f"&#9989; Сделка #{tr_id} совершена!"
													)
											self.vk.messages.send(
													peer_id=self.peer_id,
													random_id=random.randint(0, 10000000000),
													message=f"&#9989; Сделка #{tr_id} совершена!"
													)
										else:
											self.vk.messages.send(
													peer_id=self.peer_id,
													random_id=random.randint(0, 10000000000),
													message=f"&#9989; Сделка #[id{trans[5]}|{tr_id}] совершена!"
													)
									else:
										self.vk.messages.send(
												peer_id=self.peer_id,
												random_id=random.randint(0, 10000000000),
												message="&#10062; У вас недостаточно Андеров!"
												)
								else:
									self.vk.messages.send(
											peer_id=self.peer_id,
											random_id=random.randint(0, 10000000000),
											message="&#10062; Сделка отменена."
											)
							else:
								self.vk.messages.send(
										peer_id=self.peer_id,
										random_id=random.randint(0, 10000000000),
										message="&#10062; Сделка уже совершена."
										)
						else:
							self.vk.messages.send(
									peer_id=self.peer_id,
									random_id=random.randint(0, 10000000000),
									message="&#10062; Эта сделка предложена не Вам."
									)
					else:
						self.vk.messages.send(
								peer_id=self.peer_id,
								random_id=random.randint(0, 10000000000),
								message="&#10062; Сделки с таким ID не существует."
								)
			else:
				self.vk.messages.send(
						peer_id=self.peer_id,
						random_id=random.randint(0, 10000000000),
						message="&#10062; ID сделки указано неверно."
						)
		else:
			self.vk.messages.send(
					peer_id=self.peer_id,
					random_id=random.randint(0, 10000000000),
					message="&#10062; Указаны не все аргументы."
					)
	
	def personalTransRejection(self):
		if len(self.command.split(" ")) >= 2:
			trans_id = self.command.split(" ")[1]
			if trans_id.isdigit( ):
				conn = pymysql.connect(
						host="triniti.ru-hoster.com",
						user=self.user,
						password=self.passw,
						db='demkaXvl',
						charset='utf8', init_command='SET NAMES UTF8'
						)
				curs = conn.cursor( )
				curs.execute(f'SELECT verif FROM conversations WHERE peer_id = {self.peer_id}')
				if curs.fetchone( )[0] == 1:
					curs.execute(
							f"SELECT from_user, rej, purch, res_id, count FROM personal_trans WHERE trans_id = {trans_id}"
							)
					trans = curs.fetchone( )
					if trans is not None:
						if int(trans[0]) == self.user_id:
							if int(trans[1]) == 0:
								if int(trans[2]) == 0:
									
									curs.execute(f"SELECT bd_name, name FROM resourses WHERE res_id = {trans[3]}")
									res_name = curs.fetchone( )
									curs.execute(f"UPDATE personal_trans SET rej = 1 WHERE trans_id = {trans_id}")
									conn.commit( )
									curs.execute(
											f"UPDATE users SET {res_name[0]} = {res_name[0]} + {trans[4]} WHERE user_id = {self.user_id}"
											)
									conn.commit( )
									self.vk.messages.send(
											peer_id=self.peer_id,
											random_id=random.randint(0, 10000000000),
											message=f"&#9989; Сделка #{trans_id} отменена."
											)
								else:
									self.vk.messages.send(
											peer_id=self.peer_id,
											random_id=random.randint(0, 10000000000),
											message="&#10062; Нельзя отменить совершенную сделку."
											)
							else:
								self.vk.messages.send(
										peer_id=self.peer_id,
										random_id=random.randint(0, 10000000000),
										message="&#10062; Вы уже отменили эту сделку."
										)
						else:
							self.vk.messages.send(
									peer_id=self.peer_id,
									random_id=random.randint(0, 10000000000),
									message="&#10062; Вы не можете отменить чужую сделку."
									)
					else:
						self.vk.messages.send(
								peer_id=self.peer_id,
								random_id=random.randint(0, 10000000000),
								message="&#10062; Сделки с таким ID не существует."
								)
			else:
				self.vk.messages.send(
						peer_id=self.peer_id,
						random_id=random.randint(0, 10000000000),
						message="&#10062; ID сделки указано неверно."
						)
		else:
			self.vk.messages.send(
					peer_id=self.peer_id,
					random_id=random.randint(0, 10000000000),
					message="&#10062; Указаны не все аргументы."
					)
	
	def listOfPersonalTrans(self):
		conn = pymysql.connect(
				host="triniti.ru-hoster.com",
				user=self.user,
				password=self.passw,
				db='demkaXvl',
				charset='utf8', init_command='SET NAMES UTF8'
				)
		curs = conn.cursor( )
		curs.execute(f'SELECT verif FROM conversations WHERE peer_id = {self.peer_id}')
		ch = int(curs.fetchone( )[0])
		if ch == 1:
			curs.execute(
					f"SELECT from_user, res_id, count, cost, trans_id FROM personal_trans WHERE rej = 0 and to_user = {self.user_id} and purch = 0"
					)
			from_you = curs.fetchall( )
			fr = ""
			for i in from_you:
				curs.execute(f"SELECT name FROM resourses WHERE res_id = {i[1]}")
				fr += f"ID: #{i[4]}\nДля кого: @id{i[0]}\nРесурс: {curs.fetchone( )[0]}\nКол-во: {i[2]}\nСтоимость: {i[3]}\n\n"
			
			curs.execute(
					f"SELECT to_user, res_id, count, cost, trans_id FROM personal_trans WHERE rej = 0 and from_user = {self.user_id} and purch = 0"
					)
			for_you = curs.fetchall( )
			fro = ""
			for i in for_you:
				curs.execute(f"SELECT name FROM resourses WHERE res_id = {i[1]}")
				fro += f"ID: #{i[4]}\nОт кого: @id{i[0]}\nРесурс: {curs.fetchone( )[0]}\nКол-во: {i[2]}\nСтоимость: {i[3]}\n\n"
			if fr == "":
				fr = "Нет сделок"
			elif fro == "":
				fro = "Нет сделок"
			self.vk.messages.send(
					peer_id=self.peer_id,
					random_id=random.randint(0, 10000000000),
					message=f"Для вас:\n{fr}\nДля кого-либо:\n{fro}",
					disable_mentions=1
					)
	
	def PersonalTransRejForAdms(self):
		if self.user_id in self.adms:
			conn = pymysql.connect(
					host="triniti.ru-hoster.com",
					user=self.user,
					password=self.passw,
					db='demkaXvl',
					charset='utf8', init_command='SET NAMES UTF8'
					)
			curs = conn.cursor( )
			if len(self.command.split(" ")) >= 2:
				trans_id = self.command.split(" ")[1]
				if trans_id.isdigit( ):
					curs.execute(
							f"SELECT purch, rej, to_user, from_user, accept, cost, res_id, count FROM personal_trans WHERE trans_id = {trans_id}"
							)
					trans = curs.fetchone( )
					if trans is not None:
						if int(trans[0]) == 1:
							if int(trans[1]) == 0:
								if int(trans[4]) == 0:
									curs.execute(f"SELECT bd_name FROM resourses WHERE res_id = {trans[6]}")
									a = curs.fetchone( )
									curs.execute(
											f"UPDATE users SET anders = anders - {trans[5]}, {a[0]} = {a[0]} + {trans[7]} WHERE user_id = {trans[3]}"
											)
									conn.commit( )
									curs.execute(
											f"UPDATE users SET anders = anders + {trans[5]}, {a[0]} = {a[0]} - {trans[7]} WHERE user_id = {trans[2]}"
											)
									conn.commit( )
									curs.execute("UPDATE personal_trans SET accept = 1")
									conn.commit( )
									self.vk.messages.send(
											peer_id=self.peer_id,
											random_id=random.randint(0, 10000000000),
											message=f"Сделка #{trans_id} отменена."
											)
								else:
									self.vk.messages.send(
											peer_id=self.peer_id,
											random_id=random.randint(0, 10000000000),
											message="Эта сделка уже заблокирована."
											)
							else:
								self.vk.messages.send(
										peer_id=self.peer_id,
										random_id=random.randint(0, 10000000000),
										message="Эта сделка и так отменена."
										)
						else:
							self.vk.messages.send(
									peer_id=self.peer_id,
									random_id=random.randint(0, 10000000000),
									message="Нельзя отменить не совершенную сделку."
									)
					else:
						self.vk.messages.send(
								peer_id=self.peer_id,
								random_id=random.randint(0, 10000000000),
								message="Сделки с таким ID не существует."
								)
				else:
					self.vk.messages.send(
							peer_id=self.peer_id,
							random_id=random.randint(0, 10000000000),
							message="ID сделки указано неверно."
							)
			else:
				self.vk.messages.send(
						peer_id=self.peer_id,
						random_id=random.randint(0, 10000000000),
						message="Указаны не все аргументы."
						)
	
	def lotRejection(self):
		conn = pymysql.connect(
				host="triniti.ru-hoster.com",
				user=self.user,
				password=self.passw,
				db='demkaXvl',
				charset='utf8', init_command='SET NAMES UTF8'
				)
		curs = conn.cursor( )
		curs.execute(f'SELECT verif FROM conversations WHERE peer_id = {self.peer_id}')
		ch = int(curs.fetchone( )[0])
		if ch == 1:
			if len(self.command.split(" ")) >= 2:
				lot_id = self.command.split(" ")[1]
				if lot_id.isdigit( ):
					curs.execute(f"SELECT from_user, res_id, count, access, purch FROM market WHERE lot_id = {lot_id}")
					lot = curs.fetchone( )
					if lot is None:
						self.vk.messages.send(
								peer_id=self.peer_id,
								random_id=random.randint(0, 10000000000),
								message="&#10062; ID лота указано неверно."
								)
					else:
						if self.user_id == int(lot[0]):
							if int(lot[3]) == 1:
								if int(lot[4]) == 0:
									curs.execute(f"SELECT bd_name FROM resourses WHERE res_id = {lot[1]}")
									res_name = curs.fetchone( )[0]
									curs.execute(
											f"UPDATE users SET {res_name} = {res_name} + %s WHERE user_id = {self.user_id}",
											(lot[2])
											)
									conn.commit( )
									curs.execute(f"UPDATE market SET access = 0 WHERE lot_id = {lot_id}")
									conn.commit( )
									self.vk.messages.send(
											peer_id=self.peer_id,
											random_id=random.randint(0, 10000000000),
											message=f"Лот #{lot_id} убран с рынка."
											)
								else:
									self.vk.messages.send(
											peer_id=self.peer_id,
											random_id=random.randint(0, 10000000000),
											message="&#10062; Этот лот уже куплен."
											)
							else:
								self.vk.messages.send(
										peer_id=self.peer_id,
										random_id=random.randint(0, 10000000000),
										message="&#10062; Этот лот уже отменен."
										)
						else:
							self.vk.messages.send(
									peer_id=self.peer_id,
									random_id=random.randint(0, 10000000000),
									message="&#10062; Вы не можете отменить чужой лот."
									)
				else:
					self.vk.messages.send(
							peer_id=self.peer_id,
							random_id=random.randint(0, 10000000000),
							message="&#10062; ID лота указано неверно."
							)
			else:
				self.vk.messages.send(
						peer_id=self.peer_id,
						random_id=random.randint(0, 10000000000),
						message="&#10062; Указаны не все аргументы."
						)
	
	def deleteProfile(self):
		if self.user_id in self.adms:
			if len(self.command.split(" ")) >= 2:
				user = self.command.split(" ")[1]
				if user.startswith("[id") and user.endswith("]"):
					user = user.split("|")[0].replace("[id", "")
					if user.isdigit( ):
						conn = pymysql.connect(
								host="triniti.ru-hoster.com",
								user=self.user,
								password=self.passw,
								db='demkaXvl',
								charset='utf8', init_command='SET NAMES UTF8'
								)
						curs = conn.cursor( )
						curs.execute(f"SELECT user_id FROM users WHERE user_id = {user}")
						if curs.fetchone( ) is None:
							self.vk.messages.send(
									peer_id=self.peer_id,
									random_id=random.randint(0, 10000000000),
									message="Этого пользователя нет в базе данных."
									)
						else:
							curs.execute(f"DELETE FROM users WHERE user_id = {user}")
							conn.commit( )
							self.vk.messages.send(
									peer_id=self.peer_id,
									random_id=random.randint(0, 10000000000),
									message="Пользователь удален."
									)
					else:
						self.vk.messages.send(
								peer_id=self.peer_id,
								random_id=random.randint(0, 10000000000),
								message="ID пользователя указано неверно."
								)
				else:
					self.vk.messages.send(
							peer_id=self.peer_id,
							random_id=random.randint(0, 10000000000),
							message="ID пользователя указано неверно."
							)
			else:
				self.vk.messages.send(
						peer_id=self.peer_id,
						random_id=random.randint(0, 10000000000),
						message="Указаны не все аргументы."
						)
	
	def setChat(self):
		conn = pymysql.connect(
				host="triniti.ru-hoster.com",
				user=self.user,
				password=self.passw,
				db='demkaXvl',
				charset='utf8', init_command='SET NAMES UTF8'
				)
		curs = conn.cursor( )
		curs.execute(f'SELECT verif FROM conversations WHERE peer_id = {self.peer_id}')
		ch = int(curs.fetchone( )[0])
		if ch == 1:
			curs.execute(f"SELECT peer_id FROM users WHERE user_id = {self.user_id}")
			ch = curs.fetchone( )[0]
			self.vk.messages.send(
					peer_id=self.adms_chat,
					random_id=random.randint(0, 10000000000),
					message=f"[id{self.user_id}|Пользователь] сменил родительскую беседу.\n{ch} => {self.peer_id}"
					)
			curs.execute(f"UPDATE users SET peer_id = {self.peer_id} WHERE user_id = {self.user_id}")
			conn.commit( )
			self.vk.messages.send(
					peer_id=self.peer_id,
					random_id=random.randint(0, 10000000000),
					message="&#9989; Вы изменили основную беседу."
					)
	
	def changeFortName(self):
		if len(self.command.split(" ")) >= 2:
			name = self.txt.split(" ", 1)[1]
			if len(name) <= 20:
				conn = pymysql.connect(
						host="triniti.ru-hoster.com",
						user=self.user,
						password=self.passw,
						db='demkaXvl',
						charset='utf8', init_command='SET NAMES UTF8'
						)
				curs = conn.cursor( )
				curs.execute(f'SELECT verif FROM conversations WHERE peer_id = {self.peer_id}')
				ch = int(curs.fetchone( )[0])
				if ch == 1:
					curs.execute(f"UPDATE users SET fort_name = %s WHERE user_id = {self.user_id}", (name,))
					conn.commit( )
					self.vk.messages.send(
							peer_id=self.peer_id,
							random_id=random.randint(0, 10000000000),
							message="&#9989; Название установлено."
							)
			else:
				self.vk.messages.send(
						peer_id=self.peer_id,
						random_id=random.randint(0, 10000000000),
						message="&#10062; Название слишком длинное."
						)
		else:
			self.vk.messages.send(
					peer_id=self.peer_id,
					random_id=random.randint(0, 10000000000),
					message="&#10062; Указаны не все аргументы."
					)
	
	def changeFortNameForAdms(self):
		if len(self.command.split("\n")) >= 3:
			name = self.txt.split("\n")[1]
			if len(name) <= 20:
				user = self.txt.split("\n")[2]
				if user.startswith("[id") and user.endwith("]"):
					user = user.split("|")[0].replace("[id", "")
					if user.isdigit( ):
						conn = pymysql.connect(
								host="triniti.ru-hoster.com",
								user=self.user,
								password=self.passw,
								db='demkaXvl',
								charset='utf8', init_command='SET NAMES UTF8'
								)
						curs = conn.cursor( )
						curs.execute(f'SELECT verif FROM conversations WHERE peer_id = {self.peer_id}')
						if curs.fetchone( )[0] == 1:
							curs.execute(f"SELECT user_id FROM users WHERE user_id = {self.user_id}")
							if curs.fetchone( ) is not None:
								curs.execute(f"UPDATE users SET fort_name = %s WHERE user_id = {self.user_id}", (name,))
								conn.commit( )
								self.vk.messages.send(
										peer_id=self.peer_id,
										random_id=random.randint(0, 10000000000),
										message="Название установлено."
										)
							else:
								self.vk.messages.send(
										peer_id=self.peer_id,
										random_id=random.randint(0, 10000000000),
										message="Пользователя нет в базе данных."
										)
					else:
						self.vk.messages.send(
								peer_id=self.peer_id,
								random_id=random.randint(0, 10000000000),
								message="ID пользователя указано неверно."
								)
				else:
					self.vk.messages.send(
							peer_id=self.peer_id,
							random_id=random.randint(0, 10000000000),
							message="ID пользователя указано неверно."
							)
			else:
				self.vk.messages.send(
						peer_id=self.peer_id,
						random_id=random.randint(0, 10000000000),
						message="Название крепости слишком длинное."
						)
		else:
			self.vk.messages.send(
					peer_id=self.peer_id,
					random_id=random.randint(0, 10000000000),
					message="Указаны не все аргументы."
					)
	
	def verificationConv(self):
		if self.user_id in self.adms or self.user_id in self.race_adms:
			conn = pymysql.connect(
					host="triniti.ru-hoster.com",
					user=self.user,
					password=self.passw,
					db='demkaXvl',
					charset='utf8', init_command='SET NAMES UTF8'
					)
			curs = conn.cursor( )
			curs.execute(f"UPDATE conversations SET verif = 1 WHERE peer_id = {self.peer_id}")
			conn.commit( )
			self.vk.messages.send(
					peer_id=self.peer_id,
					random_id=random.randint(0, 10000000000),
					message="Беседа верифицирована."
					)
	
	def unverificationConv(self):
		if self.user_id in self.adms or self.user_id in self.race_adms:
			conn = pymysql.connect(
					host="triniti.ru-hoster.com",
					user=self.user,
					password=self.passw,
					db='demkaXvl',
					charset='utf8', init_command='SET NAMES UTF8'
					)
			curs = conn.cursor( )
			curs.execute(f"UPDATE conversations SET verif = 0 WHERE peer_id = {self.peer_id}")
			conn.commit( )
			self.vk.messages.send(
					peer_id=self.peer_id,
					random_id=random.randint(0, 10000000000),
					message="Верификация беседы удалена."
					)
	
	def attachForm(self):
		#UNUSEABLE
		if self.user_id in self.adms or self.user_id in self.race_adms:
			if 'reply_message' in self.event.object["message"].keys( ):
				if self.event.object["message"]["reply_message"]["from_id"] > 0:
					user = self.event.object["message"]["reply_message"]["from_id"]
					form = self.event.object["message"]["reply_message"]["text"]
					conn = pymysql.connect(
							host="triniti.ru-hoster.com",
							user=self.user,
							password=self.passw,
							db='demkaXvl',
							charset='utf8', init_command='SET NAMES UTF8'
							)
					curs = conn.cursor( )
					check = curs.execute(f"SELECT user_id FROM forms WHERE user_id = {user}")
					if check == 0:
						curs.execute("INSERT INTO forms VALUES (%s,%s)", (user, form))
					else:
						curs.execute("UPDATE forms SET from = %s", (user, form))
					self.vk.messages.send(
							peer_id=self.peer_id,
							random_id=random.randint(0, 10000000000),
							message="Анкета пользователя сохранена."
							)
				else:
					self.vk.messages.send(
							peer_id=self.peer_id,
							random_id=random.randint(0, 10000000000),
							message=f"&#10062; [club{str(self.event.object['message']['reply_message']['from_id']).replace('-', '')}|Эта страница] не является страницей пользователя."
							)
			else:
				self.vk.messages.send(
						peer_id=self.peer_id,
						random_id=random.randint(0, 10000000000),
						message="Ответьте на сообщение пользователя с анкетой."
						)
	
	def getForm(self):
		if self.user_id in self.adms or self.user_id in self.race_adms:
			user = self.command.split(" ")
			if len(user) >= 2:
				user = user[1].strip( )
				if self.command.split(" ")[1].startswith("http") or self.command.split(" ")[1].startswith(
						"https"
						):
					short_name = self.command.split(" ")[2].split("/")[3]
					user = self.vk.users.get(user_ids=short_name)[0]['id']
				elif self.command.split(" ")[1].startswith("[id"):
					user = self.command.split(" ")[1].split("|")[0].replace("[id", "")
			else:
				try:
					if 'reply_message' in self.event.object["message"].keys( ):
						if self.event.object["message"]["reply_message"]["from_id"] > 0:
							user = self.event.object["message"]["reply_message"]["from_id"]
						else:
							self.vk.messages.send(
									peer_id=self.peer_id,
									random_id=random.randint(0, 10000000000),
									message=f"&#10062; [club{str(self.event.object['message']['reply_message']['from_id']).replace('-', '')}|Эта страница] не является страницей пользователя."
									)
					else:
						self.vk.messages.send(
							peer_id=self.peer_id,
							random_id=random.randint(0, 10000000000),
							message=f"&#10062; Указаны не все аргументы."
							)
				except Exception:
					pass
			if isinstance(user, str):
				conn = pymysql.connect(
						host="triniti.ru-hoster.com",
						user=self.user,
						password=self.passw,
						db='demkaXvl',
						charset='utf8', init_command='SET NAMES UTF8'
						)
				curs = conn.cursor( )
				curs.execute(f"SELECT form FROM forms WHERE user_id = {user}")
				form = curs.fetchone( )
				if form is None:
					self.vk.messages.send(
							peer_id=self.peer_id,
							random_id=random.randint(0, 10000000000),
							message=f"У [id{user}|этого пользователя] нет анкеты или же ее нет в базе данных.",
							disable_mentions=1
							)
				else:
					self.vk.messages.send(
							peer_id=self.peer_id,
							random_id=random.randint(0, 10000000000),
							message=f"Анкета @id{user}:\n\n{form[0]}.",
							disable_mentions=1
							)
			else:
				self.vk.messages.send(
						peer_id=self.peer_id,
						random_id=random.randint(0, 10000000000),
						message="Аргументы указаны неправильно."
						)
		else:
			self.vk.messages.send(
					peer_id=self.peer_id,
					random_id=random.randint(0, 10000000000),
					message="Указаны не все аргументы."
					)

	def getMap(self):
		conn = pymysql.connect(
				host="triniti.ru-hoster.com",
				user=self.user,
				password=self.passw,
				db='demkaXvl',
				charset='utf8', init_command='SET NAMES UTF8'
				)
		curs = conn.cursor( )
		curs.execute(f'SELECT verif FROM conversations WHERE peer_id = {self.peer_id}')
		ch = int(curs.fetchone( )[0])
		if ch == 1:
			if len(self.command.split(" "))>=2:
				race = self.command.split(" ")[1].capitalize( )
				curs.execute("SELECT race_id FROM races WHERE race_name = %s", (race, ))
				race_id = curs.fetchone()
				if race is not None:
					curs.execute(f"SELECT link FROM maps WHERE race_id = {race_id[0]} ORDER BY time DESC")
					map = curs.fetchone()
					resource=urllib.request.urlopen(map[0])
					out=open("map.png", 'wb')
					out.write(resource.read( ))
					out.close( )
					vk_upload = vk_api.VkUpload(self.vk_session)
					photo = vk_upload.document_message(doc="map.png")
					photo = f'doc{photo[0]["owner_id"]}_{photo[0]["id"]}'
					self.vk.messages.send(
							peer_id=self.peer_id, random_id=random.randint(0, 10000000000), attachment=photo
							)
			else:
				self.vk.messages.send(
					peer_id=self.peer_id,
					random_id=random.randint(0, 10000000000),
					message="Указанной расы не существует."
					)
		else:
			curs.execute("SELECT link FROM maps WHERE race_id = 0 ORDER BY time DESC")
			map=curs.fetchone( )
			resource=urllib.request.urlopen(map[0])
			out=open("map.png", 'wb')
			out.write(resource.read( ))
			out.close( )
			vk_upload=vk_api.VkUpload(self.vk_session)
			photo=vk_upload.document_message(doc="map.png")
			photo=f'doc{photo[0]["owner_id"]}_{photo[0]["id"]}'
			self.vk.messages.send(
				peer_id=self.peer_id, random_id=random.randint(0, 10000000000), attachment=photo
				)


	def setMap(self):
		if self.user_id in self.adms_chat:
			if "doc" in self.event.object["message"].keys( ):
				if len(self.command.split(" ")) == 1:
					conn=pymysql.connect(
						host="triniti.ru-hoster.com",
						user=self.user,
						password=self.passw,
						db='demkaXvl',
						charset='utf8', init_command='SET NAMES UTF8'
						)
					curs=conn.cursor( )
					map_size=self.event.object["message"]["attachments"][0]["doc"]["type"]
					map=self.event.object["message"]["attachments"][0]["doc"]["preview"]["photo"]["sizes"][
						map_size - 1]["src"]
					curs.execute(
						f"INSERT INTO maps(link, from_user) VALUES ( %s, %s)",
						(map, self.user_id)
						)
					conn.commit( )
					self.vk.messages.send(
						peer_id=self.peer_id,
						random_id=random.randint(0, 10000000000),
						message="Общая карта сохранена!"
						)
				elif len(self.command.split(" ")) == 2:
					map_race=self.command.split(" ")[1]
					if map_race.isdigit():
						conn=pymysql.connect(
							host="triniti.ru-hoster.com",
							user=self.user,
							password=self.passw,
							db='demkaXvl',
							charset='utf8', init_command='SET NAMES UTF8'
							)
						curs=conn.cursor( )
						curs.execute(f"SELECT race_id FROM races WHERE race_id = {map_race}")
						if curs.fetchone() is not None:
							map_size=self.event.object["message"]["attachments"][0]["doc"]["type"]
							map=self.event.object["message"]["attachments"][0]["doc"]["preview"]["photo"]["sizes"][map_size-1]["src"]
							curs.execute(f"INSERT INTO maps(link, from_user, race_id) VALUES (%s, %s, %s)", (map, self.user_id, map_race))
							conn.commit()
							self.vk.messages.send(
								peer_id=self.peer_id,
								random_id=random.randint(0, 10000000000),
								message="Карта сохранена!"
								)
						else:
							self.vk.messages.send(
								peer_id=self.peer_id,
								random_id=random.randint(0, 10000000000),
								message="Аргументы указаны неправильно."
								)
					else:
						self.vk.messages.send(
							peer_id=self.peer_id,
							random_id=random.randint(0, 10000000000),
							message="Аргументы указаны неправильно."
							)
				else:
					self.vk.messages.send(
						peer_id=self.peer_id,
						random_id=random.randint(0, 10000000000),
						message="Указаны не все аргументы."
						)
			else:
				self.vk.messages.send(
					peer_id=self.peer_id,
					random_id=random.randint(0, 10000000000),
					message="Прикрепите карту с указанным документом."
					)

	def addForm(self):
		conn=pymysql.connect(
			host="triniti.ru-hoster.com",
			user=self.user,
			password=self.passw,
			db='demkaXvl',
			charset='utf8', init_command='SET NAMES UTF8'
			)
		curs=conn.cursor( )
		curs.execute(f"SELECT access FROM forms WHERE user_id = {self.user_id}")
		a = curs.fetchone()
		if a is None:
			if len(self.txt) < 20:
				self.vk.messages.send(
					peer_id=self.peer_id,
					random_id=random.randint(0, 10000000000),
					message="Скорее всего в вашей анкете указана не вся информация."
					)
			else:
				curs.execute("INSERT INTO forms (user_id, form) VALUES (%s, %s)", (self.user_id, self.txt.replace("/рег", "")))
				conn.commit()
				self.vk.messages.send(
					peer_id=self.peer_id,
					random_id=random.randint(0, 10000000000),
					message="Анкета отправлена Администрации."
					)
				curs.execute("SELECT form_id FROM forms ORDER BY form_id DESC LIMIT 1")
				form_id = curs.fetchone()[0]
				self.vk.messages.send(
					peer_id=self.adms_chat,
					random_id=random.randint(0, 10000000000),
					message=f"@all\nНовая анкета!\nID анкеты: {form_id}\nID пользователя: {self.user_id}\nАнкета:{self.txt.replace('/рег', '')}")
		else:
			if a[0] == 1:
				self.vk.messages.send(
					peer_id=self.peer_id,
					random_id=random.randint(0, 10000000000),
					message="Ваша анкета уже принята."
					)
			elif a[0] == 0:
				self.vk.messages.send(
					peer_id=self.peer_id,
					random_id=random.randint(0, 10000000000),
					message="Администрация рассматривает вашу анкету."
					)

	def accessForm(self):
		"""
		/accform [id]
		or
		/accform [id]
		[name]
		[race]
		"""
		if self.user_id in self.adms:
			if len(self.command.split(" ")) == 2:
				form_id = self.command.split(" ")[1]
				if form_id.isdigit():
					conn=pymysql.connect(
						host="triniti.ru-hoster.com",
						user=self.user,
						password=self.passw,
						db='demkaXvl',
						charset='utf8', init_command='SET NAMES UTF8'
						)
					curs=conn.cursor( )
					curs.execute(f"SELECT * FROM forms WHERE form_id = {form_id}")
					form = curs.fetchone()
					if form is not None:
						if form[3] == 0:
							curs.execute(f"UPDATE forms SET access = 1 WHERE form_id = {form_id}")
							conn.commit()
							curs.execute(f"SELECT user_id FROM users WHERE user_id = {form[1]}")
							if curs.fetchone() is None:
								user=self.vk.users.get(user_ids=form[1])
								user_name=f"{user[0]['first_name']}"
								curs.execute(
									"INSERT INTO users(user_id,peer_id,anders,nickname,food) VALUES (%s,%s,%s,%s,%s)",
									(form[1], self.peer_id, 100, user_name, 10)
									)
								conn.commit( )
								self.vk.messages.send(
									peer_id=self.peer_id,
									random_id=random.randint(0, 10000000000),
									message="Анкета принята. Пользователь добавлен в Базу Данных."
									)
							else:
								self.vk.messages.send(
									peer_id=self.peer_id,
									random_id=random.randint(0, 10000000000),
									message="Анкета принята. Пользователь уже был добавлен в Базу Данных."
									)
						else:
							self.vk.messages.send(
								peer_id=self.peer_id,
								random_id=random.randint(0, 10000000000),
								message="Эта анкета уже получила свой вердикт..."
								)
					else:
						self.vk.messages.send(
							peer_id=self.peer_id,
							random_id=random.randint(0, 10000000000),
							message="Анкеты с таким ID не существует."
							)
				else:
					self.vk.messages.send(
						peer_id=self.peer_id,
						random_id=random.randint(0, 10000000000),
						message="Аргументы указаны неправильно."
						)
			elif len(self.command.split("\n")) >= 3:
				form_id=self.command.split(" ")[1]
				if form_id.isdigit( ):
					conn=pymysql.connect(
						host="triniti.ru-hoster.com",
						user=self.user,
						password=self.passw,
						db='demkaXvl',
						charset='utf8', init_command='SET NAMES UTF8'
						)
					curs=conn.cursor( )
					curs.execute(f"SELECT * FROM forms WHERE form_id = {form_id}")
					form=curs.fetchone( )
					if form is not None:
						if form[3]==0:
							curs.execute(f"UPDATE forms SET access = 1 WHERE form_id = {form_id}")
							conn.commit( )
							curs.execute(f"SELECT user_id FROM users WHERE user_id = {form[1]}")
							if curs.fetchone( ) is None:
								user_name=self.txt.splitlines()[1].strip( )
								user_race=self.txt.splitlines()[2].strip( )
								curs.execute("SELECT race_id FROM races WHERE name = %s", (user_race,))
								race = curs.fetchone( )
								if race is None:
									self.vk.messages.send(
										peer_id=self.peer_id,
										random_id=random.randint(0, 10000000000),
										message="&#10062; Расы с таким ID не существует."
										)
								else:
									curs.execute(
										"INSERT INTO users(user_id,peer_id,anders,nickname,food, race_id) VALUES (%s,%s,%s,%s,%s)",
										(form[1], self.peer_id, 100, user_name, 10, race[0])
										)
									conn.commit( )
									self.vk.messages.send(
										peer_id=self.peer_id,
										random_id=random.randint(0, 10000000000),
										message="Анкета принята. Пользователь добавлен в Базу Данных c учетом указанных значений."
										)
									self.vk.messages.send(
										peer_id=form[1],
										random_id=random.randint(0, 10000000000),
										message="Анкета принята."
										)
							else:
								self.vk.messages.send(
									peer_id=self.peer_id,
									random_id=random.randint(0, 10000000000),
									message="Анкета принята. Пользователь уже был добавлен в Базу Данных."
									)
								self.vk.messages.send(
									peer_id=form[1],
									random_id=random.randint(0, 10000000000),
									message="Анкета принята."
									)
						else:
							self.vk.messages.send(
								peer_id=self.peer_id,
								random_id=random.randint(0, 10000000000),
								message="Эта анкета уже получила свой вердикт..."
								)
					else:
						self.vk.messages.send(
							peer_id=self.peer_id,
							random_id=random.randint(0, 10000000000),
							message="Анкеты с таким ID не существует."
							)
				else:
					self.vk.messages.send(
						peer_id=self.peer_id,
						random_id=random.randint(0, 10000000000),
						message="Аргументы указаны неправильно."
						)
			else:
				self.vk.messages.send(
					peer_id=self.peer_id,
					random_id=random.randint(0, 10000000000),
					message="Указаны не все аргументы."
					)
	def rejectionForm(self):
		if self.user_id in self.adms:
			if len(self.command.split(" ")) == 2:
				form_id=self.command.split(" ")[1]
				if form_id.isdigit( ):
					conn=pymysql.connect(
						host="triniti.ru-hoster.com",
						user=self.user,
						password=self.passw,
						db='demkaXvl',
						charset='utf8', init_command='SET NAMES UTF8'
						)
					curs=conn.cursor( )
					curs.execute(f"SELECT * FROM forms WHERE form_id = {form_id}")
					form=curs.fetchone( )
					if form is not None:
						if form[3]==0:
							if len(self.txt.splitlines( )) == 1:
								curs.execute(f"DELETE * FROM forms WHERE from_id = {form_id}")
								conn.commit( )
								curs.execute(f"SELECT user_id FROM users WHERE user_id = {form[1]}")
								if curs.fetchone( ) is None:
									self.vk.messages.send(
										peer_id=self.peer_id,
										random_id=random.randint(0, 10000000000),
										message="Анкета отклонена."
										)

									self.vk.messages.send(
										peer_id=form[1],
										random_id=random.randint(0, 10000000000),
										message="Анкета отклонена. Причины не указываются."
										)
								else:
									curs.execute(f"DELETE * FROM users WHERE user_id = {form[1]}")
									conn.commit( )
									self.vk.messages.send(
										peer_id=self.peer_id,
										random_id=random.randint(0, 10000000000),
										message="Анкета отклонена. Причины не указываются. Пользователь удален из Базы Данных."
										)
									self.vk.messages.send(
										peer_id=form[1],
										random_id=random.randint(0, 10000000000),
										message="Анкета отклонена. Причины не указываются."
										)
							else:
								curs.execute(f"DELETE * FROM forms WHERE from_id = {form_id}")
								conn.commit( )
								curs.execute(f"SELECT user_id FROM users WHERE user_id = {form[1]}")
								if curs.fetchone( ) is None:
									self.vk.messages.send(
										peer_id=self.peer_id,
										random_id=random.randint(0, 10000000000),
										message="Анкета отклонена."
										)

									self.vk.messages.send(
										peer_id=form[1],
										random_id=random.randint(0, 10000000000),
										message=f"Анкета отклонена. Причина: {self.txt.splitlines( )[1]}."
										)
								else:
									curs.execute(f"DELETE * FROM users WHERE user_id = {form[1]}")
									conn.commit( )
									self.vk.messages.send(
										peer_id=self.peer_id,
										random_id=random.randint(0, 10000000000),
										message="Анкета отклонена. Причины не указываются. Пользователь удален из Базы Данных."
										)
									self.vk.messages.send(
										peer_id=form[1],
										random_id=random.randint(0, 10000000000),
										message=f"Анкета отклонена. Причина: {self.txt.splitlines( )[1]}."
										)
						else:
							self.vk.messages.send(
								peer_id=self.peer_id,
								random_id=random.randint(0, 10000000000),
								message="Эта анкета уже получила свой вердикт..."
								)
					else:
						self.vk.messages.send(
							peer_id=self.peer_id,
							random_id=random.randint(0, 10000000000),
							message="Анкеты с таким ID не существует."
							)
				else:
					self.vk.messages.send(
						peer_id=self.peer_id,
						random_id=random.randint(0, 10000000000),
						message="Аргументы указаны неправильно."
						)
			else:
				self.vk.messages.send(
					peer_id=self.peer_id,
					random_id=random.randint(0, 10000000000),
					message="Указаны не все аргументы."
					)

	def sendMessageToUser(self):
		if self.user_id in self.adms:
			if len(self.command.split("\n")) >= 2:
				form_id=self.command.split(" ")[1]
				message=self.txt.split("\n", 1)[1]
				if form_id.isdigit( ):
					conn=pymysql.connect(
						host="triniti.ru-hoster.com",
						user=self.user,
						password=self.passw,
						db='demkaXvl',
						charset='utf8', init_command='SET NAMES UTF8'
						)
					curs=conn.cursor( )
					curs.execute(f"SELECT user_id, access FROM forms WHERE form_id = {form_id}")
					form=curs.fetchone( )
					if form is not None:
						if form[1] == 0:
							self.vk.messages.send(
								peer_id=self.peer_id,
								random_id=random.randint(0, 10000000000),
								message="Сообщение от Администрации по поводу Анкеты:\n{message}"
								)
						else:
							self.vk.messages.send(
								peer_id=self.peer_id,
								random_id=random.randint(0, 10000000000),
								message="Эта анкета уже получила свой вердикт..."
								)
					else:
						self.vk.messages.send(
							peer_id=self.peer_id,
							random_id=random.randint(0, 10000000000),
							message="Анкеты с таким ID не существует."
							)
				else:
					self.vk.messages.send(
						peer_id=self.peer_id,
						random_id=random.randint(0, 10000000000),
						message="Аргументы указаны неправильно."
						)
			else:
				self.vk.messages.send(
					peer_id=self.peer_id,
					random_id=random.randint(0, 10000000000),
					message="Указаны не все аргументы."
					)

	def removeBuild(self):
		conn = pymysql.connect(
				host="triniti.ru-hoster.com",
				user=self.user,
				password=self.passw,
				db='demkaXvl',
				charset='utf8', init_command='SET NAMES UTF8'
				)
		curs = conn.cursor( )
		curs.execute(f'SELECT verif FROM conversations WHERE peer_id = {self.peer_id}')
		ch = int(curs.fetchone( )[0])
		if ch == 1:
			percent=random.randint(50, 75)
			if len(self.command.split(" ")) == 2:
				build = self.command.split(" ")[1]
				if build.isdigit():
					curs.execute(f"SELECT bd_name, wood/100*{percent}, food/100*{percent}, steel/100*{percent}, stone/100*{percent}, b_cris/100*{percent}, w_cris/100*{percent} FROM builds WHERE build_id = {build}")
					bld = curs.fetchone()
					if bld is None:
						self.vk.messages.send(
							peer_id=self.peer_id,
							random_id=random.randint(0, 10000000000),
							message="&#10062; Здания с таким ID не существует. Чтобы узнать все о Зданиях, напишите '/listbld' (Без кавычек)"
							)
					else:
						curs.execute(f"SELECT {bld[0]} FROM users WHERE user_id = {self.user_id}")
						user_build = curs.fetchone()[0]
						if user_build > 0:
							curs.execute(f"UPDATE users SET wood = wood + {bld[1]}, food = food + {bld[2]}, steel = steel + {bld[3]}, stone = stone + {bld[4]}, b_cris = b_cris * {bld[5]}, w_cris = w_cris * {bld[6]}, {bld[0]} = {bld[0]} - 1 WHERE user_id = {self.user_id}")
							conn.commit()
							self.vk.messages.send(
								peer_id=self.peer_id,
								random_id=random.randint(0, 10000000000),
								message=f"&#9989; Построка снесена. Вам возвращено {percent}% от ресурсов."
								)
						else:
							self.vk.messages.send(
								peer_id=self.peer_id,
								random_id=random.randint(0, 10000000000),
								message="&#10062; Вы не можете снести эту постройку, т.к. у вас ее и нет вовсе."
								)
				else:
					curs.execute(
						f"SELECT bd_name, wood/100*{percent}, food/100*{percent}, steel/100*{percent}, stone/100*{percent}, b_cris/100*{percent}, w_cris/100*{percent} FROM builds WHERE name = {build.capitalize( )}"
						)
					bld=curs.fetchone( )
					if bld is None:
						self.vk.messages.send(
							peer_id=self.peer_id,
							random_id=random.randint(0, 10000000000),
							message="&#10062; Здания с таким названием не существует. Чтобы узнать все о Зданиях, напишите '/listbld' (Без кавычек)"
							)
					else:
						curs.execute(f"SELECT {bld[0]} FROM users WHERE user_id = {self.user_id}")
						user_build=curs.fetchone( )[0]
						if user_build > 0:
							curs.execute(
								f"UPDATE users SET wood = wood + {bld[1]}, food = food + {bld[2]}, steel = steel + {bld[3]}, stone = stone + {bld[4]}, b_cris = b_cris * {bld[5]}, w_cris = w_cris * {bld[6]}, {bld[0]} = {bld[0]} - 1 WHERE user_id = {self.user_id}"
								)
							conn.commit( )
							self.vk.messages.send(
								peer_id=self.peer_id,
								random_id=random.randint(0, 10000000000),
								message=f"&#9989; Построка снесена. Вам возвращено {percent}% от ресурсов."
								)
						else:
							self.vk.messages.send(
								peer_id=self.peer_id,
								random_id=random.randint(0, 10000000000),
								message="&#10062; Вы не можете снести эту постройку, т.к. у вас ее и нет вовсе."
								)

			elif len(self.command.split(" ")) >= 3:
				build=self.command.split(" ")[1]
				count=self.command.split(" ")[2]
				if count.isdigit( ):
					count=int(count)
					if build.isdigit( ):
						curs.execute(
							f"SELECT bd_name, wood/100*{percent}*{count}, food/100*{percent}*{count}, steel/100*{percent}*{count}, stone/100*{percent}*{count}, b_cris/100*{percent}*{count}, w_cris/100*{percent}*{count} FROM builds WHERE build_id = {build}"
							)
						bld=curs.fetchone( )
						if bld is None:
							self.vk.messages.send(
								peer_id=self.peer_id,
								random_id=random.randint(0, 10000000000),
								message="&#10062; Здания с таким ID не существует. Чтобы узнать все о Зданиях, напишите '/listbld' (Без кавычек)"
								)
						else:
							curs.execute(f"SELECT {bld[0]} FROM users WHERE user_id = {self.user_id}")
							user_build=curs.fetchone( )[0]
							if user_build-count > 0:
								curs.execute(
									f"UPDATE users SET wood = wood + {bld[1]}, food = food + {bld[2]}, steel = steel + {bld[3]}, stone = stone + {bld[4]}, b_cris = b_cris * {bld[5]}, w_cris = w_cris * {bld[6]}, {bld[0]} = {bld[0]} - 1 WHERE user_id = {self.user_id}"
									)
								conn.commit( )
								self.vk.messages.send(
									peer_id=self.peer_id,
									random_id=random.randint(0, 10000000000),
									message=f"&#9989; Построки снесены. Вам возвращено {percent}% от ресурсов."
									)
							else:
								self.vk.messages.send(
									peer_id=self.peer_id,
									random_id=random.randint(0, 10000000000),
									message="&#10062; Вы не можете снести эту постройку, т.к. у вас их не хватает."
									)
					else:
						curs.execute(
							f"SELECT , wood/100*{percent}*{count}, food/100*{percent}*{count}, steel/100*{percent}*{count}, stone/100*{percent}*{count}, b_cris/100*{percent}*{count}, w_cris/100*{percent}*{count} FROM builds WHERE name = {build.capitalize( )}"
							)
						bld=curs.fetchone( )
						if bld is None:
							self.vk.messages.send(
								peer_id=self.peer_id,
								random_id=random.randint(0, 10000000000),
								message="&#10062; Здания с таким названием не существует. Чтобы узнать все о Зданиях, напишите '/listbld' (Без кавычек)"
								)
						else:
							curs.execute(f"SELECT {bld[0]} FROM users WHERE user_id = {self.user_id}")
							user_build=curs.fetchone( )[0]
							if user_build-count > 0:
								curs.execute(
									f"UPDATE users SET wood = wood + {bld[1]}, food = food + {bld[2]}, steel = steel + {bld[3]}, stone = stone + {bld[4]}, b_cris = b_cris * {bld[5]}, w_cris = w_cris * {bld[6]}, {bld[0]} = {bld[0]} - 1 WHERE user_id = {self.user_id}"
									)
								conn.commit( )
								self.vk.messages.send(
									peer_id=self.peer_id,
									random_id=random.randint(0, 10000000000),
									message=f"&#9989; Построки снесены. Вам возвращено {percent}% от ресурсов."
									)
							else:
								self.vk.messages.send(
									peer_id=self.peer_id,
									random_id=random.randint(0, 10000000000),
									message="&#10062; Вы не можете снести эти постройки, т.к. у вас их не хватает."
									)
				else:
					self.vk.messages.send(
						peer_id=self.peer_id,
						random_id=random.randint(0, 10000000000),
						message="Аргументы указаны неправильно.")
			else:
				self.vk.messages.send(
					peer_id=self.peer_id,
					random_id=random.randint(0, 10000000000),
					message="Указаны не все аргументы."
					)