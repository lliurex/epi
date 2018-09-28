#!/usr/bin/env python3

import os
import subprocess
import sys
import html2text
import syslog

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

	def checking_system(self,action=None):

		check=True
		print ('  [EPIC]: Checking system...')

		self.connection=self.epicore.check_connection()

		if self.connection[0]:
			self.epicore.check_root()
			self.epicore.get_pkg_info()
			self.required_root=self.epicore.required_root()
			self.required_x=self.check_required_x()
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


	def install(self,mode):

		checksystem=self.checking_system('install')
		error=False

		if checksystem:
			self.showInfo(True)
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


			else:
				msg_log='Installation cancelled'
				print ('  [EPIC]: '+msg_log)
				self.write_log(msg_log)
				self.epicore.remove_repo_keys()
				return 0

		else:
			return 1	

	#def install		


	def uninstall_process(self):

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

	#def uninstall_process				

	def uninstall(self,mode):
	
		checksystem=self.checking_system('uninstall')
		error=False

		if checksystem:
			self.showInfo(True)
			if self.uninstall=='Yes':
				if not mode:
					response=input('  [EPIC]: Do you want to uninstall the application (yes/no)): ').lower()
				else:
					response='yes'

				if response.startswith('y'):

					msg_log='Uninstall application by CLI'
					self.write_log(msg_log)

					result=self.uninstall_process()
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