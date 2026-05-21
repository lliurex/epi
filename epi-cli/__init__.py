#!/usr/bin/env python3

import os
import subprocess
import multiprocessing
import sys
import html2text
import syslog
import time
import epi.epimanager as EpiManager
import signal
signal.signal(signal.SIGINT,signal.SIG_IGN)

class EPIC(object):

	def __init__(self,app,pkgsToInstall,debug=None):

		self.epicore=EpiManager.EpiManager(debug)
		signal.signal(signal.SIGINT,self.handler_signal)

		if app is None:
			return

		self.pkgsToInstall=pkgsToInstall
		self.valid_json=self.epicore.read_conf(app,True)

		if not self.epicore.epiFiles:
			errors={
				"path":"APP epi file not exist or its path is invalid. Use showlist to get avilabled APP epi",
				"empty":"APP epi file is empty"
			}
			msg_log=errors.get(self.valid_json.get("error"),"APP epi file it is not a valid json")
			self._print_write_log(msg_log)
			sys.exit(1)

		valid_script=self.epicore.check_script_file()

		if not valid_script.get("status"):
			msg_log=('Associated script does not exist or its path is invalid'
				if valid_json.get("error")=="path"
				else "Associated script does not have execute permissions"
			)
			self._print_write_log(msg_log)
			sys.exit(1)


		msg_log=f'APP epi file loaded by EPIC: {app}'
		self.write_log(msg_log)	

		self.remote_install,self.gui_install=self.epicore.check_remote_epi(app)

	#def __init__

	def get_info(self, show_all):

	    depends = ""
	    pkgs_selected = ""
	    pkgs_available = ""
	    pkgs_default = ""
	    tmp_list = []
	    pkgs_installed = ""
	    pkgs_available_gui = ""

	    for order in range(len(self.epicore.epiFiles) - 1, -1, -1):
	    	if order>0:
	    		tmp = self.epicore.epiFiles[order]
	    		for item in tmp["pkg_list"]:
	    			depends += item["name"] + " "
	    			self.epicore.packages_selected.append(item["name"])
	    	else:
			    if self.remote_install:
			        for item in self.remote_install:
			            name = item["name"]
			            if self.epicore.pkg_info[name]["status"] == "installed":
			                pkgs_installed += name + " "
			            pkgs_available += name + " "
			            if item["default_pkg"]:
			                pkgs_default += name + " "
			                tmp_list.append(name)

			        if not show_all:
			            if self.epicore.epiFiles[0]["selection_enabled"]["active"]:
			                if not self.pkgsToInstall:
			                    pkgs_selected = pkgs_default
			                    self.epicore.packages_selected.extend(tmp_list)
			                elif 'all' in self.pkgsToInstall:
			                    pkgs_selected = 'all'
			                    self.epicore.packages_selected.extend(item["name"] for item in self.remote_install)
			                else:
			                    pkgs_selected = "".join(f"{item} " for item in self.pkgsToInstall)
			                    self.epicore.packages_selected.extend(self.pkgsToInstall)
			            else:
			                pkgs_selected = pkgs_available
			                self.epicore.packages_selected.extend(item["name"] for item in self.remote_install)

			    if self.gui_install:
			        for item in self.gui_install:
			            name = item["name"]
			            if self.epicore.pkg_info[name]["status"] == "installed":
			                pkgs_installed += name + " "
			            pkgs_available_gui += name + " "
			            if item["default_pkg"]:
			                pkgs_default += name + " "

	    return depends, pkgs_available, pkgs_default, pkgs_installed, pkgs_selected, pkgs_available_gui

	#def get_info
	
	def listEpi(self):

		epi_list=sorted(self.epicore.cli_available_epis, key=lambda d: list(d.keys()))
		count_epi=len(epi_list)
		tmp_list=""

		if count_epi>0:	
			all_keys=[element for item in epi_list for element in item]
			tmp_list=", ".join(all_keys)

			print (f'  [EPIC]: List of all epi files that can be installed with EPIC: {tmp_list}')
		else:
			print ('  [EPIC]: No available epi file app detected')

	#def listEpi

	def listAllEpi(self):

		epi_list=sorted(self.epicore.all_available_epis, key=lambda d: list(d.keys()))
		count_epi=len(epi_list)
		tmp_list=""

		if count_epi>0:
			all_keys=[element for item in epi_list for element in item]
			tmp_list=", ".join(all_keys)
			print (f'  [EPIC]: List of all epi files availables in the system: {tmp_list}')

		else:
			print ('  [EPIC]: No available epi file app detected')

	#def listAllEpi	
	
	def showInfo(self,checked=None):
		
		checksystem=True
		show_all=False
		self.sequentialProcess=False
		self.pkg_log='aplication'

		if not checked:
			show_all=True
			print ('  [EPIC]: Searching information...')
			self.epicore.get_pkg_info()

		if not self.epicore.pkg_info:
			msg_log="Application epi file it is not a valid json. Missing some keys or keys with incorrect value in json definition. Run in debug mode for more information"
			print (f'  [EPIC]: {msg_log}')
			return 1

		if not checksystem:
			return 1	
		
		depends,pkgs_available,pkgs_default,pkgs_installed,self.pkgs,pkgs_available_gui=self.get_info(show_all)
		epi_conf=self.epicore.epiFiles[0]
		status=epi_conf.get("status")

		if status=="installed":
			zmd_status=self.epicore.get_zmd_status(0)
			if zmd_status==0:
				status="installed. It seems that the packages were installed without using EPI.It may be necessary to run EPI for proper operation"
			elif zmd_status==-1:
				status="installed. It seems that the packages were installed but the execution of EPI failed.It may be necessary to run EPI for proper operation"

		script_conf=epi_conf.get("script",{})

		if script_conf.get("remove") and not self.epicore.lock_remove_for_group:
			self.uninstall="Yes"
		else:
			self.uninstall="No"

		print ("  [EPIC]: Information availabled:")
		
		if epi_conf["selection_enabled"]["active"]:
			self.sequentialProcess=True
			if not pkgs_available:
				print ("     - Packages not availables for install with EPIC in this flavour" )
				if pkgs_available_gui!="":
					print (f"     - Packages availables to install ONLY with GUI (EPI): {pkgs_available_gui}")
				return 0	
	
			print (f"     - Packages availables to install with EPIC: {pkgs_available}")
			if pkgs_available_gui!="":
				print (f"     - Packages availables to install ONLY with GUI (EPI): {pkgs_available_gui}")
			
			if not epi_conf["selection_enabled"]["all_selected"]:
				msg_default=pkgs_default if pkgs_default else 'None'
				print (f"     - Packages selected by defafult: {msg_default}")
			else:
				print ("     - All packages are selected by default to be installed")
				print ("     - If you want to install only some packages indicate their names separated by space")
					
			if not pkgs_installed:
				print("     - Packages already installed: None")
			elif pkgs_installed==pkgs_available:
				print("     - Packages already installed: all")
			else:
				print(f"     - Packages already installed: {pkgs_installed}")

		else:
			if not pkgs_available:
				print (f"     - Application (ONLY availabled to install/uninstall with GUI (EPI) in this flavour): {pkgs_available_gui}")
			else:
				print (f"     - Application: {pkgs_available}")
		
		print (f"     - Status: {status}")
		print (f"     - Uninstall process availabled: {self.uninstall}")
		
		if depends:
			print (f"     - Additional application required: {depends}")

		return 0

	#def showInfo	

	def checking_system(self,mode,action=None):

		check=True
		print ('  [EPIC]: Checking system...')
		
		if self.check_root:
			self.lock_info=self.epicore.check_locks()
			msg_log=f"Lock info: {self.lock_info}"
		else:
			self.lock_info={}
			msg_log="Locks info: Not checked. User is not root"	

		self.write_log(msg_log)
		return check
		
	#def checking_system

	def checking_epi(self,mode,action=None):

		check=True
		msg_log=""
		self.epicore.get_pkg_info()
		
		if not self.epicore.pkg_info:
			msg_log="Application epi file it is not a valid json. Missing some keys or keys with incorrect value in json definition. Run in debug mode for more information"
			print (f'  [EPIC]: {msg_log}')
			return False

		self.required_root=self.epicore.required_root()
		self.required_x=self.check_required_x()
		self.check_pkgList=self.check_list()
		
		if self.required_root:
			msg_log=f"You need root privileges to {action} the application"
			self._print_write_log(msg_log)
			check=False
		
		if self.required_x:
			msg_log=f"Can not {action} the application with EPIC. Use epi-gtk for this"
			self._print_write_log(msg_log)
			check=False

		if not self.check_pkgList["status"]:
			error_message={
				"empty":f"No packages indicated to {action}",
				"name":f"Wrong packages indicated to {action}",
				"flavour":f"There are packages that can not {action} in this flavour",
				"cli":f"There are packages that can not {action} with EPIC"
			}
			error_type=self.check_pkgList.get("error")
			if error_type in error_message:
				msg_log=error_message[error_type]
				print (f'  [EPIC]: {msg_log}. Execute showinfo to know the packages available')
				self.write_log(msg_log)
				check=False
		
		return check

	#def check_epi	

	def check_list(self):

		if not self.epicore.epiFiles[0]["selection_enabled"]["active"]:
			return {"status": True, "error": ""}

		if len(self.pkgsToInstall) == 0:
			if len(self.remote_install) == 0:
				return {"status": False, "error": "cli"}

			if self.epicore.epiFiles[0]["selection_enabled"]["all_selected"]:
				return {"status": True, "error": ""}

			count = sum(1 for item in self.remote_install if item.get("default_pkg"))

			if count == 0:
				return {"status": False, "error": "empty"}

			return {"status": True, "error": ""}

		if "all" in self.pkgsToInstall:
			if len(self.remote_install) != len(self.epicore.epiFiles[0]["pkg_list"]):
				return {"status": False, "error": "cli"}
			return {"status": True, "error": ""}

		count_cli = 0
		count_name = 0
		count_flavour = 0

		tmp_remote = {item["name"] for item in self.remote_install}
		tmp_all = {item["name"] for item in self.epicore.epiFiles[0]["pkg_list"]}

		for pkg in self.pkgsToInstall:
			if pkg in self.epicore.skipped_pkgs_flavours:
				count_flavour += 1
			elif pkg not in tmp_remote:
				if pkg not in tmp_all:
					count_name += 1
				else:
					count_cli += 1

		if count_name > 0:
			return {"status": False, "error": "name"}
		if count_flavour > 0:
			return {"status": False, "error": "flavour"}
		if count_cli > 0:
			return {"status": False, "error": "cli"}

		return {"status": True, "error": ""}

	#def check_list

	def pulsate_check_connection(self):

		end_check = False
		result = ""
		result_queue = multiprocessing.Queue()

		self.checking_url1_t = multiprocessing.Process(target=self.checking_url1, args=(result_queue,))
		self.checking_url2_t = multiprocessing.Process(target=self.checking_url2, args=(result_queue,))
		self.checking_url1_t.start()
		self.checking_url2_t.start()

		while not end_check:
			time.sleep(0.5)

			if self.checking_url1_t.is_alive() and self.checking_url2_t.is_alive():
				continue

			if result == "" and not result_queue.empty():
				result = result_queue.get()

			if result and result[0]:
				end_check = True
			else:
				if not self.checking_url1_t.is_alive() and not self.checking_url2_t.is_alive():
					if not result_queue.empty():
						result = result_queue.get()
					end_check = True

		self.checking_url1_t.join()
		self.checking_url2_t.join()

		return result

	#def pulsate_check_connection

	def checking_url1(self, result_queue):

		result_queue.put(self.epicore.check_connection(self.epicore.urltocheck1))

	#def checking_url1

	def checking_url2(self, result_queue):

		result_queue.put(self.epicore.check_connection(self.epicore.urltocheck2))

	#def checking_url2

	def check_required_x(self):

		cont = 0

		for item in self.epicore.epiFiles:
			if self.epicore.epiFiles[item]["required_x"]:
				cont += 1

		return cont > 0

	#def check_required_x

	def manage_unlock_info(self,mode,action):

		if "Lliurex-Up" in self.lock_info:
			msg_log='The system is being updated. Wait a moment and try again'
			self._print_write_log(msg_log)
			return 0

		if self.lock_info["wait"]:
			msg_log='Apt or Dpkg is being running. Wait a moment and try again'
			self._print_write_log(msg_log)
			return 0

		if mode:
			msg_log='Apt or Dpkg are blocked. Wait a moment and try again'
			self._print_write_log(msg_log)
			return 0


		prompt='  [EPIC]: Apt or Dpkg seems blocked by a failed previous execution. You want to try to unlock it (yes/no)?'

		if input(prompt).lower().startswith('y'):
			return self.pulsate_unlocking_process(mode,action)

		msg_log="Unlocking process not executed"
		self._print_write_log(msg_log)
		return 0

	#def manage_unlock_info					

	def pulsate_unlocking_process(self,mode,action):

		self.endProcess = False
		result_queue = multiprocessing.Queue()

		self.unlocking_t = multiprocessing.Process(target=self.unlocking_process, args=(result_queue,))
		self.unlocking_t.start()

		from itertools import cycle
		frames = ["[    ]", "[=   ]", "[==  ]", "[=== ]", "[====]", "[ ===]", "[  ==]", "[   =]",
				"[    ]", "[   =]", "[  ==]", "[ ===]", "[====]", "[=== ]", "[==  ]", "[=   ]"]

		progressbar = cycle(frames)

		try:
			while self.unlocking_t.is_alive():
				time.sleep(0.5)
				print(f"  [EPIC]: The unlocking process is running. Wait a moment {next(progressbar)}", end='\r')

			try:
				result = result_queue.get(timeout=1.0)
			except Exception:
				result = None
		finally:
			self.unlocking_t.join()
			self.unlocking_t.close()  # Libera los recursos del proceso de inmediato (Python 3.7+)

		print(" "*80,end='\r')
		sys.stdout.flush()

		if result == 0:
			msg_log='The unlocking process finished successfully'
			self._print_write_log(msg_log)

			if action == 'install':
				self.install_process(mode)
			else:
				self.uninstall_process(mode)
			return 0

		msg_log='The unlocking process has failed'
		self._print_write_log(msg_log)
		return 1

	#def pulsate_unlocking_process

	def unlocking_process(self,result_queue):

		try:
			result = self.epicore.unlock_process()
			result_queue.put(result)
		except Exception:
			result_queue.put(1)

	#def unlocking_process		

	def add_repository_keys(self,order):

		cmd=self.epicore.add_repository_keys(order)
		if cmd =="":
			return

		p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE, text=True)
		output = p.communicate()
		error=self.readErrorOutput(output[1])

		if error[0]:
			msg_log=f'Error gathering information. Details:\n{error[1]}'
			self._print_write_log(msg_log)
	
	#def add_repository_keys

	def update_keyring(self):

		cmd = self.epicore.update_keyring()

		if cmd == "":
			return True

		try:
			subprocess.run(cmd, shell=True, check=False)
		except Exception:
			pass

		return True

	#def update_keyring

	def download_app(self,pkg_id):

		cmd=self.epicore.download_app(pkg_id)

		if cmd == "":
			return True

		print('  [EPIC]: Downloading application....')
		subprocess.run(cmd,shell=True,check=False)
		result=self.epicore.check_download(pkg_id)

		if result:
			msg_log=f'Downloading {self.pkg_log} - Result: OK'
			self.write_log(msg_log)
			return True

		msg_log=f'Installation aborted. Error downloading {self.pkg_log}'
		self._print_write_log(msg_log)

		return False

	#def download_app		

	def preinstall_app(self,pkg_id):

		cmd=self.epicore.preinstall_app(pkg_id)

		if cmd == "":
			return True

		print('  [EPIC]: Preparing installation...')
		subprocess.run(cmd,shell=True,check=False)

		result=self.epicore.check_preinstall(pkg_id)

		if result:
			msg_log=f'Preparing installation of {self.pkg_log} - Result: OK'
			self.write_log(msg_log)
			return True

		msg_log=f'Installation process for {self.pkg_log} aborted. Error preparing system for'
		self._print_write_log(msg_log)

		return False

	#def preinstall_app		

	def check_arquitecture(self):

		cmd=self.epicore.check_arquitecture()

		if cmd == "":
			return

		print('  [EPIC]: Checking architecture...')
		p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE, text=True)
		output=p.communicate()
		error=self.readErrorOutput(output[1])

		if error[0]:
			msg_log=f'Error checking architecture. Details:\n{error[1]}'
			self._print_write_log(msg_log)

	# def check_arquitecture

	def check_update_repos(self):

		cmd=self.epicore.check_update_repos()

		if cmd == "":
			return

		print('  [EPIC]: Checking if repositories need updating...')
		p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE, text=True)
		output=p.communicate()
		error=self.readErrorOutput(output[1])

		if error[0]:
			msg_log=f'Error Checking if repositories need updating. Details:\n{error[1]}'
			self._print_write_log(msg_log)

	#def check_update_repos
				
	def install_app(self,pkg_id):
	
		cmd=self.epicore.install_app("cli",pkg_id)

		if cmd == "":
			return True

		print('  [EPIC]: Installing application...')
		subprocess.run(cmd,shell=True,check=False)
		dpkg_status,result=self.epicore.check_install_remove("install",pkg_id)

		if result:
			msg_log=f'Installing {self.pkg_log} - Result: OK'
			self.write_log(msg_log)
			return True

		msg_log=f'Installation process for {self.pkg_log} aborted. Error installing'
		self._print_write_log(msg_log)

		return False

	#def install_app		

	def postinstall_app(self,pkg_id):
	
		cmd=self.epicore.postinstall_app(pkg_id)	

		if cmd == "":
			return True

		print('  [EPIC]: Ending installation...')
		subprocess.run(cmd,shell=True,check=False)
		result=self.epicore.check_postinstall(pkg_id)

		if result:
			msg_log=f'Ending installation of: {self.pkg_log} - Result: OK'
			self.write_log(msg_log)
			return True

		msg_log=f'Installation process for {self.pk_log} aborted. Error ending installation'
		self._print_write_log(msg_log)

		return False


	#def postinstall_app			

	def install_process(self,mode):

		self.showInfo(True)

		print(f'  [EPIC]: Packages selected to install: {self.pkgs}')
		error=False
		if not mode:
			response=input('  [EPIC]: Do you want to install the selected package(s) (yes/no)): ').lower()
		else:
			response='yes'	

		if not response.startswith('y'):
			msg_log='Installation cancelled'
			self._print_write_log(msg_log)
			self.epicore.remove_repo_keys()
			self.epicore.empty_cache_folder()
			return 0

		msg_log='Installing application by CLI'
		self.write_log(msg_log)
		order=len(self.epicore.epiFiles)
		print ('  [EPIC]: Checking internet connection. Wait a moment...')
		connection=self.pulsate_check_connection()
		

		if not connection[0]:
			msg_log=f"Internet connection not detected: {connection[1]}"
			self._print_write_log(msg_log)
			return 1

		if order>1:
			print ('****************************************************************')
			print ('*********************** INSTALLING DEPENDS *********************')
			print ('****************************************************************')

		for item in self.epicore.epiFiles:
			order=order-1
			self.epicore.zerocenter_feedback(order,'init')
			if order==0:
				totalError=0
				print ('****************************************************************')
				print ('******************** INSTALLING APPLICATION ********************')
				print ('****************************************************************')

			print('  [EPIC]: Gathering information....')
			self.add_repository_keys(order)
			self.update_keyring()
			self.check_arquitecture()
			self.check_update_repos()

			if order>0 or not self.sequentialProcess:
				result=self._pkgInstallProcess('all')
				if result:
					self.epicore.zerocenter_feedback(order,'install',True)
				else:
					error=True
			else:
				for pkg_id in self.epicore.packages_selected:
					self.pkg_log=pkg_id
					print(f'  [EPIC]: Processing the installation of: {pkg_id}')
					result=self._pkgInstallProcess(pkg_id)
					if result:
						print(f'  [EPIC]: Installation process for {pkg_id} ending OK')
					else:
						totalError+=1

				if totalError>0:
					error=True
				else:
					self.epicore.zerocenter_feedback(order,'install',True)

			if error:
				self.epicore.zerocenter_feedback(order,'install',False)
				self.epicore.remove_repo_keys()
				self.epicore.empty_cache_folder()
				msg_log="Installation endind with errors"
				self._print_write_log(msg_log)
				return 1

		msg_log='Installation completed successfully'
		self._print_write_log(msg_log)
		self.epicore.remove_repo_keys()
		self.epicore.empty_cache_folder()

		return 0

	#def install_process

	def _pkgInstallProcess(self,pkg_id):

		result=self.download_app(pkg_id)
		if not result:
			return result

		result=self.preinstall_app(pkg_id)
		if not result:
			return result

		result=self.install_app(pkg_id)
		if not result:
			return result

		return self.postinstall_app(pkg_id)

	#def _pkgInstallProcess		

	def install(self,mode,nocheck):

		msg_log=f"Action to execute: Install.Includes previous system checks: {nocheck}"
		self.write_log(msg_log)
		self.check_root=self.epicore.check_root()

		if not nocheck:
			if not self.checking_system(mode,'install'):
				return 1
		else:
			self.lock_info={}

		
		if not self.checking_epi(mode,'install'):
			return 1

		if self.lock_info:
			return self.manage_unlock_info(mode,'install')

		return self.install_process(mode)


	#def install		

	def uninstall_app(self,pkg_id):

		cmd=self.epicore.uninstall_app(0,pkg_id)

		if cmd == "":
			return True

		print('  [EPIC]: Uninstall application...')
		p=subprocess.run(cmd,shell=True,check=False)

		dpkg_status,result=self.epicore.check_install_remove("uninstall",pkg_id)
		if result:
			msg_log=f'Uninstalled process for {self.pkg_log} ending OK'
			self._print_write_log(msg_log)
			return True

		msg_log=f'Uninstalled process for {self.pkg_log} ending with errors'
		self._print_write_log(msg_log)

		return False

	#def uninstall_app 	

	def uninstall_process(self, mode):

		self.showInfo(True)
		print(f'  [EPIC]: Packages selected to uninstall: {self.pkgs}')

		if self.uninstall != 'Yes':
			msg_log = 'Uninstall process not availabled'
			self._print_write_log(msg_log)
			return 0

		if not mode:
			response = input('  [EPIC]: Do you want to uninstall the package(s) selected (yes/no)): ').lower()
		else:
			response = 'yes'

		if not response.startswith('y'):
			msg_log = 'Uninstall process canceled'
			self._print_write_log(msg_log)
			return 0

		msg_log = 'Uninstall application by CLI'
		self.write_log(msg_log)
		self.stop_uninstall = self.check_remove_meta()

		if self.stop_uninstall:
			if self.meta_remove_warning:
				if not self.skipped_remove_warning:
					msg_log = 'Uninstall blocked because remove metapackage.'
				else:
					msg_log = 'Uninstall blocked because remove metapackage and not enough permissions'
			else:
				msg_log = 'Uninstall blocked because yo do not have enough permissions'

			self._print_write_log(msg_log)
			return 1

		totalUninstallError = 0
		if not self.sequentialProcess:
			result = self.uninstall_app('all')
		else:
			for pkg in self.epicore.packages_selected:
				self.pkg_log = pkg
				print(f'  [EPIC]: Processing the uninstallation of: {pkg}')
				result = self.uninstall_app(pkg)

				if not result:
					if pkg not in self.epicore.blocked_remove_pkgs_list and pkg not in self.epicore.blocked_remove_skipped_pkgs_list:
						totalUninstallError += 1

			result = (totalUninstallError == 0)

		if not result:
			msg_log = "Uninstall process ending with errors"
			self._print_write_log(msg_log)
			self.epicore.zerocenter_feedback(0, 'uninstall', False)
			return 1

		if not self.meta_remove_warning:
			if not self.skipped_remove_warning:
				msg_log = 'Uninstall ending successfully'
			else:
				msg_log = f"Some selected application successfully uninstalled.Others not because user do not have permission to uninstall them ({self.blocked_pkgs_skipped})"
		else:
			if not self.skipped_remove_warning:
				msg_log = f"Some selected application successfully uninstalled.Others not because they are part of the system's meta-package ({self.blocked_pkgs_meta})"
			else:
				msg_log = f"Some selected application successfully uninstalled.Others not because user do not have permission to uninstall them ({self.blocked_pkgs_skipped}) and are part of the system meta-package ({self.blocked_pkgs_meta})"

		self._print_write_log(msg_log)
		self.epicore.zerocenter_feedback(0, 'uninstall', True)

		return 0

	#def uninstall_process

	def uninstall(self,mode,nocheck):
	
		msg_log=f"Action to execute: Uninstall.Includes previous system checks: {nocheck}"
		self.write_log(msg_log)
		self.check_root=self.epicore.check_root()

		if not nocheck:
			if not self.checking_system(mode,'uninstall'):
				return 1
		else:
			self.lock_info={}

		if not self.checking_epi(mode,'uninstall'):
			return 1

		if len(self.lock_info)>0:
			return self.manage_unlock_info(mode,'uninstall')

		return self.uninstall_process(mode)


	#def uninstall									

	def check_remove_meta(self):

		self.blocked_pkgs_meta = ""
		self.blocked_pkgs_skipped = ""
		stop_uninstall = False

		print('  [EPIC]: Checking if selected applications can be uninstalled...')
		self.meta_remove_warning = self.epicore.check_remove_meta()
		self.skipped_remove_warning = self.epicore.check_remove_skip_pkg()

		if self.meta_remove_warning:
			self.blocked_pkgs_meta = ", ".join(self.epicore.blocked_remove_pkgs_list)

			if len(self.epicore.packages_selected) == len(self.epicore.blocked_remove_pkgs_list):
				stop_uninstall = True

		if self.skipped_remove_warning:
			self.blocked_pkgs_skipped = ", ".join(self.epicore.blocked_remove_skipped_pkgs_list)

			if len(self.epicore.packages_selected) == len(self.epicore.blocked_remove_skipped_pkgs_list):
				stop_uninstall = True
			else:
				total_pkgs = len(self.epicore.blocked_remove_skipped_pkgs_list) + len(self.epicore.blocked_remove_pkgs_list)
				if total_pkgs == len(self.epicore.packages_selected):
					stop_uninstall = True

		if stop_uninstall:
			if self.skipped_remove_warning and self.meta_remove_warning:
				msg_log = f"Packages blocked because you do not have permission to uninstall them and remove metapackage: by permision:{self.blocked_pkgs_skipped} - by meta:{self.blocked_pkgs_meta}"
			elif self.skipped_remove_warning:
				msg_log = f"Packages blocked because you do not have permission to uninstall them: {self.blocked_pkgs_skipped}"
			else:
				msg_log = f"Packages blocked because remove metapackage: {self.blocked_pkgs_meta}"

			self._print_write_log(msg_log)

		elif self.meta_remove_warning:
			msg_log = f"Packages blocked because remove metapackage: {self.blocked_pkgs_meta}"
			self._print_write_log(msg_log)

		return stop_uninstall

	def readErrorOutput(self,output):

		if isinstance(output, tuple):
			output = output[1]

		if isinstance(output, bytes):
			output = output.decode()

		return ["E: " in output, output]

	# def readErrorOutput

	def handler_signal(self,signal,frame):

		self.epicore.remove_repo_keys()
		self.epicore.empty_cache_folder()
		msg_log="Cancel process with Ctrl+C signal"
		self._print_write_log(msg_log)

		sys.exit(0)
	
	#def handler_signal		

	def write_log(self,msg):

		syslog.openlog("EPI")
		syslog.syslog(msg)
																
		return

	def _print_write_log(self,msg):

		print(f'  [EPIC]: {msg}')
		self.write_log(msg)

		return

	#def _print_write_log

	#def write_log	
