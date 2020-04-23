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

##################################################################
## 코드 구성 및 구조 ##

#파이썬 모듈 import#

#경로 설정(절대경로)#

#server_base 모듈 import#

#기타 설정#

#class 클래스이름(server_base.ServerBase)
	#def __init__(self, hostname, num, worker_name, threading, queue, init_flag, db_config, config)
	#def inputWorker(self, num, init_flag)
	#def mainWorker(self, num, init_flag)
	#def outputWorker(self, num, init_flag)

#프로세스(워커) 종류 및 역할#
#1. 입력(inputWorker): 데이터 입력
#2. 메인(mainWorker): 데이터 처리 로직
#3. 출력(outputWorker): 처리 결과 출력
##################################################################

#analyze_url#

#파이썬 모듈 import#
import sys, os
import time
import json
import importlib
import md5
import Queue
from datetime import datetime

#경로 설정(절대경로)#
HOME_PATH = os.getcwd()
WEBKIT_PATH = os.path.join(HOME_PATH, 'server', 'analyze', 'url', 'webkit')

#server_base 모듈 import#
sys.path.append(HOME_PATH)
from server import server_base #ServerBase

#기타 설정#

class AnalyzerURL(server_base.ServerBase):

	def __init__(self, hostname, num, worker_name, threading, queue, init_flag, db_config, config):
		super(AnalyzerURL, self).__init__(hostname, num, __name__, self.__class__.__name__, worker_name, threading, queue, init_flag, db_config, config)
			
			
	#입력
	def inputWorker(self, num, init_flag):
		try:
			#inputWorker 처리 로직#
			##1. DB 연결
			##2. 처음 시작 시에 url_list 테이블에서 worker_id 초기화 및 url_analysis_flag 업데이트 'P' -> 'N'
			##3. url_list 테이블에 worker_id 등록(최대 10개) => 중복 분석 방지
			##4. url_list 테이블에서 url 가져오기
			##5. 기분석 여부 확인
			##6. input queue에 url 입력
			##7. url_analysis_flag 업데이트 'N' -> 'P' 또는 'Y'
			
			#로그 헤더
			worker_thread_num, inputWorker_log_head = self.getWorkerThreadNum('input', self.THREADING_INPUT, num)
			init_wait_time = self.waitInitInterval(self.INTERVAL_TIME_INPUT, worker_thread_num, inputWorker_log_head)
			self.putLog('info', inputWorker_log_head+" - started")
			
			##1. DB 연결
			mysql_conn, mysql_cur = self.startDB(self.THREADING_INPUT, inputWorker_log_head)
			
			##2. 처음 시작 시에 url_list 테이블에서 worker_id 초기화 및 url_analysis_flag 업데이트 'P' -> 'N'
			worker_id = self.HOSTNAME+':'+inputWorker_log_head
			if init_flag:
				while True:
					try:
						token = self.TOKEN_QUEUE.get_nowait()#초기 token['token_value']은 True
						if token['token_value']:
							self.putLog('info', inputWorker_log_head+" - set url_analysis_flag='P'->'N' for init")
							query_update = ("""update url_list set url_analysis_flag='N', worker_id='none' 
												where worker_id like %s and url_analysis_flag='P'""")
							data_update = ('%'+self.HOSTNAME+'%',)
							self.MYSQL_DB_INTERFACE.executeQuery(mysql_cur, query_update, data_update)
							self.MYSQL_DB_INTERFACE.commitQuery(mysql_conn)
							self.putLog('info', inputWorker_log_head+" - init query committed")
							token['token_value'] = False
						else:
							self.putLog('info', inputWorker_log_head+" - init already set")
						self.TOKEN_QUEUE.put_nowait(token)
						break
					except Queue.Empty:
						pass
						
			##3. url_list 테이블에 worker_id 등록(최대 10개) => 중복 분석 방지, 분석이 끝나지 않고 2시간 이상 지난 대상 포함
			self.putLog('debug', inputWorker_log_head+" - update url_list table with worker_id")
			#update 쿼리 및 실행
			query_update = ("""update url_list set worker_id=%s, url_analysis_flag='N'
								where 
								(url_analysis_flag='N' and worker_id='none')
								or (url_analysis_flag='P' and analysis_end_time is null
									and TIMESTAMPDIFF(HOUR, analysis_start_time, NOW()) > 2)
								limit 10""")
			data_update = (worker_id,)
			self.MYSQL_DB_INTERFACE.executeQuery(mysql_cur, query_update, data_update)
			self.MYSQL_DB_INTERFACE.commitQuery(mysql_conn)
			self.putLog('debug', inputWorker_log_head+" - query committed")
			
			##4. url_list 테이블에서 url 가져오기
			#select 쿼리 및 실행
			query_select = ("""select url from url_list where worker_id=%s and url_analysis_flag='N'""")
			data_select = (worker_id,)
			mysql_cur_result = self.MYSQL_DB_INTERFACE.executeQuery(mysql_cur, query_select, data_select)
			
			if mysql_cur_result.rowcount:
				self.putLog('info', inputWorker_log_head+" - got url_list")
				url_list = mysql_cur_result.fetchall() #info = [(url,), ...]
				
				self.putLog('debug', inputWorker_log_head+" - new url_list: "+str(url_list))
				self.putLog('debug', inputWorker_log_head+" - new url count: "+str(len(url_list)))
				
				for url in url_list:
					url = url[0]
					
					##5. 기분석 여부 확인
					#select 쿼리 및 실행
					query_select = ("""select id from url_info where url=%s""")
					data_select = (url,)
					mysql_cur_result = self.MYSQL_DB_INTERFACE.executeQuery(mysql_cur, query_select, data_select)
					if mysql_cur_result.rowcount:
						self.putLog('info', inputWorker_log_head+" - url already analyzed: "+url)
						url_analysis_flag = 'Y'
					else:
						##6. input queue에 url 입력
						self.INPUT_QUEUE.put_nowait(url)
						url_analysis_flag = 'P'
					##7. url_analysis_flag 업데이트 'N' -> 'P' 또는 'Y'로 업데이트
					#update 쿼리 및 실행
					analysis_start_time = datetime.now()
					query_update = ("""update url_list set analysis_start_time=%s, url_analysis_flag=%s
										where worker_id=%s and url_analysis_flag='N' and url=%s""")
					data_update = (analysis_start_time, url_analysis_flag, worker_id, url)
					self.MYSQL_DB_INTERFACE.executeQuery(mysql_cur, query_update, data_update)
			else:
				self.putLog('info', inputWorker_log_head+" - new url not found in url_list")
				
			self.MYSQL_DB_INTERFACE.commitQuery(mysql_conn)
			self.putLog('debug', inputWorker_log_head+" - query committed")
			self.endDB(mysql_conn, mysql_cur)
			self.putLog('info', inputWorker_log_head+" - ended")
		
		except Exception as e:
			_, _ , tb = sys.exc_info() # tb -> traceback object
			self.putLog('error', inputWorker_log_head+" - error line No: "+str(tb.tb_lineno)+"; "+str(e))
			
		finally:
			queue_size = self.INPUT_QUEUE.qsize()
			self.putLog('info', inputWorker_log_head+" - remained input queue count: "+str(queue_size))
			self.waitFinalInterval(self.INTERVAL_TIME_INPUT, init_wait_time, inputWorker_log_head, queue_size)

			
	#메인
	def mainWorker(self, num, init_flag):
		try:
			#mainWorker 처리 로직#
			##1. input queue에서 url 확인
			##2. webkit(webkit_XXX.py) 선택 후 url 접속 및 앱 다운로드 시도
			##3. output queue에 result 입력
			
			
			#로그 헤더
			worker_thread_num, mainWorker_log_head = self.getWorkerThreadNum('main', self.THREADING_MAIN, num)
			init_wait_time = self.waitInitInterval(self.INTERVAL_TIME_MAIN, worker_thread_num, mainWorker_log_head)
			self.putLog('info', mainWorker_log_head+" - started")
			
			#input queue 채우기 기다림
			if init_flag and not str(num) == 'default':
				self.putLog('info', mainWorker_log_head+" - init, waiting for input queue filled")
				time.sleep(1)

			try:
				#result={
				#			'webkit_name':'', 
				#			'url':'', 'ip':'', 'ipv6':'', 'country_code':'', 'html':'',
				#			'spread_info_list':[{
				#							'mid_url':'', 'mid_ip':'', 'mid_ipv6':'', 'mid_country_code':'', 
				#							'final_url':'', 'final_ip':'', 'final_ipv6':'', 'final_country_code':'', 
				#							'apk_hash':'', 'apk_file_name':'', 'datetime':datetime
				#							}, 
				#							...]
				#			'connection_flag':boolean, 'connection_error':'', 'last_conn_time':datetime, 
				#			'apk_download_flag':boolean, 'analysis_error':''
				#		}
				result = {}

				url = self.INPUT_QUEUE.get_nowait()
				
				##1. input queue에서 url 확인
				if url:
					url_hash = md5.new(url).hexdigest()
					self.putLog('info', mainWorker_log_head+" - url: "+url+", url_hash: "+url_hash)
					mainWorker_log_head_url_hash = mainWorker_log_head+"("+url_hash+")"
					
					##2. webkit(webkit_XXX.py) 선택 후 url 접속 및 앱 다운로드 시도
					self.putLog('info', mainWorker_log_head_url_hash+" - search for the webkit to apply")
					condition_part, webkit_list = self.getConditionAndSubFunction('webkit')
					webkit_result = None
					
					#webkit 실행 조건 체크
					for webkit in webkit_list:
						#초기화 webkit_flag = True
						webkit_flag = True
						webkit_name = webkit['name']
						self.putLog('debug', mainWorker_log_head_url_hash+" - try webkit "+webkit_name)
						webkit_class = self.checkConditionForSubFunction(webkit, webkit_flag, condition_part, url, mainWorker_log_head_url_hash)
							
						if webkit_class:
							if webkit_result:
								webkit_class.setLastResult(webkit_result)
							
							webkit_result = webkit_class.start()
							connection_flag = webkit_result['connection_flag']
							apk_download_flag = webkit_result['apk_download_flag']
							analysis_error = webkit_result['analysis_error']

							#webkit url 분석 결과
							if not analysis_error:
								#url 접속 체크
								if connection_flag:
									#apk 다운로드 체크
									if apk_download_flag:
										self.putLog('info', mainWorker_log_head_url_hash+" - "+webkit_name+" apk file downloaded")
										break
									else:
										self.putLog('debug', mainWorker_log_head_url_hash+" - try other webkit: apk file not downloaded")
										#앞의 webkit 결과로 condition_part 업데이트 => 다른 webkit 사용을 위한 정보
										condition_part = webkit_class.updateConditionPart(condition_part, webkit_result)
										self.putLog('debug', mainWorker_log_head_url_hash+" - updated condition_part")
										continue
								else:
									self.putLog('debug', mainWorker_log_head_url_hash+" - url connection failed")
									break
							#webkit 에러 발생 시
							else:
								self.putLog('warn', mainWorker_log_head_url_hash+" - "+webkit_name+" analysis error occurred")
								break
						else:
							self.putLog('debug', mainWorker_log_head_url_hash+" - not applicable "+webkit_name)
								
					#webkit 적용 없을 시 webkit_config 파일 문제
					if not webkit_name:
						raise Exception(mainWorker_log_head_url_hash+" - webkit not applied: webkit_config check!!")
				
					##3. output queue에 result 입력
					if webkit_result:
						self.OUTPUT_QUEUE.put_nowait(webkit_result)
					
			except Queue.Empty:
				self.putLog('info', mainWorker_log_head+" - empty input queue")
				
			self.putLog('info', mainWorker_log_head+" - ended")
			
		except Exception as e:
			_, _ , tb = sys.exc_info() # tb -> traceback object
			self.putLog('error', mainWorker_log_head+" - error line No: "+str(tb.tb_lineno)+"; "+str(e))
		
		finally:
			queue_size = self.OUTPUT_QUEUE.qsize()
			self.putLog('info', mainWorker_log_head+" - remained output queue count: "+str(queue_size))
			self.waitFinalInterval(self.INTERVAL_TIME_MAIN, init_wait_time, mainWorker_log_head, queue_size)
			

	#출력
	def outputWorker(self, num, init_flag):
		try:
			#outputWorker 처리 로직#
			##1. output queue에서 result 확인
			##2. DB 연결
			##3. DB 1차 쿼리, 테이블명: url_list
			##4. DB 2차 쿼리, 테이블명: url_info
			##5. DB 3차 쿼리를 위한 정보 조회, 테이블명: url_info
			##6. DB 3차 쿼리, 테이블명: url_info, static_analysis_info
			##7. DB commit
			##8. 앱 다운로드 시에 result_queue에 입력
			
			#로그 헤더
			worker_thread_num, outputWorker_log_head = self.getWorkerThreadNum('output', self.THREADING_OUTPUT, num)
			init_wait_time = self.waitInitInterval(self.INTERVAL_TIME_OUTPUT, worker_thread_num, outputWorker_log_head)
			self.putLog('info', outputWorker_log_head+" - started")
			
			#output queue 채우기 기다림
			if init_flag and not str(num) == 'default':
				self.putLog('info', outputWorker_log_head+" - init, waiting for output queue filled")
				time.sleep(3)

			try:
				result = self.OUTPUT_QUEUE.get_nowait()
				if self.DB_RO_MODE:
					self.putLog('warn', outputWorker_log_head+" - db read only, print result")
					self.putLog('info', outputWorker_log_head+" - result: "+str(result))
					url = result['url']
					#update 쿼리 및 실행
					mysql_conn, mysql_cur = self.startDB(self.THREADING_OUTPUT, outputWorker_log_head)
					query_update = ("""update url_list set url_analysis_flag='N', worker_id='none'
										where url=%s""")
					data_update = (url,)
					self.MYSQL_DB_INTERFACE.executeQuery(mysql_cur, query_update, data_update)
					self.MYSQL_DB_INTERFACE.commitQuery(mysql_conn)
					self.putLog('info', outputWorker_log_head+" - query committed")
					self.endDB(mysql_conn, mysql_cur)
					result = None
				
				##1. output queue에서 result 확인
				if result:
					self.putLog('info', outputWorker_log_head+" - got a result")
					webkit_name = result['webkit_name']
					url = result['url']
					ip = result['ip']
					ipv6 = result['ipv6']
					country_code = result['country_code']
					spread_info_list = result['spread_info_list']
					connection_flag = result['connection_flag']
					connection_error = result['connection_error']
					last_conn_time = result['last_conn_time']
					apk_download_flag = result['apk_download_flag']
					analysis_error = result['analysis_error']

					#DB에 데이터 업데이트 시간 저장
					time_now = datetime.now()
					
					##2. DB 연결
					mysql_conn, mysql_cur = self.startDB(self.THREADING_OUTPUT, outputWorker_log_head)

					url_hash = md5.new(url).hexdigest()
					self.putLog('info', outputWorker_log_head+" - url: "+url+", url_hash: "+url_hash)
					outputWorker_log_head_url_hash = outputWorker_log_head+"("+url_hash+")"
					
					self.putLog('info', outputWorker_log_head_url_hash+" - DB query start")
					
					##3. DB 1차 쿼리, 테이블명: url_list
					self.putLog('debug', outputWorker_log_head_url_hash+" - check if url_list table has the url: select")
					#select 쿼리 및 실행
					query_select = ("""select id from url_list where url=%s""")
					data_select = (url,)
					mysql_cur_result = self.MYSQL_DB_INTERFACE.executeQuery(mysql_cur, query_select, data_select)
					
					#조회 결과 있으면 update
					if mysql_cur_result.rowcount:
						self.putLog('debug', outputWorker_log_head_url_hash+" - found in url_list table: update")
						record = mysql_cur_result.fetchone()
						id = record[0]

						if connection_flag:
							connection_flag = 'Y'
						else:
							connection_flag = 'N'
							
						if apk_download_flag:
							apk_download_flag = 'Y'
						else:
							apk_download_flag = 'N'
							
						if analysis_error:
							url_analysis_flag = 'E'
						else:
							url_analysis_flag = 'Y'
						#update 쿼리 및 실행
						query_update = ("""update url_list set 
											connection_flag=%s, connection_error=%s, last_conn_time=%s,
											url_analysis_flag=%s, apk_download_flag=%s,
											analysis_end_time=%s,
											analysis_error=%s, worker_id='none'
											where url=%s""")
						data_update = (connection_flag, connection_error, last_conn_time, url_analysis_flag, apk_download_flag, time_now, analysis_error, url)
						self.MYSQL_DB_INTERFACE.executeQuery(mysql_cur, query_update, data_update)
					#조회 결과 없으면 안됨
					else:
						raise Exception(outputWorker_log_head_url_hash+" - not found in url_list, check log!")
					
					#apk 다운로드할 경우
					if apk_download_flag == 'Y':
						##4. DB 2차 쿼리, 테이블명: url_info
						self.putLog('debug', outputWorker_log_head_url_hash+" - check if url_info table has the url: select")
						#select 쿼리 및 실행
						query_select = ("""select id from url_info where url=%s""")
						data_select = (url,)
						mysql_cur_result = self.MYSQL_DB_INTERFACE.executeQuery(mysql_cur, query_select, data_select)
						#조회 결과 없으면 insert
						if not mysql_cur_result.rowcount:
							self.putLog('debug', outputWorker_log_head_url_hash+" - not found in url_info table: insert")
							
							ip_json = json.dumps(ip, ensure_ascii=False, encoding='utf-8')
							ipv6_json = json.dumps(ipv6, ensure_ascii=False, encoding='utf-8')
							spread_info_json = json.dumps(spread_info_list, ensure_ascii=False, encoding='utf-8')
							
							query_insert = ("""insert into url_info(
													url, ip, ipv6, country_code, 
													spread_info, webkit_name, last_update)
												values(
													%s, %s, %s, %s, 
													%s, %s, %s)""")
							data_insert = (url, ip_json, ipv6_json, country_code, spread_info_json, webkit_name, time_now)
							self.MYSQL_DB_INTERFACE.executeQuery(mysql_cur, query_insert, data_insert)
						#조회 결과 있으면 안됨
						else:
							raise Exception(outputWorker_log_head_url_hash+" - found in url_info; already analyzed: check log!")
							
						##5. DB 3차 쿼리를 위한 정보 조회, 테이블명: url_info
						mysql_cur_result = self.MYSQL_DB_INTERFACE.executeQuery(mysql_cur, query_select, data_select)
						if not mysql_cur_result.rowcount:
							raise Exception(outputWorker_log_head_url_hash+" - not found in url_info table(after insert): quit")
						else:
							record = mysql_cur_result.fetchone()
							url_info_id = record[0]
						
						for spread_info in spread_info_list:
							mid_url = spread_info['mid_url']
							final_url = spread_info['final_url']
							apk_hash = spread_info['apk_hash']
							
							static_info_hash = md5.new(url+mid_url+final_url+apk_hash).hexdigest()
							self.putLog('info', outputWorker_log_head_url_hash+" - static_info_hash: "+static_info_hash)
							outputWorker_log_head_static_info_hash = outputWorker_log_head+"("+static_info_hash+")"

							##6. DB 3차 쿼리, 테이블명: static_analysis_info
							self.putLog('debug', outputWorker_log_head_static_info_hash+" - check if static_analysis_info table has the static_info_hash: select")
							#select 쿼리 및 실행
							query_select = ("""select id from static_analysis_info where static_info_hash=%s""")
							data_select = (static_info_hash,)
							mysql_cur_result = self.MYSQL_DB_INTERFACE.executeQuery(mysql_cur, query_select, data_select)
						
							#조회 결과 없으면 insert
							if not mysql_cur_result.rowcount:
								#static_info_hash를 유일한 값(복합키)로하여 입력
								self.putLog('debug', outputWorker_log_head_static_info_hash+" - not found in static_analysis_info table: insert")
								query_insert = ("""insert into static_analysis_info(
														url_info_id,
														url, mid_url, final_url, apk_hash, static_info_hash,
														apk_analysis_flag,
														worker_id)
													values(
														%s,
														%s, %s, %s, %s, %s,
														'N',
														'none')""")
								data_insert = (url_info_id, url, mid_url, final_url, apk_hash, static_info_hash)
								self.MYSQL_DB_INTERFACE.executeQuery(mysql_cur, query_insert, data_insert)
							#조회 결과 있으면 pass
							else:
								raise Exception(outputWorker_log_head_static_info_hash+" - found in static_analysis_info; already analyzed: check log!")
					#apk 다운로드하지 않을 경우, ips_info, smsf_info, ltas_info에서 삭제
					else:
						##4-2. DB 2차 쿼리, 테이블명: url_list
						self.putLog('debug', outputWorker_log_head_url_hash+" - got source_id from url_list table: select")
						#select 쿼리 및 실행
						query_select = ("""select ips_info_id, smsf_info_id, ltas_info_id, other_info_id from url_list where url=%s""")
						data_select = (url,)
						mysql_cur_result = self.MYSQL_DB_INTERFACE.executeQuery(mysql_cur, query_select, data_select)
						if mysql_cur_result.rowcount:
							ips_info_id, smsf_info_id, ltas_info_id, other_info_id = mysql_cur_result.fetchone()
							if ips_info_id:
								self.putLog('debug', outputWorker_log_head_url_hash+" - delete url from ips_info table: delete")
								query_delete = ("""delete from ips_info where id=%s""")
								data_delete = (ips_info_id,)
								self.MYSQL_DB_INTERFACE.executeQuery(mysql_cur, query_delete, data_delete)
							if smsf_info_id:
								self.putLog('debug', outputWorker_log_head_url_hash+" - delete url from smsf_info table: delete")
								query_delete = ("""delete from smsf_info where id=%s""")
								data_delete = (smsf_info_id,)
								self.MYSQL_DB_INTERFACE.executeQuery(mysql_cur, query_delete, data_delete)
							if ltas_info_id:
								self.putLog('debug', outputWorker_log_head_url_hash+" - delete url from ltas_info table: delete")
								query_delete = ("""delete from ltas_info where id=%s""")
								data_delete = (ltas_info_id,)
								self.MYSQL_DB_INTERFACE.executeQuery(mysql_cur, query_delete, data_delete)
							if other_info_id:
								self.putLog('debug', outputWorker_log_head_url_hash+" - delete url from other_info table: delete")
								query_delete = ("""delete from other_info where id=%s""")
								data_delete = (other_info_id,)
								self.MYSQL_DB_INTERFACE.executeQuery(mysql_cur, query_delete, data_delete)
						
					self.putLog('info', outputWorker_log_head_url_hash+" - DB query end")
						
					##7. DB commit
					self.MYSQL_DB_INTERFACE.commitQuery(mysql_conn)
					self.putLog('info', outputWorker_log_head+" - query committed")
					self.endDB(mysql_conn, mysql_cur)
					
					##8. 앱 다운로드 시에 result_queue에 입력
					if apk_download_flag == 'Y':
						self.RESULT_QUEUE.put_nowait(result)
						
			except Queue.Empty:
				self.putLog('info', outputWorker_log_head+" - empty output queue")
				
			self.putLog('info', outputWorker_log_head+" - ended")
			
		except Exception as e:
			_, _ , tb = sys.exc_info() # tb -> traceback object
			self.putLog('error', outputWorker_log_head+" - error line No: "+str(tb.tb_lineno)+"; "+str(e))
			
		finally:
			queue_size = self.RESULT_QUEUE.qsize()
			self.putLog('info', outputWorker_log_head+" - remained result queue count: "+str(queue_size))
			self.waitFinalInterval(self.INTERVAL_TIME_OUTPUT, init_wait_time, outputWorker_log_head, queue_size)