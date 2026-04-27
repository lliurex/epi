#!/usr/bin/env python3

import os
from os import listdir
from os.path import isfile, isfile,isdir,join
import subprocess
import sys
import json
import platform
import tempfile
import datetime
import urllib.request

import json, dbus
import dpkgunlocker.dpkgunlockermanager as DpkgUnlockerManager
import shutil
import n4d.client as client
import codecs
import pwd
import grp

class EpiManager:
	
	def __init__(self,args=None):

		try:
			if args[0]:
				self.debug=1
			else:
				self.debug=0
			self.get_available_list=args[1]
		except:
			if args:
				self.debug=1
			else:
				self.debug=0
			self.get_available_list=True
	
		try:
			storeBus=dbus.Bus()
			storeProxy=storeBus.get_object('net.lliurex.store','/')
			self.dbusStore=dbus.Interface(storeProxy,dbus_interface='org.kde.krunner1')
		except Exception as e:
			self.dbusStore=None
			self._show_debug("storeProxy",str(e))
		
		self.dpkgUnlocker=DpkgUnlockerManager.DpkgUnlockerManager()
		self.reposPath="/etc/apt/sources.list.d/"
		self.sources_list="epi.list"
		self.epi_sources=os.path.join(self.reposPath,self.sources_list)
		self.epi_keyring_file="epi_keyring"
		self.epi_keyring_path=os.path.join("/tmp",self.epi_keyring_file)
		self.keyring_path="/etc/apt/trusted.gpg.d/"
		
		self.urltocheck1="http://lliurex.net"
		self.urltocheck2="https://github.com/lliurex"

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
					"custom_icon_path":"",
					"check_zomando_state":True,
					"wiki":"",
					"lock_remove_groups":[],
					"check_meta":True
					}

		self.packages_selected=[]
		self.partial_installed=False
		self.zmd_paths="/usr/share/zero-center/zmds"
		self.app_folder="/usr/share/zero-center/applications"
		self.skipped_pkgs_flavours=[]
		self._user_groups=[]
		self.skipped_pkgs_groups=[]
		self._get_flavours()
		self._get_user_groups()
		self.blocked_remove_skipped_pkgs_list=[]
		self.lock_remove_for_group=False
		if self.get_available_list:
			self.list_available_epi()
		self.epiFiles={}
		self.order=0
		self.root=False
		self.init_n4d_client()
		self.types_without_download=["apt","localdeb","snap","flatpak"]
		self.types_with_download=["deb","file"]
		self.lliurex_meta_pkgs=["lliurex-meta-server","lliurex-meta-server-lite","lliurex-meta-client","lliurex-meta-client-lite","lliurex-meta-minimal-client","lliurex-meta-desktop","lliurex-meta-desktop-lite","lliurex-meta-music","lliurex-meta-infantil"]
		self.blocked_remove_pkgs_list=[]
		self.meta_removed_warning=False
		self.download_path="/var/cache/epi-downloads"
		self.check_meta=True
		self.valid_epi_files=["apt","deb","file","localdeb","mix","snap","flatpak"]
		

	#def __init__	

	def _show_debug(self,function,msg):

		if self.debug==1:
			print(f"[EPI-DEBUG]: Function: {function} - Message: {msg}")

	#def _show_debug

	def check_connection(self,url):
		
		result=[]
		try:
			res=urllib.request.urlopen(url)
			result.append(True)
			
		except Exception as e:
			result.append(False)
			result.append(str(e))
		
		self._show_debug("check_connection",f"Result: {result}")

		return result	

	#def check_connection	

	def read_conf(self,epi_file,cli=False,standalone=None):

		if standalone:
			self.epiFiles={}
			self.order=0
		elif cli:
			path=self._get_epi_path(epi_file)
			if path!="":
				epi_file=path

		if not os.path.isfile(epi_file):
			self._show_debug("read_conf", f"Epi file does not exist or path is invalid: {epi_file}")
			return {"status": False, "error": "path"}

		try:
			with open(epi_file, 'r') as f:
				epi_load = json.load(f)
		except Exception as e:
			self._show_debug("read_conf", f"Epi file is not a valid JSON. Error: {e}")
			return {"status": False, "error": "json"}

		if not epi_load:
			self._show_debug("read_conf", f"Epi file is empty: {epi_file}")
			return {"status": False, "error": "empty"}

		epi_conf = self.epi_base.copy()
		epi_conf.update(epi_load)

		self.epiFiles[self.order] = epi_conf
		self.zomando_name[self.order] = epi_conf.get("zomando", "")

		depends = epi_conf.get("depends", "")
		if depends:
			self.order += 1
			try:
				self.read_conf(depends)
			except Exception:
				pass

		return {"status": True, "error": ""}	

	#def read_conf		

	def check_script_file(self):

		script=self.epiFiles[0]["script"]

		if len(script)>0:
			if os.path.exists(script["name"]) and os.path.isfile(script["name"]):
				if not os.access(script["name"],os.X_OK):
					return {"status":False,"error":"permissions"}
			else:
				self._show_debug("check_scrip_file",f"Script file not exits or path is not valid:{script["name"]}")
				return {"status":False,"error":"path"}

		return {"status":True,"error":""}
	
	#def check_script_file

	def get_pkg_info(self):

		pkg_list=[]
		self.pkg_info={}
		if not self.get_available_list:
			self.skipped_pkgs_groups=[]
			self.skipped_pkgs_flavours=[]

		tmp_list=self.epiFiles.copy()
		
		if self.dbusStore:
			self.showMethod=self.dbusStore.get_dbus_method('show')                            
				
		for item in tmp_list:
			pkg_list=[]
			pkg_list=tmp_list[item]["pkg_list"]
			if 'type' in tmp_list[item]:
				type_epi=tmp_list[item]["type"]
				if type_epi not in self.valid_epi_files:
					self._show_debug("get_pkg_info",f"Unable to get pkg info. Key 'type' has a not valid value: {tmp_list[item]["type"]}")
					break
			else:
				self._show_debug("get_pkg_info","Unable to get pkg info. Key 'type' not defined epi file")
				break
			
			script=self.check_getStatus_byScript(item)
			info=self.get_basic_info(pkg_list,item,type_epi,script)

			if info:
				cont=0
				if item==0:
					self.lock_remove_for_group=self._is_remove_lock_for_group(tmp_list[item]["lock_remove_groups"])	
					self.check_meta=tmp_list[item]["check_meta"]
				for element in pkg_list:
					name=element["name"]
					if info[name]["status"]=="installed":
						cont+=1

				if cont==len(pkg_list):
					if item>0:
						zmd_status=self.get_zmd_status(item)
						if zmd_status==1:
							self.epiFiles.pop(item)
							self.zomando_name.pop(item)
						else:
							self.epiFiles[item]["status"]="availabled"
							self.pkg_info.update(info)

					else:
						self.epiFiles[item]["status"]="installed"
						self.pkg_info.update(info)
				else:
					if item==0:
						if cont>0 and tmp_list[item]["selection_enabled"]["active"]:
							self.partial_installed=True
					self.epiFiles[item]["status"]="availabled"
					self.pkg_info.update(info)
			
				self._show_debug("get_pkg_info",f"Content of epi file: {self.epiFiles}")
				self._show_debug("get_pkg_info",f"Packages info: {self.pkg_info}")
			else:
				self.pkg_info={}
				break
					
	#def get_pkg_info

	def get_basic_info(self,pkg_list,order,type_epi,script):			

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
			search=False
			pkg_type=""

			if type_epi=="mix":
				pkg_type=item.get("type","")
			else:
				pkg_type=type_epi

			if pkg_type:
				if pkg_type in self.valid_epi_files:
					if pkg_type!="localdeb":
						pkg=item.get("name","")
						download_byScript=self._check_download_byScript(order)
						if pkg_type=="file":
							if script=="":
								self._show_debug("get_pkg_info","Unable to get pkg info. Key 'getStatus' not defined in script or has 'False' value")
								break
						if pkg_type in self.types_with_download:
							if not download_byScript:
								abort=False
								if "version" not in item:
									self._show_debug('get_pkg_info',f"Unable to get pkg info. Key 'version' not defined in pkg_list for pkg {pkg}. This key is required if script's 'download' key is not defined or has a value of 'False'")
									abort=True
								if 'url_download' not in item:
									self._show_debug('get_pkg_info',f"Unable to get pkg info. Key 'url_download' not defined in pkg_list for pkg {pkg}. This key is required if script's 'download' key is not defined or has a value of 'False'")
									abort=True
								if abort:
									self._show_debug("get_pkg_info","Unable to get pkg info. Key 'download' not defined in script or  has 'False' value. This key is required if pkg_list's 'version' and 'url_download' keys are not defined")
									break
						status=self.check_pkg_status(app,pkg_type,script)
					else:
						data=self.get_localdeb_info(app,order)	
						summary=data[0]
						description=data[1]
						status=data[2]
						name=item["name"]
						debian_name=item["version"]["all"]	
						search=True	
					
					pkg_info[app]={}
					pkg_info[app]["debian_name"]=debian_name
					pkg_info[app]["component"]=component
					pkg_info[app]["status"]=status
					pkg_info[app]["description"]=description
					pkg_info[app]["icon"]=icon
					pkg_info[app]["name"]=name
					pkg_info[app]["summary"]=summary
					pkg_info[app]["type"]=pkg_type
					pkg_info[app]["search"]=search
				else:
					self._show_debug("get_pkg_info",f"Unable to get pkg info. Key 'pkg_type' for pkg {item["name"]} has incorrect value: {pkg_type}")
					break
			else:
				self._show_debug("get_pkg_info",f"Unable to get pkg info. Key 'pkg_type' not defined in 'pkg_list' for pkg {item["name"]}")
				break

		return pkg_info

	#def get_basic_info			

	def get_store_info(self,pkg):			

		info=""
		
		self.pkg_info[pkg]["search"]=True

		if self.dbusStore:
			try:
				pkginfo=self.showMethod(pkg,"")
				info=json.loads(pkginfo)[0]

				if info:
					data=json.loads(info)
					self.pkg_info[pkg]["description"]=data.get("description","")
					self.pkg_info[pkg]["icon"]=data.get("icon","")
					self.pkg_info[pkg]["name"]=data.get("name","")
					self.pkg_info[pkg]["summary"]=data.get("summary","")
					self.pkg_info[pkg]["debian_name"]=data.get("package",data.get("pkgname",''))
					self.pkg_info[pkg]["component"]=data.get("component",'')
			except:
				self._show_debug("_get_store_info",f"pkg: {pkg}; error parsing json")
		

	#def get_store_info			

	def check_pkg_status(self,pkg,pkg_type,script):

		if pkg_type != "file" or not script:
			return self._get_pkg_status(pkg, pkg_type)

		try:
			cmd = [script, "getStatus", pkg]
			process = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)

			stdout, _ = process.communicate()

			self._show_debug("check_pkg_status",f"pkg: {pkg}; status result by script: {stdout}")

			first_line = (stdout or "").splitlines()[0] if stdout else ""
			if first_line == "0":
				return "installed"

			if first_line == "Not found":
				return self._get_pkg_status(pkg, pkg_type)

			return "available"

		except Exception:
			return "available"
						
	#def check_pkg_status	

	def _get_pkg_status(self,pkg,pkg_type):

		cmd=""
		status_by_code=True
		if pkg_type in ["apt","deb","localdeb"]:
			cmd=f'dpkg -l {pkg} | grep "^i[i]"'
		elif pkg_type=="snap":
			cmd=f'snap list | grep {pkg} | cut -d " " -f 1'
			status_by_code=False
		elif pkg_type=="flatpak":
			cmd=f'flatpak list | grep {pkg} | cut -d " " -f 1'
			status_by_code=False

		p=subprocess.run(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		code=p.returncode
		pout=p.stdout.decode()
		self._show_debug("_get_pkg_status",f"pkg: {pkg}; result by command:{p}")
		
		if code!=0:
			return "availale"

		if status_by_code:
			return 'installed'

		if pout:
			return "installed"
		else:
			return "available"

	#def _get_pkg_status

	def get_localdeb_info(self,pkg,order):

		summary=""
		description=""
		status=""
		
		try:
			script=self.epiFiles[order]["script"]["name"]
			if os.path.exists(script):
				cmd=f"{script} getInfo {pkg};"
				p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
				poutput=p.communicate()
				if len(poutput)>0:
					summary=poutput[0].decode("utf-8").split("\n")[0].split("||")[0]
					if len(poutput)>1:
						description=poutput[0].decode("utf-8").split("\n")[0].split("||")[1]
		except:
			pass

		status=self._get_pkg_status(pkg,"localdeb")
		data=[summary,description,status]
		
		return data					
	
	#def get_localdeb_info 	


	def check_locks(self):

		'''
		0:Detect correct block. Must waiting
		1:Detect wrong lock. Can be unlock
		'''

		locks_info = self.dpkgUnlocker.checkingLocks()
		locks_detect = {}

		unlock_count = 0
		wait_count = 0

		if locks_info.get("Lliurex-Up") == 1:
			locks_detect["Lliurex-Up"] = True

		for lock_name in ("Dpkg", "Apt"):
			lock_status = locks_info.get(lock_name, 0)

			if lock_status == 0:
				continue

			if lock_status == 2:
				locks_detect[lock_name] = 1
				unlock_count += 1
			else:
				locks_detect[lock_name] = 0
				wait_count += 1

		if locks_detect:
			locks_detect["wait"] = wait_count > 0

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
			with open("/etc/epi.token","w"):
				pass
			os.remove("/etc/epi.token")
			self.root=True
		except:
			if not os.path.exists(os.path.expanduser("~/.cache/epi-downloads/")):
				os.mkdir(os.path.expanduser("~/.cache/epi-downloads/"))
			self.download_path=os.path.expanduser("~/.cache/epi-downloads/")

		return self.root	

	#def check_root		


	def required_root (self):

		match=False
		if not self.root:
			for item in self.epiFiles:
				if self.epiFiles[item]["type"]!="file" or self.epiFiles[item]["required_root"]:
					match=True
					break 
				
		return match

	#def required_root		


	def required_eula(self):

		eulas = []

		for order, data in self.epiFiles.items():
			for pkg in data.get("pkg_list", []):
				eula = pkg.get("eula", "")

				if not eula:
					continue

				eulas.append(
					{
						"order": order,
						"pkg_name": pkg.get("name", ""),
						"eula": eula,
					}
				)

		self._show_debug("required_eula",f"Packages with eula: {eulas}",)

		return eulas

	#def required_eula	
	
	def test_install(self):

		result_test = ["", ""]
		pkg_list = ""

		try:
			first_file = self.epiFiles[0]
			if first_file.get("type") != "localdeb":
				return result_test

			script = first_file.get("script", {}).get("name")
			if not script or not os.path.exists(script):
				return result_test

			cmd = [script, "testInstall"]
			process = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
			stdout, _ = process.communicate()

			if not stdout:
				return result_test

			test = stdout.splitlines()[0]
			if test != "1":
				parts = test.split("||")
				if len(parts) > 1:
					test = parts.pop()

					for item in parts:
						if item:
							pkg_list += f" - {item}\n"

			result_test[0] = test
			result_test[1] = pkg_list

			return result_test
		
		except Exception:
			return result_test

    #def test_install

	def check_update_repos(self):
		
		#Only update repos if needed
		
		cmd=""
		update_repo=False

		if self.type in ["apt","mix"]:
			current_date=datetime.date.today().strftime('%y%m%d')
			filename='/var/cache/apt/pkgcache.bin'

			if os.path.exists(filename):
				lastmod=os.path.getmtime(filename)
				lastupdate=datetime.datetime.fromtimestamp(lastmod).strftime('%y%m%d')
			else:
				self.update=True
				lastupdate=current_date
		
			if current_date !=lastupdate or self.update:
				cmd="LANG=C LANGUAGE=en apt-get update; "
			else:
				for item in self.epi_conf.get("pkg_list",[]):
					app=item.get("name","")
					if app in self.packages_selected:
						update_repo=False
						app=item["name"]
						command=f"LANG=C LANGUAGE=en apt-cache policy {app}"
						p=subprocess.Popen(command,shell=True, stdout=subprocess.PIPE)
						output,_=p.communicate()
						if output:
							lines = output.decode(errors="ignore").splitlines()
							if len(lines)<=2:
								update_repo=True
							else:
								try:
									update_repo=lines[2].split(":")[1].strip() == ""
								except:
									update_repo=True
						else:
							update_repo=True

						if update_repo:
							cmd="LANG=C LANGUAGE=en apt-get update; "
							self._show_debug("check_update_repos",f"Required update: {update_repo} - Command to update: {cmd}")
							return cmd		

		
		self._show_debug("check_update_repos",f"Required update: {update_repo} - Command to update: {cmd}")

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
		
		self._show_debug("check_arquitecture",f"Required i386: {self.force32} - Command to add i386:{cmd}")
		
		return cmd		

	#def check_arquitecture	
	
	def add_repository_keys(self,order):

		self.epi_conf=self.epiFiles[order]
		self.epi_order=order
		self.type=self.epi_conf["type"]
		cmd=""
		cmd_parts=[]
		self.add_key=False

		if self.type not in ["apt","mix"]:
			self._show_debug("add_repository_keys",f"Command to add keys: {cmd}")
			return cmd
			
		repos_list=self.epi_conf.get("repository",[])

		if repos_list:
			with open(self.epi_sources,'w') as f:
				for item in repos_list:
					url=item.get("url","")
					if url:
						for line in url.split(";"):
							f.write(line+'\n')
					
					key_cmd=item.get("key_cmd","")
					if key_cmd:
						cmd_parts.append(f"{key_cmd};")
						self.add_key=True
						continue	
					
					script_conf=self.epi_conf.get("script",{})
					if script_conf.get("addRepoKeys"):
						script_path=script_conf.get("name","")
						if script_path and os.path.exists(script_path):
							cmd_parts.append(f'{script_path} addRepoKeys;')
							self.add_key=True

		if not self.add_key:
			cmd_parts,append("apt-get update;")

		cmd="".join(cmd_parts)
		self._show_debug("add_repository_keys",f"Command to add keys: {cmd}")
		return cmd		

	#def add_repository_keys	


	def get_app_version(self,item=None):

		item=item or {}
		self.force32=self.epi_conf.get("force32",False)
		version=item.get("version",{})

		if self.force32:
			version=version.get("32b","")
		elif 'all' in version:
			version=version.get("all","")
		else:
			if platform.architecture()[0]=='64bit':	
				version=version.get("64b","")
			else:
				version=version.get("32b","")
			
		self._show_debug("get_app_version",f"Version to install: {version}")

		return version

	def download_app(self, pkg_id):

		self.manage_download = True
		self.download_folder = []
		self.type = self.epi_conf.get("type")

		cmd = ""
		cmd_file=""
		external_script=""

		if self.type in self.types_without_download:
			self._show_debug("download_app", f"Command to download: {cmd}")
			return cmd

		script_conf = self.epi_conf.get("script", {})
		if script_conf.get("download"):
			script_path = script_conf.get("name", "")
			if os.path.exists(script_path):
				self.manage_download = False
				external_script = f"{script_path} download "

		selected_items = [
			item for item in self.epi_conf.get("pkg_list", [])
			if item["name"] in self.packages_selected and (pkg_id == "all" or item["name"] == pkg_id)
		]

		if self.type in self.types_with_download:
			if self.type == "file" and not self.manage_download:
				pkg_names = " ".join(item["name"] for item in selected_items)
				cmd = f"{external_script}{pkg_names}"
			else:
				for item in selected_items:
					cmd = self._get_download_cmd(self.type, item, cmd)

		elif self.type == "mix":
			for item in selected_items:
				i_type = item.get("type")
				if i_type in self.types_with_download:
					if not self.manage_download and i_type == "file":
						cmd_file += f"{item['name']} "
					else:
						cmd = self._get_download_cmd(i_type, item, cmd)

			if cmd_file: 
				 cmd = f"{cmd} {external_script}{cmd_file}".strip()

		if cmd.strip():
			self.token_result_download = tempfile.mkstemp("_result_download")
			cmd = f"{cmd.strip()}; echo $? > {self.token_result_download[1]};"

		self._show_debug("download_app", f"Command to download: {cmd}")

		return cmd
		
	#def download_app

	def _get_download_cmd(self,item_type,item,cmd):

		self.download_folder=[]
		tmp_file=""
		version=self.get_app_version(item)
		url=item.get("url_download","")

		if item_type=="deb": 
			file_name=f"{item["name"]}.deb"
		elif item_type=="file":
			file_name=item.get("alias_download", version)
		else:
			file_name=version	

		tmp_file = os.path.join(self.download_path, file_name)
		self.download_folder.append(tmp_file)
		
		if os.path.exists(tmp_file):
			cmd = f"{cmd.strip()}; rm -f {tmp_file};".strip()
		
		cmd=f'{cmd.strip()} wget {url}{version} --progress=bar:force --no-check-certificate -O {tmp_file}'
		
		return cmd

	#def _get_download_cmd

	def check_download(self,pkg_id):

		result=True
		content=""
		
		if self.type not in self.types_without_download:
			count=0
			pkgs_todownload=len(self.download_folder)

			if len(self.download_folder)>0:
				for item in self.download_folder:
					if os.path.exists(item):
						if pkg_id!="all" and pkg_id not in item:
							pass
						else:
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

		self._show_debug("check_download",f"Downlodad status: Result: {result} - Token Content: {content}")
		return result

	#def check_download		

	def preinstall_app(self,pkg_id):
	
		cmd=""

		if len(self.epi_conf["script"])>0:
			self.token_result_preinstall=tempfile.mkstemp("_result_preinstall")
			script=self.epi_conf["script"]["name"]
			if os.path.exists(script):
				cmd="%s preInstall "%script
				for item in self.epi_conf["pkg_list"]:
					if item["name"] in self.packages_selected:
						if pkg_id!="all" and item["name"]!=pkg_id:
							pass
						else:
							cmd+="%s "%item["name"]

				cmd='%s; echo $? > %s;'%(cmd,self.token_result_preinstall[1])

		self._show_debug("preinstall_app",f"Preinstall Command: {cmd}")
		return cmd		

	#def preinstall_app	
	
	def check_preinstall(self,pkg_id):
		
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

		self._show_debug("check_preinstall",f"Presintall result: Result: {result} - Token content: {content}")
	
		return result

	#def check_preinstall_app	

	def install_app(self,calledfrom,pkg_id):
	
		self.token_result_install=""
		pkgs_apt=0
		add_i386=""
		cmd=""

		info_to_install=self._get_app_to_install(pkg_id)

		if self.type=="apt" or info_to_install[0]=="apt":
			cmd=self._get_install_cmd_base(calledfrom,"apt")	
			cmd="%s%s"%(cmd,info_to_install[1])
				
		elif self.type=="deb" or info_to_install[0]=="deb":
			pkg=""
			cmd=self._get_install_cmd_base(calledfrom,"deb")
			for item in self.download_folder:
				if os.path.exists(item):
					for app in info_to_install[1]:
						if app in item:
							pkg="%s %s"%(pkg,item)
							break
						
			cmd=cmd+pkg	

		elif self.type=="localdeb":
			cmd=self._get_install_cmd_base(calledfrom,"apt")
			for item in self.epi_conf["pkg_list"]:
				name=item["version"]["all"]
				pkg=os.path.join(item["url_download"],name)
				if pkg_id!="all" and item["name"]!=pkg_id:
					pass
				else:
					cmd="%s%s"%(cmd,pkg)

		elif self.type=="file" or info_to_install[0]=="file":
			cmd=self._get_install_file_cmd_base()
			if cmd !="":
				cmd="%s %s"%(cmd,info_to_install[1])
				cmd_file_token='; echo $? > %s'%self.token_result_install[1]
				cmd='%s%s'%(cmd,cmd_file_token)
		
		elif self.type=="snap" or info_to_install[0]=="snap":
			cmd=self._get_install_snap_cmd_base()
			cmd="%s%s"%(cmd,info_to_install[1])
			
		elif self.type=="flatpak" or info_to_install[0]=="flatpak":
			cmd=self._get_install_flatpak_cmd_base()
			cmd="%s%s"%(cmd,info_to_install[1])
		
		cmd="%s;"%cmd
		cmd=cmd.strip()
		if cmd==";":
			cmd=""
	
		self._show_debug("install_app",f"Install Command: {cmd}")

		return cmd	

	#def install_app

	def _get_app_to_install(self,pkg_id):

		app_to_install=""
		app_type=""

		for item in self.epi_conf["pkg_list"]:
			if item["name"] in self.packages_selected:
				app=item["name"]
				if pkg_id!="all" and pkg_id!=app:
					pass
				else:
					app_to_install="%s %s"%(app_to_install,app)
					if self.type=="mix":
						app_type=item["type"]
						break

		return [app_type,app_to_install]

	#def _get_app_to_install

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

	def _get_install_file_cmd_base(self):

		cmd_tmp=""
		self.token_result_install=tempfile.mkstemp("_result")
		script=self.epi_conf["script"]["name"]
		
		if os.path.exists(script):
			cmd_tmp="%s installPackage "%script	
		
		return cmd_tmp 

	#def _get_install_file_cmd_base	

	def _get_install_snap_cmd_base(self):

		cmd="snap install "
		return cmd

	#def _get_install_snap_cmd_base

	def _get_install_flatpak_cmd_base(self):

		cmd="flatpak -y --system install "
		return cmd

	#def _get_install_flatpak_cmd_base

	def update_keyring(self):

		cmd=""
		if os.path.exists(self.epi_keyring_path):
			dest_path=os.path.join(self.keyring_path,self.epi_keyring_file+".gpg")
			shutil.copy(self.epi_keyring_path,dest_path)
			cmd="apt-get update;"
		else:
			if self.add_key:
				cmd="apt-get update;"
				
		return cmd
		
	#def update_keyring			

	def check_install_remove(self,action,pkg_id):

		dpkg_status = {}
		count_not_installed = 0
		pkgs_installed_count = 0
		pkgs_ref = []
		result = False
		content = ""

		if action == "install":
			epi_type = self.type
			config = self.epi_conf
			if hasattr(self, 'token_result_install') and self.token_result_install:
				token = self.token_result_install[1] 
			else:
				token=""
		else:
			config = self.epiFiles[0]
			epi_type = config.get("type")
			if hasattr(self, 'token_result_remove') and self.token_result_remove: 
				token = self.token_result_remove[1]
			else:
				token=""

		selection_enabled = config.get("selection_enabled", {}).get("active", False)
		pkgs_list = config.get("pkg_list", [])
		file_with_list = (epi_type == "file" and selection_enabled)

		if not file_with_list and epi_type == "file":
			if pkgs_list:
				target_pkg_id = pkgs_list[0]["name"]
			else:
				target_pkg_id=pkg_id
		else:
			for item in pkgs_list:
				name = item["name"]
				if pkg_id != "all" and name != pkg_id:
					continue

				if name in self.packages_selected:
					if action == "remove":
						is_blocked = (name in self.blocked_remove_skipped_pkgs_list or (epi_type != "file" and name in self.blocked_remove_pkgs_list))
						if not is_blocked:
							pkgs_ref.append(name)
					else:
						pkgs_ref.append(name)

		if epi_type == "file" and not file_with_list:
			if token and os.path.exists(token):
				with open(token, 'r') as f:
					content = f.readline().strip()
				result = ('0' in content)
				os.remove(token)
			else:
				status = self.check_pkg_status(target_pkg_id, epi_type, self.check_getStatus_byScript(0))
				is_installed = (status == "installed")
				if action == "install": 
					result = is_installed
				else:
					result= not is_installed

		else:
			if epi_type == "mix" and action == "install":
				order = self.epi_order
			elif epi_type in ["mix", "file"]:
				order = 0
			else:
				order = ""
			script = self.check_getStatus_byScript(order)
			for item in pkgs_list:
				name = item["name"]
				if pkg_id != "all" and name != pkg_id:
					continue

				if name in self.packages_selected:
					if epi_type == "mix":
						p_type = item["type"] 
					else:
						p_type=epi_type

					status = self.check_pkg_status(name, p_type, script)
					dpkg_status[name] = status
					if status != "installed":
						count_not_installed += 1
				else:
					if self.pkg_info.get(name, {}).get("status") == "installed":
						pkgs_installed_count += 1

			if action == "install":
				result = (count_not_installed == 0)
			else:
				result = (count_not_installed > 0 and count_not_installed == len(pkgs_ref))
				self.partial_installed = (pkgs_installed_count > 0)

		self._show_debug("check_install_remove", f"Action: {action} - Result: {result} - Dpkg Status: {dpkg_status} - Token: {content}")
		
		return dpkg_status, result

	#def check_install_remove	

	def postinstall_app(self,pkg_id):
		
		cmd=""
		
		if len(self.epi_conf["script"])>0:
			self.token_result_postinstall=tempfile.mkstemp("_result_postinstall")
			script=self.epi_conf["script"]["name"]
			if os.path.exists(script):
				cmd="%s postInstall "%script
				for item in self.epi_conf["pkg_list"]:
					if item["name"] in self.packages_selected:
						if pkg_id!="all" and item["name"]!=pkg_id:
							pass
						else:
							cmd+="%s "%item["name"]

				cmd='%s; echo $? > %s;'%(cmd,self.token_result_postinstall[1])

		self._show_debug("postinstall_app",f"Postinstall Command:{cmd}")

		return cmd	

	#def postinstall_app	
	
	def check_postinstall(self,pkg_id):
		
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

		self._show_debug("check_postinstall",f"Postinstall result: Result: {result} - Token content: {content}")
		
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

	def uninstall_app(self,order,pkg_id):

		cmd=""

		if self.epiFiles[order]["script"]["remove"]:
			self.token_result_remove=tempfile.mkstemp("_result_remove")
			script=self.epiFiles[order]["script"]["name"]
			if os.path.exists(script):
				cmd="%s remove "%script
				for item in self.epiFiles[order]["pkg_list"]:
					if item["name"] in self.packages_selected:
						if item["name"] not in self.blocked_remove_pkgs_list:
							if item["name"] not in self.blocked_remove_skipped_pkgs_list:
								if pkg_id!="all" and item["name"]!=pkg_id:
									pass
								else:
									cmd+="%s "%item["name"]

				cmd='%s; echo $? > %s;'%(cmd,self.token_result_remove[1])
		
		self._show_debug("uninstall_app",f"Uninstall Command: {cmd}")

		return cmd

	#def uninstall_app	

	def zerocenter_feedback(self,order,action,result=None):

		zomando_name=self.zomando_name[order]
		cmd=""

		if zomando_name!="":
			if action=="init":
				cmd="zero-center add-pulsating-color " +zomando_name
			else:
				if self.epiFiles[order]["selection_enabled"]["active"]:
					if self.get_zmd_status(order)!=0:
						cmd="zero-center remove-pulsating-color %s ;zero-center set-non-configured %s"%(zomando_name,zomando_name)
					else:
						cmd="zero-center remove-pulsating-color %s"%zomando_name
				elif action=="install":
					if result:
						cmd="zero-center remove-pulsating-color %s ;zero-center set-configured %s"%(zomando_name,zomando_name)
					else:
						cmd="zero-center remove-pulsating-color %s ;zero-center set-failed %s"%(zomando_name,zomando_name)
				elif action=="uninstall":
					if result:
						cmd="zero-center remove-pulsating-color %s ;zero-center set-non-configured %s"%(zomando_name,zomando_name)
					else:
						cmd="zero-center remove-pulsating-color %s ;zero-center set-failed %s"%(zomando_name,zomando_name)

			os.system(cmd)		

	#def zero-center_feedback	
	
	def cli_install(self):

		remote_available=[]
		selection_enabled={}
		zomando=""
		required_x=False
		only_gui_available=[]

		if self.epiFiles[0]["required_x"]:
			required_x=True
			#return [remote_available,selection_enabled]									

		path_custom_icons=self.epiFiles[0]["custom_icon_path"]
		selection_enabled["selection_enabled"]=self.epiFiles[0]["selection_enabled"]
		zomando=self.epiFiles[0]["zomando"]
		add_to_list=True

		for item in self.epiFiles[0]["pkg_list"]:
			try:
				if item["required_x"]:
					add_to_list=False
			except:
				if required_x:
					add_to_list=False
				else:
					add_to_list=True

			pkg={}
			pkg["name"]=item["name"]
			try:
				pkg["custom_name"]=item["custom_name"]
			except:
				pkg["custom_name"]=item["name"]
			try:
				if path_custom_icons!="":
					pkg["custom_icon"]=os.path.join(path_custom_icons,item["custom_icon"])
				else:
					pkg["custom_icon"]=""
			except:
				pkg["custom_icon"]=""
			try:
				pkg["default_pkg"]=item["default_pkg"]
			except:
				pkg["default_pkg"]=False
					
			try:
				pkg["skip_flavours"]=item["skip_flavours"]
			except:
				pkg["skip_flavours"]=[]
			try:
				pkg["skip_groups"]=item["skip_groups"]
			except:
				pkg["skip_groups"]=[]
					
			if add_to_list:
				remote_available.append(pkg)
			else:
				only_gui_available.append(pkg)			
		
		return [remote_available,selection_enabled,zomando,required_x,only_gui_available]									

	#def cli_install	

	def list_available_epi(self):

		self.remote_available_epis=[]
		self.available_epis=[]
		self.all_available_epis=[]
		self.cli_available_epis=[]
		self.skipped_pkgs_groups=[]
		self.skipped_pkgs_flavours=[]

		for item in listdir(self.zmd_paths):
			t=join(self.zmd_paths,item)
			if isfile(t):
				f=open(t,'r')
				content=f.readlines()
				for line in content:
					if '.epi' in line:
						line=line.split('epi-gtk')
						try:
							line=line[1].strip(" ").split(" ")
							line=line[0].strip("\n").strip(" ")
							check=self.read_conf(line,False,True)["status"]
							if check:
								remote=self.cli_install()
								tmp={}
								epi_name=os.path.basename(line)
								tmp[epi_name]={}
								tmp[epi_name]=remote[1]
								tmp[epi_name]["zomando"]=remote[2]
								tmp[epi_name]["pkg_list"]=remote[0]
								if len(remote[0])>0:
									if not remote[3]:
										self.cli_available_epis.append(tmp)
										if not self.is_zmd_service(remote[2]):
											tmp[epi_name]["pkg_list"]=self._clean_pkg_skipped_for_client(remote[0])
											self.remote_available_epis.append(tmp)
								tmp[epi_name]["only_gui_available"]=remote[4]
								self.all_available_epis.append(tmp)
								self.available_epis.append(line)

						except Exception as e:
							pass	
						
	#def list_available_epi	

	def check_remote_epi(self,epi):

		tmp_cli=[]
		tmp_gui=[]
		epi=os.path.basename(epi)
		for item in self.all_available_epis:
			for element in item:
				if epi==element:
					for pkg in item[element]["pkg_list"]:
						if not self.is_pkg_skipped_for_flavour(pkg["name"],pkg["skip_flavours"]):
							if self.is_pkg_skipped_for_group(pkg["name"],pkg["skip_groups"]) in [0,2]:
								tmp_cli.append(pkg)
					#return item[element]["pkg_list"]
					for pkg in item[element]["only_gui_available"]:
						if not self.is_pkg_skipped_for_flavour(pkg["name"],pkg["skip_flavours"]):
							if self.is_pkg_skipped_for_group(pkg["name"],pkg["skip_groups"]) in [0,2]:
								tmp_gui.append(pkg)

		return tmp_cli,tmp_gui
	
	#def check_remote_epi
	 				
	def _get_epi_path(self,epi):

		epi_path=""
		epi_extension=epi.split(".epi")
		
		if len(epi_extension)>1:
			for item in self.available_epis:
				if epi in item:
					epi_path=item
					break

		return epi_path

	#def _get_epi_path

	def get_epi_deb(self,epi=None):

		epi_deb=""
		if epi!=None:	
			epi_path=self._get_epi_path(epi)
			cmd="dpkg -S %s"%epi_path
			p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
			poutput,perror=p.communicate()

			if len(poutput)>0:
				if type(poutput) is bytes:
					poutput=poutput.decode()

				epi_deb=poutput.split(":")[0]

		return epi_deb

	#def get_epi_deb

	def init_n4d_client(self):

		try:
			self.n4dClient=client.Client('https://localhost:9779')
		except Exception as e:
			self._show_debug("init_n4d_client_app","Error:%s"%(str(e)))
			self.n4dClient=None
			pass

	#def init_n4d_client

	def get_zmd_status(self,order):

		'''
			zmd status code:
				 0: not-configured
				 1: configured
				-1: failed
		'''

		zmd_status=0
		
		if self.epiFiles[order]["check_zomando_state"]:
			if self.n4dClient!=None:
				try:
					zmds_info=self.n4dClient.get_variable("ZEROCENTER")
				except Exception as e:
					self._show_debug("get_zmd_status.Get ZEROCENTER variable",f"Error: {e}")
					return 1

				if len(zmds_info):
					try:
						status=zmds_info[self.zomando_name[order]].get('state')
						zmd_status=status
					except Exception as e:
						self._show_debug("get_zmd_status. Get zmd status",f"Error: {e}")
						pass 
			else:
				zmd_status=1
		else:
			zmd_status=1

		return zmd_status
	
	#def get_zmd_status

	def check_remove_meta(self):

		self.blocked_remove_pkgs_list=[]
		tmp_blocked_remove_pkgs_list=[]

		if self.check_meta:
			for pkg in self.packages_selected:
				tmp_blocked_remove_pkgs_list=[]
				cmd="apt-get remove --simulate %s"%pkg
				psimulate=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
				rawoutputsimulate=psimulate.stdout.readlines()
				rawpkgstoremove=[aux.decode().strip() for aux in rawoutputsimulate if aux.decode().startswith('Remv')]

				r=[aux.replace('Remv ','') for aux in rawpkgstoremove]

				if len(r)>0:
					for item in r:
						tmp=item.split(' ')[0]
						tmp_blocked_remove_pkgs_list.append(tmp)

					for item in tmp_blocked_remove_pkgs_list:
						if item in self.lliurex_meta_pkgs:
							self.blocked_remove_pkgs_list.append(pkg) 
							break	

			if len(self.blocked_remove_pkgs_list)>0:
				self.meta_removed_warning=True

			self._show_debug("check_remove_meta. Check if pkg uninstall remove lliurex-meta",f"List: {self.blocked_remove_pkgs_list}")

		else:
			self.meta_removed_warning=False
			self._show_debug("check_remove_meta.Check if pkg uninstall remove lliurex-meta","Checking are disabled")
 

		return self.meta_removed_warning


	#def check_remove_meta

	def is_zmd_service(self,zomando):

		app_file=zomando+".app"
		app_path=os.path.join(self.app_folder,app_file)
		if os.path.exists(app_path):
			with open(app_path,'r',encoding='utf-8') as fd:
				content=fd.readlines()
				fd.close()
			
			for line in content:
				key,value=line.split("=")
				if key=="Category":
					tmp_categ=value.strip("\n")
					if tmp_categ=="Services":
						return True 
					else:
						return False 
		else:
			return True

	#def is_zmd_service

	def check_getStatus_byScript(self,order):

		script=""
		if order!="":
			try:
				tmp_script=self.epiFiles[order]["script"]["name"]
				if os.path.exists(tmp_script):
					if self.epiFiles[order]["script"]["getStatus"]:
						script=tmp_script
			except Exception as e:
				pass

		return script

	#def check_getStatus_byScript

	def _check_download_byScript(self,order):

		download_byScript=False

		if order!="":
			try:
				tmp_script=self.epiFiles[order]["script"]["name"]
				if os.path.exists(tmp_script):
					if self.epiFiles[order]["script"]["download"]:
						download_byScript=True
			except Exception as e:
				pass

		return download_byScript

	#def _check_download_byScript

	def empty_cache_folder(self):

		if os.path.exists(self.download_path):
			for filename in os.listdir(self.download_path):
				file_path=os.path.join(self.download_path,filename)
				try:
					if os.path.isfile(file_path):
						os.remove(file_path)
				except:
					pass

	#def empty_cache_folder

	def _get_flavours(self):

		self._flavours=[]
		cmd='lliurex-version -v'
		p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
		result=p.communicate()[0]
		if type(result) is bytes:
			result=result.decode()
			self._flavours = [ x.strip() for x in result.split(',') ]	
	
	#def _getFlavours

	def is_pkg_skipped_for_flavour(self,pkg_id,skipped_flavours):

		for flavour in self._flavours:
			for element in skipped_flavours:
				if element in flavour:
					if pkg_id not in self.skipped_pkgs_flavours:
						self.skipped_pkgs_flavours.append(pkg_id)
					return True

		return False

	#def is_pkg_skipped_for_flavour

	def _get_user_groups(self):

		try:
			user=pwd.getpwuid(int(os.environ["PKEXEC_UID"])).pw_name
			gid = pwd.getpwnam(user).pw_gid
			groups_gids = os.getgrouplist(user, gid)
			self._user_groups = [ grp.getgrgid(x).gr_name for x in groups_gids ]
		except:
			try:
				user=os.environ["USER"]
				gid = pwd.getpwnam(user).pw_gid
				groups_gids = os.getgrouplist(user, gid)
				self._user_groups = [ grp.getgrgid(x).gr_name for x in groups_gids ]
			except:
				pass	

	#def _get_user_groups

	def is_pkg_skipped_for_group(self,pkg_id,skipped_groups):

		'''
			Values for pkg_skipped:
			- 0: pkg not skipped
			- 1: pkg skipped for all actions
			- 2: pkg skipped for remove action
		'''
		pkg_skipped=0
		if 'admins' not in self._user_groups:
			for item in skipped_groups:
				if item["group"] in self._user_groups:
					if item["action"]=="all":
						pkg_skipped=1
					elif item["action"]=="remove":
						pkg_skipped=2
						if pkg_id not in self.skipped_pkgs_groups:
							self.skipped_pkgs_groups.append(pkg_id)
					break

		return pkg_skipped

	#def is_pkg_skipped_for_group

	def _is_remove_lock_for_group(self,skipped_groups):

		if 'admins' not in self._user_groups:
			if len(skipped_groups)>0:
				for group in skipped_groups:
					if group in self._user_groups:
						return True

		return False

	#def _is_remove_lock_for_group

	def check_remove_skip_pkg(self):

		self.skipped_pkg_warning=False
		self.blocked_remove_skipped_pkgs_list=[]

		for item in self.packages_selected:
			if item in self.skipped_pkgs_groups:
				self.skipped_pkg_warning=True
				if item not in self.blocked_remove_skipped_pkgs_list:
					self.blocked_remove_skipped_pkgs_list.append(item)
				break

		self._show_debug("check_remove_skip_pkg. Check if pkg uninstall is in skipped list",f"List: {self.blocked_remove_skipped_pkgs_list}")

		return self.skipped_pkg_warning

	#def check_remove_skip_pkg

	def _clean_pkg_skipped_for_client(self,pkg_list):

		tmp_list=[]

		for pkg in pkg_list:
			match=False
			if len(pkg["skip_flavours"])>0:
				for item in pkg["skip_flavours"]:
					if 'client' in item:
						match=True
						break
			if not match:
				tmp_list.append(pkg)

		return tmp_list

	#def _clean_pkg_skipped_for_client

#class EpiManager


if __name__=="__main__":
	
	epi=EpiManager()
