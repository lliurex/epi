#!/usr/bin/env python3

import os
import subprocess
import sys
import json
import platform
#import socket
import tempfile
import time
import datetime
import urllib.request

import lliurexstore.storeManager as StoreManager
import dpkgunlocker.dpkgunlockermanager as DpkgUnlockerManager


class EpiManager:
	
	def __init__(self):


		self.storeManager=StoreManager.StoreManager(autostart=False)
		self.dpkgUnlocker=DpkgUnlockerManager.DpkgUnlockerManager()
		self.reposPath="/etc/apt/sources.list.d/"
		self.sources_list="epi.list"
		self.epi_sources=os.path.join(self.reposPath,self.sources_list)
		self.epi_keyring="/tmp/epi_keyring"
						
		self.order=0
		self.epiFiles={}
		self.arquitecture=False
		self.update=False
		self.zomando_name={}
		self.epi_base={"repository":[],
					"force32" : False,
					"required_x" : False,
					"script": {},
					"depends":"",
					"zomando":"",
					"required_root":False,
					"required_dconf":False
					}

		#self.read_conf(epi_file)
	
		
	#def __init__	

	
	def check_connection(self):
	
		result=[]
		try:
			res=urllib.request.urlopen("http://lliurex.net")
			result.append(True)
			
		except Exception as e:
			result.append(False)
			result.append(str(e))
			
		return result	

	#def check_connection	

	def read_conf(self,epi_file):


		if os.path.exists(epi_file):
			f=open(epi_file)
			try:
				epi_load=json.load(f)
				epi_conf=self.epi_base.copy()
				f.close()
				epi_conf.update(epi_load)
				self.epiFiles[self.order]=epi_conf
				self.zomando_name[self.order]=epi_conf["zomando"]
				try:
					if epi_conf["depends"]!="":
						self.order=self.order+1
						self.read_conf(epi_conf["depends"])
				except :
					pass
			except:
				return False

		return True			

	#def read_conf		


	def get_pkg_info(self):

		pkg_list=[]
		self.pkg_info={}
		tmp_list=self.epiFiles.copy()
				
		for item in tmp_list:
			pkg_list=[]
			pkg_list=tmp_list[item]["pkg_list"]
			type_epi=tmp_list[item]["type"]
			info=self.get_store_info(pkg_list,item,type_epi)

			cont=0

			for element in pkg_list:
				name=element["name"]
				if info[name]["status"]=="installed":
					cont=cont+1

			if cont==len(pkg_list):
				if item>0:
					self.epiFiles.pop(item)
					self.zomando_name.pop(item)
				else:
					self.epiFiles[item]["status"]="installed"
					self.pkg_info.update(info)
			else:
				self.epiFiles[item]["status"]="availabled"
				self.pkg_info.update(info)	

	#def get_pkg_info				
							

	def get_store_info(self,pkg_list,order,type_epi):			

			self.getStatus_byscript=False
			pkg_info={}
						
			for item in pkg_list:
				app=item["name"]
				name=""
				summary=""
				status=""
				description=""
				icon=""
				debian_name=""
				component=""
				if type_epi!="localdeb":
					try:
						pkg=item["key_store"]
						action="info"
						self.storeManager.execute_action(action,pkg)
						while self.storeManager.is_action_running(action):
							time.sleep(0.2)

						ret=self.storeManager.get_status(action)

						if ret["status"]==0:
							data=self.storeManager.get_result(action)

							if len(data)>0:

								description=data["info"][0]["description"]
								icon=data["info"][0]["icon"]
								name=data["info"][0]["name"]
								summary=data["info"][0]["summary"]
								debian_name=data["info"][0]["package"]
								component=data["info"][0]["component"]

								status=self.check_pkg_status(app,order)
								if not self.getStatus_byscript and status!="installed":
									if (data["info"][0]["state"]) !="":
										status=data["info"][0]["state"]

							else:
								status=self.check_pkg_status(app,order)		
						else:
							status=self.check_pkg_status(app,order)	
					
					except:
						status=self.check_pkg_status(app,order)	
				else:
					data=self.get_localdeb_info(app,order)	
					summary=data[0]
					description=data[1]
					status=data[2]
					name=item["name"]
					debian_name=item["version"]["all"]		
				
				pkg_info[app]={}
				pkg_info[app]["debian_name"]=debian_name
				pkg_info[app]["component"]=component
				pkg_info[app]["status"]=status
				pkg_info[app]["description"]=description
				pkg_info[app]["icon"]=icon
				pkg_info[app]["name"]=name
				pkg_info[app]["summary"]=summary

			return pkg_info

	#def get_store_info			

	def check_pkg_status(self,pkg,order=None):
	

		try:
			if self.epiFiles[order]["script"]["getStatus"]:
				self.getStatus_byscript=True
		except:
			pass

		if self.getStatus_byscript:
			if order !=None:
				try:
					script=self.epiFiles[order]["script"]["name"]
					if os.path.exists(script):
						cmd=script +' getStatus ' + pkg;
						p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
						poutput=p.communicate()
						if len(poutput)>0:
							if poutput[0].decode("utf-8").split("\n")[0]=='0':
								return "installed"
						
				except Exception as e:
					self.getStatus_byscript=False
					#print (str(e))
					pass
		else:					

			cmd='dpkg -l '+ pkg + '| grep "^i[i]"'
			p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
			poutput,perror=p.communicate()

			if len(poutput)>0:
				return "installed"
		
				
		return "available"	

	#def check_pkg_status	

	def get_localdeb_info(self,pkg,order):

		summary=""
		description=""
		status=""
		try:
			script=self.epiFiles[order]["script"]["name"]
			if os.path.exists(script):
				cmd=script +' getInfo ' + pkg;
				p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
				poutput=p.communicate()
				if len(poutput)>0:
					summary=poutput[0].decode("utf-8").split("\n")[0].split("||")[0]
					if len(poutput)>1:
						description=poutput[0].decode("utf-8").split("\n")[0].split("||")[1]

		except:
			pass

		cmd='dpkg -l '+ pkg + '| grep "^i[i]"'
		p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		poutput,perror=p.communicate()

		if len(poutput)>0:
			status="installed"	
		else:
			status="available"	

		data=[summary,description,status]
		
		return data					
	
	#def get_localdeb_info 	


	def check_locks(self):

		'''
		0:Detect correct block. Must waiting
		1:Detect wrong lock. Can be unlock
		'''

		locks_detect={}
		locks_info=self.dpkgUnlocker.checkingLocks()
		cont_unlock=0
		cont_wait=0

		if locks_info["Lliurex-Up"]==1:
			locks_detect["Lliurex-Up"]=True

		if locks_info["Dpkg"]!=0:
			if locks_info["Dpkg"]==2:
				cont_unlock+=1
				locks_detect["Dpkg"]=1
			else:
				locks_detect["Dpkg"]=0
				cont_wait+=1	

		if locks_info["Apt"]!=0:
			if locks_info["Apt"]==2:
				locks_detect["Apt"]=1
				cont_unlock+=1
			else:
				locks_detect["Apt"]=0
				cont_wait+=1

		if len(locks_detect)>0:
			if cont_wait>0:
				locks_detect["wait"]=True
			else:
				locks_detect["wait"]=False
								

		return locks_detect

	#def check_locks	
		 				
	def unlock_process(self):
	
		cmd="/usr/sbin/dpkg-unlocker-cli unlock -u"
		result=subprocess.call(cmd,shell=True,stdout=subprocess.PIPE)
		return result

	#def unlock_process					
		
	def check_root(self):

		self.root=False

		try:
			f=open("/etc/epi.token","w")
			f.close()
			os.remove("/etc/epi.token")
			self.download_path="/var/cache/epi-downloads"
			self.root=True
		except:
			if not os.path.exists(os.path.expanduser("~/.cache/epi-downloads/")):
				os.mkdir(os.path.expanduser("~/.cache/epi-downloads/"))
			self.download_path=os.path.expanduser("~/.cache/epi-downloads/")

	#def check_root		


	def required_root (self):

		cont=0

		if not self.root:
			for item in self.epiFiles:
				if self.epiFiles[item]["type"]!="file":
					cont=cont+1

				else:
					if self.epiFiles[item]["required_root"]:
						cont=cont+1
							
			if cont>0:
				return True
			else:
				return False	

		else:
			return False		

	#def required_root		


	def required_eula(self):

		eulas=[]

		for item in self.epiFiles:
			cont=0
			for pkg in self.epiFiles[item]["pkg_list"]:
				try:
					if pkg["eula"]!="":
						tmp={}
						tmp["order"]=item
						tmp["pkg_name"]=pkg["name"]
						tmp["eula"]=pkg["eula"]
						eulas.append(tmp)
				except:
					pass		
					
		return eulas

	#def required_eula	
	
	def test_install(self):

		result_test=[]
		test=""
		pkg_list=""

		try:
			script=self.epiFiles[0]["script"]["name"]
			if os.path.exists(script):
				cmd=script +' testInstall ';
				p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
				poutput=p.communicate()
				if len(poutput)>0:
					test=poutput[0].decode("utf-8").split("\n")[0]
					if test!="1":
						parse_test=test.split("||")
						if len(parse_test)>1:
							test=parse_test.pop()
							for item in parse_test:
								pkg_list=pkg_list+item+" "
		except:
			pass
		
		result_test.append(test)
		result_test.append(pkg_list)	

		return result_test	

	#def test_install	

	def check_update_repos(self):
		
		#Only update repos if needed
		current_date=datetime.date.today().strftime('%y%m%d')
		filename='/var/cache/apt/pkgcache.bin'
		lastmod=os.path.getmtime(filename)
		lastupdate=datetime.datetime.fromtimestamp(lastmod).strftime('%y%m%d')
		cmd=""

		if current_date !=lastupdate or self.update:
			cmd="LANG=C LANGUAGE=en apt-get update; "
		else:
			for item in self.epi_conf["pkg_list"]:
				update_repo=False
				app=item["name"]
				command="LANG=C LANGUAGE=en apt-cache policy %s"%app
				p=subprocess.Popen(command,shell=True, stdout=subprocess.PIPE)
				output=p.communicate()
				if str(output[0]) != '':
					tmp=str(output[0]).split("\\n")
					if len(tmp)>1:
						if tmp[2].split(":")[1]=="":
							update_repo=True
							
					else:
						update_repo=True
						

				else:
					update_repo=True

				if update_repo:	
					cmd="LANG=C LANGUAGE=en apt-get update; "
					return cmd		

		return cmd
		
	#def check_update_repos	

	def check_arquitecture(self):

		self.force32=self.epi_conf['force32']
		cmd=""
		
		if self.force32:
			if platform.architecture()[0]=='64bit':
				cmd='dpkg --add-architecture i386; '
				self.update=True
								
		self.arquitecture=True
		return cmd		

	#def check_arquitecture	
	
	def add_repository_keys(self,order):

		self.epi_conf=self.epiFiles[order]

		cmd=""
		self.type=self.epi_conf["type"]

		if self.type=="apt":

			repos_list=self.epi_conf["repository"]

			if len(repos_list)>0:
				f = open(self.epi_sources,'w')
				for item in repos_list:
					if item["url"]!="":
						lines=item["url"].split(";")
						for line in lines:
							f.write(line+'\n')
					try:
						key_cmd=item["key_cmd"]
						if key_cmd !="":
							cmd=cmd+key_cmd+';'	
					except Exception as e:
						if len(self.epi_conf["script"])>0:
							try:
								if self.epi_conf["script"]["addRepoKeys"]:
									script=self.epi_conf["script"]["name"]
									if os.path.exists(script):
										command=script + ' addRepoKeys;'
										cmd=cmd+command
							except Exception as e:
								#print (str(e))
								pass

				f.close()
				self.update=True

			
		return cmd		

	#def add_repository_keys	


	def get_app_version(self,item=None):

		self.force32=self.epi_conf["force32"]

		if self.force32:
			version=item["version"]["32b"]
			
		else:
			try:
				version=item["version"]["all"]
			except Exception as e:
				if platform.architecture()[0]=='64bit':	
					version=item["version"]["64b"]
				else:
					version=item["version"]["32b"]
			
		return version

	#def get_app_version	
						
	def download_app(self):

		self.manage_download=True
		self.download_folder={}
		cmd=""

		self.type=self.epi_conf["type"]
		if self.type !='apt' and self.type !='localdeb':
			self.token_result_download=tempfile.mkstemp("_result_download")
			
			if self.type=="file":
				if len(self.epi_conf["script"])>0:
					try:
						if self.epi_conf["script"]["download"]:
							script=self.epi_conf["script"]["name"]
							if os.path.exists(script):
								cmd=script +' download; echo $? >' + self.token_result_download[1] +';'
								self.manage_download=False
					except:
						pass			

			if self.manage_download:

				for item in self.epi_conf["pkg_list"]:
					version=self.get_app_version(item)
					if self.type=="deb":
						name=item["name"]+".deb"
						tmp_file=os.path.join(self.download_path,name)
					elif self.type=="file":
						try:
							tmp_file=os.path.join(self.download_path,item["alias_download"])
						except Exception as e:	
							#name=item["name"]
							tmp_file=os.path.join(self.download_path,version)
				
					url=item["url_download"]
					
					if os.path.exists(tmp_file):
						cmd=cmd+'rm -f '+ tmp_file +';'
					self.download_folder["name"]=tmp_file
					cmd=cmd+'wget ' +url+version + ' --progress=bar:force --no-check-certificate -O ' + tmp_file +'; '

				cmd=cmd + ' echo $? >' + self.token_result_download[1] +';'	
			

		return cmd			
					
	#def download_app		


	def check_download(self):

		
		result=True

		if self.type !='apt' and self.type !='localdeb':

			
			if os.path.exists(self.token_result_download[1]):
				file=open(self.token_result_download[1])
				content=file.readline()
				if '0' not in content:
					result=False
				file.close()
				os.remove(self.token_result_download[1])

				if result:	
					if self.manage_download:
						pkgs_todownload=len(self.download_folder)
						cont=0

						for item in self.download_folder:
							if os.path.exists(self.download_folder[item]):
								cont=cont+1

						if cont != pkgs_todownload:
							result=False

		return result

	#def check_download		

	def preinstall_app(self):
	

		cmd=""

		if len(self.epi_conf["script"])>0:
			self.token_result_preinstall=tempfile.mkstemp("_result_preinstall")
			script=self.epi_conf["script"]["name"]
			if os.path.exists(script):
				cmd=script +' preInstall; echo $? >' + self.token_result_preinstall[1] +';'

		return cmd		

	#def preinstall_app	
	

	def check_preinstall(self):
		
		result=True

		try:
			if os.path.exists(self.token_result_preinstall[1]):
				file=open(self.token_result_preinstall[1])
				content=file.readline()
				if '0' not in content:
					result=False
				file.close()
				os.remove(self.token_result_preinstall[1])

		except:			
			pass

		return result


	#def check_preinstall_app	

	def install_app(self):
	
		add_i386=""
		
		if not self.arquitecture:
			add_i386=self.check_arquitecture()


		cmd=""
		
		if self.type=="apt":

			update_repos=self.check_update_repos()
			cmd=add_i386+update_repos+"apt-get install --reinstall --allow-downgrades --yes "
			for item in self.epi_conf["pkg_list"]:
				app=item["name"]
				cmd=cmd + app +" "

	
			
		elif self.type=="deb":
			
			cmd="dpkg -i "
			for item in self.epi_conf["pkg_list"]:
				name=item["name"]+".deb"
				pkg=self.download_folder["name"]
				cmd=cmd+pkg +" "

		elif self.type=="localdeb":
			cmd="apt-get install --reinstall --allow-downgrades --yes "
			for item in self.epi_conf["pkg_list"]:
				name=item["version"]["all"]
				pkg=os.path.join(item["url_download"],name)
				cmd=cmd+pkg+ " "

		elif self.type=="file":
			self.token_result_install=tempfile.mkstemp("_result")
			script=self.epi_conf["script"]["name"]
			if os.path.exists(script):
				cmd=script + ' installPackage; echo $? >' + self.token_result_install[1]

		cmd=cmd+";"
		return cmd	

	#def install_app	


	def check_install_remove(self,action):

		dpkg_status={}
		cont=0
		token=""
		
		if action=="install":
				
			if self.type !="file":
				pkgs=self.epi_conf["pkg_list"]
			
				for item in pkgs:
					status=self.check_pkg_status(item["name"])
				
					if status=="installed":
						cont=cont+1
				
					dpkg_status[item["name"]]=status

				if cont==len(pkgs):
					result=True
		
				else:
					result=False

			else:
				token=self.token_result_install[1]	
				if os.path.exists(token):
					file=open(token)
					content=file.readline()
					if '0' not in content:
						result=False
					else:
						result=True	
										
					file.close()
					os.remove(token)

		else:
		
			if self.epiFiles[0]["type"] !="file":
					pkgs=self.epiFiles[0]["pkg_list"]			
					for item in pkgs:
						status=self.check_pkg_status(item["name"])
						if status!="installed":
							cont=cont+1
						dpkg_status[item["name"]]=status

		
			token=self.token_result_remove[1]
			if os.path.exists(token):
					file=open(token)
					content=file.readline()
					if '0' not in content:
						result=False
					else:
						result=True	
							
					file.close()
					os.remove(token)

		return dpkg_status,result			

	
		
	#def check_install_remove	

	def postinstall_app(self):
	

		cmd=""
		
		if len(self.epi_conf["script"])>0:
			self.token_result_postinstall=tempfile.mkstemp("_result_postinstall")
			script=self.epi_conf["script"]["name"]
			if os.path.exists(script):
				cmd=script + ' postInstall; echo $? >' + self.token_result_postinstall[1] +';'

		return cmd	

	#def postinstall_app	
	
	def check_postinstall(self):
		
		result=True

		try:
			if os.path.exists(self.token_result_postinstall[1]):
				file=open(self.token_result_postinstall[1])
				content=file.readline()
				if '0' not in content:
					result=False
				file.close()
				os.remove(self.token_result_postinstall[1])
		except:
			pass			

		return result

	#def check_postinstall	

	def remove_repo_keys(self):
	
		if os.path.exists(self.epi_sources):
			os.remove(self.epi_sources)	

		if os.path.exists(self.epi_keyring):
			os.remove(self.epi_keyring)	

	#def remove_repo_keys	

	def uninstall_app(self,order):

		cmd=""

		if self.epiFiles[order]["script"]["remove"]:
			self.token_result_remove=tempfile.mkstemp("_result_remove")
			script=self.epiFiles[order]["script"]["name"]
			if os.path.exists(script):
				cmd=script + ' remove; echo $? >' + self.token_result_remove[1] + ';'

		return cmd

	#def uninstall_app	

	def zerocenter_feedback(self,order,action,result=None):

		zomando_name=self.zomando_name[order]

		if zomando_name!="":
			if action=="init":
				cmd="zero-center add-pulsating-color " +zomando_name
			elif action=="install":
				if result:
					cmd="zero-center remove-pulsating-color "+zomando_name + " ;zero-center set-configured " +zomando_name
					
				else:
					cmd="zero-center remove-pulsating-color "+zomando_name + " ;zero-center set-failed " +zomando_name
			elif action=="uninstall":
				if result:
					cmd="zero-center remove-pulsating-color "+zomando_name + " ;zero-center set-non-configured " +zomando_name
				else:
					cmd="zero-center remove-pulsating-color "+zomando_name + " ;zero-center set-failed " +zomando_name

			os.system(cmd)		

	#def zero-center_feedback	


#class ApplicationInstallerManager


if __name__=="__main__":
	
	epi=EpiManager()
