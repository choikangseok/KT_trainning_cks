#-*- coding:utf-8 -*-

## python 작성 규칙 ##
#0. 파일이름: 소문자 (동사_)명사_명사.py
#1. 변수이름: 소문자, 명사_명사
#2. 상수, 글로벌 변수, 클래스(객체) 변수 이름: 대문자, 명사_명사
#3. 함수이름: camelCase, 동사(명사)
#4. 클래스이름: CamelCase, 명사명사
#5. 모듈(파일)이름: 소문자, (특성_)기능(_대상_분류)
#6. 문자열 print, logging -> "~", DB쿼리 -> """~""", 기타 -> '~'
#7. 문자열 합치기(+), str(문자 외 변수)
#8. 정규표현식은 ur'' 처리

#webkit_base#

#<url 계위>
#[url, mid_url, final_url, land_url, link, land_link, referer 개념]
#0depth(base)		1depth								2depth								3depth
#url				-> apk(final_url)
#					-> html(land_url:referer; link) 	-> apk(final_url; link:mid_url)
#														-> html(land_link:referer, link)	-> apk(final_url; link:mid_url)
#																							-> html(drop)
#[current_url 개념]
#0depth(base)		1depth								2depth								3depth
#url				-> final_url(current_url)
#					-> land_url(current_url)			-> final_url(current_url)
#														-> land_link(current_url)			-> final_url(current_url)
#

#파이썬 모듈 import#
import os, sys
import json
import re
import random
import md5, sha
import socket
import win_inet_pton
import urllib
import time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from geoip import geolite2
from androguard.core.bytecodes.apk import APK
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.common.exceptions import StaleElementReferenceException, UnexpectedAlertPresentException
from pyvirtualdisplay import Display
from dns import resolver

#경로 설정(절대경로)#
HOME_PATH = os.getcwd()
WEBKIT_PATH = os.path.join(HOME_PATH, 'server', 'analyze', 'url', 'webkit')
HTML_FILE_PATH = os.path.join(HOME_PATH, 'server', 'analyze', 'url', 'html_file')
APK_FILE_TEMP_PATH = os.path.join(HOME_PATH, 'server', 'analyze', 'apk', 'apk_file', 'temp')
APK_FILE_TEST_PATH = os.path.join(HOME_PATH, 'client', 'test', 'test_apk')

#사용자 서브 모듈 import#
from sub_module.interface import interface_file #InterfaceFile
from sub_module.interface import interface_db_mysql #InterfaceDBMysql
from sub_module.interface import interface_http #InterfaceHTTP
from sub_module.parser import custom_parser #CustomParser
from whitelist import whitelist #WhiteList

