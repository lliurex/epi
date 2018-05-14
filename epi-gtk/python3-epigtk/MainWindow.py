#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango, GdkPixbuf, Gdk, Gio, GObject,GLib



import signal
import os
import subprocess
import json
import sys
import syslog
import time
import threading
import tempfile



signal.signal(signal.SIGINT, signal.SIG_DFL)

from . import settings
import gettext
gettext.textdomain(settings.TEXT_DOMAIN)
_ = gettext.gettext

class MainWindow:
	
	def __init__(self,epi_file=None):

		self.core=Core.Core.get_core()

		self.epi_file=epi_file

	#def init

	
	
	def load_gui(self):
		
		builder=Gtk.Builder()
		builder.set_translation_domain(settings.TEXT_DOMAIN)
		ui_path=self.core.ui_path
		builder.add_from_file(ui_path)

		self.css_file=self.core.rsrc_dir+"epi-gtk.css"
		self.ok_image=self.core.rsrc_dir+"ok.svg"
		self.error_image=self.core.rsrc_dir+"error.svg"
		self.sp1=self.core.rsrc_dir+"sp1.svg"
		self.sp2=self.core.rsrc_dir+"sp2.svg"
		self.sp3=self.core.rsrc_dir+"sp3.svg"
		self.sp4=self.core.rsrc_dir+"sp4.svg"
		self.sp5=self.core.rsrc_dir+"sp5.svg"
		self.sp6=self.core.rsrc_dir+"sp6.svg"
		self.sp7=self.core.rsrc_dir+"sp7.svg"
		self.sp8=self.core.rsrc_dir+"sp8.svg"
		
		self.stack = Gtk.Stack()
		self.stack.set_transition_duration(10)
		self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
		
		self.main_window=builder.get_object("main_window")
		self.main_window.set_title("EPI-GTK")
		self.main_box=builder.get_object("main_box")
		self.next_button=builder.get_object("next_button")
		self.apply_button=builder.get_object("apply_button")
		image = Gtk.Image()
		image.set_from_stock(Gtk.STOCK_APPLY,Gtk.IconSize.MENU)
		self.apply_button.set_image(image)	
		self.uninstall_button=builder.get_object("uninstall_button")	
		image = Gtk.Image()
		image.set_from_stock(Gtk.STOCK_REMOVE,Gtk.IconSize.MENU)
		self.uninstall_button.set_image(image)		

		self.return_button=builder.get_object("return_button")
		self.chooserBox=self.core.chooserBox
		self.loadingBox=self.core.loadingBox
		self.epiBox=self.core.epiBox
		self.infoBox=self.core.infoBox

		self.stack.add_titled(self.chooserBox,"chooserBox","ChooserBox")
		self.stack.add_titled(self.loadingBox,"loadingBox","LoadingBox")
		self.stack.add_titled(self.epiBox,"epiBox", "EpiBox")
		self.stack.add_titled(self.infoBox,"infoBox","InfoBox")

		self.main_box.pack_start(self.stack,True,False,5)

		
		self.set_css_info()

		self.connect_signals()
		self.init_install_process()
		self.init_threads()
		
		self.main_window.show_all()

		self.next_button.hide()
		self.apply_button.hide()
		self.uninstall_button.hide()
		self.return_button.hide()
		self.epiBox.epi_depend_label.hide()
		self.epiBox.terminal_label.hide()
		self.epiBox.terminal_scrolled.hide()
		self.epiBox.viewport.hide()
		
		self.install_dep=True
		self.final_column=0
		self.final_row=0

		if self.epi_file!=None:
			self.init_process()
		else:
			self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
			self.stack.set_visible_child_name("chooserBox")	

		
		
	#def load_gui

	def set_css_info(self):
		
		
		self.style_provider=Gtk.CssProvider()
		f=Gio.File.new_for_path(self.css_file)
		self.style_provider.load_from_file(f)
		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),self.style_provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		self.main_window.set_name("WINDOW")

	#def set_css_info	
				
			
	def connect_signals(self):
		
		self.main_window.connect("destroy",self.quit)
		self.apply_button.connect("clicked",self.install_process)
		self.uninstall_button.connect("clicked",self.uninstall_process)
		self.return_button.connect("clicked",self.go_back)
		self.next_button.connect("clicked",self.go_forward)
	
		
	#def connect_signals

	def go_forward(self,widget):

		self.epi_file=self.core.chooserBox.epi_loaded
		self.stack.set_transition_duration(1000)
		self.init_process()

	#def go_forward	

	def init_process(self):

		msg_log='APP conf file loaded by EPI-GTK: ' + self.epi_file
		self.write_log(msg_log)
		self.next_button.hide()
		self.loadingBox.loading_spinner.start()
		self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
		self.stack.set_visible_child_name("loadingBox")	
		self.stack.set_transition_duration(1000)
		GLib.timeout_add(100,self.pulsate_checksystem)
	
	#def init_process

	def init_threads(self):

		self.checking_system_t=threading.Thread(target=self.checking_system)
		self.checking_system_t.daemon=True
		self.checking_system_t.launched=False
		self.checking_system_t.done=False

		GObject.threads_init()

	#def init_threads	


	def load_info(self):

		self.epiBox.load_info(self.load_epi_conf)
		
		if self.order>1:
			self.epiBox.epi_depend_label.show()
			self.epiBox.scrolledwindow.set_size_request(500,160)
		else:
			if len(self.load_epi_conf[0]["pkg_list"])>1:
				self.epiBox.scrolledwindow.set_size_request(500,160)
			else:	
				self.epiBox.scrolledwindow.set_size_request(500,90)
		
	
	#def load_info

	def pulsate_checksystem(self):

		error=False

		if not self.checking_system_t.launched:
			self.checking_system_t.start()
			self.checking_system_t.launched=True


		if self.checking_system_t.done:

			if self.connection:
				if self.order>0:
					if not self.required_root:
						self.load_info()
						self.apply_button.show()
						self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
						if self.load_epi_conf[0]["status"]=="installed":
							self.epiBox.terminal_label.set_name("MSG_LABEL")
							self.epiBox.terminal_label.show()
							msg_code=0
							msg=self.get_msg_text(msg_code)
							self.epiBox.terminal_label.set_text(msg)
							self.show_apply_uninstall_buttons()
						self.stack.set_visible_child_name("epiBox")	

						return False
					else:
						error=True
						msg_code=2	
				else:
					error=True
					msg_code=1
					
			else:
				error=True
				msg_code=3
								

		if error:
			self.loadingBox.loading_spinner.stop()
			self.loadingBox.loading_label.set_name("MSG_ERROR_LABEL")	
			msg_error=self.get_msg_text(msg_code)
			self.write_log(msg_error)
			self.loadingBox.loading_label.set_text(msg_error)
			return False


		if self.checking_system_t.launched:
			if not self.checking_system_t.done:
				return True	


	#def pulsate_checksystem			
	
	def checking_system(self):
	
		time.sleep(1)
		self.connection=self.core.epiManager.check_connection()
		
		if self.connection:
			self.core.epiManager.read_conf(self.epi_file)
			epi_loaded=self.core.epiManager.epiFiles
			order=len(epi_loaded)
			if order>0:
				self.core.epiManager.check_root()
				self.core.epiManager.get_pkg_info()
				self.required_root=self.core.epiManager.required_root()
				self.checking_system_t.done=True
				self.load_epi_conf=self.core.epiManager.epiFiles
				self.order=len(self.load_epi_conf)
			else:
				self.load_epi_conf=epi_loaded
				self.order=order
			

		self.checking_system_t.done=True	

	#def checking_system	

	def check_remove_script(self):

		remove=False
		if len(self.load_epi_conf[0]["script"])>0:
			try:
				remove=self.load_epi_conf[0]["script"]["remove"]
			except Exception as e:
				pass

		return remove

	#def check_remove_script			

	def show_remove_button(self,action=None):

		remove=self.check_remove_script()

		status=self.load_epi_conf[0]["status"]

		if remove:
			if action=="install":
				self.uninstall_button.show()
				self.uninstall_button.set_sensitive(True)
			elif action=="uninstalled":
					self.uninstall_button.hide()
			else:
				if status=="installed":
					self.uninstall_button.show()

				else:
					self.uninstall_button.hide()		
			
		else:
			self.uninstall_button.hide()	

	#def show_remove_button			


	def show_apply_uninstall_buttons(self):

		remove=self.check_remove_script()
		status=self.load_epi_conf[0]["status"]

		if status=='availabled':
			self.apply_button.set_label(_("Install"))
			self.apply_button.set_sensitive(True)
			self.uninstall_button.hide()

		else:
			self.apply_button.set_label(_("Reinstall"))
			self.apply_button.set_sensitive(True)
			if remove:
				self.uninstall_button.show()
				self.uninstall_button.set_sensitive(True)

			else:
				self.uninstall_button.hide()			

	#def show_apply_uninstall_buttons			

	def init_install_process(self):

		self.add_repository_keys_launched=False
		self.add_repository_keys_done=False

		self.download_app_launched=False
		self.download_app_done=False

		self.check_download_launched=False
		self.check_download_done=False

		self.preinstall_app_launched=False
		self.preinstall_app_done=False

		self.check_preinstall_launched=False
		self.check_preinstall_donde=False

		self.install_app_launched=False
		self.install_app_done=False

		self.check_install_launched=False
		self.check_install_done=False

		self.postinstall_app_launched=False
		self.postinstall_app_done=False

		self.check_postinstall_launched=False
		self.check_postinstall_done=False


	#def init_install_process	

	def spinner_sync(self,order):

		
		if self.sp_cont>40:
			self.sp_cont=0
				
		if self.sp_cont==0:
			self.img=self.sp1
			
		elif self.sp_cont==5:
			self.img=self.sp2
					
		elif self.sp_cont==10:
			self.img=self.sp3
			
		elif self.sp_cont==15:
			self.img=self.sp4
			
		elif self.sp_cont==20:
			self.img=self.sp5

		elif self.sp_cont==25:
			self.img=self.sp6

		elif self.sp_cont==30:
			self.img=self.sp7

		elif self.sp_cont==35:
			self.img=self.sp8			

	
		elements=self.epiBox.update_icons[order]
		for item in elements:
			item['icon_status'].set_from_file(self.img)
			
	#def spinner_sync						


	def install_process(self,wigdet):

		self.sp_cont=0
		self.epiBox.terminal_scrolled.show()
		self.epiBox.viewport.show()
		self.init_install_process()
		self.apply_button.set_sensitive(False)
		self.uninstall_button.set_sensitive(False)
		
		if self.install_dep:
			if self.order>0:
				self.order=self.order-1
		else:
			self.order=0

		self.epiBox.terminal_label.set_name("MSG_LABEL")
		self.core.epiManager.zerocenter_feedback(self.order,"init")	
		GLib.timeout_add(100,self.pulsate_install_package,self.order)

	#def install_processs


	def pulsate_install_package(self,order):
		
		self.spinner_sync(order)
		self.sp_cont=self.sp_cont+1
		error=False

		if not self.add_repository_keys_launched:
			self.epiBox.terminal_label.show()
			msg=self.get_msg_text(4)
			self.epiBox.terminal_label.set_text(msg)
			self.add_repository_keys_launched=True
			self.sp_cont=self.sp_cont+1
			if order==0:
				self.install_dep=False
				
			self.add_repository_keys(order)
			
		
		if self.add_repository_keys_done:
			if not self.download_app_launched:
				msg=self.get_msg_text(5)
				self.epiBox.terminal_label.set_text(msg)
				self.download_app_launched=True
				self.download_app()

			if self.download_app_done:

				if not self.check_download_launched:
					self.check_download_launched=True
					self.check_download()

				if self.check_download_done:
					if self.download_result:	
									
						if not self.preinstall_app_launched:
							msg=self.get_msg_text(6)
							self.epiBox.terminal_label.set_text(msg)
							self.preinstall_app_launched=True
							self.preinstall_app()

						if self.preinstall_app_done:	

							if not self.check_preinstall_launched:
								self.check_preinstall_launched=True
								self.check_preinstall()

							if self.check_preinstall_done:
								
								
								if self.preinstall_result:
									if not self.install_app_launched:
										msg=self.get_msg_text(7)
										self.epiBox.terminal_label.set_text(msg)
										self.install_app_launched=True
										self.install_app()

									if self.install_app_done:

										if not self.check_install_launched:
											self.check_install_launched=True
											self.check_install()

											
										if self.check_install_done:	
											if self.installed:
												if not self.postinstall_app_launched:
													msg=self.get_msg_text(8)
													self.epiBox.terminal_label.set_text(msg)
													self.postinstall_app_launched=True
													self.postinstall_app()	

												if self.postinstall_app_done:

													if not self.check_postinstall_launched:
														self.check_postinstall_launched=True
														self.check_postinstall()

													if self.check_postinstall_done:
														
														if self.postinstall_result:	
															params=[order,True,'install',None]
															self.update_icon(params)
															self.core.epiManager.zerocenter_feedback(self.order,"install",True)

															if self.order>0:
																self.order=self.order-1
																self.sp_cont=0
																self.init_install_process()
																GLib.timeout_add(100,self.pulsate_install_package,self.order)

															else:
																msg=self.get_msg_text(9)
																self.epiBox.terminal_label.set_name("MSG_CORRECT_LABEL")
																self.epiBox.terminal_label.set_text(msg)
																self.write_log_terminal('install')
																self.load_epi_conf[0]["status"]="installed"
																self.write_log(msg)
																self.show_apply_uninstall_buttons()
																return False
															return False

														else:
															error=True
															error_code=10
															params=[order,False,'install',None]
											else:
												error=True
												error_code=11
												params=[order,False,'install',self.dpkg_status]
												
								else:
									error=True
									error_code=12
									params=[order,False,'install',None]
																				
					else:
						error=True
						error_code=13
						params=[order,False,'install',None]
										

		if error:
			msg_error=self.get_msg_text(error_code)
			self.epiBox.terminal_label.set_name("MSG_ERROR_LABEL")
			self.epiBox.terminal_label.set_text(msg_error)
			self.update_icon(params)
			self.core.epiManager.zerocenter_feedback(params[0],"install",False)
			self.write_log_terminal('install')
			self.write_log(msg_error)
			return False

		if self.add_repository_keys_launched:
			
			if 	not self.add_repository_keys_done:
				if os.path.exists(self.token_keys[1]):
					return True
				else:
					
					self.add_repository_keys_done=True
					return True
		
		if self.download_app_launched:
			
			if 	not self.download_app_done:
				if os.path.exists(self.token_download[1]):
					return True
				else:
					self.download_app_done=True
					return True	

		if self.check_download_launched:
			if not self.check_download_done:
				return True			
		
		if self.preinstall_app_launched:
			
			if 	not self.preinstall_app_done:
				if os.path.exists(self.token_preinstall[1]):
					return True
				else:
					self.preinstall_app_done=True
					return True		

		if self.check_preinstall_launched:
			if not self.check_preinstall_done:
				return				

		if self.install_app_launched:
			
			if 	not self.install_app_done:
				if os.path.exists(self.token_install[1]):
					return True
				else:
					self.install_app_done=True
					return True		

		if self.check_install_launched:
			if not self.check_install_done:
				return True


		if self.postinstall_app_launched:
			
			if 	not self.postinstall_app_done:
				if os.path.exists(self.token_postinstall[1]):
					return True
				else:
					self.postinstall_app_done=True
					return True		

		if self.check_postinstall_launched:
			if not self.check_postinstall_done:
				return										

	#def pulsate_install_package				

	def add_repository_keys(self,order):

		command=self.core.epiManager.add_repository_keys(order)
		length=len(command)
		if length>0:
			command=self.create_process_token(command,"keys")
			length=len(command)
			self.epiBox.vterminal.feed_child(command,length)
		else:
			self.add_repository_keys_done=True

	#def add_repository_keys		

	def download_app(self):

		command=self.core.epiManager.download_app()
		length=len(command)
		if length>0:
			command=self.create_process_token(command,"download")
			length=len(command)
			self.epiBox.vterminal.feed_child(command,length)
		else:
			self.download_app_done=True	

	#def download_app		

	def check_download(self):

		self.download_result=self.core.epiManager.check_download()
		self.check_download_done=True

	#def check_download

	def check_preinstall(self):

		self.preinstall_result=self.core.epiManager.check_preinstall()
		self.check_preinstall_done=True

	#def check_preinstall		

	
	def preinstall_app(self):

		command=self.core.epiManager.preinstall_app()

		length=len(command)
		if length>0:
			command=self.create_process_token(command,"preinstall")
			length=len(command)
			self.epiBox.vterminal.feed_child(command,length)

		else:
			self.preinstall_app_done=True	 		

	#def preinstall_app		


	def install_app(self):

	 	command=self.core.epiManager.install_app()

	 	length=len(command)
	 	if length>0:
	 		command=self.create_process_token(command,"install")
	 		length=len(command)
	 		self.epiBox.vterminal.feed_child(command,length)
	 	else:
	 		self.install_app_done=True	

	 #def install_app

	def check_install(self):

		self.dpkg_status,self.installed=self.core.epiManager.check_install_remove("install")
		self.check_install_done=True

	#def check_install	

	def postinstall_app(self):

	 	command=self.core.epiManager.postinstall_app()
	 	length=len(command)
	 	if length>0:
	 		command=self.create_process_token(command,"postinstall")
	 		length=len(command)
	 		self.epiBox.vterminal.feed_child(command,length)
	 	else:
	 		self.postinstall_app_done=True	 		

	#def postinstall_app

	def check_postinstall(self):

		self.postinstall_result=self.core.epiManager.check_postinstall()
		self.check_postinstall_done=True

	#def check_postinstall					

	def init_uninstall_process(self):

		self.remove_package_launched=False
		self.remove_package_done=False

		self.check_remove_launched=False
		self.check_remove_done=False

	#def init_uninstall_process	

	def uninstall_process(self,widget):

		dialog = Gtk.MessageDialog(None,0,Gtk.MessageType.WARNING, Gtk.ButtonsType.YES_NO, "EPI-GTK")
		msg=self.get_msg_text(14)
		dialog.format_secondary_text(msg)
		response=dialog.run()
		dialog.destroy()
		

		if response==Gtk.ResponseType.YES:

			self.sp_cont=0
			self.epiBox.terminal_scrolled.show()
			self.epiBox.viewport.show()
			self.init_uninstall_process()
			self.apply_button.set_sensitive(False)
			self.uninstall_button.set_sensitive(False)
			self.epiBox.terminal_label.set_name("MSG_LABEL")
			
			GLib.timeout_add(100,self.pulsate_uninstall_process,0)

	#def uninstall_process		


	def pulsate_uninstall_process(self,order):

		self.spinner_sync(order)
		self.sp_cont=self.sp_cont+1
		
		if not self.remove_package_launched:
			self.epiBox.terminal_label.show()
			msg=self.get_msg_text(15)
			self.epiBox.terminal_label.set_text(msg)
			self.remove_package_launched=True
			self.sp_cont=self.sp_cont+1
			self.uninstall_app(order)


		if self.remove_package_done:

			if not self.check_remove_launched:
				self.check_remove_launched=True
				self.check_remove()
			
			if self.check_remove_done:
				
				if self.remove:
					msg=self.get_msg_text(16)
					self.epiBox.terminal_label.set_name("MSG_CORRECT_LABEL")
					self.epiBox.terminal_label.set_text(msg)
					params=[order,True,'remove',None]
					self.update_icon(params)
					self.load_epi_conf[0]["status"]="availabled"
					self.show_apply_uninstall_buttons()
					if self.order==0:
						self.install_dep=False
					self.core.epiManager.zerocenter_feedback(0,"uninstall",True)
					self.write_log_terminal('uninstall')
					self.write_log(msg)
					return False
				else:
					msg=self.get_msg_text(17)
					self.epiBox.terminal_label.set_name("MSG_ERROR_LABEL")
					self.epiBox.terminal_label.set_text(msg)
					params=[order,False,'remove',self.dpkg_status]
					self.update_icon(params)
					self.core.epiManager.zerocenter_feedback(0,"uninstall",False)
					self.write_log_terminal('unistall')
					self.write_log(msg)
					return False

	

		if self.remove_package_launched:
			if 	not self.remove_package_done:
				if os.path.exists(self.token_uninstall[1]):
					return True
				else:
					self.remove_package_done=True
					return True		

		if self.check_remove_launched:
			if not self.check_remove_done:
				return True				

	#def pulsate_uninstall_process				


	def uninstall_app(self,order):

		command=self.core.epiManager.uninstall_app(order)

		length=len(command)
		if length>0:
			command=self.create_process_token(command,"uninstall")
			length=len(command)
			self.epiBox.vterminal.feed_child(command,length)

		else:
			self.preinstall_app_done=True	

	#def uninstall_app	

	def check_remove(self):

		self.dpkg_status,self.remove=self.core.epiManager.check_install_remove("uninstall")
		self.check_remove_done=True

	#def check_remove	

	def update_icon(self,params):

		order=params[0]
		result=params[1]
		process=params[2]
		dpkg_status=params[3]

		elements=self.epiBox.update_icons[order]

		elements=self.epiBox.update_icons[order]
		for item in elements:
			item['icon_status'].set_from_file(self.img)

		if result:
			for item in elements:
				item['icon_status'].set_from_file(self.ok_image)
				if process=="install":
					if order==0:
						item['icon_package'].set_from_file(self.core.epiBox.package_installed)

					else:
						item['icon_package'].set_from_file(self.core.epiBox.package_installed_dep)

				else:
					if order==0:
						item['icon_package'].set_from_file(self.core.epiBox.package_availabled)
					else:
						item['icon_package'].set_from_file(self.core.epiBox.package_availabled_dep)


		else:
			if dpkg_status !=None and len(dpkg_status)>0:
				for item in elements:
					status=dpkg_status[item['icon_status'].id]
					if process=="install":
						if status=="installed":
							item['icon_status'].set_from_file(self.ok_image)
							if order==0:
								item["icon_package"].set_from_file(self.core.epiBox.package_installed)	
							else:
								item["icon_package"].set_from_file(self.core.epiBox.package_installed_dep)	
		
						else:
							item['icon_status'].set_from_file(self.error_image)

							if order==0:
								item["icon_package"].set_from_file(self.core.epiBox.package_availabled)
							else:
								item["icon_package"].set_from_file(self.core.epiBox.package_availabled_dep)

					else:
						if status=="availabled":
							item["icon_status"].set_from_file(self.ok_image)
						else:
							item["icon_status"].set_from_file(self.error_image)	

			else:
				for item in elements:
					item['icon_status'].set_from_file(self.error_image)			


	#def update_icon
															
	def go_back(self,widget):

		self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_RIGHT)
		self.stack.set_visible_child_name("epiBox")		
		self.apply_button.show()
		self.return_button.hide()
		self.show_apply_uninstall_buttons()

	#def go_back	


	def get_msg_text(self,code):

		if code==0:
			msg=_("Application already installed")
		elif code==1:
			msg=_("Application epi file does not exist")	
		elif code==2:
			msg=_("You need root privileges")
		elif code==3:
			msg=_("Internet connection not detected")
		elif code==4:
			msg=_("Gathering Information...")
		elif code==5:
			msg=_("Downloading application...")
		elif code==6:
			msg=_("Preparing installation...")
		elif code==7:
			msg=_("Installing application...")
		elif code==8:
			msg=_("Ending the installation...")
		elif code==9:
			msg=_("Installation completed successfully")
		elif code==10:
			msg=_("Installation aborted. Error ending installation")
		elif code==11:
			msg=_("Installation aborted. Error installing application")
		elif code==12:
			msg=_("Installation aborted. Error preparing system")
		elif code==13:
			msg=_("Installation aborted. Unable to download package")
		elif code==14:
			msg=_("Do you want uninstall the application?")
		elif code==15:
			msg=_("Uninstall application...")
		elif code==16:
			msg=_("Application successfully uninstalled")
		elif code==17:
			msg=_("Uninstalled process ending with errors")
		

		return msg	

	#def get_msg_text

	def create_process_token(self,command,action):


		if action=="keys":
			self.token_keys=tempfile.mkstemp('_keys')
			remove_tmp=' rm -f ' + self.token_keys[1] + ';'+'\n'
			
		elif action=="download":
			self.token_download=tempfile.mkstemp('_download')
			remove_tmp=' rm -f ' + self.token_download[1] + ';'+'\n'

		elif action=="preinstall":
			self.token_preinstall=tempfile.mkstemp('_preinstall')	
			remove_tmp=' rm -f ' + self.token_preinstall[1] + ';'+'\n'
			
		elif action=="install":
			self.token_install=tempfile.mkstemp('_install')
			remove_tmp=' rm -f ' + self.token_install[1] +';'+'\n'

		elif action=="postinstall":	
			self.token_postinstall=tempfile.mkstemp('_postinstall')
			remove_tmp=' rm -f ' + self.token_postinstall[1] +';'+'\n'

		elif action=="uninstall":
			self.token_uninstall=tempfile.mkstemp('_uninstall')
			remove_tmp=' rm -f ' + self.token_uninstall[1] +';'+'\n'

		cmd=command+remove_tmp
		return cmd

	#def create_process_token			

	def quit(self,widget):

		msg_log='Quit'
		self.write_log(msg_log)
		self.core.epiManager.remove_repo_keys()
		Gtk.main_quit()	

	#def quit	

	def write_log_terminal(self,action):

		init_row=self.final_row
		init_column=self.final_column

		self.final_column,self.final_row = self.epiBox.vterminal.get_cursor_position()
		log_text=self.epiBox.vterminal.get_text_range(init_row,init_column,self.final_row,self.final_column)[0]

		log_text=log_text.split("\n")

		
		if action=="install":
			syslog.openlog("EPI")
			syslog.syslog("Install Application")
		else:
			syslog.openlog("EPI")
			syslog.syslog("Uninstall Application")
				
		
		for item in log_text:
			if item!="":
				self.write_log(item)
																				
		return

	#def write_log_terminal	

	def write_log(self,msg):
	
		syslog.openlog("EPI")
		syslog.syslog(msg)	

	#def write_log	

	
	def start_gui(self):
		
		GObject.threads_init()
		Gtk.main()
		
	#def start_gui

	

	
#class MainWindow
'''

if __name__=="__main__":
	
	lgd.start_gui()
'''	
from . import Core
