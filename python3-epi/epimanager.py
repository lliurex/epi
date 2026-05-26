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
			storeProxy=storeBus.get_object('net.lliurex.rebost','/net/lliurex/rebost')
			self.dbusStore=dbus.Interface(storeProxy,dbus_interface='net.lliurex.rebost')
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
		
		try:
			with urllib.request.urlopen(url,timeout=5) as response:
				result=(True,f"Connection successfully")
		except Exception as e:
			result=(False,str(e))
		
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
			else:
				if any(epi_file in item for item in self.epi_with_json_problems):
					return {"status":False,"error":"json"}
				
				for item in self.epi_with_depends_problems:
					if epi_file in item.get("epi",""):
						return {"status":False,"error":"depends","data":item.get("depends","")}


		if not os.path.isfile(epi_file):
			self._show_debug("read_conf", f"Epi file does not exist or path is invalid: {epi_file}")
			return {"status": False, "error": "path","depends":""}

		try:
			with open(epi_file, 'r') as f:
				epi_load = json.load(f)
		except Exception as e:
			self._show_debug("read_conf", f"Epi file is not a valid JSON. Error: {e}")
			return {"status": False, "error": "json","depends":""}

		if not epi_load:
			self._show_debug("read_conf", f"Epi file is empty: {epi_file}")
			return {"status": False, "error": "empty","depends":""}

		epi_conf = self.epi_base.copy()
		epi_conf.update(epi_load)

		self.epiFiles[self.order] = epi_conf
		self.zomando_name[self.order] = epi_conf.get("zomando", "")

		depends = epi_conf.get("depends", "")
		if depends:
			self.order += 1
			try:
				result=self.read_conf(depends)
				if not result["status"]:
					result["depends"]=depends
					return result				
			except Exception as e:
				self._show_debug("read_conf", f"Error: {e}")
				pass

		return {"status": True, "error": "","depends":""}	

	#def read_conf		

	def check_script_file(self):

		script=self.epiFiles[0]["script"]

		if len(script)>0:
			script_path=script.get("name","")
			if os.path.exists(script_path) and os.path.isfile(script_path):
				if not os.access(script_path,os.X_OK):
					return {"status":False,"error":"permissions"}
			else:
				self._show_debug("check_script_file",f"Script file not exits or path is not valid:{script_path}")
				return {"status":False,"error":"path"}

		return {"status":True,"error":""}
	
	#def check_script_file

	def get_pkg_info(self):

		pkg_list=[]
		self.pkg_info={}

		if not self.get_available_list:
			self.skipped_pkgs_groups=[]
			self.skipped_pkgs_flavours=[]

		if self.dbusStore:
			self.showMethod=self.dbusStore.get_dbus_method('show')                            
				
		items_to_pop=[]

		for item,epi_file in self.epiFiles.items():
			pkg_list=epi_file.get("pkg_list",[])
			type_epi=epi_file.get("type","")
			if type_epi:
				if type_epi not in self.valid_epi_files:
					self._show_debug("get_pkg_info",f"Unable to get pkg info. Key 'type' has a not valid value: {type_epi}")
					break
			else:
				self._show_debug("get_pkg_info","Unable to get pkg info. Key 'type' not defined epi file")
				break
			
			script=self.check_getStatus_byScript(item)
			info=self.get_basic_info(pkg_list,item,type_epi,script)

			if not info:
				self.pkg_info={}
				break

			if item==0:
				self.lock_remove_for_group=self._is_remove_lock_for_group(epi_file["lock_remove_groups"])	
				self.check_meta=epi_file["check_meta"]

			all_installed = all(info.get(el["name"], {}).get("status") == "installed" for el in pkg_list)
			any_installed = any(info.get(el["name"], {}).get("status") == "installed" for el in pkg_list)

			if all_installed:
				if item>0:
					if self.get_zmd_status(item)==1:
						items_to_pop.append(item)
					else:
						epi_file["status"]="availabled"
						self.pkg_info.update(info)

				else:
					epi_file["status"]="installed"
					self.pkg_info.update(info)
			else:
				if item == 0 and any_installed and epi_file.get("selection_enabled", {}).get("active"):
					self.partial_installed=True
				
				epi_file["status"]="availabled"
				self.pkg_info.update(info)
			
	
		for item in items_to_pop:
			self.epiFiles.pop(item)
			self.zomando_name.pop(item)

		self._show_debug("get_pkg_info",f"Content of epi file: {self.epiFiles}")
		self._show_debug("get_pkg_info",f"Packages info: {self.pkg_info}")
						
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

			if not pkg_type:
				self._show_debug("get_pkg_info",f"Unable to get pkg info. Key 'pkg_type' not defined in 'pkg_list' for pkg {item['name']}")
				pkg_info={}
				break
		
			if pkg_type not in self.valid_epi_files:
				self._show_debug("get_pkg_info",f"Unable to get pkg info. Key 'pkg_type' for pkg {item['name']} has incorrect value: {pkg_type}")
				pkg_info={}
				break
			
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
							pkg_info={}
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
			except Exception as e:
				self._show_debug("_get_store_info",f"pkg: {pkg}; error parsing json: {e}")
		
	#def get_store_info			

	def check_pkg_status(self,pkg,pkg_type,script):

		if pkg_type != "file" or not script:
			return self._get_pkg_status(pkg, pkg_type)

		try:
			cmd = [script, "getStatus", pkg]
			process = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)

			stdout, _ = process.communicate(timeout=30)

			self._show_debug("check_pkg_status",f"pkg: {pkg}; status result by script: {stdout}")

			lines=(stdout or "").splitlines()
			first_line =lines[0].strip() if lines else ""
			if first_line == "0":
				return "installed"

			if first_line == "Not found":
				return self._get_pkg_status(pkg, pkg_type)

			return "available"

		except Exception as e:
			self._show_debug("check_pkg_status",f"pkg: {pkg}; Error: {e}")
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
			return "available"

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
				p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
				poutput=p.communicate(timeout=30)

				output_str = poutput.decode("utf-8", errors="replace").strip()

				if output_str:
					first_line = output_str.splitlines()[0]
					parts = first_line.split("||", 1)
					summary = parts[0]
					if len(parts) > 1:
						description = parts[1]
		except Exception as e:
			self._show_debug("get_localdeb_info",f"pkg: {pkg}; Error: {e}")
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
		
		except Exception as e:
			self._show_debug("test_install",f"Error: {e}",)
			return result_test

    #def test_install

	def check_update_repos(self):
		
		#Only update repos if needed
		
		cmd=""
		update_repo=False

		if self.type not in ["apt","mix"]:
			self._show_debug("check_update_repos",f"Required update: {update_repo} - Command to update: {cmd}")
			return cmd
	
		current_date=datetime.date.today().strftime('%y%m%d')
		filename='/var/cache/apt/pkgcache.bin'

		if os.path.exists(filename):
			lastmod=os.path.getmtime(filename)
			lastupdate=datetime.datetime.fromtimestamp(lastmod).strftime('%y%m%d')
		else:
			self.update=True
			lastupdate=""
		
		if current_date !=lastupdate or self.update:
			cmd="LANG=C LANGUAGE=en apt-get update; "
			self._show_debug("check_update_repos",f"Required update: {update_repo} - Command to update: {cmd}")
			return cmd

			
		for item in self.epi_conf.get("pkg_list",[]):
			app=item.get("name","")
			
			if not app or app not in self.packages_selected:
				continue
			
			update_repo=False
			command=f"LANG=C LANGUAGE=en apt-cache policy {app}"
			p=subprocess.Popen(command,shell=True, stdout=subprocess.PIPE,text=True)
			output,_=p.communicate()
			
			if output:
				lines = output.splitlines()
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
		
		if not self.force32:
			self._show_debug("check_arquitecture",f"Required i386: {self.force32} - Command to add i386:{cmd}")
			return cmd		
		
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
			cmd_parts.append("apt-get update;")

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

	#def get_app_version

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

		self.token_result_download = tempfile.NamedTemporaryFile(suffix="_result_download",delete=False)
		self.token_result_download.close()

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

			cmd = f"{cmd} {external_script}{cmd_file}".strip()

		if cmd.strip():
			cmd = f"{cmd.strip()}; echo $? > {self.token_result_download.name};"

		self._show_debug("download_app", f"Command to download: {cmd}")

		return cmd
		
	#def download_app

	def _get_download_cmd(self,item_type,item,cmd):

		self.download_folder=[]
		tmp_file=""
		version=self.get_app_version(item)
		url=item.get("url_download","")

		if item_type=="deb": 
			file_name=f"{item['name']}.deb"
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

		if self.type in self.types_without_download:
			self._show_debug("check_download",f"Download status: Result: {result} - Token Content: {content}")
			return result
		
		pkgs_todownload=len(self.download_folder)

		count = sum( 1 for item in self.download_folder if os.path.exists(item) and (pkg_id == "all" or pkg_id in item))
		
		token_path=self.token_result_download.name
		
		if os.path.exists(token_path):
			result, content=self._handle_file_token(token_path)
			selection_active = self.epi_conf.get("selection_enabled", {}).get("active", False)
			
			if result and self.manage_download and count != pkgs_todownload and not selection_active:
				result=False
			elif not result and selection_active and count >0:
				result=True

		self._show_debug("check_download",f"Download status: Result: {result} - Token Content: {content}")
		
		return result

	#def check_download		
	
	def preinstall_app(self,pkg_id):
	
		cmd=""

		script_conf=self.epi_conf.get("script",{})

		if script_conf and "name" in script_conf:
			script_path=script_conf["name"]

			if os.path.exists(script_path):
				self.token_result_preinstall=tempfile.NamedTemporaryFile(suffix="_result_preinstall",delete=False)
				self.token_result_preinstall.close()

				selected_pkgs = [
					pkg["name"] for pkg in self.epi_conf.get("pkg_list", [])
						if pkg["name"] in self.packages_selected and (pkg_id == "all" or pkg["name"] == pkg_id)
				]
				if selected_pkgs:
					pkg_string = " ".join(selected_pkgs)
					cmd = f"{script_path} preInstall {pkg_string}; echo $? > {self.token_result_preinstall.name};"

		self._show_debug("preinstall_app",f"Preinstall Command: {cmd}")
		
		return cmd		

	#def preinstall_app	
	
	def check_preinstall(self,pkg_id):
		
		result=True
		content=""

		try:
			if os.path.exists(self.token_result_preinstall.name):
				result, content=self._handle_file_token(self.token_result_preinstall.name)
		except Exception:			
			pass

		self._show_debug("check_preinstall",f"Presintall result: Result: {result} - Token content: {content}")
	
		return result

	#def check_preinstall_app	

	def install_app(self,calledfrom,pkg_id):
	
		self.token_result_install=[]
		cmd=""
		info_to_install=self._get_app_to_install(pkg_id)
		install_type = info_to_install[0] if info_to_install[0] else self.type
		payload = info_to_install[1]

		simple_handlers = {
			"apt": lambda: f"{self._get_install_cmd_base(calledfrom, 'apt')}{payload}",
			"snap": lambda: f"{self._get_install_snap_cmd_base()}{payload}",
			"flatpak": lambda: f"{self._get_install_flatpak_cmd_base()}{payload}"
		}
		
		if install_type in simple_handlers:
			cmd = simple_handlers[install_type]()
			
		elif install_type =="deb":
			pkgs = [item for item in self.download_folder 
				if os.path.exists(item) and any(app in item for app in payload)]
			cmd = f"{self._get_install_cmd_base(calledfrom, 'deb')}{' '.join(pkgs)}"
			
		elif install_type =="localdeb":
			pkgs = []
			for item in self.epi_conf.get("pkg_list", []):
				if pkg_id == "all" or item["name"] == pkg_id:
					pkgs.append(os.path.join(item["url_download"], item["version"]["all"]))
			cmd = f"{self._get_install_cmd_base(calledfrom, 'apt')}{' '.join(pkgs)}"
			
		elif install_type == "file":
			base_cmd = self._get_install_file_cmd_base()
			if base_cmd:
				token_suffix = f'; echo $? > {self.token_result_install.name}' if self.token_result_install else ""
				cmd = f"{base_cmd} {payload}{token_suffix}"
				
		cmd = cmd.strip()
		if cmd and not cmd.endswith(";"):
			cmd += ";"
			
		if cmd==";":
			cmd=""
	
		self._show_debug("install_app",f"Install Command: {cmd}")

		return cmd	

	#def install_app

	def _get_app_to_install(self,pkg_id):

		apps=[]
		app_type=""

		for item in self.epi_conf.get("pkg_list",[]):
			name=item.get("name","")
			if name in self.packages_selected:
				if pkg_id=="all" or pkg_id==name:
					apps.append(name)
					if self.type=="mix":
						app_type=item.get("type","")
						break
		
		app_to_install=" ".join(apps)

		return [app_type,app_to_install]

	#def _get_app_to_install

	def _get_install_cmd_base(self,calledfrom,pkg_type):

		if self.epi_conf.get("required_dconf"):
			frontend = "kde" if calledfrom == "gui" else ""
			env_prefix = f"LANG=C LANGUAGE=en DEBIAN_FRONTEND={frontend}".strip()
		else:
			env_prefix = "LANG=C LANGUAGE=en DEBIAN_FRONTEND=noninteractive"

		pkg_commands = {
			"apt": "apt-get install --reinstall --allow-downgrades --yes ",
			"localdeb": "apt-get install --reinstall --allow-downgrades --yes ",
			"deb": "dpkg -i "
		}

		base_cmd = pkg_commands.get(pkg_type, "")

		return f"{env_prefix} {base_cmd}"

	# def _get_install_cmd_base

	def _get_install_file_cmd_base(self):

		self.token_result_install=tempfile.NamedTemporaryFile(suffix="_result",delete=False)
		self.token_result_install.close()
		script=self.epi_conf.get("script",{}).get("name","")
		
		if os.path.exists(script):
			return f"{script} installPackage "	
		
		return "" 

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

		if action=="install":
			return self._check_install(pkg_id)
		else:
			return self._check_remove(pkg_id)

	#def check_install_remove

	def postinstall_app(self, pkg_id):

		cmd = ""
		script_conf = self.epi_conf.get("script", {})
		script_path = script_conf.get("name", "")

		if script_conf and os.path.exists(script_path):
			self.token_result_postinstall= tempfile.NamedTemporaryFile(suffix="_result_postinstall",delete=False)
			self.token_result_postinstall.close()
			
			pkgs_to_add = [
				item["name"] for item in self.epi_conf.get("pkg_list", [])
				if item["name"] in self.packages_selected and (pkg_id == "all" or item["name"] == pkg_id)
			]
			
			args = " ".join(pkgs_to_add)
			cmd = f"{script_path} postInstall {args}; echo $? > {self.token_result_postinstall.name};"
			self._show_debug("postinstall_app", f"Postinstall Command: {cmd}")
			
		return cmd

	#def postinstall_app	
	
	def check_postinstall(self,pkg_id):
		
		result=True
		content=""
		try:
			if os.path.exists(self.token_result_postinstall.name):
				result, content =self._handle_file_token(self.token_result_postinstall.name)
		except Exception:
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

		cmd = ""
		epi_file = self.epiFiles.get(order, {})
		script_conf = epi_file.get("script", {})
		script_path = script_conf.get("name", "")

		if script_conf.get("remove") and os.path.exists(script_path):
			self.token_result_remove = tempfile.NamedTemporaryFile(suffix="_result_remove",delete=False)
			self.token_result_remove.close()

			pkgs_to_remove = [
				item["name"] for item in epi_file.get("pkg_list", [])
				if (item["name"] in self.packages_selected and
					item["name"] not in self.blocked_remove_pkgs_list and
					item["name"] not in self.blocked_remove_skipped_pkgs_list and
					(pkg_id == "all" or item["name"] == pkg_id))
			]

			if pkgs_to_remove:
				args = " ".join(pkgs_to_remove)
				cmd = f"{script_path} remove {args}; echo $? > {self.token_result_remove.name};"
	
			self._show_debug("uninstall_app", f"Uninstall Command: {cmd}")

		return cmd

	#def uninstall_app
	
	def zerocenter_feedback(self,order,action,result=None):

		zomando_name = self.zomando_name.get(order, "")
		if not zomando_name:
			return

		remove_pulse = f"zero-center remove-pulsating-color {zomando_name}"
		set_non_cfg = f"zero-center set-non-configured {zomando_name}"
		set_cfg = f"zero-center set-configured {zomando_name}"
		set_failed = f"zero-center set-failed {zomando_name}"

		cmd = ""

		if action == "init":
			cmd = f"zero-center add-pulsating-color {zomando_name}"

		elif self.epiFiles[order]["selection_enabled"]["active"]:
			if self.get_zmd_status(order) != 0:
				cmd = f"{remove_pulse} ;{set_non_cfg}"
			else:
				cmd = remove_pulse
		elif action in ["install", "uninstall"]:
			if result:
				status_cmd = set_cfg if action == "install" else set_non_cfg
				cmd = f"{remove_pulse} ;{status_cmd}"
			else:
				cmd = f"{remove_pulse} ;{set_failed}"

		if cmd:
			subprocess.run(cmd,shell=True)
	
	#def zerocenter_feedback
	
	def cli_install(self):

		epi_zero = self.epiFiles[0]
		required_x = epi_zero.get("required_x", False)
		path_custom_icons = epi_zero.get("custom_icon_path", "")
		zomando = epi_zero.get("zomando", "")

		selection_enabled = {"selection_enabled": epi_zero.get("selection_enabled", {})}

		remote_available = []
		only_gui_available = []

		for item in epi_zero.get("pkg_list", []):
			item_requires_x = item.get("required_x", required_x)

			pkg = {
				"name": item["name"],
				"custom_name": item.get("custom_name", item["name"]),
				"default_pkg": item.get("default_pkg", False),
				"skip_flavours": item.get("skip_flavours", []),
				"skip_groups": item.get("skip_groups", []),
				"custom_icon": ""
			}

			custom_icon_file = item.get("custom_icon")
			if path_custom_icons and custom_icon_file:
				pkg["custom_icon"] = os.path.join(path_custom_icons, custom_icon_file)

			if item_requires_x:
				only_gui_available.append(pkg)
			else:
				remote_available.append(pkg)

		return {
			"remote_available": remote_available,
			"only_gui_available": only_gui_available,
			"selection_enabled": epi_zero.get("selection_enabled", {}),
			"zomando": epi_zero.get("zomando", ""),
			"required_x": required_x
		}

	#def cli_install
	
	def list_available_epi(self):

		self.remote_available_epis = []
		self.available_epis = []
		self.all_available_epis = []
		self.cli_available_epis = []
		self.skipped_pkgs_groups = []
		self.skipped_pkgs_flavours = []
		self.epi_with_json_problems=[]
		self.epi_with_depends_problems=[]

		if not os.path.exists(self.zmd_paths):
			return

		for item in os.listdir(self.zmd_paths):
			path_item = os.path.join(self.zmd_paths, item)

			if not os.path.isfile(path_item):
				continue

			try:
				with open(path_item, 'r') as f:
					content = f.readlines()

				for line in content:
					if '.epi' not in line or 'epi-gtk' not in line:
						continue

					parts = line.split('epi-gtk')
					if len(parts) < 2:
						continue

					epi_path = parts[1].strip().split(" ")[0].strip()
					conf = self.read_conf(epi_path, False, True)

					if not conf.get("status"):
						if conf.get("depends")!="" and conf.get("depends") not in self.epi_with_depends_problems:
							tmp={
								"epi":epi_path,
								"depends":conf.get("depends")
							}
							if tmp not in self.epi_with_depends_problems:
								self.epi_with_depends_problems.append(tmp)
						else:
							if conf.get("error")=="json":
								if epi_path not in self.epi_with_json_problems:
									self.epi_with_json_problems.append(epi_path)
						continue

					remote = self.cli_install()
					epi_name = os.path.basename(epi_path)

					epi_data = {
						"selection_enabled": remote["selection_enabled"],
						"zomando": remote["zomando"],
						"pkg_list": remote["remote_available"],
						"only_gui_available": remote["only_gui_available"]
					}

					tmp = {epi_name: epi_data}

					if len(remote["remote_available"]) > 0:
						if not remote["required_x"]:
							self.cli_available_epis.append(tmp)

							if not self.is_zmd_service(remote["zomando"]):
								clean_pkg_list = self._clean_pkg_skipped_for_client(remote["remote_available"])
								remote_tmp = {epi_name: {**epi_data, "pkg_list": clean_pkg_list}}
								self.remote_available_epis.append(remote_tmp)

					self.all_available_epis.append(tmp)
					self.available_epis.append(epi_path)

			except Exception as e:
				self._show_debug("list_available_epi", f"Error processing {item}: {e}")

	#def list_available_epi

	def check_remote_epi(self, epi):

		tmp_cli, tmp_gui = [], []
		target_epi = os.path.basename(epi)

		for item in self.all_available_epis:
			if target_epi not in item:
				continue

			epi_data = item[target_epi]

			to_process = [
				(epi_data.get("pkg_list", []), tmp_cli),
				(epi_data.get("only_gui_available", []), tmp_gui)
			]

			for source_list, target_list in to_process:
				for pkg in source_list:
					name = pkg["name"]
					skip_f = not self.is_pkg_skipped_for_flavour(name, pkg.get("skip_flavours", []))
					skip_g = self.is_pkg_skipped_for_group(name, pkg.get("skip_groups", [])) in [0, 2]

					if skip_f and skip_g:
						target_list.append(pkg)

			break 

		return tmp_cli, tmp_gui

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

		if epi is None:
			return ""

		epi_path=self._get_epi_path(epi)
		cmd=f"dpkg -S {epi_path}"
		p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
		poutput,_=p.communicate()

		if not poutput:
			return ""

		for line in poutput.strip().split("\n"):
			if ":" not in line:
				continue
			pkg,path=line.split(":",1)
			if path.strip()==epi_path:
				return pkg.strip()

		return ""

	#def get_epi_deb

	def init_n4d_client(self):

		try:
			self.n4dClient=client.Client('https://localhost:9779')
		except Exception as e:
			self._show_debug("init_n4d_client_app","Error:%s"%(str(e)))
			self.n4dClient=None
			pass

	#def init_n4d_client

	def get_zmd_status(self, order):

		"""
		zmd status code:
			0: not-configured
			1: configured
			1: failed
		"""
		
		if not self.epiFiles[order].get("check_zomando_state") or self.n4dClient is None:
			return 1
			
		try:
			zmds_info = self.n4dClient.get_variable("ZEROCENTER")
			if not zmds_info:
				return  0
		except Exception as e:
			self._show_debug("get_zmd_status.Get ZEROCENTER variable", f"Error: {e}")
			return 1
			
		try:
			zomando = self.zomando_name[order]
			return zmds_info.get(zomando, {}).get('state', 0)
		except Exception as e:
			self._show_debug("get_zmd_status. Get zmd status", f"Error: {e}")
			return 0

   	#def get_zmd_status

	def check_remove_meta(self):

		self.blocked_remove_pkgs_list = []
		self.meta_removed_warning = False

		if not self.check_meta:
			self._show_debug("check_remove_meta", "Checking is disabled")
			return False

		meta_pkgs_set = set(self.lliurex_meta_pkgs)

		for pkg in self.packages_selected:
			try:
				cmd = ["apt-get", "remove", "--simulate", pkg]
				process = subprocess.run(
					cmd, 
					stdout=subprocess.PIPE,
					stderr=subprocess.DEVNULL,
					text=True,
					check=True
				)

				pkgs_to_remove = [line.split()[1]
					for line in process.stdout.splitlines() 
					if line.startswith("Remv ")
				]

				if any(p in meta_pkgs_set for p in pkgs_to_remove):
					self.blocked_remove_pkgs_list.append(pkg)
			
			except subprocess.CalledProcessError:
				self._show_debug("check_remove_meta", f"Error simulating removal of {pkg}")

		self.meta_removed_warning = len(self.blocked_remove_pkgs_list) > 0
		self._show_debug("check_remove_meta. Check if pkg uninstall remove lliurex-meta", 
			f"List: {self.blocked_remove_pkgs_list}")

		return self.meta_removed_warning

    #def check_remove_meta

	def is_zmd_service(self, zomando):

		app_path = os.path.join(self.app_folder, f"{zomando}.app")

		if not os.path.exists(app_path):
			return True

		try:
			with open(app_path, 'r', encoding='utf-8') as fd:
				for line in fd:
					if "=" in line:
						key, value = line.split("=", 1) 
						if key.strip() == "Category":
							return value.strip() == "Services"
		except Exception as e:
			self._show_debug("is_zmd_service", f"Error: {e}") 
			pass

		return False

	#def is_zmd_service
	
	def check_getStatus_byScript(self, order):

		if  order is None or order =="":
			return ""

		order_data = self.epiFiles.get(order, {})
		script_info = order_data.get("script", {})
		script_path = script_info.get("name", "")
		get_status = script_info.get("getStatus", False)

		if script_path and get_status and os.path.exists(script_path):
			return script_path

		return ""

	#def check_getStatus_byScript
	
	def _check_download_byScript(self, order):

		if  order is None or order =="":
			return False

		order_data = self.epiFiles.get(order, {})
		script_info = order_data.get("script", {})
		script_path = script_info.get("name", "")
		download = script_info.get("download", False)

		if script_path and download and os.path.exists(script_path):
			return True

		return False

	#def check_getStatus_byScript

	def empty_cache_folder(self):

		if not os.path.isdir(self.download_path):
			return

		for filename in os.listdir(self.download_path):
			file_path = os.path.join(self.download_path, filename)
			try:
				if os.path.isfile(file_path):
					os.remove(file_path)
			except Exception as e:
				pass

	#de empty_cache_folder
	
	def _get_flavours(self):

		self._flavours = []
		cmd = ['lliurex-version', '-v']

		try:
			result = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
			if result:
				self._flavours = [x.strip() for x in result.split(',') if x.strip()]
		except (subprocess.CalledProcessError, FileNotFoundError):
			self._show_debug("_get_flavours", "Error executing lliurex-version")

	#def _get_flavours

	def is_pkg_skipped_for_flavour(self, pkg_id, skipped_flavours):

		is_skipped = any(
			element in flavour 
			for flavour in self._flavours 
			for element in skipped_flavours
		)

		if is_skipped:
			if pkg_id not in self.skipped_pkgs_flavours:
				self.skipped_pkgs_flavours.append(pkg_id)
				return True
		
		return False

	#def is_pkg_skipped_for_flavour
	
	def _get_user_groups(self):

		self._user_groups = []

		user = os.environ.get("PKEXEC_UID")

		if user:
			try:
				user = pwd.getpwuid(int(user)).pw_name
			except (ValueError, KeyError):
				user = os.environ.get("USER")
		else:
			user = os.environ.get("USER")

		if not user:
			return

		try:
			user_info = pwd.getpwnam(user)
			groups_gids = os.getgrouplist(user, user_info.pw_gid)
			self._user_groups = [grp.getgrgid(gid).gr_name for gid in groups_gids]
		except Exception as e:
			self._show_debug("_get_user_groups", f"Error retrieving groups for {user}: {e}")

	#def def _get_user_groups
	
	def is_pkg_skipped_for_group(self, pkg_id, skipped_groups):

		'''
			Values for pkg_skipped:
			- 0: pkg not skipped
			- 1: pkg skipped for all actions
			- 2: pkg skipped for remove action
		'''
		if 'admins' in self._user_groups:
			return 0

		for item in skipped_groups:
			if item["group"] not in self._user_groups:
				continue

			action = item.get("action")

			if action == "all":
				return 1
			if action == "remove":
				if pkg_id not in self.skipped_pkgs_groups:
					self.skipped_pkgs_groups.append(pkg_id)
				return 2
		
		return 0

	#def is_pkg_skipped_for_group
	
	def _is_remove_lock_for_group(self, skipped_groups):

		if 'admins' in self._user_groups:
			return False

		return not set(skipped_groups).isdisjoint(self._user_groups)

	def check_remove_skip_pkg(self):

		blocked_items = set(self.packages_selected) & set(self.skipped_pkgs_groups)

		self.blocked_remove_skipped_pkgs_list = list(blocked_items)
		self.skipped_pkg_warning = len(self.blocked_remove_skipped_pkgs_list) > 0

		self._show_debug(
			"check_remove_skip_pkg. Check if pkg uninstall is in skipped list",
			f"List: {self.blocked_remove_skipped_pkgs_list}"
		)

		return self.skipped_pkg_warning

	#def check_remove_skip_pkg
	
	def _clean_pkg_skipped_for_client(self, pkg_list):

		return [ pkg for pkg in pkg_list 
			if not any('client' in flavour for flavour in pkg.get("skip_flavours", []))
		]
	
	#def _clean_pkg_skipped_for_client
	
	def _check_install(self, pkg_id):
		
		dpkg_status, pkgs_ref, result, content = {}, [], False, ""
		
		epi_type = self.type
		config = self.epi_conf
		token = self.token_result_install.name if hasattr(self, 'token_result_install') and self.token_result_install else ""
		
		selection_enabled = config.get("selection_enabled", {}).get("active", False)
		file_with_list = (epi_type == "file" and selection_enabled)
		pkgs_list, pkgs_ref = self._get_common_pkg_lists(config, epi_type, pkg_id, "install")
		
		if epi_type == "file" and not file_with_list:
			if token and os.path.exists(token):
				result, content = self._handle_file_token(token)
			else:
				target_pkg_id = pkgs_list[0]["name"] if pkgs_list else pkg_id
				status = self.check_pkg_status(target_pkg_id, epi_type, self.check_getStatus_byScript(0))
				result = (status == "installed")
		else:
			order = self.epi_order if epi_type == "mix" else ""
			script = self.check_getStatus_byScript(order)
			
			dpkg_status, count_not_installed, _ = self._process_pkg_status(pkgs_list, pkg_id, epi_type, script)
			result = (count_not_installed == 0)
			
		self._show_debug("check_install", f"Action: install - Result: {result} - Dpkg Status: {dpkg_status} - Token: {content}")
		
		return dpkg_status, result
	
	#def _chek_install
	
	def _check_remove(self, pkg_id):
		
		dpkg_status, pkgs_ref, result, content = {}, [], False, ""
		
		config = self.epiFiles[0]
		epi_type = config.get("type")
		token = self.token_result_remove.name if hasattr(self, 'token_result_remove') and self.token_result_remove else ""
		
		selection_enabled = config.get("selection_enabled", {}).get("active", False)
		file_with_list = (epi_type == "file" and selection_enabled)
		pkgs_list, pkgs_ref = self._get_common_pkg_lists(config, epi_type, pkg_id, "remove")
		
		if epi_type == "file" and not file_with_list:
			if token and os.path.exists(token):
				result, content = self._handle_file_token(token)
			else:
				target_pkg_id = pkgs_list[0]["name"] if pkgs_list else pkg_id
				status = self.check_pkg_status(target_pkg_id, epi_type, self.check_getStatus_byScript(0))
				result = (status != "installed")
		else:
			order = 0 if epi_type in ["mix", "file"] else ""
			script = self.check_getStatus_byScript(order)
			
			dpkg_status, count_not_installed, pkgs_installed_count = self._process_pkg_status(pkgs_list, pkg_id, epi_type, script)
			result = (count_not_installed > 0 and count_not_installed == len(pkgs_ref))
			self.partial_installed = (pkgs_installed_count > 0)
			
		self._show_debug("check_remove", f"Action: remove - Result: {result} - Dpkg Status: {dpkg_status} - Token: {content}")
		
		return dpkg_status, result

	#def check_remove
	
	def _get_common_pkg_lists(self, config, epi_type, pkg_id, action):
		
		pkgs_ref = []
		pkgs_list = config.get("pkg_list", [])
		
		for item in pkgs_list:
			name = item["name"]
			if pkg_id != "all" and name != pkg_id:
				continue
				
			if name in self.packages_selected:
				if action == "remove":
					is_blocked = (name in self.blocked_remove_skipped_pkgs_list or 
					(epi_type != "file" and name in self.blocked_remove_pkgs_list))
					if not is_blocked:
						pkgs_ref.append(name)
				else:
					pkgs_ref.append(name)
					
		return pkgs_list, pkgs_ref

	#def _get_common_pkg_lists

	def _process_pkg_status(self, pkgs_list, pkg_id, epi_type, script):
		
		dpkg_status = {}
		count_not_installed = 0
		pkgs_installed_count = 0
		
		for item in pkgs_list:
			name = item["name"]
			if pkg_id != "all" and name != pkg_id:
				continue
				
			if name in self.packages_selected:
				p_type = item["type"] if epi_type == "mix" else epi_type
				status = self.check_pkg_status(name, p_type, script)
				dpkg_status[name] = status
				
				if status != "installed":
					count_not_installed += 1
			else:
				if self.pkg_info.get(name, {}).get("status") == "installed":
					pkgs_installed_count += 1
					
		return dpkg_status, count_not_installed, pkgs_installed_count	

	#def _process_pkg_status

	def _handle_file_token(self, token):
		
		with open(token, 'r') as f:
			content = f.readline().strip()
			
		result = ('0' in content)
		os.remove(token)
		
		return result, content

	#def _handle_file_token

#class EpiManager


if __name__=="__main__":
	
	epi=EpiManager()
