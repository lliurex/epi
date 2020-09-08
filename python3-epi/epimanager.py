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
import shutil


class EpiManager:
	
	def __init__(self,args=None):

		if args:
			self.debug=1
		else:	
			self.debug=0
		
		self.storeManager=StoreManager.StoreManager(autostart=False)
		self.dpkgUnlocker=DpkgUnlockerManager.DpkgUnlockerManager()
		self.reposPath="/etc/apt/sources.list.d/"
		self.sources_list="epi.list"
		self.epi_sources=os.path.join(self.reposPath,self.sources_list)
		self.epi_keyring_file="epi_keyring"
		self.epi_keyring_path=os.path.join("/tmp",self.epi_keyring_file)
		self.keyring_path="/etc/apt/trusted.gpg.d/"
		
		self.urltocheck1="http://lliurex.net"
		self.urltocheck2="https://github.com/lliurex"

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
					"required_dconf":False,
					"selection_enabled":{"active":False,"all_selected":False},
					"custom_icon_path":""
					}

		self.packages_selected=[]
		self.partial_installed=False
		#self.read_conf(epi_file)
	
		
	#def __init__	

	def _show_debug(self,function,msg):

		if self.debug==1:
			print("[EPI-DEBUG]: Function: %s - Message: %s"%(function,msg))

	#def _show_debug

	def check_connection(self,url):
		
		result=[]
		try:
			res=urllib.request.urlopen(url)
			result.append(True)
			
		except Exception as e:
			result.append(False)
			result.append(str(e))
		
		self._show_debug("check_connection","Result: %s"%(result))
			
		return result	

	#def check_connection	

	def read_conf(self,epi_file):


		if os.path.exists(epi_file) and os.path.isfile(epi_file):
			f=open(epi_file)
			try:
				epi_load=json.load(f)
				epi_conf=self.epi_base.copy()
				f.close()
				if len(epi_load)>0:
					epi_conf.update(epi_load)
					self.epiFiles[self.order]=epi_conf
					self.zomando_name[self.order]=epi_conf["zomando"]
					try:
						if epi_conf["depends"]!="":
							self.order=self.order+1
							self.read_conf(epi_conf["depends"])
					except :
						pass
				else:
					self._show_debug("read_conf","Epi files is empty: %s"%(epi_file))
					return {"status":False,"error":"empty"}
		

			except Exception as e:
				self._show_debug("read_conf","Epi file is not a valid json. Error: %s"%(str(e)))
				return {"status":False,"error":"json"}

		else:
			self._show_debug("read_conf","Epi files not exists or path is not valid: %s"%(epi_file))
			return {"status":False,"error":"path"}

		return {"status":True,"error":""}		

	#def read_conf		

	def check_script_file(self):

		script=self.epiFiles[0]["script"]

		if len(script)>0:
			if os.path.exists(script["name"]) and os.path.isfile(script["name"]):
				if not os.access(script["name"],os.X_OK):
					return {"status":False,"error":"permissions"}
			else:
				self._show_debug("check_scrip_file","Script file not exits or path is not valid: %s"%(script["name"]))
				return {"status":False,"error":"path"}

		return {"status":True,"error":""}
	
	#def check_script_file

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
				if item==0:
					if cont>0 and tmp_list[item]["selection_enabled"]["active"]:
						self.partial_installed=True	

				self.epiFiles[item]["status"]="availabled"
				self.pkg_info.update(info)
					
		
		self._show_debug("get_pkg_info","Content of epi file: %s"%(self.epiFiles))
		self._show_debug("get_pkg_info","Packages info: %s"%(self.pkg_info))
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
			self.getStatus_byscript=False
			pass

		if self.getStatus_byscript:
			if order !=None:
				try:
					script=self.epiFiles[order]["script"]["name"]
					if os.path.exists(script):
						cmd=script +' getStatus ' + pkg;
						p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
						poutput=p.communicate()
						self._show_debug("check_pkg_status","pkg: %s; status result by script:poutput: %s"%(pkg,poutput))

						if len(poutput)>0:
							if poutput[0].decode("utf-8").split("\n")[0]=='0':
								return "installed"
							elif poutput[0].decode("utf-8").split("\n")[0]=='Not found':
								return self._get_pkg_status(pkg)

				except Exception as e:
					self.getStatus_byscript=False
					
					pass
		else:					
			return self._get_pkg_status(pkg)
		
				
		return "available"	

	#def check_pkg_status	

	def _get_pkg_status(self,pkg):

		cmd='dpkg -l '+ pkg + '| grep "^i[i]"'
		p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		poutput,perror=p.communicate()

		self._show_debug("_get_pkg_status","pkg: %s; result by command:poutput: %s; perror: %s"%(pkg,poutput,perror))

		if len(poutput)>0:
			return "installed"

	#def _get_pkg_status

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

		return self.root	

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
		
		self._show_debug("required_eula","Packages with eula: %s"%(eulas))
		return eulas

	#def required_eula	
	
	def test_install(self):

		result_test=[]
		test=""
		pkg_list=""

		if self.epiFiles[0]["type"]=="localdeb":
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
									pkg_list=pkg_list+"- "+item+"\n"
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
		update_repo=False

		if self.type in ["apt","mix"]:
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
						self._show_debug("check_update_repos","Required update: %s - Command to update: %s"%(update_repo,cmd))
						return cmd		

		
		self._show_debug("check_update_repos","Required update: %s - Command to update: %s"%(update_repo,cmd))

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
		
		self._show_debug("check_arquitecture","Required i386: %s - Command to add i386:%s"%(self.force32,cmd))
		
		return cmd		

	#def check_arquitecture	
	
	def add_repository_keys(self,order):

		self.epi_conf=self.epiFiles[order]
		self.epi_order=order
		self.type=self.epi_conf["type"]
		cmd=""

		if self.type in ["apt","mix"]:

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

		self._show_debug("add_repository_keys","Command to add keys:%s"%(cmd))
		return cmd		

	#def add_repository_keys	


	def get_app_version(self,item=None):

		self.force32=self.epi_conf["force32"]
		version=""

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
			
		self._show_debug("get_app_version","Version to install: %s"%(version))

		return version

	#def get_app_version	
						
	def download_app(self):

		self.manage_download=True
		self.download_folder=[]
		cmd=""
		cmd_file=""

		self.type=self.epi_conf["type"]

		if self.type not in ['apt','localdeb']:
			if len(self.epi_conf["script"])>0:
				try:
					if self.epi_conf["script"]["download"]:
						script=self.epi_conf["script"]["name"]
						if os.path.exists(script):
							self.manage_download=False
							cmd_file=script + " download "
				except:
					pass

			self.token_result_download=tempfile.mkstemp("_result_download")
			
			if self.type in ["deb","file"]:	

				if self.type=="file":
					if not self.manage_download:
						cmd=cmd_file
						for pkg in self.packages_selected:
							cmd+="%s "%pkg
						cmd+='; echo $? >' + self.token_result_download[1] +';'
				if self.manage_download:
					for item in self.epi_conf["pkg_list"]:
						if item["name"] in self.packages_selected:
							cmd=self._get_download_cmd(self.type,item,cmd)
					cmd=cmd + ' echo $? >' + self.token_result_download[1] +';'	

			elif self.type=="mix":
				
				for item in self.epi_conf["pkg_list"]:
					if item["name"] in self.packages_selected:
						if item["type"] in ["deb","file"]:
							if self.manage_download:
								cmd=self._get_download_cmd(item["type"],item,cmd)
							else:
								if item["type"]=="file":
									cmd_file+="%s "%item["name"]	
								else:
									cmd=self._get_download_cmd(item["type"],item,cmd)
									
				if cmd_file!="":
					cmd_file+=";"

				cmd=cmd +' '+cmd_file+'echo $? >' + self.token_result_download[1] +';'	
		
		self._show_debug("download_app","Command to download: %s"%(cmd))
		return cmd			
					
	#def download_app		

	def _get_download_cmd(self,item_type,item,cmd):

		tmp_file=""
		version=self.get_app_version(item)

		if item_type=="deb": 
			name=item["name"]+".deb"
			tmp_file=os.path.join(self.download_path,name)
		elif item_type=="file":
			try:
				tmp_file=os.path.join(self.download_path,item["alias_download"])
			except Exception as e:	
				tmp_file=os.path.join(self.download_path,version)
		

		url=item["url_download"]
		if os.path.exists(tmp_file):
			cmd=cmd+'rm -f '+ tmp_file +';'
		
		self.download_folder.append(tmp_file)
		cmd=cmd+'wget ' +url+version + ' --progress=bar:force --no-check-certificate -O ' + tmp_file +'; '

		return cmd

	#def _get_download_cmd

	def check_download(self):

		
		result=True
		content=""

		if self.type not in ['apt','localdeb']:

			count=0
			pkgs_todownload=len(self.download_folder)

			if len(self.download_folder)>0:
				for item in self.download_folder:
					if os.path.exists(item):
						count=count+1
			
			if os.path.exists(self.token_result_download[1]):
				file=open(self.token_result_download[1])
				content=file.readline()
				if '0' not in content:
					result=False
				file.close()
				os.remove(self.token_result_download[1])

				if result:	
					if self.manage_download:
						if count != pkgs_todownload:
							if not self.epi_conf["selection_enabled"]["active"]:
								result=False
				else:
					if self.epi_conf["selection_enabled"]["active"]:
						if count>0:		
							result=True

		self._show_debug("check_download","Downlodad status: Result: %s - Token Content: %s"%(result,content))
		
		return result

	#def check_download		

	def preinstall_app(self):
	
		cmd=""

		if len(self.epi_conf["script"])>0:
			self.token_result_preinstall=tempfile.mkstemp("_result_preinstall")
			script=self.epi_conf["script"]["name"]
			if os.path.exists(script):
				cmd=script + " preInstall "
				for pkg in self.packages_selected:
					cmd+="%s "%pkg
				cmd+='; echo $? >' + self.token_result_preinstall[1] +';'

		self._show_debug("preinstall_app","Preinstall Command: %s"%(cmd))
		return cmd		

	#def preinstall_app	
	

	def check_preinstall(self):
		
		result=True
		content=""

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

		self._show_debug("check_preinstall","Presintall result: Result: %s - Token content: %s"%(result,content))
	
		return result


	#def check_preinstall_app	

	def install_app(self,calledfrom):
	
		self._copy_epi_keyring()
		self.token_result_install=""
		pkgs_apt=0
		add_i386=""
		cmd=""
		
		'''
		if not self.arquitecture:
			add_i386=self.check_arquitecture()
		'''
	
		if self.type=="mix":
			result_mix=self._check_epi_mix_content(calledfrom)
			pkgs_apt=result_mix[0]
			pkgs_deb=result_mix[1]
			pkgs_file=result_mix[2]
			cmd_dpkg=result_mix[3]
			cmd_file=result_mix[4]
			
		
		if self.type=="apt" or pkgs_apt>0:
			#update_repos=self.check_update_repos()
			#cmd=add_i386+update_repos+"apt-get install --reinstall --allow-downgrades --yes "
			cmd=self._get_install_cmd_base(calledfrom,"apt")
			
		if self.type=="apt":	
			for item in self.epi_conf["pkg_list"]:
				if item["name"] in self.packages_selected:
					app=item["name"]
					cmd=cmd + app +" "
				
		elif self.type=="deb":
			pkg=""
			cmd=self._get_install_cmd_base(calledfrom,"deb")
			for item in self.download_folder:
				if os.path.exists(item):
					pkg=pkg+' '+item
			
			cmd=cmd+pkg	

		elif self.type=="localdeb":
			cmd=self._get_install_cmd_base(calledfrom,"apt")
			for item in self.epi_conf["pkg_list"]:
				name=item["version"]["all"]
				pkg=os.path.join(item["url_download"],name)
				cmd=cmd+pkg+ " "

		elif self.type=="file":
			cmd=self._get_install_file_cmd_base()
			if cmd !="":
				for pkg in self.packages_selected:
					cmd+="%s "%pkg
				cmd+='; echo $? >' + self.token_result_install[1]	
		
		elif self.type=="mix":
			for item in self.epi_conf["pkg_list"]:
				if item["name"] in self.packages_selected:
					if item["type"]=="apt":
						cmd=cmd + item["name"] +" "
					
					elif item["type"]=="deb":
						for pkg in self.download_folder:
							if os.path.exists(pkg):
								if item["name"] in pkg:
									cmd_dpkg=cmd_dpkg+ pkg + " "	
					
					elif item["type"]=="file":
						if cmd_file!="":
							cmd_file+="%s "%item["name"]

			
			
			if cmd_dpkg!="":
				if cmd!="":
					cmd=cmd+"; "+cmd_dpkg
				else:
					cmd=cmd_dpkg	
			
			if cmd_file!="":
				cmd_file+='; echo $? >' + self.token_result_install[1]
				if cmd!="":
					cmd=cmd+"; "+cmd_file
				else:
					cmd=cmd_file		

		cmd=cmd+";"

		self._show_debug("install_app","Install Command: %s"%(cmd))

		return cmd	

	#def install_app

	def _get_install_cmd_base(self,calledfrom,pkg_type):

		cmd_headed=""
		apt_headed="apt-get install --reinstall --allow-downgrades --yes "
		dpkg_headed="dpkg -i "

		if self.epi_conf["required_dconf"]:
			if calledfrom =="gui":
				cmd_headed="LANG=C LANGUAGE=en DEBIAN_FRONTEND=kde "
			else:
				cmd_headed="LANG=C LANGUAGE=en "
		else:
			cmd_headed="LANG=C LANGUAGE=en DEBIAN_FRONTEND=noninteractive "

		if pkg_type in ["apt","localdeb"]:
			cmd_headed=cmd_headed+apt_headed
		elif pkg_type =="deb":
			cmd_headed=cmd_headed+dpkg_headed

		return cmd_headed		

	# def _check_debconf_required

	def _check_epi_mix_content(self,calledfrom):
		
		pkgs_apt=0
		pkgs_file=0
		pkgs_deb=0
		cmd_file=""
		cmd_dpkg=""
		result=[]

		for item in self.epi_conf["pkg_list"]:
			if item["name"] in self.packages_selected:
				if item["type"]=="apt":
					pkgs_apt+=1
				
				elif item["type"]=="deb":
					pkgs_deb+=1

				elif item["type"]=="file":
					pkgs_file+=1	
						
		if pkgs_deb>0:
			cmd_dpkg=self._get_install_cmd_base(calledfrom,"deb")	

		if pkgs_file>0:
			cmd_file=self._get_install_file_cmd_base()	

		result=[pkgs_apt,pkgs_deb,pkgs_file,cmd_dpkg,cmd_file]

		return result

	#def _check_epi_mix_content

	def _get_install_file_cmd_base(self):

		cmd_tmp=""
		self.token_result_install=tempfile.mkstemp("_result")
		script=self.epi_conf["script"]["name"]
		
		if os.path.exists(script):
			cmd_tmp=script + " installPackage "	
		
		return cmd_tmp 

	#def _get_install_file_cmd_base	

	def _copy_epi_keyring(self):

		if os.path.exists(self.epi_keyring_path):
			if not os.path.exists(os.path.join(self.keyring_path,self.epi_keyring_file+".gpg")):
				dest_path=os.path.join(self.keyring_path,self.epi_keyring_file+".gpg")
				shutil.copy(self.epi_keyring_path,dest_path)

		return
		
	#def _copy_epi_keyring			

	def check_install_remove(self,action):

		dpkg_status={}
		count=0
		pkgs_installed=0
		token=""
		pkgs_ref=[]
		result=False
		content=""


		if action=="install":
			epi_type=self.type
			if epi_type == "file":
				if self.token_result_install!="":
					token=self.token_result_install[1]
			
			elif epi_type!="file":
				pkgs=self.epi_conf["pkg_list"]
		else:
			epi_type=self.epiFiles[0]["type"]
			if epi_type=="file":
				token=self.token_result_remove[1]
				
			elif epi_type !="file":
				pkgs=self.epiFiles[0]["pkg_list"]
				for item in pkgs:
					if item["name"] in self.packages_selected:
						pkgs_ref.append(item["name"])


		if epi_type=="file":
			if os.path.exists(token):
				file=open(token)
				content=file.readline()
				if '0' not in content:
					result=False
				else:
					result=True	
							
				file.close()
				os.remove(token)

		elif epi_type !="file":
			for item in pkgs:
				if item["name"] in self.packages_selected:
					if epi_type=="mix":
						if action=="install":
							status=self.check_pkg_status(item["name"],self.epi_order)
						else:
							status=self.check_pkg_status(item["name"],0)
			
					else:
						status=self.check_pkg_status(item["name"])
	
				#if item["name"] in self.packages_selected:
					dpkg_status[item["name"]]=status
					if status!="installed":
						count+=1
				else:
					if self.pkg_info[item["name"]]["status"]=="installed":
						#if status=="installed":
						pkgs_installed+=1			
									

			if action=="install":
				if count==0:
					result=True
			
				else:
					result=False
			else:
				if count>0:
					if count==len(pkgs_ref):
						result=True
					else:
						result=False
				else:
					resul=False
				

				if pkgs_installed>0:
					self.partial_installed=True
				else:
					self.partial_installed=False			
		
		self._show_debug("check_install_remove","Action: %s - Result: %s - Dpkg Status: %s - Token content: %s"%(action,result,dpkg_status,content))

		return dpkg_status,result			

		
		
	#def check_install_remove	

	def postinstall_app(self):
		
		cmd=""
		
		if len(self.epi_conf["script"])>0:
			self.token_result_postinstall=tempfile.mkstemp("_result_postinstall")
			script=self.epi_conf["script"]["name"]
			if os.path.exists(script):
				cmd=script + " postInstall "
				for pkg in self.packages_selected:
					cmd+="%s "%pkg

				cmd+='; echo $? >' + self.token_result_postinstall[1] +';'

		self._show_debug("postinstall_app","Postinstall Command:%s"%(cmd))

		return cmd	

	#def postinstall_app	
	
	def check_postinstall(self):
		
		result=True
		content=""
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

		self._show_debug("check_postinstall","Postinstall result: Result: %s - Token content: %s"%(result,content))
		
		return result

	#def check_postinstall	

	def remove_repo_keys(self):
	
		if os.path.exists(self.epi_sources):
			os.remove(self.epi_sources)	

		if os.path.exists(self.epi_keyring_path):
			os.remove(self.epi_keyring_path)	

		dest_path=os.path.join(self.keyring_path,self.epi_keyring_file+".gpg")	
		if os.path.exists(dest_path):
			os.remove(dest_path)	

	#def remove_repo_keys	

	def uninstall_app(self,order):

		cmd=""

		if self.epiFiles[order]["script"]["remove"]:
			self.token_result_remove=tempfile.mkstemp("_result_remove")
			script=self.epiFiles[order]["script"]["name"]
			if os.path.exists(script):
				cmd=script + " remove "

				for pkg in self.packages_selected:
					cmd+="%s "%pkg

				cmd+='; echo $? >' + self.token_result_remove[1] + ';'
				#cmd=script + ' remove '+str(self.packages_selected)+'; echo $? >' + self.token_result_remove[1] + ';'
		
		self._show_debug("uninstall_app","Uninstall Command:%s"%(cmd))

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