class WebkitBase(object):
	
	def __init__(self, hostname, log_queue, log_head, config, db_config, webkit_name, url):
		self.HOSTNAME = hostname
		self.MODULE_NAME = webkit_name
		self.BASE_URL = url
		self.CLASS_NAME = self.__class__.__name__
		self.PLATFORM = sys.platform
		
		#파서
		self.PARSER = custom_parser.CustomParser(self.MODULE_NAME)
		
		#인터페이스
		self.FILE_INTERFACE = interface_file.InterfaceFile(self.MODULE_NAME)#File 인터페이스
		self.MYSQL_DB_INTERFACE = interface_db_mysql.InterfaceDBMysql(self.MODULE_NAME)#DB 인터페이스
		self.HTTP_INTERFACE = interface_http.InterfaceHTTP(self.MODULE_NAME)#HTTP 인터페이스
		
		#화이트 리스트
		self.WHITELIST = whitelist.WhiteList(self.MODULE_NAME)
		
		#LOG 큐
		self.LOG_QUEUE = log_queue
		self.LOG_HEAD = log_head
		
		#DB 관련
		self.DB_CONFIG = db_config
		self.DB_RO_MODE = db_config['ro_mode']
		self.DB_COMMENT = db_config['comment']
		
		#config 부분(config_num, config_dict), config.json => [{key:value, ...} ...]
		self.CONFIG_NUM = config[0]
		self.USER_AGENT_INFO = config[1]['user_agent_info']
		self.USER_AGENT_COUNT = len(self.USER_AGENT_INFO)
		self.TEST_FLAG = config[1]['test_flag']
		
		#webkit 브라우저
		self.WEBDRIVER = None
		self.TEMP_APK_PATH = ''
		
		#webkit 결과
		self.WEBKIT_RESULT = {
								'webkit_name':webkit_name,		
								'url':url,					#condition_part: 기준 url(불변)
								'current_url':'',			#condition_part: url 접속 후 도달한 url
								'land_url':'',				#condition_part: html을 응답하는 url
								'html':'',					#condition_part: html
								'link':[''],				#condition_part: html 내의 링크
								'land_link':[''], 			#condition_part: html을 응답하는 링크
								'browser_use':'no',			#condition_part: browser 사용 여부
								'browser_url':'',			#condition_part: browser에서 최초 접속할 url
								'ip':None,
								'ipv6':None,
								'country_code':None,
								'spread_info_list':[],				
								'connection_flag':False,
								'connection_error':None,		
								'last_conn_time':None,
								'apk_download_flag':False,
								'analysis_error':None
							}

	
	#로깅
	def putLog(self, level, log_string):
		#level 0:None, 1:'debug', 2:'info', 3:'warn', 4:'error', 5:'critical'
		if self.LOG_QUEUE:
			self.LOG_QUEUE.put_nowait({'level':level, 'hostname':self.HOSTNAME, 'module_name':self.MODULE_NAME, 'config_num':self.CONFIG_NUM, 'string':log_string})
	
	
	#webkit 실행
	def start(self):
		self.run()
		return self.WEBKIT_RESULT
		
	
	#여기에 webkit 작성
	def run(self):
		pass
		
	
	#이전 결과를 다음에 조건 매칭에 활용
	def updateConditionPart(self, condition_part, last_result):
		try:
			not_update_part = ['test']
			for part in condition_part:
				if part not in not_update_part:
					if isinstance(last_result[part], str):
						last_result[part] = self.PARSER.convertToUnicode(last_result[part])
					condition_part[part] = last_result[part]

			return condition_part
			
		except Exception as e:
			_, _ , tb = sys.exc_info() # tb -> traceback object
			raise Exception(self.CLASS_NAME+'.'+str(sys._getframe().f_code.co_name)+' error(line No.: '+str(tb.tb_lineno)+'): '+str(e))

			
	def setLastResult(self, last_result):
		try:
			self.putLog('debug', self.LOG_HEAD+" - set Last Result")
			not_update_part = ['webkit_name', 'url']
			for part in last_result:
				if part not in not_update_part:
					self.WEBKIT_RESULT[part] = last_result[part]
		
		except Exception as e:
			_, _ , tb = sys.exc_info() # tb -> traceback object
			raise Exception(self.CLASS_NAME+'.'+str(sys._getframe().f_code.co_name)+' error(line No.: '+str(tb.tb_lineno)+'): '+str(e))
			
	
	def showResult(self):
		try:
			self.putLog('debug', self.LOG_HEAD+" - webkit result")
			for part in self.WEBKIT_RESULT:
				if isinstance(self.WEBKIT_RESULT[part], unicode):
					self.putLog('debug', self.LOG_HEAD+" - "+part+": "+self.WEBKIT_RESULT[part])
				else:
					self.putLog('debug', self.LOG_HEAD+" - "+part+": "+str(self.WEBKIT_RESULT[part]))
		
		except Exception as e:
			_, _ , tb = sys.exc_info() # tb -> traceback object
			raise Exception(self.CLASS_NAME+'.'+str(sys._getframe().f_code.co_name)+' error(line No.: '+str(tb.tb_lineno)+'): '+str(e))
	
	
	def startDB(self):
		try:
			#DB 연결
			mysql_conn = None
			mysql_cur = None
			
			#connectDB(self, db_config)
			mysql_conn = self.MYSQL_DB_INTERFACE.connectDB(self.DB_CONFIG)
			self.putLog('debug', self.LOG_HEAD+" - got DB connection")
			
			#getBufferedCursor(self, mysql_conn)
			mysql_cur = self.MYSQL_DB_INTERFACE.getBufferedCursor(mysql_conn)
			self.putLog('debug', self.LOG_HEAD+" - got DB cursor")
			
			return (mysql_conn, mysql_cur)

		except Exception as e:
			_, _ , tb = sys.exc_info() # tb -> traceback object
			raise Exception(self.CLASS_NAME+'.'+str(sys._getframe().f_code.co_name)+' error(line No.: '+str(tb.tb_lineno)+'): '+str(e))
	
	
	def endDB(self, mysql_conn, mysql_cur):
		try:
			if mysql_conn:
				if mysql_cur:
					mysql_cur.close()
				#closeConnection(self, mysql_conn)
				self.MYSQL_DB_INTERFACE.closeConnection(mysql_conn)
				self.putLog('debug', self.CLASS_NAME+" - db connection closed")

		except Exception as e:
			_, _ , tb = sys.exc_info() # tb -> traceback object
			raise Exception(self.CLASS_NAME+'.'+str(sys._getframe().f_code.co_name)+' error(line No.: '+str(tb.tb_lineno)+'): '+str(e))


	def checkFromDB(self, query_check, data_check, get_result_flag=False, plural_flag=True):
		try:
			mysql_conn, mysql_cur = self.startDB()			
			mysql_cur_result = self.MYSQL_DB_INTERFACE.executeQuery(mysql_cur, query_check, data_check)
			if mysql_cur_result.rowcount:
				if get_result_flag:
					if plural_flag:
						return mysql_cur_result.fetchall()
					else:
						return mysql_cur_result.fetchone()
				else:
					return True
			else:
				return False
				
			self.endDB(mysql_conn, mysql_cur)
			
		except Exception as e:
			_, _ , tb = sys.exc_info() # tb -> traceback object
			raise Exception(self.CLASS_NAME+'.'+str(sys._getframe().f_code.co_name)+' error(line No.: '+str(tb.tb_lineno)+'): '+str(e))
			
	
	def insertIntoURLLIST(self, url, referer):
		try:
			url = self.parseLink(url, referer)
			if url:
				if self.DB_RO_MODE:
					self.putLog('info', self.LOG_HEAD+" - db read only, print result")
					self.putLog('info', self.LOG_HEAD+" - url not inserted: "+url)
				else:
					url_hash = self.getHashValue(url)
					webkit_name = self.WEBKIT_RESULT['webkit_name']
					parsed_phone_number = self.PARSER.parseByRegexGroup(self.PARSER.MPHONE_REGEX_GROUP, url)
					if parsed_phone_number:
						phone_number_mid = parsed_phone_number.group('mid')
						phone_number_tail = parsed_phone_number.group('tail')
						phone_number = phone_number_mid+phone_number_tail
						self.putLog('debug', self.LOG_HEAD+" - phone_number found: "+phone_number)
					else:
						phone_number = ''
					get_time = datetime.now()
					get_time_date = get_time.strftime('%Y-%m-%d')
				
					mysql_conn, mysql_cur = self.startDB()

					#DB 1차 쿼리, 테이블명: other_info
					self.putLog('debug', self.LOG_HEAD+" - check if other_info table has the url: select")
					#select 쿼리 및 실행
					query_select = ("""select id, referer, phone_number, count_all, count_per_date, first_get_time, last_get_time from other_info where url=%s""")
					data_select = (url,)
					mysql_cur_result = self.MYSQL_DB_INTERFACE.executeQuery(mysql_cur, query_select, data_select)
				
					#조회 결과 있으면 update
					if mysql_cur_result.rowcount:
						self.putLog('debug', self.LOG_HEAD+" - found in other_info table: update")
								
						other_info_id, referer_json, phone_number_json, count_all, count_per_date_json, first_get_time, last_get_time = mysql_cur_result.fetchone()
						
						#referer_json: JSON형태의 문자열(utf-8)
						# => referer_db: {["YYYY-MM-DD":u"referer"] ...}
						#count_per_date_json: JSON형태의 문자열(utf-8)
						# => count_per_date_db: {"YYYY-MM-DD":number ...}
						
						referer_db = json.loads(referer_json, encoding='utf-8')
						phone_number_db = json.loads(phone_number_json, encoding='utf-8')
						count_per_date_db = json.loads(count_per_date_json)
						
						#수집시간 비교, 최초 로그 수집시간 결정
						if (first_get_time - get_time).days > -1:
							first_get_time = get_time
						else:
							last_get_time = get_time
						
						#날짜마다 카운트 및 referer 저장
						if get_time_date in count_per_date_db:
							count_per_date_db[get_time_date] += 1
							#referer 동일한지 확인 후 저장
							if referer not in referer_db[get_time_date]:
								referer_db[get_time_date].append(referer)
						else:
							count_per_date_db[get_time_date] = 1
							referer_db[get_time_date] = [referer]
							
						#전화번호 추가(중복 제거)
						if phone_number_db:
							if phone_number not in phone_number_db:
								phone_number_db.append(phone_number)
						else:
							phone_number_db = [phone_number]
						
						#referer_db 문자열(unicode)을 utf-8로 인코딩하여 JSON형태의 문자열 생성
						referer_json = json.dumps(referer_db, ensure_ascii=False, encoding='utf-8')
						phone_number_json = json.dumps(phone_number_db, ensure_ascii=False, encoding='utf-8')
						count_all += 1
						count_per_date_json = json.dumps(count_per_date_db)
						
						query_update = ("""update other_info set 
											referer=%s, phone_number=%s,
											count_all=%s, count_per_date=%s,
											first_get_time=%s, last_get_time=%s, last_update=%s, last_update_by=%s 
											where id=%s""")
						data_update = (referer_json, phone_number_json, count_all, count_per_date_json, first_get_time, last_get_time,get_time, webkit_name, other_info_id)
						self.MYSQL_DB_INTERFACE.executeQuery(mysql_cur, query_update, data_update)
					#조회 결과 없으면 insert 혹은 pass
					else:
						#apk 다운로드 되지 않으면 other_info 테이블에서 삭제되어 url_list만 업데이트 -> 추후 화이트리스트 추가에 활용
						self.putLog('debug', self.LOG_HEAD+" - check if url_list table has the url: select")
						
						query_select = ("""select other_info_id from url_list where url=%s""")
						data_select = (url,)
						mysql_cur_result = self.MYSQL_DB_INTERFACE.executeQuery(mysql_cur, query_select, data_select)
						if mysql_cur_result.rowcount:
							other_info_id = mysql_cur_result.fetchone()[0]
						else:
							self.putLog('debug', self.LOG_HEAD+" - not found in other_info and url_list table: insert")
							
							referer_json = json.dumps({get_time_date:[referer]}, ensure_ascii=False, encoding='utf-8')
							phone_number_json = json.dumps([phone_number], ensure_ascii=False, encoding='utf-8')
							count_all = 1
							count_per_date_json = json.dumps({get_time_date:1})
							
							query_insert = ("""insert into other_info(
													url, referer, phone_number,
													count_all, count_per_date, 
													first_get_time, last_get_time, last_update, last_update_by)
												values(
													%s, %s, %s,
													%s, %s, 
													%s, %s, %s, %s)""")
							data_insert = (url, referer_json, phone_number_json, count_all, count_per_date_json, get_time, get_time, get_time, webkit_name)
							self.MYSQL_DB_INTERFACE.executeQuery(mysql_cur, query_insert, data_insert)
						
							##4. DB 2차 쿼리를 위한 정보 조회, 테이블명: other_info
							query_select = ("""select id from other_info where url=%s""")
							data_select = (url,)
							mysql_cur_result = self.MYSQL_DB_INTERFACE.executeQuery(mysql_cur, query_select, data_select)
							if not mysql_cur_result.rowcount:
								raise Exception(self.LOG_HEAD+" - not found in other_info table(after insert): quit")
							else:
								other_info_id = mysql_cur_result.fetchone()[0]
					
					#DB 2차 쿼리, 테이블명: url_list
					self.putLog('debug', self.LOG_HEAD+" - check if url_list table has the url: select")
					#select 쿼리 및 실행
					query_select = ("""select id, count_all, count_all_by_collector, count_per_date, count_per_date_by_collector, first_get_time, last_get_time from url_list where url = %s""")
					data_select = (url,)
					mysql_cur_result = self.MYSQL_DB_INTERFACE.executeQuery(mysql_cur, query_select, data_select)
					
					#조회 결과 있으면 update
					if mysql_cur_result.rowcount:
						self.putLog('debug', self.LOG_HEAD+" - found in url_list table: update")
						
						id, count_all, count_all_by_collector_json, count_per_date_json, count_per_date_by_collector_json, first_get_time, last_get_time = mysql_cur_result.fetchone()
						count_all_by_collector_db = json.loads(count_all_by_collector_json)
						count_per_date_db = json.loads(count_per_date_json)
						count_per_date_by_collector_db = json.loads(count_per_date_by_collector_json)
						
						#시간 비교, 파일 생성 시간에 따라
						if (first_get_time - get_time).days > -1:
							first_get_time = get_time
						else:
							last_get_time = get_time
						
						#수집URL 전체 카운트
						count_all += 1
						
						#OTHER 수집URL 전체 카운트
						if 'OTHER' in count_all_by_collector_db:
							count_all_by_collector_db['OTHER'] += 1
						else:
							count_all_by_collector_db['OTHER'] = 1
						count_all_by_collector_json = json.dumps(count_all_by_collector_db)
						
						#수집URL 날짜마다 카운트
						if get_time_date in count_per_date_db:
							count_per_date_db[get_time_date] += 1
						else:
							count_per_date_db[get_time_date] = 1
						count_per_date_json = json.dumps(count_per_date_db)
						
						#OTHER 수집URL 날짜마다 카운트
						if 'OTHER' in count_per_date_by_collector_db:
							if get_time_date in count_per_date_by_collector_db['OTHER']:
								count_per_date_by_collector_db['OTHER'][get_time_date] += 1
							else:
								count_per_date_by_collector_db['OTHER'][get_time_date] = 1
						else:
							count_per_date_by_collector_db['OTHER'] = {}
							count_per_date_by_collector_db['OTHER'][get_time_date] = 1
						count_per_date_by_collector_json = json.dumps(count_per_date_by_collector_db)
						
						#update 쿼리 및 실행
						query_update = ("""update url_list set 
											other_info_id=%s,
											count_all=%s, count_all_by_collector=%s,
											count_per_date=%s, count_per_date_by_collector=%s,
											first_get_time=%s, last_get_time=%s, last_update=%s, last_update_by=%s
											where id=%s""")
						data_update = (other_info_id, count_all, count_all_by_collector_json, count_per_date_json, count_per_date_by_collector_json, first_get_time, last_get_time, get_time, webkit_name, id)
						self.MYSQL_DB_INTERFACE.executeQuery(mysql_cur, query_update, data_update)
					#조회 결과 없으면 insert
					else:
						self.putLog('debug', self.LOG_HEAD+" - not found in url_list table: insert")
						
						count_all = 1
						count_all_by_collector_json = json.dumps({'OTHER':1})
						count_per_date_json = json.dumps({get_time_date:1})
						count_per_date_by_collector_json = json.dumps({'OTHER':{get_time_date:1}})
						
						#insert 쿼리 및 실행
						query_insert = ("""insert into url_list(
												other_info_id, 
												url, url_hash, 
												count_all, count_all_by_collector,
												count_per_date, count_per_date_by_collector,
												url_analysis_flag,
												first_get_time, last_get_time, last_update, last_update_by)
											values(
												%s, 
												%s, %s, 
												%s, %s,
												%s, %s,
												'N',
												%s, %s, %s, %s)""")
						data_insert = (other_info_id, url, url_hash, count_all, count_all_by_collector_json, count_per_date_json, count_per_date_by_collector_json, get_time, get_time, get_time, webkit_name)
						self.MYSQL_DB_INTERFACE.executeQuery(mysql_cur, query_insert, data_insert)
				
					self.putLog('info', self.LOG_HEAD+" - DB query end")
					
					#DB commit
					self.MYSQL_DB_INTERFACE.commitQuery(mysql_conn)
					self.putLog('info', self.LOG_HEAD+" - query committed")
					self.endDB(mysql_conn, mysql_cur)
			
		except Exception as e:
			_, _ , tb = sys.exc_info() # tb -> traceback object
			raise Exception(self.CLASS_NAME+'.'+str(sys._getframe().f_code.co_name)+' error(line No.: '+str(tb.tb_lineno)+'): '+str(e))
			
	
	def getPhoneNumberListbyURL(self, url):
		try:
			#쿼리 타입 4가지: 1.url, 2.url의 hostdomain, 3.url의 ip, 4. url의 ipv6
			self.putLog('debug', self.LOG_HEAD+' - got phone number')
			phone_number_list = []
			query_map_list = []
			query_type1 = ("""select phone_number from ltas_info where url=%s""")
			query_type2 = ("""select phone_number from ltas_info where url like %s""")
			query_type3 = ("""select phone_number from ltas_info where ip like %s""")
			query_type4 = ("""select phone_number from ltas_info where ipv6 like %s""")
			
			#url 쿼리 및 데이터 매핑
			parsed_url = self.PARSER.parseByRegexGroup(self.PARSER.URL_PARSING_REGEX_GROUP, url)
			if parsed_url:
				hostdomain = parsed_url.group('hostdomain')
				query_map_list.append((query_type1, (url,)))
				query_map_list.append((query_type2, ('%'+hostdomain+'%',)))
			
			#ip, ipv6 쿼리 및 데이터 매핑
			ip_list, ipv6_list, _ = self.getURLInfo(url)
			for ip in ip_list:
				query_map_list.append((query_type3, ('%'+ip+'%',)))
			for ipv6 in ipv6_list:
				query_map_list.append((query_type4, ('%'+ipv6+'%',)))
			
			#url이 base_url과 다를 시, 추가로 base_url 쿼리 및 데이터 매핑
			if url != self.BASE_URL:
				parsed_base_url = self.PARSER.parseByRegexGroup(self.PARSER.URL_PARSING_REGEX_GROUP, self.BASE_URL)
				if parsed_url:
					base_hostdomain = parsed_base_url.group('hostdomain')
					query_map_list.append((query_type1, (self.BASE_URL,)))
					#url과 base_url의 hostdomain이 다를 시에만 매핑
					if hostdomain != base_hostdomain:
						query_map_list.append((query_type2, ('%'+base_hostdomain+'%',)))
			
			#DB에서 번호 조회 
			for query_map in query_map_list:
				phone_number_json = self.checkFromDB(query_map[0], query_map[1], True, True)	
				if phone_number_json:
					phone_number_list += json.loads(phone_number_json, encoding='utf-8')

			#DB에 번호 없으면 랜덤 생성(3회)
			if not phone_number_list:
				for _ in range(3):
					phone_number_list.append(self.getRandomNumbers(8))

			return phone_number_list
		
		except Exception as e:
			_, _ , tb = sys.exc_info() # tb -> traceback object
			raise Exception(self.CLASS_NAME+'.'+str(sys._getframe().f_code.co_name)+' error(line No.: '+str(tb.tb_lineno)+'): '+str(e))
			
	
	def getRandomNumbers(self, count):
		try:
			random_numbers = ''
			for _ in range(count):
				random_numbers += str(random.randint(0,9))
				
			return random_numbers
		
		except Exception as e:
			_, _ , tb = sys.exc_info() # tb -> traceback object
			raise Exception(self.CLASS_NAME+'.'+str(sys._getframe().f_code.co_name)+' error(line No.: '+str(tb.tb_lineno)+'): '+str(e))
			
	
	def getHashValue(self, text, type='md5'):
		try:
			if type == 'md5':
				hash = md5.new(text).hexdigest()
			elif type == 'sha':
				hash = sha.new(text).hexdigest()
				
			return hash
		
		except Exception as e:
			_, _ , tb = sys.exc_info() # tb -> traceback object
			raise Exception(self.CLASS_NAME+'.'+str(sys._getframe().f_code.co_name)+' error(line No.: '+str(tb.tb_lineno)+'): '+str(e))
	
	
	def getTempURL(self, url, part_list):
		try:
			scheme = ''
			hostdomain = ''
			url_ip = ''
			url_ipv6 = ''
			path = ''
			parsed_url = self.PARSER.parseByRegexGroup(self.PARSER.URL_PARSING_REGEX_GROUP, url)
			if parsed_url:
				if 'scheme' in part_list:
					scheme = parsed_url.group('scheme')
				if 'hostdomain' in part_list:
					hostdomain = parsed_url.group('hostdomain')
				if 'url_ip' in part_list:
					url_ip = parsed_url.group('url_ip')
				if 'url_ipv6' in part_list:
					url_ipv6 = parsed_url.group('url_ipv6')
				if 'path' in part_list:
					path = parsed_url.group('path')
				temp_url = scheme+(hostdomain or url_ip or url_ipv6)+path
			
			return temp_url
			
		except Exception as e:
			_, _ , tb = sys.exc_info() # tb -> traceback object
			raise Exception(self.CLASS_NAME+'.'+str(sys._getframe().f_code.co_name)+' error(line No.: '+str(tb.tb_lineno)+'): '+str(e))


	## 여기부터 webkit_base 주요 활용 함수
	#webkit 일반 기능
	def checkURL(self, url, referer=None, base_flag=False, head_flag=False, html_save=False):
		try:
			#HTTP 헤더 정보를 통해 기본 정보 확인
			connection_flag, connection_error, analysis_error, apk_flag, html_flag, get_request_flag, white_flag = self.checkByHeader(url, referer)
			spread_info = None
			current_url = None
			html = None
			
			#접속 가능하고 4xx, 5xx 에러가 없을 시
			if connection_flag and not connection_error:
				self.putLog('debug', self.LOG_HEAD+" - url: "+url+", connected")
				#접속 결과 체크
				if base_flag:
					self.WEBKIT_RESULT['last_conn_time'] = datetime.now()
					self.WEBKIT_RESULT['connection_flag'] = connection_flag
					#whitelist
					if white_flag:
						self.putLog('debug', self.LOG_HEAD+" - whitelist url found")
						self.WEBKIT_RESULT['analysis_error'] = "whitelist url connected"
					elif analysis_error:
						self.putLog('debug', self.LOG_HEAD+" - analysis failed: "+str(analysis_error))
						self.WEBKIT_RESULT['analysis_error'] = analysis_error
					
				#url분석 결과 체크
				if not head_flag and not white_flag and not analysis_error:
					#html이거나 추가 GET요청 필요 시
					if html_flag or get_request_flag:
						self.putLog('debug', self.LOG_HEAD+" - try to get html")
						current_url, html, html_flag, connection_error, analysis_error = self.getHTML(url, referer)
						if html_flag and html_save:
							self.WEBKIT_RESULT['land_url'] = current_url
							self.WEBKIT_RESULT['html'] = html
							self.putLog('info', self.LOG_HEAD+" - html and land_url updated")
					#apk이거나 추가 GET요청 필요 시
					if (apk_flag or get_request_flag) and not html_flag:
						self.putLog('debug', self.LOG_HEAD+" - try to get apk")
						apk_flag, spread_info, connection_error, analysis_error = self.getAPK(url, referer)
						if apk_flag:
							self.WEBKIT_RESULT['spread_info_list'].append(spread_info)
					#에러 발생 시
					if connection_error or analysis_error:
						self.WEBKIT_RESULT['analysis_error'] = connection_error or analysis_error
					#html, apk, whitelist 아닐 시
					elif not html_flag and not apk_flag:
						self.putLog('debug', self.LOG_HEAD+" - neither apk nor html")
						self.WEBKIT_RESULT['analysis_error'] = "neither apk nor html"
			else:
				if base_flag:
					if connection_error:
						self.putLog('debug', self.LOG_HEAD+" - connection failed: "+str(connection_error))
						self.WEBKIT_RESULT['connection_error'] = connection_error
					if analysis_error:
						self.putLog('debug', self.LOG_HEAD+" - analysis failed: "+str(analysis_error))
						self.WEBKIT_RESULT['analysis_error'] = analysis_error
			
			return (current_url, html, html_flag, apk_flag)
							
		except Exception as e:
			_, _ , tb = sys.exc_info() # tb -> traceback object
			raise Exception(self.CLASS_NAME+'.'+str(sys._getframe().f_code.co_name)+' error(line No.: '+str(tb.tb_lineno)+'): '+str(e))
	
	
	def checkByHeader(self, url, referer=None):
		try:
			connection_flag, response, connection_error = self.connectURL(url, referer, True, True)
			apk_flag = False
			html_flag = False
			get_request_flag = False
			white_flag = False
			analysis_error = None
			
			path = ''
			parsed_url = self.PARSER.parseByRegexGroup(self.PARSER.URL_PARSING_REGEX_GROUP, url)
			if parsed_url:
				path = parsed_url.group('path')
				if not path:
					path = ''
			
			if response:
				redirect_count = 0
				while True:
					#301, 302: 리다이렉트 응답일 경우 재요청
					if response.code == 301 or response.code == 302:
						redirect_count += 1
						current_url = response.geturl()
						redirect_url = response.headers['Location']
						redirect_url = self.parseLink(redirect_url, current_url)
						#리다이렉트 ULR과 현재 URL이 다를 경우
						if redirect_url and redirect_url != current_url:
							self.putLog('debug', self.LOG_HEAD+" - redirect_url: "+redirect_url+", redirect_count: "+str(redirect_count))
							white_flag, message = self.WHITELIST.check(redirect_url)
							if white_flag:
								self.putLog('debug', self.LOG_HEAD+" - whitelist redirect_url found:"+redirect_url+" by "+message)
								break
							#5회 초과 리다이렉트 되거나 url path가 .apk로 끝나는 경우 GET으로 요청하도록
							elif redirect_count > 5 or path.lower().endswith('.apk'):
								get_request_flag = True
								connection_error = None
								break
						
						#리다이렉트 ULR과 현재 URL이 같을 경우
						elif redirect_url and redirect_url == current_url:
							self.putLog('debug', self.LOG_HEAD+" - redirect_url is same as the current_url, redirect_count: "+str(redirect_count))
							#2회 초과 리다이렉트 되거나 url path가 .apk로 끝나는 경우 GET으로 요청하도록
							if redirect_count > 2 or path.lower().endswith('.apk'):
								get_request_flag = True
								connection_error = None
								break		
						else:
							self.putLog('debug', "no redirection")
							break
						
						#리다이렉트 URL 접속
						_, response, connection_error = self.connectURL(redirect_url, True, True)
						if response:
							continue
						else:
							self.putLog('debug', self.LOG_HEAD+" - connection_error: "+str(connection_error))
							break
					#405: HEAD 메소드 허용 안됨인 경우, url path가 .apk로 끝나는 경우 GET으로 요청하도록
					elif response.code == 405 or path.lower().endswith('.apk'):
						get_request_flag = True
						connection_error = None
						break
					#최종 응답
					else:
						content_type = ''
						download_file = ''
						data_size = 0
						meta = response.info()
						if meta.getheaders("Content-Type"):
							content_type = meta.getheaders("Content-Type")[0]
						if meta.getheaders("Content-Disposition"):
							download_file = meta.getheaders("Content-Disposition")
						if meta.getheaders("Content-Length"):
							data_size = meta.getheaders("Content-Length")[0]
							self.putLog('debug', self.LOG_HEAD+" - data size: "+str(data_size))
						else:
							self.putLog('debug', self.LOG_HEAD+" - data size: unknown")
						
						#헤더 정보를 보고 파일 다운로드로 확인된 경우 
						if content_type.find('android') != -1 or content_type.find('octet-stream') != -1 or download_file:
							self.putLog('info', self.LOG_HEAD+" - found file")
							#50MB 미만 시에만 다운로드 진행
							if int(data_size) < 50000000:
								apk_flag = True
							else:
								analysis_error = 'file size is over 50MB'
								self.putLog('debug', self.LOG_HEAD+" - file size is over 50MB")
						#html일 경우
						elif content_type.find('html') != -1:
							self.putLog('info', self.LOG_HEAD+" - found html")
							#50MB 미만 시에만 분석 진행
							if int(data_size) < 50000000:
								html_flag = True
							else:
								analysis_error = 'html size is over 50MB'
								self.putLog('debug', self.LOG_HEAD+" - html size is over 50MB")
						break
			else:
				self.putLog('info', self.LOG_HEAD+" - connection failed")
				
			return (connection_flag, connection_error, analysis_error, apk_flag, html_flag, get_request_flag, white_flag)
			
		except Exception as e:
			_, _ , tb = sys.exc_info() # tb -> traceback object
			raise Exception(self.CLASS_NAME+'.'+str(sys._getframe().f_code.co_name)+' error(line No.: '+str(tb.tb_lineno)+'): '+str(e))
			
	
	def getAPK(self, url, referer=None):
		try:
			connection_flag, response, connection_error = self.connectURL(url, referer)
			apk_flag = False
			spread_info = {
						'mid_url':'',
						'mid_ip':'',
						'mid_ipv6':'',
						'mid_country_code':'',
						'final_url':'',
						'final_ip':'',
						'final_ipv6':'',
						'final_country_code':'',
						'apk_hash':'',
						'apk_file_name':'',
						'datetime':str(datetime.now())
						}
			analysis_error = None
			
			if connection_flag and response and not connection_error:
				path = ''
				parsed_url = self.PARSER.parseByRegexGroup(self.PARSER.URL_PARSING_REGEX_GROUP, url)
				if parsed_url:
					path = parsed_url.group('path')
					if not path:
						path = ''
						
				#Content-Type 및 Content-Disposition 확인
				content_type = ''
				download_file = ''
				meta = response.info()
				if meta.getheaders("Content-Type"):
					content_type = meta.getheaders("Content-Type")[0]
				if meta.getheaders("Content-Disposition"):
					download_file = meta.getheaders("Content-Disposition")
				
				#파일 다운로드일 경우
				if content_type.find('android') != -1 or content_type.find('octet-stream') != -1 or download_file or path.lower().endswith('.apk'):
					#실제 데이터에서 파일 사이즈 확인
					try:
						raw_data = response.read()
						file_size = len(raw_data)
						#파일 사이즈 50MB 미만, 파일 유형이 apk인 것만 저장
						if int(file_size) < 50000000:
							#apk 여부 확인
							try:
								apk = APK(raw_data, raw=True)	
								if apk.is_valid_APK():
									final_url = response.geturl()
									self.putLog('info', self.LOG_HEAD+" - valid apk file found from: "+final_url)
									#apk_hash 화이트리스트 체크
									apk_hash = md5.new(raw_data).hexdigest()
									white_flag, message = self.WHITELIST.check(apk_hash=apk_hash)
									if white_flag:
										self.putLog('debug', self.LOG_HEAD+" - whitelist apk_hash found:"+apk_hash+" by "+message)
									else:
										#파일 이름 확인
										if download_file:
											#http 헤더에서 파일 이름 파싱
											header = download_file[0]
											file_name_regex_in_header = ur"filename=\"?(?P<apk_file_name>\S+)\"?"
											parsed_apk_file_name = self.PARSER.parseByRegexGroup(file_name_regex_in_header, header)
										else:
											#없을 시 url(path, query)에서 파일 이름 파싱
											parsed_final_url = self.PARSER.parseByRegexGroup(self.PARSER.URL_PARSING_REGEX_GROUP, final_url)
											if parsed_final_url:
												#path에서 파일 이름 파싱
												if parsed_final_url.group('path'):
													path = parsed_final_url.group('path')
													file_name_regex_in_path = ur"[/](?P<apk_file_name>[\uAC00-\uD800\u3130-\u318F\w%()\[\]{}.-]+[.]apk$)"
													parsed_apk_file_name = self.PARSER.parseByRegexGroup(file_name_regex_in_path, path)
													#없을 시 query에서 파일 이름 파싱
													if not parsed_apk_file_name and parsed_final_url.group('query'):
														query = parsed_final_url.group('query')
														file_name_regex_in_query = ur"[=](?P<apk_file_name>[\uAC00-\uD800\u3130-\u318F\w%()\[\]{}.-]+[.]apk$)"
														parsed_apk_file_name = self.PARSER.parseByRegexGroup(file_name_regex_in_query, query)
										#파일 이름 결정
										if parsed_apk_file_name:
											apk_file_name = parsed_apk_file_name.group('apk_file_name')
										else:
											apk_file_name = 'unknown.apk'
											
										spread_info['apk_hash'] = apk_hash
										spread_info['apk_file_name'] = apk_file_name
										
										#final_ip, final_ipv6, final_country_code 확인
										final_ip, final_ipv6, final_country_code = self.getURLInfo(final_url)
										spread_info['final_url'] = final_url
										spread_info['final_ip'] = final_ip
										spread_info['final_ipv6'] = final_ipv6
										spread_info['final_country_code'] = final_country_code
												
										if referer:
											#mid_ip, mid_ipv6, mid_country_code 확인
											mid_ip, mid_ipv6, mid_country_code = self.getURLInfo(referer)
											spread_info['mid_url'] = referer
											spread_info['mid_ip'] = mid_ip
											spread_info['mid_ipv6'] = mid_ipv6
											spread_info['mid_country_code'] = mid_country_code
										
										self.saveAPK(apk_hash, raw_data)
										apk_flag = True
								else:
									self.putLog('info', self.LOG_HEAD+" - file is not apk")
									analysis_error = 'file is not apk'
									
							except Exception as e:
								self.putLog('warn', self.LOG_HEAD+" - not apk case: "+str(e))
								analysis_error = 'not apk case: '+str(e)
						else:
							self.putLog('debug', self.LOG_HEAD+" - file size is over 50MB")
							analysis_error = 'file size is over 50MB'
							
					except socket.timeout as e:
						analysis_error = 'get apk error: '+str(e)
				else:
					self.putLog('debug', self.LOG_HEAD+" - not apk case: not android or octet-stream content-type , not endswith .apk in url path")
					analysis_error = 'not apk case: not android or octet-stream content-type , not endswith .apk in url path'
			else:
				self.putLog('debug', self.LOG_HEAD+" - connection error")
					
			return (apk_flag, spread_info, connection_error, analysis_error)
		
		except Exception as e:
			_, _ , tb = sys.exc_info() # tb -> traceback object
			raise Exception(self.CLASS_NAME+'.'+str(sys._getframe().f_code.co_name)+' error(line No.: '+str(tb.tb_lineno)+'): '+str(e))
		
		
	def saveAPK(self, apk_hash, raw_data):
		try:
			if raw_data:
				#기존에 다운받은 파일인지 DB에서 확인
				query_check = ("""select id from apk_info where apk_hash=%s""")
				data_check = (apk_hash,)
				if self.checkFromDB(query_check, data_check):
					self.putLog('debug', self.LOG_HEAD+" - apk already downloaded:"+apk_hash)
				else:
					if self.TEST_FLAG:
						apk_path = APK_FILE_TEST_PATH
					else:
						apk_path = APK_FILE_TEMP_PATH
					#writeBinaryFile(file_name, data, path='')
					self.FILE_INTERFACE.writeBinaryFile(apk_hash, raw_data, apk_path)
					self.putLog('debug', self.LOG_HEAD+" - apk downloaded: "+apk_hash+".apk")
			
		except Exception as e:
			_, _ , tb = sys.exc_info() # tb -> traceback object
			raise Exception(self.CLASS_NAME+'.'+str(sys._getframe().f_code.co_name)+' error(line No.: '+str(tb.tb_lineno)+'): '+str(e))
			
			
	def getHTML(self, url, referer=None):
		try:
			connection_flag, response, connection_error = self.connectURL(url, referer)
			current_url = None
			html = None
			html_flag= False
			analysis_error = None
			
			if connection_flag and response and not connection_error:
				content_type = ''
				meta = response.info()
				if meta.getheaders("Content-Type"):
					content_type = meta.getheaders("Content-Type")[0]
				if content_type.find('html') != -1:
					current_url = response.geturl()
					try:
						raw_data = response.read()
						#unicode로 변환
						if raw_data:
							html = self.PARSER.convertToUnicode(raw_data)	
							html = self.compactHTML(html)
							html_flag = True
					
					except socket.timeout as e:
						analysis_error = 'get html error: '+str(e)
			
			return (current_url, html, html_flag, connection_error, analysis_error)
			
		except Exception as e:
			_, _ , tb = sys.exc_info() # tb -> traceback object
			raise Exception(self.CLASS_NAME+'.'+str(sys._getframe().f_code.co_name)+' error(line No.: '+str(tb.tb_lineno)+'): '+str(e))
		
		
	def saveHTML(self, url, raw_data):
		try:
			#접속한 url의 html 파일로 저장 -> 추후 분석 용도
			if raw_data:
				html = raw_data.encode('utf-8', 'ignore')
				query_check = ("""select url_hash, count_all from url_list where url=%s""")
				data_check = (url,)
				result_record = self.checkFromDB(query_check, data_check, get_result_flag=True, plural_flag=False)
				if result_record:
					url_hash, count_all = result_record
					if count_all > 10 or self.PARSER.parseByRegexGroup(self.PARSER.MPHONE_REGEX_GROUP, url):
						self.FILE_INTERFACE.writeTextFile(url_hash+'.html', html, HTML_FILE_PATH)
						self.putLog('debug', self.LOG_HEAD+" - html downloaded: "+url_hash+".html")
					
		except Exception as e:
			_, _ , tb = sys.exc_info() # tb -> traceback object
			raise Exception(self.CLASS_NAME+'.'+str(sys._getframe().f_code.co_name)+' error(line No.: '+str(tb.tb_lineno)+'): '+str(e))
	
	
	def connectURL(self, url, referer=None, no_redirect_flag=False, head_flag=False):
		try:
			https_flag = url.startswith('https')
			#https 접속
			if https_flag:
				opener = self.HTTP_INTERFACE.getOpener(https=https_flag, no_redirect=no_redirect_flag)
			#http 접속
			else:
				opener = self.HTTP_INTERFACE.getOpener(no_redirect=no_redirect_flag)
			
			headers = self.USER_AGENT_INFO[random.randint(0, self.USER_AGENT_COUNT-1)]
				
			request = self.HTTP_INTERFACE.getRequest(url, headers, head_flag)
			if referer:
				request.add_header('Referer', referer)
			
			#접속 시도
			connection_flag, response, connection_error = self.HTTP_INTERFACE.openURLHttp(opener, request)

			return (connection_flag, response, connection_error)

		except Exception as e:
			_, _ , tb = sys.exc_info() # tb -> traceback object
			raise Exception(self.CLASS_NAME+'.'+str(sys._getframe().f_code.co_name)+' error(line No.: '+str(tb.tb_lineno)+'): '+str(e))
	
	
	def getURLInfo(self, url):
		try:
			#ip, ipv6, country_code 확인
			ip = []
			ipv6 = []
			country_code = None
			parsed_url = self.PARSER.parseByRegexGroup(self.PARSER.URL_PARSING_REGEX_GROUP, url)
			scheme = parsed_url.group('scheme')
			hostdomain = parsed_url.group('hostdomain')
			port = parsed_url.group('port')
			if hostdomain:
				try:
					if port:
						addrinfo_list = socket.getaddrinfo(str(hostdomain), str(port))
					else:
						if scheme.find('https') != -1:
							addrinfo_list = socket.getaddrinfo(str(hostdomain), '443')
						else:
							addrinfo_list = socket.getaddrinfo(str(hostdomain), '80')
					for addrinfo in addrinfo_list:
						family, _, _, _, sockaddr = addrinfo
						if family == 2:
							ip.append(sockaddr[0])
						if family == 6:
							ipv6.append(sockaddr[0])
				
				except socket.error:
					dns_resolver = resolver.Resolver()
					dns_resolver.nameservers = ['8.8.8.8']
					dns_result = dns_resolver.query(hostdomain, 'A')
					for result in dns_result:
						ip.append(result)
			else:
				url_ip = parsed_url.group('url_ip')
				if url_ip:
					ip.append(url_ip)
				url_ipv6 = parsed_url.group('url_ipv6')
				if url_ipv6:
					url_ipv6 = url_ipv6[1:-1]
					ipv6.append(url_ipv6)
			if ip:
				geo_info = geolite2.lookup(str(ip[0]))
			elif ipv6:
				geo_info = geolite2.lookup(str(ipv6[0]))
			
			if geo_info:
				country_code = geo_info.country
			else:
				country_code = 'unknown'
				
			return (ip, ipv6, country_code)
			
		except Exception as e:
			_, _ , tb = sys.exc_info() # tb -> traceback object
			raise Exception(self.CLASS_NAME+'.'+str(sys._getframe().f_code.co_name)+' error(line No.: '+str(tb.tb_lineno)+'): '+str(e))
	
	
	def saveBaseURLInfo(self):
		try:
			ip, ipv6, country_code = self.getURLInfo(self.BASE_URL)
			self.WEBKIT_RESULT['ip'] = ip
			self.WEBKIT_RESULT['ipv6'] = ipv6
			self.WEBKIT_RESULT['country_code'] = country_code
			self.WEBKIT_RESULT['html'] = ''
		
		except Exception as e:
			_, _ , tb = sys.exc_info() # tb -> traceback object
			raise Exception(self.CLASS_NAME+'.'+str(sys._getframe().f_code.co_name)+' error(line No.: '+str(tb.tb_lineno)+'): '+str(e))

				
	def getLinkFromHTML(self, html, current_url, link_regex=''):
		try:
			link_list = []
			html_soup = BeautifulSoup(html, 'lxml')
			if html_soup:
				#a태그 href 속성에서 link 가져오기
				for href_contained_tag in html_soup.find_all(href=re.compile(link_regex)):
					link = href_contained_tag.get('href')
					if link not in link_list and link != current_url and link != self.BASE_URL:
						self.putLog('debug', self.LOG_HEAD+" - link from href: "+link)
						link_list.append(link)

				#http-equiv에서 link 가져오기
				for meta_tag in html_soup.find_all('meta'):
					meta_tag_http_equiv = meta_tag.get('http-equiv')
					meta_tag_content = meta_tag.get('content')
					if meta_tag_http_equiv and meta_tag_content:
						if meta_tag_http_equiv.lower() == 'refresh' and meta_tag_content.lower().find('url') != -1:
							if meta_tag_content.split('='):
								link = meta_tag_content.split('=')[1].strip()
								if self.PARSER.parseByRegex(link_regex, link):
									if link not in link_list and link != current_url and link != self.BASE_URL:
										self.putLog('debug', self.LOG_HEAD+" - link from http-equiv: "+link)
										link_list.append(link)
			
			#location.href, window.location에서 link 가져오기
			link_list_regex1 = self.PARSER.parseByRegex(self.PARSER.LINK_REGEX1_GROUP, html)
			if link_list_regex1:
				for link in link_list_regex1:
					if self.PARSER.parseByRegex(link_regex, link):
						if link not in link_list and link != current_url and link != self.BASE_URL:
							self.putLog('debug', self.LOG_HEAD+" - link from location.href or window.location: "+link)
							link_list.append(link)
						
			#location.replace(), location.assign()에서 link 가져오기
			link_list_regex2 = self.PARSER.parseByRegex(self.PARSER.LINK_REGEX2_GROUP, html)
			if link_list_regex2:
				for link in link_list_regex2:
					if self.PARSER.parseByRegex(link_regex, link):
						if link not in link_list and link != current_url and link != self.BASE_URL:
							self.putLog('debug', self.LOG_HEAD+" - link from location.replace() or location.assign(): "+link)
							link_list.append(link)
						
			if not link_list:
				self.putLog('info', self.LOG_HEAD+" - link not found with regex: "+str(link_regex))
				
			link_list_final = []
			for link in link_list:
				referer = self.WEBKIT_RESULT['land_url']
				link = self.parseLink(link, referer)
				if link:
					link_list_final.append(link)
					
			return link_list_final

		except Exception as e:
			_, _ , tb = sys.exc_info() # tb -> traceback object
			raise Exception(self.CLASS_NAME+'.'+str(sys._getframe().f_code.co_name)+' error(line No.: '+str(tb.tb_lineno)+'): '+str(e))
	
	
	def getLinkFromTag(self, html, pattern, current_url):
		try:
			link = None
			html_start = None
			start_pattern = pattern['start'][0]
			start_offset = pattern['start'][1]
			start_direction = pattern['start'][2]
			prepend = pattern['start'][3]
			end_pattern = pattern['end'][0]
			end_offset = pattern['end'][1]
			end_direction = pattern['end'][2]
			append = pattern['end'][3]
			
			if html:
				if start_direction == 'r':
					if html.rfind(start_pattern) != -1:
						start = html.rfind(start_pattern)
						html_start = html[start+start_offset:]
				else:
					if html.find(start_pattern) != -1:
						start = html.find(start_pattern)
						html_start = html[start+start_offset:]
				
				if html_start and end_direction == 'r':
					if html_start.rfind(end_pattern) != -1:
						end = html_start.rfind(end_pattern)
						link = html_start[:end+end_offset]
				elif html_start:
					if html_start.find(end_pattern) != -1:
						end = html_start.find(end_pattern)
						link = html_start[:end+end_offset]
						
				if link:
					link = prepend+link+append
					link = self.parseLink(link, current_url)
				else:
					link = current_url
				
			return link
			
		except Exception as e:
			_, _ , tb = sys.exc_info() # tb -> traceback object
			raise Exception(self.CLASS_NAME+'.'+str(sys._getframe().f_code.co_name)+' error(line No.: '+str(tb.tb_lineno)+'): '+str(e))

			
	def parseLink(self, link, referer, filter_extension=[]):
		try:
			#unicode로 변경
			link = self.PARSER.convertToUnicode(link)
			if referer:
				referer = self.PARSER.convertToUnicode(referer)
			#referer 확인
			self.putLog('debug', self.LOG_HEAD+" - referer: "+referer)
			parsed_referer = self.PARSER.parseByRegexGroup(self.PARSER.URL_PARSING_REGEX_GROUP, referer)
			if parsed_referer:
				referer_hostdomain = parsed_referer.group('hostdomain')
				referer_url_ip = parsed_referer.group('url_ip')
				referer_url_ipv6 = parsed_referer.group('url_ipv6')
				referer_port = parsed_referer.group('port')
				if referer_hostdomain:
					self.putLog('debug', self.LOG_HEAD+" - referer_hostdomain: "+referer_hostdomain)
				elif referer_url_ip:
					self.putLog('debug', self.LOG_HEAD+" - referer_url_ip: "+referer_url_ip)
				elif referer_url_ipv6:
					self.putLog('debug', self.LOG_HEAD+" - referer_url_ip: "+referer_url_ipv6)
				referer_scheme = parsed_referer.group('scheme')
				
				if referer_port:
					referer_part = referer_scheme+(referer_hostdomain or referer_url_ip or referer_url_ipv6)+':'+referer_port
				else:
					referer_part = referer_scheme+(referer_hostdomain or referer_url_ip or referer_url_ipv6)
				
			#link 형태
			#1. http(s)://hostdomain or ip or ipv6(:port(/path(?query)))
			#2.	hostdomain or ip(:port(/path(?query)))
			#3.	/path(?query)
			#4.	path(?query)
				
			#'/' 또는 './'로 시작하는 path 형태인 경우 (ex /abc/efg/... or ./abc/efg/)
			if link.startswith('/') or link.startswith('./') or link.startswith('../'):
				#3.	/path(?query)
				link = referer_part+link
			#그외 url 체크
			else:
				#scheme이 http(s)가 아닌 것 제외
				if link.find('://') != -1:
					end = link.find('://')
					scheme = link[:end]
					if end > 10:
						self.putLog('debug', self.LOG_HEAD+" - not http(s): "+scheme)
						link = None
				
				if link:
					parsed_link = self.PARSER.parseByRegexGroup(self.PARSER.URL_PARSING_REGEX_GROUP, link)
					if parsed_link:
						if parsed_link.group('scheme'):
							#1. http(s)://hostdomain or ip(/path(?query))
							self.putLog('debug', self.LOG_HEAD+" - link: "+link)
						else:
							link_hostdomain = parsed_link.group('hostdomain')
							link_url_ip = parsed_link.group('url_ip')
							link_url_ipv6 = parsed_link.group('url_ipv6')
							if link_hostdomain:
								extension_list = [
													'.asp', '.aspx', 
													'.jsp', '.do',
													'.php', '.php2', '.php3', '.php4', '.php5',
													'.html', '.xhtml', '.htm', '.xhtm',
													'.txt', '.exe', '.apk'
												]
								#link의 hostdomain이 extension으로 끝날 경우 => path(ex abc.html)
								for extension in extension_list:
									if link_hostdomain.endswith(extension):
										#4.	path(?query)
										self.putLog('debug', self.LOG_HEAD+" - link_hostdomain: "+referer_hostdomain)
										link = referer_part+'/'+link
										break
								else:
									#2.	hostdomain or ip(/path(?query))
									self.putLog('debug', self.LOG_HEAD+" - link_hostdomain: "+link_hostdomain)
									link = referer_scheme+link
							elif link_url_ip or link_url_ipv6:
								link = referer_scheme+link
					elif link.startswith('#') or link.startswith('javascript'):
						self.putLog('debug', self.LOG_HEAD+" - not url format[1]: "+link)
						link = None
					else:
						link = referer_part+'/'+link
							
			#url 형태 인지 최종 체크
			if link:
				parsed_link = self.PARSER.parseByRegexGroup(self.PARSER.URL_PARSING_REGEX_GROUP, link)
				if parsed_link:
					scheme = parsed_link.group('scheme')
					hostdomain = parsed_link.group('hostdomain')
					url_ip = parsed_link.group('url_ip')
					url_ipv6 = parsed_link.group('url_ipv6')
					port = parsed_link.group('port')
					path = parsed_link.group('path')
					query = parsed_link.group('query')
					fragment = parsed_link.group('fragment')
					
					#url인코딩
					if query:
						query = self.encodeURL(query)
					if fragment:
						fragment = self.encodeURL(fragment)
					if port:
						link = (scheme or '')+(hostdomain or url_ip or url_ipv6 or '')+':'+port+(path or '')+(query or '')+(fragment or '')
					else:
						link = (scheme or '')+(hostdomain or url_ip or url_ipv6 or '')+(path or '')+(query or '')+(fragment or '')
					self.putLog('debug', self.LOG_HEAD+" - url-encoded link: "+link)
					
					#화이트리스트 적용
					white_flag, message = self.WHITELIST.check(link)
					if white_flag:
						self.putLog('debug', self.LOG_HEAD+" - whitelist link found:"+link+" by "+message)
						link = None
					#필터 적용
					if filter_extension:
						link = self.filterLink(link, filter_extension)
				else:
					self.putLog('debug', self.LOG_HEAD+" - not url format[2]: "+link)
					link = None
				
			return link
					
		except Exception as e:
			_, _ , tb = sys.exc_info() # tb -> traceback object
			raise Exception(self.CLASS_NAME+'.'+str(sys._getframe().f_code.co_name)+' error(line No.: '+str(tb.tb_lineno)+'): '+str(e))
				
				
	def filterLink(self, link, filter_extension):
		try:
			parsed_link = self.PARSER.parseByRegexGroup(self.PARSER.URL_PARSING_REGEX_GROUP, link)
			path = parsed_link.group('path')
			if path:
				for extension in filter_extension:
					if path.endswith(extension):
						break
				else:
					link = None
			return link

		except Exception as e:
			_, _ , tb = sys.exc_info() # tb -> traceback object
			raise Exception(self.CLASS_NAME+'.'+str(sys._getframe().f_code.co_name)+' error(line No.: '+str(tb.tb_lineno)+'): '+str(e))
	
	
	def encodeURL(self, target):
		try:
			target = target.encode('utf-8')
			target = urllib.quote_plus(target)
			return target
			
		except Exception as e:
			_, _ , tb = sys.exc_info() # tb -> traceback object
			raise Exception(self.CLASS_NAME+'.'+str(sys._getframe().f_code.co_name)+' error(line No.: '+str(tb.tb_lineno)+'): '+str(e))

	
	def compactHTML(self, html):
		try:
			html = html.replace(" ","")
			html = html.replace("'+'","")
			html = html.replace('\\u003d','=')
			html = html.replace('\\u0026','&')
			
			return html
			
		except Exception as e:
			_, _ , tb = sys.exc_info() # tb -> traceback object
			raise Exception(self.CLASS_NAME+'.'+str(sys._getframe().f_code.co_name)+' error(line No.: '+str(tb.tb_lineno)+'): '+str(e))
			
	
	def checkBrowserUse(self, browser_url):
		try:
			_, html, html_flag, _ = self.checkURL(browser_url)
			if html:
				self.WEBKIT_RESULT['browser_use'] = 'yes'
				self.WEBKIT_RESULT['browser_url'] = browser_url
				self.putLog('info', self.LOG_HEAD+" - browser needed")
			else:
				self.putLog('info', self.LOG_HEAD+" - browser not needed")
		
		except Exception as e:
			_, _ , tb = sys.exc_info() # tb -> traceback object
			raise Exception(self.CLASS_NAME+'.'+str(sys._getframe().f_code.co_name)+' error(line No.: '+str(tb.tb_lineno)+'): '+str(e))
		
	
	#webkit 브라우저 기능
	def setWebDriver(self, browser_url):
		try:
			webdriver_flag = False
			current_url = None
			html = None
			apk_flag = None
			user_agent = self.USER_AGENT_INFO[random.randint(0, self.USER_AGENT_COUNT-1)]['User-Agent']
			if self.TEST_FLAG:
				apk_path = APK_FILE_TEST_PATH
			else:
				apk_path = APK_FILE_TEMP_PATH
			
			#apk 다운로드 임시 디렉토리 생성
			time_now = datetime.now()
			time_now_str = time_now.strftime('%Y%m%d%H%M%S')
			url_hash = md5.new(self.BASE_URL).hexdigest()
			temp_apk_path = os.path.join(apk_path, time_now_str+'_'+url_hash)
			#임시 디렉토리 생성 정보 저장
			self.TEMP_APK_PATH = temp_apk_path
			#기존에 생성된 임시 디렉토리 확인
			while True:
				#생성된지 1시간 이상된 임시 디렉토리 일괄 삭제
				file_list = self.FILE_INTERFACE.listFile(apk_path)
				for file_name in file_list:
					full_file_name = os.path.join(apk_path, file_name)
					if os.path.isdir(full_file_name):
						file_info = self.FILE_INTERFACE.stateFile(full_file_name)
						make_time = datetime.fromtimestamp(file_info.st_mtime)
						if time_now - make_time > timedelta(hours=1):
							self.FILE_INTERFACE.removeFile(full_file_name, recursive_flag=True)
				
				#신규 생성
				if not os.path.exists(temp_apk_path):
					os.mkdir(temp_apk_path)
					time.sleep(0.5)
				else:
					self.putLog('info', self.LOG_HEAD+" - temp_apk_path: "+temp_apk_path)
					break
			
			#파이어폭스 옵션 설정
			options = Options()
			#다른 이름으로 저장
			options.set_preference('browser.download.folderList',2)
			#확인 결과창 스킵
			options.set_preference('browser.download.manager.showWhenStarting', False)
			#다운로드 디렉토리 지정 -> 앞서 생성한 임시 디렉토리
			options.set_preference('browser.download.dir', temp_apk_path)
			#다운로드 대상 타입(MIME) 지정 -> 안드로이드 앱 관련으로만 다운로드
			options.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/octet-stream, application/vnd.android.package-archive')
			profile = webdriver.FirefoxProfile()
			#user-agent 모바일로 변경
			profile.set_preference("general.useragent.override", user_agent)

			#파이어폭스 드라이버 객체 생성, 페이지 로드 타임아웃 10초
			if self.WEBDRIVER:
				webdriver_flag = True
				self.putLog('info', self.LOG_HEAD+" - firefox browser started: "+str(browser_url))
			else:
				try:
					geckodriver_path = ''
					if self.PLATFORM.find('win') != -1:
						geckodriver_path = os.path.join(WEBKIT_PATH, 'geckodriver.exe')
						#백그라운드 실행
						if not self.TEST_FLAG:
							options.headless = True
					elif self.PLATFORM.find('linux') != -1:
						geckodriver_path = os.path.join(WEBKIT_PATH, 'geckodriver')
						#백그라운드 실행
						if not self.TEST_FLAG:
							display = Display(visible=0, size=(1024, 768))
							display.start()
					else:
						self.putLog('error', self.LOG_HEAD+" - not supported platform; window, linux only")
					
					if geckodriver_path and os.path.exists(geckodriver_path):
						self.WEBDRIVER = webdriver.Firefox(executable_path=geckodriver_path, firefox_profile=profile, options=options, log_path=os.path.devnull)
						self.WEBDRIVER.set_page_load_timeout(30)
						if self.WEBDRIVER:
							webdriver_flag = True

				except IOError as e:
					self.putLog('error', self.LOG_HEAD+" - failed to start firefox browser: "+str(e))
					self.FILE_INTERFACE.removeFile(temp_apk_path)
			
			current_url, html, apk_flag = self.checkURLbyBrowser(browser_url, temp_apk_path, wait=30)
				
			return (webdriver_flag, temp_apk_path, current_url, html, apk_flag)
		
		except Exception as e:
			_, _ , tb = sys.exc_info() # tb -> traceback object
			raise Exception(self.CLASS_NAME+'.'+str(sys._getframe().f_code.co_name)+' error(line No.: '+str(tb.tb_lineno)+'): '+str(e))
	
	
	def checkURLbyBrowser(self, url, temp_apk_path, wait=1, html_save=False):
		try:
			current_url, html = self.connectURLbyBrowser(url, wait)
			apk_flag, spread_info_list = self.getAPKbyBrowser(temp_apk_path, current_url, referer=url)
			self.WEBKIT_RESULT['current_url'] = current_url
			if apk_flag:
				self.WEBKIT_RESULT['spread_info_list'] += spread_info_list
			elif current_url and html and html_save:
				self.WEBKIT_RESULT['land_url'] = current_url
				self.WEBKIT_RESULT['html'] = html
			
			return (current_url, html, apk_flag)
		
		except Exception as e:
			_, _ , tb = sys.exc_info() # tb -> traceback object
			raise Exception(self.CLASS_NAME+'.'+str(sys._getframe().f_code.co_name)+' error(line No.: '+str(tb.tb_lineno)+'): '+str(e))
	
	
	def connectURLbyBrowser(self, url, wait):
		try:
			try:
				current_url = None
				html = None
				self.WEBDRIVER.get(url)
				self.setTimeForWaiting(wait)
				try:
					WebDriverWait(self.WEBDRIVER, 3).until(EC.alert_is_present(), 'alert popup') 
					alert = self.WEBDRIVER.switch_to.alert
					alert.accept()
				except TimeoutException:
					pass
				current_url = self.WEBDRIVER.current_url
				html = self.getHTMLbyBrowser()
				
			except TimeoutException:
				self.putLog('debug', self.LOG_HEAD+" - browser error: time out")
				current_url = url
			
			except WebDriverException as e:
				self.putLog('debug', self.LOG_HEAD+" - browser error: "+str(e)+", "+url)
				self.WEBKIT_RESULT['analysis_error'] = str(e)
				
			return (current_url, html)

		except Exception as e:
			_, _ , tb = sys.exc_info() # tb -> traceback object
			raise Exception(self.CLASS_NAME+'.'+str(sys._getframe().f_code.co_name)+' error(line No.: '+str(tb.tb_lineno)+'): '+str(e))
						
	
	def getAPKbyBrowser(self, temp_apk_path, final_url, referer=None):
		try:
			apk_flag = False
			spread_info_list = []
			if os.path.exists(temp_apk_path):
				spread_info = {
						'mid_url':'',
						'mid_ip':'',
						'mid_ipv6':'',
						'mid_country_code':'',
						'final_url':'',
						'final_ip':'',
						'final_ipv6':'',
						'final_country_code':'',
						'apk_hash':'',
						'apk_file_name':'',
						'datetime':str(datetime.now())
						}
				file_list = self.FILE_INTERFACE.listFile(temp_apk_path)
				if file_list:
					for file_name in file_list:
						#파일 다운로드 완료까지 기다림 3초 후 파일크기 비교
						download_time = 0
						download_time_limit = 60
						while True:
							#실제 데이터에서 파일 사이즈 확인
							raw_data = self.FILE_INTERFACE.readBinaryFile(file_name, temp_apk_path)
							temp_file_size = len(raw_data)
							if int(temp_file_size) >= 50000000:
								file_size = temp_file_size
								break
							time.sleep(3)
							download_time += 3
							raw_data = self.FILE_INTERFACE.readBinaryFile(file_name, temp_apk_path)
							file_size = len(raw_data)
							if temp_file_size == file_size:
								break
							
							if download_time >= download_time_limit:
								break
					
						#파일 사이즈 50MB 미만, 파일 유형이 apk인 것만 저장
						if int(file_size) < 50000000:
							try:
								apk = APK(raw_data, raw=True)
								if apk.is_valid_APK():
									apk_hash = md5.new(raw_data).hexdigest()
									white_flag, message = self.WHITELIST.check(apk_hash=apk_hash)
									if white_flag:
										self.putLog('debug', self.LOG_HEAD+" - whitelist apk_hash found:"+apk_hash+" by "+message)
									else:
										#파일 이름 결정
										apk_file_name = self.PARSER.convertToUnicode(file_name)
											
										spread_info['apk_hash'] = apk_hash
										spread_info['apk_file_name'] = apk_file_name
										
										#final_ip, final_ipv6, final_country_code 확인
										final_ip, final_ipv6, final_country_code = self.getURLInfo(final_url)
										spread_info['final_url'] = final_url
										spread_info['final_ip'] = final_ip
										spread_info['final_ipv6'] = final_ipv6
										spread_info['final_country_code'] = final_country_code	
												
										if referer:
											#mid_ip, mid_ipv6, mid_country_code 확인
											mid_ip, mid_ipv6, mid_country_code = self.getURLInfo(referer)
											spread_info['mid_url'] = referer
											spread_info['mid_ip'] = mid_ip
											spread_info['mid_ipv6'] = mid_ipv6
											spread_info['mid_country_code'] = mid_country_code
										
										spread_info_list.append(spread_info)
										self.saveAPKbyBrowser(apk_hash, raw_data, file_name, temp_apk_path)
										apk_flag = True
								else:
									self.putLog('info', self.LOG_HEAD+" - file is not apk")
									
							except Exception as e:
								self.putLog('warn', self.LOG_HEAD+" - not apk: "+str(e))
						else:
							self.putLog('debug', self.LOG_HEAD+" - file size is over 50MB")
				else:
					self.putLog('debug', self.LOG_HEAD+" - empty temp_apk_path directory; apk not downloaded")
			else:
				self.putLog('debug', self.LOG_HEAD+" - temp_apk_path directory not exists; apk not downloaded")
				
			return (apk_flag, spread_info_list)
									
		except Exception as e:
			_, _ , tb = sys.exc_info() # tb -> traceback object
			raise Exception(self.CLASS_NAME+'.'+str(sys._getframe().f_code.co_name)+' error(line No.: '+str(tb.tb_lineno)+'): '+str(e))
	
	
	def saveAPKbyBrowser(self, apk_hash, raw_data, file_name, temp_apk_path):
		try:
			if raw_data:
				#기존에 다운받은 파일인지 DB에서 확인
				query_check = ("""select id from apk_info where apk_hash=%s""")
				data_check = (apk_hash,)
				if self.checkFromDB(query_check, data_check):
					self.putLog('debug', self.LOG_HEAD+" - apk already downloaded:"+apk_hash)
				else:
					if self.TEST_FLAG:
						apk_path = APK_FILE_TEST_PATH
					else:
						apk_path = APK_FILE_TEMP_PATH
					src = os.path.join(temp_apk_path, file_name)
					dst = os.path.join(apk_path, apk_hash)
					#writeBinaryFile(file_name, data, path='')
					self.FILE_INTERFACE.moveFile(src, dst)
					self.putLog('debug', self.LOG_HEAD+" - apk downloaded: "+apk_hash+".apk")
					
		except Exception as e:
			_, _ , tb = sys.exc_info() # tb -> traceback object
			raise Exception(self.CLASS_NAME+'.'+str(sys._getframe().f_code.co_name)+' error(line No.: '+str(tb.tb_lineno)+'): '+str(e))
	
	
	def getHTMLbyBrowser(self):
		try:
			html = None
			try:
				html = self.WEBDRIVER.page_source
				if html:
					html = self.PARSER.convertToUnicode(html)
					html = self.compactHTML(html)
					
			except WebDriverException as e:
				self.putLog('debug', self.LOG_HEAD+" - get html error, by browser: "+str(e))
				self.WEBKIT_RESULT['analysis_error'] = 'get html error, by browser: '+str(e)
			
			return html
		
		except Exception as e:
			_, _ , tb = sys.exc_info() # tb -> traceback object
			raise Exception(self.CLASS_NAME+'.'+str(sys._getframe().f_code.co_name)+' error(line No.: '+str(tb.tb_lineno)+'): '+str(e))
			
	
	def findHTMLElements(self, target, type='id'):
		try:
			self.WEBDRIVER.implicitly_wait(3)
			if type == 'id':
				#type = By.ID
				html_element = self.WEBDRIVER.find_element_by_id(target)
			elif type == 'tag':
				#type = By.TAG_NAME
				html_element = self.WEBDRIVER.find_elements_by_tag_name(target)
			elif type == 'class':
				#type = By.CLASS_NAME
				html_element = self.WEBDRIVER.find_elements_by_class_name(target)
			elif type == 'name':
				#type = By.NAME
				html_element = self.WEBDRIVER.find_elements_by_name(target)
			elif type == 'css':
				#type = By.CSS_SELECTOR
				html_element = self.WEBDRIVER.find_elements_by_css_selector(target)
			elif type == 'xpath':
				#type = By.XPATH
				html_element = self.WEBDRIVER.find_elements_by_xpath(target)
			#html_element = WebDriverWait(self.WEBDRIVER, 5).until(EC.presence_of_all_elements_located((type, target)))
			
			return html_element
			
		except TimeoutException:
			self.putLog('debug', self.LOG_HEAD+" - html element not found until timeout")
			return None
		
		except NoSuchElementException:
			return None
		
		except Exception as e:
			_, _ , tb = sys.exc_info() # tb -> traceback object
			raise Exception(self.CLASS_NAME+'.'+str(sys._getframe().f_code.co_name)+' error(line No.: '+str(tb.tb_lineno)+'): '+str(e))	
		

	def click(self, temp_apk_path, target, type='css', wait=1, html_save=False):
		try:
			current_url = None
			html = None
			apk_flag = False
			html_element = self.findHTMLElements(target, type)
			if html_element:
				if type == 'id':
					count = 1
					html_element = [html_element]
				else:
					count = len(html_element)
				for idx in range(count):
					try:
						referer = self.WEBDRIVER.current_url
						try:
							html_element[idx].click()
						
						except WebDriverException:
							self.WEBDRIVER.execute_script("arguments[0].click();", html_element[idx])
						
						self.setTimeForWaiting(wait)
						current_url = self.WEBDRIVER.current_url
						html = self.getHTMLbyBrowser()
						apk_flag, spread_info_list = self.getAPKbyBrowser(temp_apk_path, current_url, referer)
						if apk_flag:
							self.WEBKIT_RESULT['spread_info_list'] = spread_info_list
							break
						elif current_url and html:
							if html_save:
								self.WEBKIT_RESULT['current_url'] = current_url
								self.WEBKIT_RESULT['land_url'] = current_url
								self.WEBKIT_RESULT['html'] = html
							break
								
					except StaleElementReferenceException:
						self.putLog('debug', 'element stale')
						
					except UnexpectedAlertPresentException:
						try:
							WebDriverWait(self.WEBDRIVER, 3).until(EC.alert_is_present(), 'alert popup') 
							alert = self.WEBDRIVER.switch_to.alert
							alert.accept()
						except TimeoutException:
							self.putLog('debug', 'alert timeout')
						
					except WebDriverException as e:
						self.putLog('debug', self.LOG_HEAD+" - browser error: "+str(e)+", "+url)
						self.WEBKIT_RESULT['analysis_error'] = str(e)
			else:
				self.putLog('debug', self.LOG_HEAD+" - html element not found by: "+type+", "+target)
				
			return (current_url, html, apk_flag)
		
		except Exception as e:
			_, _ , tb = sys.exc_info() # tb -> traceback object
			raise Exception(self.CLASS_NAME+'.'+str(sys._getframe().f_code.co_name)+' error(line No.: '+str(tb.tb_lineno)+'): '+str(e))
			
			
	def setValue(self, value, target, type='css'):
		try:
			html_element = self.findHTMLElements(target, type)
			if html_element:
				if type == 'id':
					count = 1
					html_element = [html_element]
				else:
					count = len(html_element)
				for idx in range(count):
					html_element[idx].clear()
					html_element[idx].send_keys(value)
			else:
				self.putLog('debug', self.LOG_HEAD+" - html element not found by: "+type+", "+target)
			
		except Exception as e:
			_, _ , tb = sys.exc_info() # tb -> traceback object
			raise Exception(self.CLASS_NAME+'.'+str(sys._getframe().f_code.co_name)+' error(line No.: '+str(tb.tb_lineno)+'): '+str(e))
	
	
	def setTimeForWaiting(self, seconds):
		try:
			self.WEBDRIVER.implicitly_wait(seconds)
		
		except Exception as e:
			_, _ , tb = sys.exc_info() # tb -> traceback object
			raise Exception(self.CLASS_NAME+'.'+str(sys._getframe().f_code.co_name)+' error(line No.: '+str(tb.tb_lineno)+'): '+str(e))

		
	def runAction(self, temp_apk_path, action_list, browser_url=None):
		try:
			current_url = None
			html = None
			apk_flag = False
			for action in action_list:
				#action = (id, type, target, target_type, wait, current_url, save, value)
				id = action[0]
				type = action[1]
				target = action[2]
				target_type = action[3]
				wait = action[4]
				if action[5]:
					current_url = action[5]
				save = action[6]
				value = action[7]
				
				self.putLog('debug', self.LOG_HEAD+" - action id: "+str(id))
				#사용 필드: type, current_url
				if type == 'initSet':
					self.putLog('debug', self.LOG_HEAD+" - action: "+type+", "+current_url+" and html")
					html = value
				#사용 필드: type, target, target_type, wait, save
				elif type == 'click':
					self.putLog('debug', self.LOG_HEAD+" - action: "+type+", "+target)
					current_url, html, apk_flag = self.click(temp_apk_path, target, target_type, wait, save)
				#사용 필드: type, target, target_type, value
				elif type == 'setValue':
					self.putLog('debug', self.LOG_HEAD+" - action: "+type+", "+target+", "+value)
					self.setValue(value, target, target_type)
				#사용 필드: type, wait, current_url, save
				elif type == 'checkURLbyBrowser':
					self.putLog('debug', self.LOG_HEAD+" - action: "+type+", "+current_url)
					current_url, html, apk_flag = self.checkURLbyBrowser(current_url, temp_apk_path, wait, save)
				#사용 필드: type, target, target_type, value
				elif type == 'checkCondition':
					self.putLog('debug', self.LOG_HEAD+" - action: "+type+", "+target_type)
					if target:
						text = target
					elif target_type == 'html':
						text = html
					elif target_type == 'current_url':
						text = current_url
					if text:
						result = self.PARSER.checkByRegex(value, text)
						if result:
							self.putLog('debug', self.LOG_HEAD+" - result: "+result)
						else:
							break
					else:
						break
				#사용 필드: type, target, target_type, current_url, save, value
				elif type == 'getLinkFromTag':
					self.putLog('debug', self.LOG_HEAD+" - action: "+type+", "+str(target_type))
					if target:
						html = target
					link = self.getLinkFromTag(html, target_type, current_url)
					if link:
						self.putLog('debug', self.LOG_HEAD+" - found link: "+link)
						if save and link not in value:
							self.insertIntoURLLIST(link, current_url)
						current_url = link
					else:
						current_url = None
						html = None
						self.putLog('debug', self.LOG_HEAD+" - link not found")
						break
				
				#type이 'click', 'checkURLbyBrowser' 경우 결과 체크
				if type in ['click', 'checkURLbyBrowser']:
					if current_url and html and not apk_flag:
						pass
					else:
						break
						
			return (current_url, html, apk_flag)
		
		except Exception as e:
			_, _ , tb = sys.exc_info() # tb -> traceback object
			raise Exception(self.CLASS_NAME+'.'+str(sys._getframe().f_code.co_name)+' error(line No.: '+str(tb.tb_lineno)+'): '+str(e))
	
	
	def checkExceptionCase(self):
		try:
			exception_flag = False
			current_url = self.WEBKIT_RESULT['current_url']
			spread_info_list = self.WEBKIT_RESULT['spread_info_list']
			if current_url.find('cl.ly') != -1:
				for spread_info in spread_info_list:
					final_url = spread_info['final_url']
					if final_url.find('s3.amazonaws.com') == -1:
						self.WEBKIT_RESULT['apk_download_flag'] = False
						self.WEBKIT_RESULT['spread_info_list'] = []
						exception_flag = True
						break
						
			return exception_flag
		
		except Exception as e:
			_, _ , tb = sys.exc_info() # tb -> traceback object
			raise Exception(self.CLASS_NAME+'.'+str(sys._getframe().f_code.co_name)+' error(line No.: '+str(tb.tb_lineno)+'): '+str(e))
				
	
	def closeBrowser(self):
		try:
			self.WEBDRIVER.quit()
			if self.TEMP_APK_PATH:
				if os.path.exists(self.TEMP_APK_PATH):
					self.FILE_INTERFACE.removeFile(self.TEMP_APK_PATH, recursive_flag=True)
			
		except Exception as e:
			_, _ , tb = sys.exc_info() # tb -> traceback object
			raise Exception(self.CLASS_NAME+'.'+str(sys._getframe().f_code.co_name)+' error(line No.: '+str(tb.tb_lineno)+'): '+str(e))
