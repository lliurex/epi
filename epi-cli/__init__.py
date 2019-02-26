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

	def __init__(self,app):

		self.epicore=EpiManager.EpiManager()
		self.valid_json=self.epicore.read_conf(app)
		signal.signal(signal.SIGINT,self.handler_signal)

		if len(self.epicore.epiFiles)==0:
			if self.valid_json:
				msg_log='APP epi file not exist'
			else:
				msg_log='APP epi file it is not a valid json'	
			print ('  [EPIC]: '+msg_log)
			self.write_log(msg_log)
			sys.exit(1)
		else:
			msg_log='APP epi file loaded by EPIC: ' + app
			self.write_log(msg_log)	


	#def __init__		

	def get_info(self):


		order=len(self.epicore.epiFiles)
		depends=""
		pkgs=""
		
		for item in self.epicore.epiFiles:
			order=order-1
			tmp=self.epicore.epiFiles[order]
			for item in tmp["pkg_list"]:
				if order>0:
					depends=depends+item["name"]+" "
				else:	
					pkgs=pkgs+item["name"] +" "
			
		return depends,pkgs	

	#def get_info			




	def showInfo(self,checked=None):
		
		checksystem=True
		if not checked:
			print ('  [EPIC]: Searching information...')
			self.epicore.get_pkg_info()

		if checksystem:
			depends,pkgs=self.get_info()

			epi_conf=self.epicore.epiFiles[0]
			status=epi_conf["status"]
			
			try:
				if epi_conf["script"]["remove"]:
					self.uninstall="Yes"
			except Exception as e:
				self.uninstall="No"

			print ("  [EPIC]: Information availabled:")
			print ("     Application: " + pkgs)
			print ("     Status: " + status)
			print ("     Uninstall process availabled: " + self.uninstall)
			if len(depends)>0:
				print ("     Additional application required: " + depends)


			return 0
		else:
			return 1	

	#def showInfo	

	def checking_system(self,mode,action=None):

		check=True
		print ('  [EPIC]: Checking system...')

		self.connection=self.epicore.check_connection()

		if self.connection[0]:
			self.epicore.check_root()
			self.epicore.get_pkg_info()
			self.required_root=self.epicore.required_root()
			self.required_x=self.check_required_x()
			self.lock_info=self.epicore.check_locks()
			msg_log="Lock info :"+str(self.lock_info)
			self.write_log(msg_log)
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
		else:
			msg_log="Internet connection not detected: "+self.connection[1] 
			print ('  [EPIC]: '+msg_log)
			self.write_log(msg_log)
			check=False

		return check

	#def checking_system

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
				msg_loc="Apt or Dpks is being updated"
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


	def install_app(self):
	
		cmd=self.epicore.install_app()

		if cmd !="":
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
		error=False
		if not mode:
			response=input('  [EPIC]: Do you want to install the application (yes/no)): ').lower()
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

	def install(self,mode):

		msg_log="Action to execute: Install"
		self.write_log(msg_log)
		checksystem=self.checking_system(mode,'install')
		if checksystem:
			if len(self.lock_info)>0:
				return self.manage_unlock_info(mode,'install')
			else:
				return self.install_process(mode)

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

		if self.uninstall=='Yes':
			if not mode:
				response=input('  [EPIC]: Do you want to uninstall the application (yes/no)): ').lower()
			else:
				response='yes'

			if response.startswith('y'):

				msg_log='Uninstall application by CLI'
				self.write_log(msg_log)

				result=self.uninstall_app()
				if result:
					self.epicore.zerocenter_feedback(0,'uninstall',result)
					msg_log='Application successfully uninstalled'
					print('  [EPIC]: '+msg_log)
					self.write_log(msg_log)
					return 0
				else:
					self.epicore.zerocenter_feedback(0,'uninstall',result)
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

	def uninstall(self,mode):
	
		msg_log="Action to execute: Uninstall"
		self.write_log(msg_log)
		checksystem=self.checking_system(mode,'uninstall')

		if checksystem:
			if len(self.lock_info)>0:
				return self.manage_unlock_info(mode,'uninstall')
			else:
				return self.uninstall_process(mode)
		else:
			return 1		


	#def uninstall									


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