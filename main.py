# -*- coding: utf-8 -*-
import requests
import random
import time
import json
import socket
import struct
from db import Database
from random import randrange
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class API(object):
	def __init__(self):
		self.s=requests.Session()
		self.s.verify=False
		self.setProxy()
		self.db=Database()

	def setProxy(self):
		self.s.proxies.update({'http': 'http://127.0.0.1:8888','https': 'https://127.0.0.1:8888',})

	def setPlatform(self,s):
		if s==2:
			self.platform='ios'
		else:
			self.platform='android'

	def setRegion(self,s=1):
		if s == 1:
			self.game='https://production-api.rs.aktsk.jp'
			self.version='1.15.0-95320b97c1ad9a8e782d8ab70c4cb3df'
			self.region=1
		else:
			self.game='https://production-api.rs-eu.aktsk.com'
			self.version='1.11.5-3cacaaeb16306f8887952e48f8afdc39'
			self.region=2

	def setSecret(self,s):
		self.secret=s

	def setUDID(self,s):
		self.udid=s

	def rndHex(self,n):
		return ''.join([random.choice('0123456789ABCDEF') for x in range(n)])
	
	def rndDeviceId(self):
		s='%s-%s-%s-%s-%s'%(self.rndHex(8),self.rndHex(4),self.rndHex(4),self.rndHex(4),self.rndHex(12))
		return s
		
	def log(self,msg):
		try:
			print('[%s] %s'%(time.strftime('%H:%M:%S'),msg))#.decode('utf-8')))
		except:
			return
		
	def callAPI(self,url,data=None):
		self.s.headers.update({'X-Mikoto-Request-Id':self.rndDeviceId().lower()})
		if data:
			r=self.s.post(self.game+url,data=json.dumps(data,separators=(',', ':'),ensure_ascii=False).encode('utf-8'),headers={'Content-Length':None})
		else:
			r=self.s.post(self.game+url)
		d=json.loads(r.content)
		if 'token' in d:
			self.log(d['token'])
			self.token=d['token']
			self.s.headers.update({'X-Mikoto-Token':self.token})
			del self.s.headers['X-Mikoto-Device-UUID']
		if 'assets_version' in d:
			self.assets_version=d['assets_version']
			self.master_version=d['master_version']
			self.s.headers.update({'X-Mikoto-Master-Version':self.master_version,'X-Mikoto-Assets-Version':self.assets_version})
		if 'player_id' in d:
			self.log('player_id:%s'%(d['player_id']))
			self.player_id=d['player_id']
		if 'player' in d or 'aurum' in d:
			if 'player' in d:
				player=d['player']
			else:
				player=d
			self.player=player
			self.log('aurum:%s free:%s stamina:%s/%s rank:%s'%(player['aurum'],player['free'],player['stamina'],player['max_stamina'],player['rank']))
		return d
	
	def auth_signup(self):
		return self.callAPI('/auth/signup')

	def auth_signin(self):
		return self.callAPI('/auth/signin')

	def status(self):
		return self.callAPI('/status')

	def player_create(self):
		return self.callAPI('/player/create',{"nick_name":"ポルカ","device_type":1} if self.region==1 else {"language":1,"lives_in_eea":True,"is_16_years_old_or_over":True,"country":"RU","nick_name":"Polka","device_type":1})

	def player_summary(self):
		return self.callAPI('/player/summary')

	def quest_resume(self):
		return self.callAPI('/quest/resume')

	def tutorial_quest_create(self):
		return self.callAPI('/tutorial/quest/create')

	def tutorial_quest_attack(self,d):
		return self.callAPI('/tutorial/quest/attack',d)

	def player_nickname_update(self,nick_name='Mila432'):
		return self.callAPI('/player/nickname/update',{"nick_name":nick_name})

	def player_detail(self):
		return self.callAPI('/player/detail')

	def quest_story_clear(self,quest_id):
		return self.callAPI('/quest/story/clear',{"quest_id":quest_id})

	def party_summary(self):
		return self.callAPI('/party/summary')

	def party_update(self,d):
		return self.callAPI('/party/update',d)

	def player_weapon_list(self):
		return self.callAPI('/player/weapon/list')

	def player_accessory_list(self):
		return self.callAPI('/player/accessory/list')

	def player_armor_list(self):
		return self.callAPI('/player/armor/list')

	def player_info(self):
		return self.callAPI('/player/info')

	def quest_info(self):
		return self.callAPI('/quest/info')

	def quest_party_summary(self,quest_id):
		return self.callAPI('/quest/party/summary',{"quest_id":quest_id})

	def quest_create(self,quest_id,party_number=1):
		return self.callAPI('/quest/create',{"quest_id":quest_id,"party_number":party_number})

	def quest_attack(self,d):
		return self.callAPI('/quest/attack',d)

	def quest_status(self):
		return self.callAPI('/quest/status')

	def player_login(self):
		return self.callAPI('/player/login',{"device_uuid":self.udid,"is_tracking_enabled":False,"advertising_id":"00000000-0000-0000-0000-000000000000"})

	def home_guest(self):
		return self.callAPI('/home/guest')

	def gacha_list(self):
		return self.callAPI('/gacha/list')

	def home_info(self):
		return self.callAPI('/home/info')

	def present_box_list(self,_filter):
		return self.callAPI('/present_box/list',{"filter":_filter})

	def gacha_step_up_button_draw(self,gname,gid):
		return self.callAPI('/gacha/%s/draw'%('button' if gname=='gacha_button_id' else'step_up_button'),{gname:gid})

	def present_box_open(self,present_box_ids):
		return self.callAPI('/present_box/open',{"present_box_ids":present_box_ids})

	def freeGasha(self):
		for j in self.gacha_list()['gachas']:
			if 'gacha_buttons' in j and j['gacha_buttons']:
				for i in j['gacha_buttons']:
					if i['gacha_button']['required_quantity']==0:
						self.log('id:%s'%(i['gacha_button']['gacha_button_id']))
						self.gacha_step_up_button_draw('gacha_button_id',i['gacha_button']['gacha_button_id'])
			if 'gacha_step_up_buttons' in j and j['gacha_step_up_buttons']:
				for i in j['gacha_step_up_buttons']:
					if i['required_quantity']==0:
						self.log('id:%s'%(i['gacha_step_up_button_id']))
						self.gacha_step_up_button_draw('gacha_step_up_button_id',i['gacha_step_up_button_id'])

	def login(self):
		self.s.headers.update({'Content-Type':'application/json','X-Mikoto-Request-Id':'7f33bd72-f490-4938-a215-db093ff009de','X-Mikoto-Client-Version':self.version,'X-Mikoto-Platform':self.platform,'X-Mikoto-Device-Secret':self.secret,'X-Mikoto-Device-UUID':self.udid,'X-Mikoto-Device-Model':'iPad7,5 iOS 13.3.1','Connection':'TE','TE':'identity','User-Agent':'BestHTTP'})
		self.status()
		self.auth_signin()
		self.player_create()
		self.player_summary()
		self.quest_resume()
		self.player_login()
		self.home_guest()
		self.home_info()
		self.player_info()
		
	def doQuest(self,quest_id):
		skills={}
		e=self.quest_create(quest_id)
		enemies=[]
		if 'created_quest' in e:
			for t in e['created_quest']['battle']['enemies']:
				if t['hp']==0:	continue
				enemies.append(t['member_id'])
		if 'battle' in e:
			for t in e['battle']['enemies']:
				if t['hp']==0:	continue
				enemies.append(t['member_id'])
		if 'created_quest' in e:
			for t in e['created_quest']['battle']['allies']:
				if t['member_id'] not in skills:
					skills[t['member_id']]=set()
				for s in t['skills']:
					skills[t['member_id']].add(s['skill_id'])
		if 'battle' in e:
			for t in e['battle']['allies']:
				if t['member_id'] not in skills:
					skills[t['member_id']]=set()
				for s in t['skills']:
					skills[t['member_id']].add(s['skill_id'])
		while(1):
			rndid=min(enemies)
			time.sleep(randrange(5))
			r=self.quest_attack({"commands":[{"actor_id":1,"skill_id":max(skills[1]),"target_id":rndid,"over_drive":False},{"actor_id":2,"skill_id":max(skills[2]),"target_id":rndid,"over_drive":False},{"actor_id":3,"skill_id":max(skills[3]),"target_id":rndid,"over_drive":False},{"actor_id":4,"skill_id":max(skills[4]),"target_id":rndid,"over_drive":False},{"actor_id":5,"skill_id":max(skills[5]),"target_id":rndid,"over_drive":False}],"is_auto":False})
			for t in r['battle']['allies']:
				if t['member_id'] not in skills:
					skills[t['member_id']]=set()
				for s in t['skills']:
					skills[t['member_id']].add(s['skill_id'])
			if 'battle_result' in r and r['battle_result']:
				if r['battle_result']['status']=='continue':
					enemies=[]
					for t in r['battle']['enemies']:
						self.log('id:%s hp:%s'%(t['member_id'],t['hp']))
						if t['hp']==0:	continue
						enemies.append(t['member_id'])
				if r['battle_result']['status']=='win':
					j=self.quest_status()
					battle=j['created_quest']['battle'] if 'created_quest' in j else j['battle']
					for t in battle['allies']:
						if t['member_id'] not in skills:
							skills[t['member_id']]=set()
						for s in t['skills']:
							skills[t['member_id']].add(s['skill_id'])
					enemies=[]
					for t in battle['enemies']:
						if t['hp']==0:	continue
						enemies.append(t['member_id'])
					if 91 in enemies:
						enemies=[91]
					if battle['final_round']<battle['round']:
						self.log('quest finished')
						return
				if r['battle_result']['status']=='complete':
					self.log('quest finished')
					return
		
	def genRandomIP(self):
		return socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))

if __name__ == '__main__':
	a=API()
	a.setRegion()
	a.setPlatform(2)
	a.setSecret('19e27ae7-0000-0000-0000-3d85913c0968')
	a.setUDID('080A2F5B-0000-0000-0000-1F50F469F0AA')
	a.login()
	a.freeGasha()