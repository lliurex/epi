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
		if app!=None:
			self.pkgsToInstall=pkgsToInstall
			self.valid_json=self.epicore.read_conf(app,True)

			if len(self.epicore.epiFiles)==0:
				if self.valid_json["error"]=="path":
					msg_log='APP epi file not exist or its path is invalid. Use showlist to get avilabled APP epi'
				elif self.valid_json["error"]=="empty":
					msg_log='APP epi file is empty'
				else:	
					msg_log='APP epi file it is not a valid json'	
				print ('  [EPIC]: '+msg_log)
				self.write_log(msg_log)
				sys.exit(1)
			else:
				valid_script=self.epicore.check_script_file()
				if not valid_script["status"]:
					if valid_script["error"]=="path":
						msg_log='Associated script does not exist or its path is invalid'
					else:
						msg_log='Associated script does not have execute permissions'
					print ('  [EPIC]: '+msg_log)
					self.write_log(msg_log)	
					sys.exit(1)

				msg_log='APP epi file loaded by EPIC: ' + app
				self.write_log(msg_log)	
				self.remote_install=self.epicore.check_remote_epi(app)


	#def __init__

	def get_info(self,show_all):

		order=len(self.epicore.epiFiles)
		depends=""
		pkgs_selected=""
		pkgs_available=""
		pkgs_default=""
		tmp_list=[]

		for item in self.epicore.epiFiles:
			order=order-1
			if order>0:
				tmp=self.epicore.epiFiles[order]
				for item in tmp["pkg_list"]:
					depends=depends+item["name"]+" "
					self.epicore.packages_selected.append(item["name"])
			else:
				if len(self.remote_install)>0:
					for item in self.remote_install:
						pkgs_available=pkgs_available+item["name"]+" "
						if item["default_pkg"]:
							pkgs_default=pkgs_default+item["name"]+" "
							tmp_list.append(item["name"])


					if not show_all:
						if self.epicore.epiFiles[0]["selection_enabled"]["active"]:
							if len(self.pkgsToInstall)==0:
								pkgs_selected=pkgs_default
								for item in tmp_list:
									self.epicore.packages_selected.append(item)
							else:
								if 'all' in self.pkgsToInstall:
									pkgs_selected='all'
									for item in self.remote_install:
										self.epicore.packages_selected.append(item["name"])
								else:
									for item in self.pkgsToInstall:
										pkgs_selected=pkgs_selected+item +" "
										self.epicore.packages_selected.append(item)
						else:
							pkgs_selected=pkgs_available
							for item in self.remote_install:
								self.epicore.packages_selected.append(item["name"])

		return depends,pkgs_available,pkgs_default,pkgs_selected

	#def get_info			

	def listEpi(self):

		epi_list=sorted(self.epicore.cli_available_epis, key=lambda d: list(d.keys()))
		count_epi=len(epi_list)
		tmp=""
		count=1

		if count_epi>0:				
			for item in epi_list:
				for element in item:
					if count<count_epi:
						tmp=tmp+element+", "
					else:
						tmp=tmp+element
					count+=1
			print ('  [EPIC]: List of all epi files that can be installed with EPIC: '+tmp)
		
		else:
			print ('  [EPIC]: No available epi file app detected')


	#def listEpi	
	
	def showInfo(self,checked=None):
		
		checksystem=True
		show_all=False
		if not checked:
			show_all=True
			print ('  [EPIC]: Searching information...')
			self.epicore.get_pkg_info()


		if checksystem:
			depends,pkgs_available,pkgs_default,self.pkgs=self.get_info(show_all)

			epi_conf=self.epicore.epiFiles[0]
			status=epi_conf["status"]
			
			if status=="installed":
				zmd_status=self.epicore.get_zmd_status(0)
				if zmd_status==0:
					status="installed. It seems that the packages were installed without using EPI.It may be necessary to run EPI for proper operation"
				elif zmd_status==-1:
					status="installed. It seems that the packages were installed but the execution of EPI failed.It may be necessary to run EPI for proper operation"

			try:
				if epi_conf["script"]["remove"]:
					self.uninstall="Yes"
			except Exception as e:
				self.uninstall="No"

			print ("  [EPIC]: Information availabled:")
			if self.epicore.epiFiles[0]["selection_enabled"]["active"]:
				print ("     - Packages availables: " + pkgs_available)
				if not self.epicore.epiFiles[0]["selection_enabled"]["all_selected"]:
					if pkgs_default=="":
						print ("     - Packages selected by defafult: None")
					else:
						print ("     - Packages selected by defafult: "+pkgs_default)
					print ("     - If you want to install all, indicate 'all'. If you want to install only some packages indicate their names separated by space")
				else:
					print ("     - All packages are selected by default to be installed")
					print ("     - If you want to install only some packages indicate their names separated by space")
			
			else:
				if pkgs_available!="":
					print ("     - Application: " + pkgs_available)
				else:		
					print ("     - Application not availabled to install/uninstall via terminal. Use epi-gtk for this")
					return 0
			print ("     - Status: " + status)
			print ("     - Uninstall process availabled: " + self.uninstall)
			if len(depends)>0:
				print ("     - Additional application required: " + depends)

			return 0
		else:
			return 1	

	#def showInfo	

	def checking_system(self,mode,action=None):

		check=True
		print ('  [EPIC]: Checking system...')

		#self.connection=self.epicore.check_connection()
		
		connection=self.pulsate_check_connection()
		
		if connection[0]:
			if self.check_root:
				self.lock_info=self.epicore.check_locks()
				msg_log="Lock info :"+str(self.lock_info)
			else:
				self.lock_info={}
				msg_log="Locks info: Not checked. User is not root"	
			self.write_log(msg_log)
			
		else:
			msg_log="Internet connection not detected: "+connection[1] 
			print ('  [EPIC]: '+msg_log)
			self.write_log(msg_log)
			check=False

		return check
		

	#def checking_system

	def checking_epi(self,mode,action=None):

		check=True
		self.epicore.get_pkg_info()
		self.required_root=self.epicore.required_root()
		self.required_x=self.check_required_x()
		self.check_pkgList=self.check_list()
		if self.required_root:
			msg_log="You need root privileges to " + action + " the application"
			print ('  [EPIC]: '+msg_log)
			self.write_log(msg_log)
			check=False
		if self.required_x:
			msg_log="Can not " + action + " the application via terminal. Use epi-gtk for this"
			print ('  [EPIC]: '+ msg_log)
			self.write_log(msg_log)
			check=False
		if not self.check_pkgList["status"]:
			if self.check_pkgList["error"]=="empty":
				msg_log="No packages indicated to "+action
				print ('  [EPIC]: '+ msg_log+ '. Execute showinfo to know the packages available')
				check=False
			elif self.check_pkgList["error"]=="name":
				msg_log="Wrong packages indicated to "+action
				print ('  [EPIC]: '+ msg_log+'. Execute showinfo to know the packages available')
				check=False
			elif self.check_pkgList["error"]=="cli":
				msg_log="There are packages that can not " + action + " via terminal"	
				print ('  [EPIC]: '+ msg_log+'. Execute showinfo to know the packages available')
				check=False

		return check

	#def check_epi	

	def check_list(self):

		if self.epicore.epiFiles[0]["selection_enabled"]["active"]:
			
			if len(self.pkgsToInstall)==0:
				if len(self.remote_install)==0:
					return {"status":False,"error":"cli"}
				else:	
					if not self.epicore.epiFiles[0]["selection_enabled"]["all_selected"]:
						count=0
						for item in self.remote_install:
							if item in self.remote_install:
								if item["default_pkg"]:
									count+=1
						if count==0:
							return {"status":False,"error":"empty"}
						else:
							return {"status":True,"error":""}	
					
					else:
						return {"status":True,"error":""}
			else:
				count_cli=0
				count_name=0
				tmp_remote=[]
				tmp_all=[]

				if "all" not in self.pkgsToInstall:
					for item in self.remote_install:
						tmp_remote.append(item["name"])
					for item in self.epicore.epiFiles[0]["pkg_list"]:
						tmp_all.append(item["name"])	
					for pkg in self.pkgsToInstall:
						if pkg not in tmp_remote:
							if pkg not in tmp_all:
								count_name+=1
							else:	
								count_cli+=1
					if count_name>0:
						return {"status":False,"error":"name"}
					if count_cli>0:
						return {"status":False,"error":"cli"}	
				else:
					if len(self.remote_install)!=len(self.epicore.epiFiles[0]["pkg_list"]):
						return {"status":False,"error":"cli"}		

		return {"status":True,"error":""}	

	#def check_list			

	def pulsate_check_connection(self):

		end_check=False
		
		result=""
		result_queue=multiprocessing.Queue()
		
		self.checking_url1_t=multiprocessing.Process(target=self.checking_url1,args=(result_queue,))
		self.checking_url2_t=multiprocessing.Process(target=self.checking_url2,args=(result_queue,))
		self.checking_url1_t.start()
		self.checking_url2_t.start()

		while not end_check:

			time.sleep(0.5)
			if self.checking_url1_t.is_alive() and self.checking_url2_t.is_alive():
				end_check=False

			else:
				if result=="":
					result=result_queue.get()
				if not result[0]:
					if self.checking_url1_t.is_alive() or self.checking_url2_t.is_alive():
						end_check=False
					else:
						result=result_queue.get()
						end_check=True

				else:
					end_check=True
		
		return result			
		
	#def pulsate_check_connection	

	def checking_url1(self,result_queue):

		result_queue.put(self.epicore.check_connection(self.epicore.urltocheck1))

	#def checking_url1	

	def checking_url2(self,result_queue):

		result_queue.put(self.epicore.check_connection(self.epicore.urltocheck2))

 	#def checking_url2

	def check_required_x(self):

		cont=0
		for item in self.epicore.epiFiles:
			if self.epicore.epiFiles[item]["required_x"]:
				cont=cont+1
		if cont>0:
			return True
		else:
			return False	

	#def check_required_x	


	def manage_unlock_info(self,mode,action):

		if "Lliurex-Up" in self.lock_info:
			msg_log="The system is being updated"
			print ('  [EPIC]: '+msg_log+'. Wait a moment and try again')
			self.write_log(msg_log)
			return 0

		else:
			if self.lock_info["wait"]:
				msg_log="Apt or Dpkg is being updated"
				print ('  [EPIC]: '+msg_log+'. Wait a moment and try again')
				self.write_log(msg_log)
				return 0
			else:
				if mode:
					msg_log="Apt or Dpkg are blocked"
					print ('  [EPIC]: '+msg_log+'. Wait a moment and try again')
					self.write_log(msg_log)	
					return 0
				else:
					response=input('  [EPIC]: Apt or Dpkg seems blocked by a failed previous execution. You want to try to unlock it (yes/no)?').lower()	
					if response.startswith('y'):
						self.pulsate_unlocking_process(mode,action)
					else:
						msg_log="Unlocking process not executed"
						print ('  [EPIC]: '+msg_log)
						self.write_log(msg_log)
						return 0	

	#def manage_unlock_info					


	def pulsate_unlocking_process(self,mode,action):

		self.endProcess=False
		
		result_queue=multiprocessing.Queue()
		self.unlocking_t=multiprocessing.Process(target=self.unlocking_process,args=(result_queue,))
		self.unlocking_t.start()
		

		progressbar= ["[    ]","[=   ]","[==  ]","[=== ]","[====]","[ ===]","[  ==]","[   =]","[    ]","[   =]","[  ==]","[ ===]","[====]","[=== ]","[==  ]","[=   ]"]
		i=1
		while self.unlocking_t.is_alive():
			time.sleep(0.5)
			per=i%16
			print("  [EPIC]: The unlocking process is running. Wait a moment " + progressbar[per],end='\r')
			#sys.stdout.flush()
			#sys.stdout.write("\r\33[2K")
			i+=1

		result=result_queue.get()
		
		if result ==0:
			sys.stdout.flush()
			msg_log="The unlocking process finished successfully"
			self.write_log(msg_log)
			print ('  [EPIC]: '+msg_log)
			if action=='install':
				self.install_process(mode)
			else:
				self.uninstall_process(mode)	
		else:
			msg_log="The unlocking process has failed"
			print ('  [EPIC]: '+msg_log)
			self.write_log(msg_log)
			return 1

	#def pulsate_unlocking_process	


	def unlocking_process(self,result_queue):

		result_queue.put(self.epicore.unlock_process())

	#def unlocking_process		

	def add_repository_keys(self,order):

		print('  [EPIC]: Gathering information....')
		
		cmd=self.epicore.add_repository_keys(order)
		if cmd !="":
			p=subprocess.Popen(cmd,shell=True,stderr=subprocess.PIPE)
			output=p.communicate()
			error=self.readErrorOutput(output[1])
			if error:
				msg_log='Installation aborted. Error gathering information: ' +'\n'+str(output[1])
				print('  [EPIC]: '+msg_log)
				self.write_log(msg_log)
				return False
			else:
				msg_log='Gathering information: OK'
				self.write_log(msg_log)
				return True	

		else:
			return True		

	#def add_repository_keys		

	def download_app(self):

		cmd=self.epicore.download_app()

		if cmd !="":
			print('  [EPIC]: Downloading application....')
			os.system(cmd)
			result=self.epicore.check_download()
			if result:
				msg_log='Downloading application: OK'
				self.write_log(msg_log)
				return True	
			else:
				msg_log='Installation aborted. Error downloading application'
				print('  [EPIC]: '+msg_log)
				self.write_log(msg_log)
				return False	
		else:
			return True		

	#def download_app		


	def preinstall_app(self):

		cmd=self.epicore.preinstall_app()

		if cmd !="":
			print('  [EPIC]: Preparing installation...')
			p=subprocess.Popen(cmd,shell=True,stderr=subprocess.PIPE)
			output=p.communicate()
			error=self.readErrorOutput(output[1])
			if error:
				msg_log='Installation aborted. Error preparing system:' '\n' + str(output[1])
				print('  [EPIC]: ' +msg_log)
				self.write_log(msg_log)
				return False
			else:
				result=self.epicore.check_preinstall()
				if result:
					msg_log='Preparing installation: OK'
					self.write_log(msg_log)
					return True	
				else:
					msg_log='Installation aborted. Error preparing system'
					print('  [EPIC]: '+msg_log)
					self.write_log(msg_log)

					return False	
		else:
			return True		

	#def preinstall_app		

	def check_arquitecture(self):

		cmd=self.epicore.check_arquitecture()

		if cmd !="":
			print('  [EPIC]: Checking architecture...')
			p=subprocess.Popen(cmd,shell=True,stderr=subprocess.PIPE)
			output=p.communicate()
			error=self.readErrorOutput(output[1])
			if error:
				msg_log='Installation aborted. Error checking architecture:' +'\n'+str(output[1])
				print('  [EPIC]: '+msg_log)
				self.write_log(msg_log)
				return False
			else:
				return True
		else:
			return True

	# def check_arquitecture

	def check_update_repos(self):

		cmd=self.epicore.check_update_repos()

		if cmd !="":
			print('  [EPIC]: Checking if repositories need updating...')
			p=subprocess.Popen(cmd,shell=True,stderr=subprocess.PIPE)
			output=p.communicate()
			error=self.readErrorOutput(output[1])
			if error:
				msg_log='Installation aborted. Error Checking if repositories need updating:' +'\n'+str(output[1])
				print('  [EPIC]: '+msg_log)
				self.write_log(msg_log)
				return False
			else:
				return True
		else:
			return True

	#def check_update_repos
				
	def install_app(self):
	
		cmd=self.epicore.install_app("cli")

		if cmd !="":
			'''
			if not self.epicore.epiFiles[0]["required_dconf"]:
				cmd="LANG=C LANGUAGE=en DEBIAN_FRONTEND=noninteractive "+cmd
			else:
				cmd="LANG=C LANGUAGE=en "+cmd
			'''
			print('  [EPIC]: Installing application...')
			p=subprocess.Popen(cmd,shell=True,stderr=subprocess.PIPE)
			output=p.communicate()
			error=self.readErrorOutput(output[1])
			if error:
				msg_log='Installation aborted. Error installing application:' +'\n'+str(output[1])
				print('  [EPIC]: '+msg_log)
				self.write_log(msg_log)
				return False
			else:
				dpkg_status,result=self.epicore.check_install_remove("install")
				if result:
					msg_log='Installing application: OK'
					self.write_log(msg_log)
					return True	
				else:
					msg_log='Installation aborted. Error installing application'
					print('  [EPIC]: '+msg_log)
					self.write_log(msg_log)
					return False	
		else:
			return True		

	#def install_app		

	def postinstall_app(self):
	
		cmd=self.epicore.postinstall_app()	

		if cmd !="":
			print('  [EPIC]: Ending installation...')
			p=subprocess.Popen(cmd,shell=True,stderr=subprocess.PIPE)
			output=p.communicate()
			error=self.readErrorOutput(output[1])
			if error:
				msg_log='Installation aborted. Error ending installation:' +'\n'+str(output[1])
				print('  [EPIC]: '+msg_log)
				self.write_log(msg_log)
				return False
			else:
				result=self.epicore.check_postinstall()
				if result:
					msg_log='Ending installation. OK'
					self.write_log(msg_log)
					return True	
				else:
					msg_log='Installation aborted. Error ending installation'
					print('  [EPIC]: '+msg_log)
					self.write_log(msg_log)
					return False	
		else:
			return True		

	#def postinstall_app			

	def install_process(self,mode):

		self.showInfo(True)

		print('  [EPIC]: Packages selected to install: '+self.pkgs)
		error=False
		if not mode:
			response=input('  [EPIC]: Do you want to install the selected package(s) (yes/no)): ').lower()
		else:
			response='yes'	

		if response.startswith('y'):
			msg_log='Installing application by CLI'
			self.write_log(msg_log)
			order=len(self.epicore.epiFiles)
			if order>1:
				print ('****************************************************************')
				print ('*********************** INSTALLING DEPENDS *********************')
				print ('****************************************************************')

			for item in self.epicore.epiFiles:
				order=order-1
				self.epicore.zerocenter_feedback(order,'init')
				if order==0:
					print ('****************************************************************')
					print ('******************** INSTALLING APPLICATION ********************')
					print ('****************************************************************')

				result=self.add_repository_keys(order)
				if result:
					result=self.download_app()
					if result:
						result=self.preinstall_app()
						if result:
							result=self.check_arquitecture()
							if result:
								result=self.check_update_repos()
								if result:
									result=self.install_app()
									if result:
										result=self.postinstall_app()
										if result:
											self.epicore.zerocenter_feedback(order,'install',result)
										else:
											error=True	
									else:
										error=True
								else:
									error=True		
							else:
								error=True
						else:
							error=True
								
					else:
						error=True
				else:
					error=True

				if error:
					self.epicore.zerocenter_feedback(order,'install',result)
					self.epicore.remove_repo_keys()
					return 1

			msg_log='Installation completed successfully'
			print('  [EPIC]: '+msg_log)
			self.write_log(msg_log)
			self.epicore.remove_repo_keys()
			return 0

		else:
			msg_log='Installation cancelled'
			print ('  [EPIC]: '+msg_log)
			self.write_log(msg_log)
			self.epicore.remove_repo_keys()
			return 0

	#def install_process		

	def install(self,mode,nocheck):

		msg_log="Action to execute: Install.Includes previous system checks: "+str(nocheck)
		self.write_log(msg_log)
		self.check_root=self.epicore.check_root()

		if not nocheck:
			checksystem=self.checking_system(mode,'install')
		else:
			self.lock_info={}
			checksystem=True
		
		if checksystem:
			checkepi=self.checking_epi(mode,'install')
			if checkepi:
				if len(self.lock_info)>0:
					return self.manage_unlock_info(mode,'install')
				else:
					return self.install_process(mode)
			else:
				return 1

		else:
			return 1	

	#def install		

	def uninstall_app(self):

		cmd=self.epicore.uninstall_app(0)

		if cmd !="":
			print('  [EPIC]: Uninstall application...')
			p=subprocess.Popen(cmd,shell=True,stderr=subprocess.PIPE)
			output=p.communicate()
			error=self.readErrorOutput(output[1])
			if error:
				msg_log='Uninstalled process ending with errors:' +'\n'+str(output[1])
				print('  [EPIC]: '+msg_log)
				self.write_log(msg_log)
				return False
			else:
				dpkg_status,result=self.epicore.check_install_remove("uninstall")
				if result:
					return True	
				else:
					msg_log='Uninstalled process ending with errors'
					print('  [EPIC]: '+msg_log)
					self.write_log(msg_log)
					return False	
		else:
			return True	


	#def uninstall_app 	

	def uninstall_process(self,mode):

		self.showInfo(True)
		print('  [EPIC]: Packages selected to uninstall: '+self.pkgs)

		if self.uninstall=='Yes':
			if not mode:
				response=input('  [EPIC]: Do you want to uninstall the package(s) selected (yes/no)): ').lower()
			else:
				response='yes'

			if response.startswith('y'):

				msg_log='Uninstall application by CLI'
				self.write_log(msg_log)
				self.stop_uninstall=self.check_remove_meta()

				if not self.stop_uninstall:
					result=self.uninstall_app()
					if result:
						if not self.metaRemovedWarning:
							msg_log='Application successfully uninstalled'
						else:
							msg_log="Some selected application successfully uninstalled.Others not because they are part of the system's meta-package (%s)"%self.blockedPkgs
						
						print('  [EPIC]: '+msg_log)
						self.write_log(msg_log)
						self.epicore.zerocenter_feedback(0,'uninstall',result)
						return 0

					else:
						self.epicore.zerocenter_feedback(0,'uninstall',result)
						return 1
				else:
					msg_log='Uninstall blocked because remove metapackage.'
					print('  [EPIC]: '+msg_log)
					self.write_log(msg_log)
					return 1
			else:
				msg_log='Uninstall process canceled'
				print ('  [EPIC]: '+msg_log)
				self.write_log(msg_log)
				return 0

		else:
			msg_log='Uninstall process not availabled'
			print ('  [EPIC]: '+msg_log)
			self.write_log(msg_log)
			return 0

					
	#def uninstall_process				

	def uninstall(self,mode,nocheck):
	
		msg_log="Action to execute: Uninstall.Includes previous system checks: "+str(nocheck)
		self.write_log(msg_log)
		self.check_root=self.epicore.check_root()

		if not nocheck:
			checksystem=self.checking_system(mode,'uninstall')
		else:
			self.lock_info={}
			checksystem=True
		if checksystem:
			checkepi=self.checking_epi(mode,'uninstall')
			if checkepi:
				if len(self.lock_info)>0:
					return self.manage_unlock_info(mode,'uninstall')
				else:
					return self.uninstall_process(mode)
			else:
				return 1
		else:
			return 1		


	#def uninstall									

	def check_remove_meta(self):

		self.blockedPkgs=""
		stop_uninstall=False

		print('  [EPIC]: Checking if selected applications can be uninstalled...')
		self.metaRemovedWarning=self.epicore.check_remove_meta()

		if self.metaRemovedWarning:
			count=1
			for item in self.epicore.blockedRemovePkgsList:
				if count<len(self.epicore.blockedRemovePkgsList):
					self.blockedPkgs=self.blockedPkgs+item+", "
				else:
					self.blockedPkgs=self.blockedPkgs+item
				count+=1	

			if len(self.epicore.packages_selected)==len(self.epicore.blockedRemovePkgsList):
				stop_uninstall=True

		msg_log="Packages blocked because remove metapackage: %s"%self.blockedPkgs
		print('  [EPIC]: '+msg_log)
		self.write_log(msg_log)

		return stop_uninstall

	#def check_remove_meta

	def readErrorOutput(self,output):

		cont=0
		if type(output) is bytes:
			output=output.decode()
		lines=output.split('\n')
		for line in lines:
			if "E: " in line:
				cont=cont+1

		if cont>0:
			return True
		else:
			return False	

	# def readErrorOutput		

	def handler_signal(self,signal,frame):

		print("\n  [EPIC]: Cancel process with Ctrl+C signal")
		self.epicore.remove_repo_keys()
		msg_log="Cancel process with Ctrl+C signal"
		self.write_log(msg_log)
		sys.exit(0)
	
	#def handler_signal		

	def write_log(self,msg):

		syslog.openlog("EPI")
		syslog.syslog(msg)
																
		return

	#def write_log	
