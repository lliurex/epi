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
	
	def __init__(self,noCheck=False,epi_file=None):

		self.core=Core.Core.get_core()

		self.epi_file=epi_file
		self.no_check=noCheck

	#def init
	
	def load_gui(self):
		
		builder=Gtk.Builder()
		builder.set_translation_domain(settings.TEXT_DOMAIN)
		ui_path=self.core.ui_path
		builder.add_from_file(ui_path)

		self.css_file=self.core.rsrc_dir+"epi-gtk.css"
		self.ok_image=self.core.rsrc_dir+"ok.png"
		self.error_image=self.core.rsrc_dir+"error.png"
		self.sp1=self.core.rsrc_dir+"sp1.png"
		self.sp2=self.core.rsrc_dir+"sp2.png"
		self.sp3=self.core.rsrc_dir+"sp3.png"
		self.sp4=self.core.rsrc_dir+"sp4.png"
		self.sp5=self.core.rsrc_dir+"sp5.png"
		self.sp6=self.core.rsrc_dir+"sp6.png"
		self.sp7=self.core.rsrc_dir+"sp7.png"
		self.sp8=self.core.rsrc_dir+"sp8.png"
		
		self.stack = Gtk.Stack()
		self.stack.set_transition_duration(10)
		self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
		
		self.main_window=builder.get_object("main_window")
		self.main_window.set_title("EPI")
		self.main_window.resize(675,550)
		self.banner_box=builder.get_object("banner_box")
		self.main_box=builder.get_object("main_box")
		self.feedback_box=builder.get_object("feedback_box")
		self.feedback_ok_img=builder.get_object("feedback_ok_img")
		self.feedback_error_img=builder.get_object("feedback_error_img")
		self.feedback_info_img=builder.get_object("feedback_info_img")
		self.feedback_warning_img=builder.get_object("feedback_warning_img")
		self.feedback_label=builder.get_object("feedback_label")
		self.feedback_label.set_halign(Gtk.Align.CENTER)

		self.next_button=builder.get_object("next_button")
		self.apply_button=builder.get_object("apply_button")
		image = Gtk.Image()
		image.set_from_stock(Gtk.STOCK_APPLY,Gtk.IconSize.MENU)
		self.apply_button.set_image(image)	
		self.unlock_button=builder.get_object("unlock_button")
		image1 = Gtk.Image()
		image1.set_from_stock(Gtk.STOCK_APPLY,Gtk.IconSize.MENU)
		self.unlock_button.set_image(image1)
		self.uninstall_button=builder.get_object("uninstall_button")	
		image = Gtk.Image()
		image.set_from_stock(Gtk.STOCK_REMOVE,Gtk.IconSize.MENU)
		self.uninstall_button.set_image(image)		

		self.return_button=builder.get_object("return_button")
		self.chooserBox=self.core.chooserBox
		self.loadingBox=self.core.loadingBox
		self.dependsBox=self.core.dependsBox
		self.epiBox=self.core.epiBox
		self.infoBox=self.core.infoBox
		self.terminalBox=self.core.terminalBox

		self.stack.add_titled(self.chooserBox,"chooserBox","ChooserBox")
		self.stack.add_titled(self.loadingBox,"loadingBox","LoadingBox")
		self.stack.add_titled(self.dependsBox,"dependsBox","DependsBox")
		self.stack.add_titled(self.epiBox,"epiBox", "EpiBox")
		self.stack.add_titled(self.infoBox,"infoBox","InfoBox")
		self.stack.add_titled(self.terminalBox,"terminalBox","TerminalBox")

		self.main_box.pack_start(self.stack,True,False,5)
		
		self.set_css_info()

		self.connect_signals()
		self.init_install_process()
		self.init_threads()
		
		self.main_window.show_all()
		self.next_button.hide()
		self.apply_button.hide()
		self.unlock_button.hide()
		self.uninstall_button.hide()
		self.return_button.hide()
		self.epiBox.view_terminal_btn.set_sensitive(False)
		self.epiBox.epi_depend_label.set_text("")
		self.epiBox.select_pkg_btn.set_visible(False)
		
		self.eulaBox=self.core.eulaBox
		self.install_dep=True
		self.eula_accepted=True
		self.final_column=0
		self.final_row=0
		self.time_out=5
		self.retry=0
		self.lock_quit=False
		self.show_depends=False
		self.loadingBox.manage_loading_msg_box(True)
		self.manage_feedback_box(True)

		if self.epi_file!=None:
			if self.epi_file!="--error":
				self.init_process()
			else:	
				self.deb_error()
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
		self.banner_box.set_name("BANNER_BOX")
		self.feedback_label.set_name("MSG_LABEL")

	#def set_css_info	
			
	def connect_signals(self):
		
		self.main_window.connect("destroy",self.quit)
		self.main_window.connect("delete-event",self.unable_quit)
		self.apply_button.connect("clicked",self.apply_button_clicked)
		self.uninstall_button.connect("clicked",self.uninstall_process)
		self.return_button.connect("clicked",self.go_back)
		self.next_button.connect("clicked",self.go_forward)
		self.unlock_button.connect("clicked",self.unlock_clicked)
	
	#def connect_signals

	def go_forward(self,widget):

		self.epi_file=self.core.chooserBox.epi_loaded
		self.stack.set_transition_duration(1000)
		self.init_process()

	#def go_forward	

	def deb_error(self):

		msg_log='APP conf file loaded by EPI-GTK: ' + self.epi_file
		self.write_log(msg_log)
		msg_log="Error preparing deb processing to generate the epi files"
		self.write_log(msg_log)
		self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
		self.stack.set_visible_child_name("loadingBox")
		#self.loadingBox.loading_label.set_name("MSG_ERROR_LABEL")	
		msg_error=self.get_msg_text(25)
		self.loadingBox.loading_label.set_text(msg_error)
		self.loadingBox.manage_loading_msg_box(False)
	
	#def deb_error	

	def init_process(self):

		msg_log='APP conf file loaded by EPI-GTK: ' + self.epi_file
		self.write_log(msg_log)
		self.next_button.hide()
		self.loadingBox.loading_spinner.start()
		self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
		self.stack.set_visible_child_name("loadingBox")	
		self.stack.set_transition_duration(1000)
		self.connection=[]
		self.first_connection=False
		self.second_connection=False

		self.init_threads()

		self.checking_system_t.start()
		self.checking_system_t.launched=True	

		if not self.no_check:
			self.checking_url1_t.start()
			self.checking_url1_t.launched=True
			self.checking_url2_t.start()
			self.checking_url2_t.launched=True
		else:
			self.first_connection=True
			self.second_connection=True

		GLib.timeout_add(100,self.pulsate_checksystem)

	#def init_process

	def init_threads(self):

		self.checking_url1_t=threading.Thread(target=self.checking_url1)
		self.checking_url2_t=threading.Thread(target=self.checking_url2)
		self.checking_system_t=threading.Thread(target=self.checking_system)
		self.unlock_process_t=threading.Thread(target=self.unlock_process)
		self.checking_url1_t.daemon=True
		self.checking_url2_t.daemon=True
		self.checking_system_t.daemon=True
		self.unlock_process_t.daemon=True
		self.checking_system_t.launched=False
		self.checking_url1_t.launched=False
		self.checking_url2_t.launched=False
		self.unlock_process_t.launched=False
		self.checking_system_t.done=False
		self.unlock_process_t.done=False

		GObject.threads_init()

	#def init_threads	

	def load_info(self):

		self.epiBox.load_info()
		
		if self.order>1:
			self.show_depends=True
	
	#def load_info

	def checking_url1(self):

		self.connection=self.core.epiManager.check_connection(self.core.epiManager.urltocheck1)
		self.first_connection=self.connection[0]
	
	#def checking_url1	

	def checking_url2(self):

		self.connection=self.core.epiManager.check_connection(self.core.epiManager.urltocheck2)
		self.second_connection=self.connection[0]
 	
 	#def checking_url2

	def pulsate_checksystem(self):

		end_check=False
		error=False
		url_error=False

		if not self.no_check:
			if self.checking_url1_t.is_alive() and self.checking_url2_t.is_alive():
				return True 
			else:
				if not self.first_connection and not self.second_connection:
					if self.checking_url1_t.is_alive() or self.checking_url2_t.is_alive():
						return True
					else:
						end_check=True
				else:
					end_check=True
		else:
			end_check=True

		if end_check:
			if self.checking_system_t.done:
				if not self.first_connection and not self.second_connection:
					msg_code=3
					error=True
					url_error=True
				else:
					if self.valid_json["status"]:	
						if self.valid_script["status"]:		
							if not self.required_root:
								if len (self.lock_info)>0:
									self.load_unlock_panel()
									return False
								else:
									if self.test_install[0]!='':
										if self.test_install[0]=='1':
											error=True
											msg_code=25
										else:
											self.load_depends_panel()
											return False
									else:		
										self.load_info_panel()
										return False
							else:
								error=True
								msg_code=2	
						else:
							error=True
							if self.valid_script["error"]=="path":
								msg_code=32
							else:
								msg_code=33				
					else:
						error=True
						if self.valid_json["error"]=="path":
							msg_code=1
						elif self.valid_json["error"]=="json":
							msg_code=18
						else:
							msg_code=34			
			
		if error:
			self.loadingBox.loading_spinner.stop()
			#self.loadingBox.loading_label.set_name("MSG_ERROR_LABEL")	
			msg_error=self.get_msg_text(msg_code)
			if url_error:
				self.write_log(msg_error+":"+self.connection[1])
			else:
				self.write_log(msg_error)	
			self.loadingBox.loading_label.set_text(msg_error)
			self.loadingBox.manage_loading_msg_box(False)
			return False

		if self.checking_system_t.launched:
			if not self.checking_system_t.done:
				return True	

	#def pulsate_checksystem			
	
	def checking_system(self):
	
		self.valid_json=self.core.epiManager.read_conf(self.epi_file)
		if self.valid_json["status"]:
			self.valid_script=self.core.epiManager.check_script_file()
			if self.valid_script["status"]:
				epi_loaded=self.core.epiManager.epiFiles
				order=len(epi_loaded)
				if order>0:
					check_root=self.core.epiManager.check_root()
					self.core.epiManager.get_pkg_info()
					self.required_root=self.core.epiManager.required_root()
					self.required_eula=self.core.epiManager.required_eula()
					if len(self.required_eula)>0:
						self.eula_accepted=False
					if check_root:
						if not self.no_check:	
							self.lock_info=self.core.epiManager.check_locks()
						else:
							self.lock_info={}
						self.write_log("Locks info: "+ str(self.lock_info))
					else:
						self.lock_info={}
						self.write_log("Locks info: Not checked. User is not root")
					self.test_install=self.core.epiManager.test_install()
					self.write_log("Locks info: "+ str(self.lock_info))
					self.checking_system_t.done=True
					self.load_epi_conf=self.core.epiManager.epiFiles
					self.order=len(self.load_epi_conf)
				else:
					self.load_epi_conf=epi_loaded
					self.order=order
					self.checking_system_t.done=True
			else:
				self.checking_system_t.done=True		
		else:
			self.checking_system_t.done=True	

	#def checking_system	

	def load_unlock_panel(self):

		waiting=0

		if "Lliurex-Up" in self.lock_info:
			self.loadingBox.loading_spinner.hide()
			self.write_log("Lock info: The system is being updated")
			msg=self.get_msg_text(19)
			self.loadingBox.loading_label.set_text(msg)
			self.loadingBox.manage_loading_msg_box(False)

		else:
			if self.lock_info["wait"]:
				self.is_working=False
				self.abort=False
				self.lock_error=False
				self.loadingBox.loading_spinner.start()
				self.write_log("Lock info: Apt or Dpkg are being executed. Checking if they have finished...")
				msg=self.get_msg_text(20)
				self.loadingBox.loading_label.set_text(msg)
				GLib.timeout_add_seconds(5, self.is_worker)
			else:
				self.unlock_button.show()
				self.loadingBox.loading_spinner.hide()
				self.unlock_button.show()
				msg=self.get_msg_text(22)
				self.loadingBox.loading_label.set_text(msg)
				self.loadingBox.manage_loading_msg_box(False)

	#def load_unlock_panel			
				
	def is_worker(self):
	
		if self.retry<self.time_out:
			locks=self.core.epiManager.check_locks()
			if len(locks)>0:
				self.retry+=5
			else:
				self.abort=True
		else:
			locks=self.core.epiManager.check_locks()
			if len(locks)>0:
				self.loadingBox.loading_spinner.hide()
				self.loadingBox.manage_loading_msg_box(False)
				if "Lliurex-Up" in self.lock_info:
					self.write_log("Lock checking finished: The system is being updated")
					msg=self.get_msg_text(19)
					self.loadingBox.loading_label.set_text(msg)	
					return False
				else:
					if locks["wait"]:
						self.write_log("Lock checking finished: Apt or Dpkg are being executed. Wait")
						msg=self.get_msg_text(21)
						self.loadingBox.loading_label.set_text(msg)
						return False
					else:
						self.unlock_button.show("Lock checking finished: Apt or Dpkg are blocked")
						msg=self.get_msg_text(22)
						self.loadingBox.loading_label.set_text(msg)
						return False
			else:
				self.abort=True			

		if self.abort:
			self.write_log("Lock checking finished: no locks detected")
			self.loadingBox.loading_spinner.hide()
			self.unlock_button.hide()
			self.load_info_panel()	
			return False
		else:
			return True

	#def is_worker		

	def unlock_clicked(self,widget):
	
		self.unlock_button.set_sensitive(False)
		msg=self.get_msg_text(23)
		self.loadingBox.loading_label.set_text(msg)
		self.init_threads()
		self.loadingBox.loading_spinner.show()
		GLib.timeout_add(5,self.pulsate_unlock_process)

	#def unlock_clicked	
		
	def pulsate_unlock_process(self):

		if not self.unlock_process_t.launched:
			self.loadingBox.loading_spinner.start()
			self.unlock_process_t.start()
			self.unlock_process_t.launched=True

		if self.unlock_process_t.done:
			self.loadingBox.loading_spinner.hide()
			self.unlock_button.hide()
			if self.unlock_result==0:
				self.write_log("Unlock process ok")
				self.load_info_panel()
				return False

			else:
				msg=self.get_msg_text(24)
				self.write_log("Unlock process failed: "+str(self.unlock_result))
				#self.loadingBox.loading_label.set_name("MSG_ERROR_LABEL")
				self.loadingBox.manage_loading_msg_box(False)
				self.loadingBox.loading_label.set_text(msg)
				return False

		if self.unlock_process_t.launched:
			if not self.unlock_process_t.done:
				return True

	#pulsate_unlock_process		

	def unlock_process(self):
	
		self.unlock_result=self.core.epiManager.unlock_process()
		self.unlock_process_t.done=True

	#def unlock_process				

	def load_info_panel(self):

		self.load_info()
		self.apply_button.show()
		self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
		if self.load_epi_conf[0]["status"]=="installed":
			zmd_configured=self.core.epiManager.get_zmd_status(0)
			if not self.load_epi_conf[0]["selection_enabled"]["active"]:
				if zmd_configured==1:
					msg_code=0
					msg=self.get_msg_text(msg_code)
					self.feedback_label.set_text(msg)
					self.manage_feedback_box(False,"info")
				elif zmd_configured==0:
					msg_code=35
					msg=self.get_msg_text(msg_code)
					self.feedback_label.set_text(msg)
					self.manage_feedback_box(False,"warning")
				elif zmd_configured==-1:
					msg_code=36
					msg=self.get_msg_text(msg_code)
					self.feedback_label.set_text(msg)
					self.manage_feedback_box(False,"warning")

		self.show_apply_uninstall_buttons()
		self.stack.set_visible_child_name("epiBox")	

	#def load_info_panel

	def load_depends_panel(self):

		self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
		if self.test_install[1]!="":
			msg=self.get_msg_text(26)
			msg_error=msg+"\n"+str(self.test_install[1])
		else:
			msg=self.get_msg_text(27)
			msg_error=msg+"\n"+str(self.test_install[0])

		self.write_log("Test to install local deb: Unable to install package:"+str(self.test_install))
		self.dependsBox.depends_label.set_text(msg_error)
		self.stack.set_visible_child_name("dependsBox")
		
	#def load_depends_panel
		
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

		self.remove_btn=self.check_remove_script()
		status=self.load_epi_conf[0]["status"]

		if status=='availabled':

			if not self.eula_accepted:
				if not self.load_epi_conf[0]["selection_enabled"]["active"]:
					self._get_label_install_button("eula")
			else:	
				self._get_label_install_button("install")
			
			if self.core.epiManager.partial_installed:
				if not self.epiBox.show_terminal:
					self.uninstall_button.show()
					#self.uninstall_button.set_sensitive(True)
			else:	
				self.uninstall_button.hide()
		else:
			self.eula_accepted=True
			self._get_label_install_button("reinstall")
			if self.remove_btn:
				if not self.epiBox.show_terminal:
					self.uninstall_button.show()
			else:
				self.uninstall_button.hide()			

	#def show_apply_uninstall_buttons			

	def _get_label_install_button(self,action):

		if action=="eula":
			self.apply_button.set_label(_("Accept Eula and Install"))
		elif action=="install":
			self.apply_button.set_label(_("Install"))
		elif action=="reinstall":
			self.apply_button.set_label(_("Reinstall"))

	#def _get_label_install_button

	def init_install_process(self):

		self.add_repository_keys_launched=False
		self.add_repository_keys_done=False

		self.update_keyring_launched=False
		self.update_keyring_done=False

		self.download_app_launched=False
		self.download_app_done=False

		self.check_download_launched=False
		self.check_download_done=False

		self.preinstall_app_launched=False
		self.preinstall_app_done=False

		self.check_preinstall_launched=False
		self.check_preinstall_done=False

		self.check_arquitecture_launched=False
		self.check_arquitecture_done=False

		self.check_update_repos_launched=False
		self.check_update_repos_done=False

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
			if item["pkg_name"] not in self.core.epiManager.blockedRemovePkgsList:
				item['icon_status'].set_from_file(self.img)
			
	#def spinner_sync						

	def apply_button_clicked(self,widget):

		pkgs_not_selected=False
		eula=True
		self.manage_feedback_box(True)

		if self.load_epi_conf[0]["selection_enabled"]["active"]:
			count=0
			for item in self.load_epi_conf[0]["pkg_list"]:
				if item["name"] in self.core.epiManager.packages_selected:
					count=count+1
			if count==0:
				pkgs_not_selected=True

			if pkgs_not_selected:					
				dialog = Gtk.MessageDialog(None,0,Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "EPI")
				msg=self.get_msg_text(28)
				dialog.format_secondary_text(msg)
				response=dialog.run()
				dialog.destroy()
				self.lock_quit=False
				eula=False
		
		if eula:
					
			if self.eula_accepted:
				self.install_process()
			else:
				self.eulas_tocheck=self.required_eula.copy()
				for item in range(len(self.eulas_tocheck)-1, -1, -1):
					if self.eulas_tocheck[item]["pkg_name"] not in self.core.epiManager.packages_selected:
						self.eulas_tocheck.pop(item)
				self.eulas_toshow=self.eulas_tocheck.copy()
				self.eula_order=len(self.eulas_tocheck)-1
				self.accept_eula()

	#def apply_button_clicked
	
	def accept_eula(self):

		if not self.load_epi_conf[0]["selection_enabled"]["active"]:

			if len(self.eulas_tocheck)>0:
					self.eulaBox.load_info(self.eulas_tocheck[self.eula_order])
			else:
				self.eula_accepted=True
				
		else:
			if len(self.eulas_toshow)>0:
					self.eulaBox.load_info(self.eulas_tocheck[self.eula_order])	
			else:
				self.eula_accepted=True
				
		if self.eula_accepted:
			self.eulaBox.eula_window.hide()
			if len(self.core.epiManager.packages_selected)>0:
				self.write_log("Eula accepted")
				self.install_process()				
			else:
				self.eula_accepted=False
	
	#def accept_eula

	def install_process(self):

		self.epiBox.manage_application_cb(False)
		self.epiBox.select_pkg_btn.set_sensitive(False)
		self.write_log("Packages selected to install: %s"%self.core.epiManager.packages_selected)
		self.epiBox.get_icon_toupdate()
		self.lock_quit=True
		self.sp_cont=0
		self.epiBox.search_entry.set_sensitive(False)
		self.terminalBox.manage_vterminal(True,False)
		self.terminalBox.terminal_label.set_text(_("Installation process details"))
		self.init_install_process()
		self.apply_button.set_sensitive(False)
		self.uninstall_button.set_sensitive(False)
		self.epiBox.view_terminal_btn.set_sensitive(True)
		self.epiBox.view_terminal_btn.set_label(_("See installation details"))

		if self.install_dep:
			if self.show_depends:
				self.epiBox.epi_depend_label.set_text(_("(D) Addicitional application required"))
				self.epiBox.show_depend_box()
			if self.order>0:
				self.order=self.order-1
		else:
			self.order=0

		self.core.epiManager.zerocenter_feedback(self.order,"init")	
		GLib.timeout_add(100,self.pulsate_install_package,self.order)

	#def install_processs

	def pulsate_install_package(self,order):
		
		self.spinner_sync(order)
		self.sp_cont=self.sp_cont+1
		error=False

		if not self.add_repository_keys_launched:
			msg=self.get_msg_text(4)
			self.feedback_label.set_text(msg)
			self.add_repository_keys_launched=True
			self.sp_cont=self.sp_cont+1
			if order==0:
				self.install_dep=False
				
			self.add_repository_keys(order)
			
		if self.add_repository_keys_done:
			if not self.update_keyring_launched:
				self.update_keyring_launched=True 
				self.update_keyring()

			if self.update_keyring_done:
				if not self.download_app_launched:
					msg=self.get_msg_text(5)
					self.feedback_label.set_text(msg)
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
								self.feedback_label.set_text(msg)
								self.preinstall_app_launched=True
								self.preinstall_app()

							if self.preinstall_app_done:	

								if not self.check_preinstall_launched:
									self.check_preinstall_launched=True
									self.check_preinstall()

								if self.check_preinstall_done:

									if self.preinstall_result:
										if not self.check_arquitecture_launched:
											msg=self.get_msg_text(30)
											self.feedback_label.set_text(msg)
											self.check_arquitecture_launched=True
											self.check_arquitecture()

										if self.check_arquitecture_done:
											if not self.check_update_repos_launched:
												msg=self.get_msg_text(31)
												self.feedback_label.set_text(msg)
												self.check_update_repos_launched=True
												self.check_update_repos()

											if self.check_update_repos_done:
												if not self.install_app_launched:
													msg=self.get_msg_text(7)
													self.feedback_label.set_text(msg)
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
																self.feedback_label.set_text(msg)
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
																			self.epiBox.manage_application_cb(True)
																			self.epiBox.select_pkg_btn.set_sensitive(True)
																			self.epiBox.search_entry.set_sensitive(True)
																			self.lock_quit=False
																			msg=self.get_msg_text(9)
																			self.manage_feedback_box(False,"success")
																			self.feedback_label.set_text(msg)

																			self.terminalBox.manage_vterminal(False,True)
																			self.write_log_terminal('install')
																			self.load_epi_conf[0]["status"]="installed"
																			self.write_log(msg)
																			self.show_apply_uninstall_buttons()
																			self.uninstall_button.set_sensitive(True)
																			self.apply_button.set_sensitive(True)
																			self.core.epiManager.remove_repo_keys()

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
			self.epiBox.manage_application_cb(True)
			self.epiBox.select_pkg_btn.set_sensitive(True)
			self.epiBox.search_entry.set_sensitive(True)
			self.lock_quit=False
			self.terminalBox.manage_vterminal(False,True)
			msg_error=self.get_msg_text(error_code)
			self.manage_feedback_box(False,"error")
			self.feedback_label.set_text(msg_error)

			self.update_icon(params)
			self.core.epiManager.zerocenter_feedback(params[0],"install",False)
			self.write_log_terminal('install')
			self.write_log(msg_error)
			self.core.epiManager.remove_repo_keys()
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

		if self.update_keyring_launched:
			if 	not self.update_keyring_done:
				if os.path.exists(self.token_keyring[1]):
					return True
				else:
					self.update_keyring_done=True
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

		if self.check_arquitecture_launched:
			if not self.check_arquitecture_done:
				if os.path.exists(self.token_arquitecture[1]):
					return True
				else:
					self.check_arquitecture_done=True
					return True	

		if self.check_update_repos_launched:
			if not self.check_update_repos_done:
				if os.path.exists(self.token_updaterepos[1]):
					return True
				else:
					self.check_update_repos_done=True
					return True						

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
			self.terminalBox.vterminal.feed_child(command,length)
		else:
			self.add_repository_keys_done=True

	#def add_repository_keys

	def update_keyring(self):

		command=self.core.epiManager.update_keyring()
		length=len(command)

		if length>0:
			command=self.create_process_token(command,"keyring")
			length=len(command)
			self.terminalBox.vterminal.feed_child(command,length)
		else:
			self.update_keyring_done=True

	#def update_keyring

	def download_app(self):

		command=self.core.epiManager.download_app()
		length=len(command)
		if length>0:
			command=self.create_process_token(command,"download")
			length=len(command)
			self.terminalBox.vterminal.feed_child(command,length)
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
			self.terminalBox.vterminal.feed_child(command,length)
		else:
			self.preinstall_app_done=True	 		

	#def preinstall_app		

	def check_arquitecture(self):

		command=self.core.epiManager.check_arquitecture()
		length=len(command)
		if length>0:
			command=self.create_process_token(command,"arquitecture")
			length=len(command)
			self.terminalBox.vterminal.feed_child(command,length)
		else:
			self.check_arquitecture_done=True	

	#def check_arquitecture
	
	def check_update_repos(self):

		command=self.core.epiManager.check_update_repos()
		length=len(command)
		if length>0:
			command=self.create_process_token(command,"updaterepos")
			length=len(command)
			self.terminalBox.vterminal.feed_child(command,length)
		else:
			self.check_update_repos_done=True	

	#def check_update_repos

	def install_app(self):

	 	command=self.core.epiManager.install_app("gui")
	 	length=len(command)
	 	if length>0:
	 		command=self.create_process_token(command,"install")
	 		length=len(command)
	 		self.terminalBox.vterminal.feed_child(command,length)
	 		self.terminalBox.vterminal.set_sensitive(True)
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
	 		self.terminalBox.vterminal.feed_child(command,length)
	 	else:
	 		self.postinstall_app_done=True	 		

	#def postinstall_app

	def check_postinstall(self):

		self.postinstall_result=self.core.epiManager.check_postinstall()
		self.check_postinstall_done=True

	#def check_postinstall					

	def init_uninstall_process(self):

		self.check_remove_meta_t=threading.Thread(target=self.check_remove_meta)
		self.check_remove_meta_t.launched=False
		self.check_remove_meta_t.done=False

		self.remove_package_launched=False
		self.remove_package_done=False

		self.check_remove_launched=False
		self.check_remove_done=False

	#def init_uninstall_process	

	def uninstall_process(self,widget):

		show_uninstall_question=False
		pkgs_not_selected=False

		if self.load_epi_conf[0]["selection_enabled"]["active"]:
			count=0
			for item in self.load_epi_conf[0]["pkg_list"]:
				if item["name"] in self.core.epiManager.packages_selected:
						count=count+1
			if count==0:
				pkgs_not_selected=True

			if pkgs_not_selected:		
	
				dialog = Gtk.MessageDialog(None,0,Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "EPI")
				msg=self.get_msg_text(29)
				dialog.format_secondary_text(msg)
				response=dialog.run()
				dialog.destroy()
				self.lock_quit=False

			else:		
				show_uninstall_question=True

		else:
			show_uninstall_question=True

		if show_uninstall_question:

			dialog = Gtk.MessageDialog(None,0,Gtk.MessageType.WARNING, Gtk.ButtonsType.YES_NO, "EPI")
			msg=self.get_msg_text(14)
			dialog.format_secondary_text(msg)
			response=dialog.run()
			dialog.destroy()
				
			if response==Gtk.ResponseType.YES:
				self.epiBox.view_terminal_btn.set_sensitive(True)
				self.epiBox.view_terminal_btn.set_label(_("See uninstall details"))
				self.terminalBox.terminal_label.set_text(_("Uninstall process details"))

				self.write_log("Packages selected to uninstall: %s"%self.core.epiManager.packages_selected)
				self.epiBox.manage_application_cb(False)
				self.epiBox.select_pkg_btn.set_sensitive(False)
				self.epiBox.search_entry.set_sensitive(False)
				self.epiBox.get_icon_toupdate()
				self.lock_quit=True
				self.stop_uninstall=False
				self.terminalBox.manage_vterminal(True,False)
				self.sp_cont=0
				self.init_uninstall_process()
				self.apply_button.set_sensitive(False)
				self.uninstall_button.set_sensitive(False)
				GLib.timeout_add(100,self.pulsate_uninstall_process,0)

	#def uninstall_process		

	def pulsate_uninstall_process(self,order):

		if not self.check_remove_meta_t.launched:
			self.manage_feedback_box(True,"error")
			msg=self.get_msg_text(37)
			self.feedback_label.set_text(msg)
			self.check_remove_meta_t.launched=True
			self.check_remove_meta_t.start()

		if self.check_remove_meta_t.done:

			if not self.stop_uninstall:
				self.spinner_sync(order)
				self.sp_cont=self.sp_cont+1

				if not self.remove_package_launched:
					self.manage_feedback_box(True,"error")
					msg=self.get_msg_text(15)
					self.feedback_label.set_text(msg)
					self.remove_package_launched=True
					self.sp_cont=self.sp_cont+1
					self.epiBox.view_terminal_btn.set_sensitive(True)
					self.epiBox.view_terminal_btn.set_label(_("See uninstall details"))
					self.terminalBox.terminal_label.set_text(_("Uninstall process details"))
					self.uninstall_app(order)

				if self.remove_package_done:

					if not self.check_remove_launched:
						self.check_remove_launched=True
						self.check_remove()
					
					if self.check_remove_done:
						self.lock_quit=False
						self.terminalBox.manage_vterminal(False,True)
						self.epiBox.manage_application_cb(True)
						self.epiBox.select_pkg_btn.set_sensitive(True)
						self.epiBox.search_entry.set_sensitive(True)

						if self.remove:
							if self.metaRemovedWarning:
								msg=self.get_msg_text(39)
								self.manage_feedback_box(False,"warning")
							else:
								msg=self.get_msg_text(16)
								self.manage_feedback_box(False,"success")
							
							self.feedback_label.set_text(msg)					
							params=[order,True,'remove',None]
							self.update_icon(params)
							self.load_epi_conf[0]["status"]="availabled"
							self.show_apply_uninstall_buttons()
							self.uninstall_button.set_sensitive(True)
							self.apply_button.set_sensitive(True)
							
							if self.order==0:
								self.install_dep=False
							self.core.epiManager.zerocenter_feedback(0,"uninstall",True)
							self.write_log_terminal('uninstall')
							self.write_log(msg)
							return False
						else:
							msg=self.get_msg_text(17)
							self.manage_feedback_box(False,"error")
							self.feedback_label.set_text(msg)
							params=[order,False,'remove',self.dpkg_status]
							self.update_icon(params)
							self.core.epiManager.zerocenter_feedback(0,"uninstall",False)
							self.write_log_terminal('unistall')
							self.write_log(msg)
							return False
			else:
				msg=self.get_msg_text(38)
				self.write_log("Uninstall blocked because remove metapackage.: %s"%self.core.epiManager.blockedRemovePkgsList)
				self.manage_feedback_box(False,"error")
				self.feedback_label.set_text(msg)
				self.show_apply_uninstall_buttons()
				self.uninstall_button.set_sensitive(True)
				self.apply_button.set_sensitive(True)
				self.epiBox.manage_application_cb(True)
				self.epiBox.select_pkg_btn.set_sensitive(True)
				self.epiBox.search_entry.set_sensitive(True)
				self.lock_quit=False
				return False
				
		if self.check_remove_meta_t.launched:
			if not self.check_remove_meta_t.done:
				return True

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

	def check_remove_meta(self):

		self.metaRemovedWarning=self.core.epiManager.check_remove_meta()
		self.write_log("Check remove meta-package. Packages blocked because remove metapackage.: %s"%self.core.epiManager.blockedRemovePkgsList)
		
		if self.metaRemovedWarning:
			if len(self.core.epiManager.packages_selected)==len(self.core.epiManager.blockedRemovePkgsList):
				self.stop_uninstall=True
		
		self.check_remove_meta_t.done=True 

	#def check_remove_meta

	def uninstall_app(self,order):

		command=self.core.epiManager.uninstall_app(order)
		length=len(command)
		if length>0:
			command=self.create_process_token(command,"uninstall")
			length=len(command)
			self.terminalBox.vterminal.feed_child(command,length)
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
		for item in elements:
			item['icon_status'].set_from_file(self.img)

		if result:
			for item in elements:
				
				if process=="install":
					item['icon_status'].set_from_file(self.ok_image)
					
					if order==0:
						try:
							item["icon_run"].show()
							item['icon_info'].hide()
						except:
							pass	
						if item["custom"]:
							item['icon_package'].set_from_pixbuf(item['icon_installed'])
						else:
							#item['icon_package'].set_from_file(self.core.epiBox.package_installed)
							item['icon_package'].set_from_file(item['icon_installed'])
					else:
						item['icon_package'].set_from_file(self.core.epiBox.package_installed_dep)
				else:
					if item["pkg_name"] in self.core.epiManager.blockedRemovePkgsList:
						item['icon_status'].set_from_file(self.error_image)
					else:
						item['icon_status'].set_from_file(self.ok_image)
					
					if order==0:
						try:
							item['icon_info'].show()
							item["icon_run"].hide()
						except:
							pass

						if item["pkg_name"] not in self.core.epiManager.blockedRemovePkgsList:
							if item["custom"]:
								item['icon_package'].set_from_pixbuf(item['icon'])
							else:
								item['icon_package'].set_from_file(item['icon'])
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
								if item["custom"]:
									item["icon_package"].set_from_pixbuf(item["icon_installed"])	
								else:
									item["icon_package"].set_from_file(item["icon_installed"])	
							else:
								item["icon_package"].set_from_file(self.core.epiBox.package_installed_dep)	
						else:
							item['icon_status'].set_from_file(self.error_image)

							if order==0:
								if item["custom"]:
									item["icon_package"].set_from_pixbuf(item["icon"])	
								else:	
									item["icon_package"].set_from_file(item['icon'])
							else:
								item["icon_package"].set_from_file(self.core.epiBox.package_availabled_dep)
					else:
						if status=="availabled":
							item["icon_status"].set_from_file(self.ok_image)
						else:
							item["error"]=True
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
		
		if self.epiBox.show_terminal:
			self.epiBox.show_terminal=False	
		self.show_apply_uninstall_buttons()

	#def go_back	

	def get_msg_text(self,code):

		msg=""
		if code==0:
			msg=_("Application already installed")
		elif code==1:
			msg=_("Application epi file does not exist or its path is invalid")	
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
		elif code==18:
			msg=_("Application epi file it is not a valid json")
		elif code==19:
			msg=_("The system is being updated. Wait a few minutes and try again")
		elif code==20:
			msg=_("Apt or Dpkg are being executed. Checking if they have finished")		
		elif code==21:	
			msg=_("Apt or Dpkg are being executed. Wait a few minutes and try again")		
		elif code==22:
			msg=_("Apt or Dpkg seems blocked by a failed previous execution\nClick on Unlock to try to solve the problem")	
		elif code==23:
			msg=_("Executing the unlocking process. Wait a moment...")	
		elif code==24:
			msg=_("The unlocking process has failed")
		elif code==25:
			msg=_("The package will not be able to be installed\nAn error occurred during processing")
		elif code==26:
			msg=_("Problems with the following dependencies: ")	
		elif code==27:
			msg=_("The following error has been detected: ")
		elif code==28:
			msg=_("There is no package selected to be installed")
		elif code==29:
			msg=_("There is no package selected to be uninstalled")				
		elif code==30:
			msg=_("Checking system architecture...")
		elif code==31:
			msg=_("Checking if repositories need updating...")		
		elif code==32:
			msg=_("Associated script does not exist or its path is invalid")
		elif code==33:
			msg=_("Associated script does not have execute permissions")	
		elif code==34:
			msg=_("Application epi file is empty")
		elif code==35:
			msg=_("It seems that the packages were installed without using EPI.\nIt may be necessary to run EPI for proper operation")
		elif code==36:
			msg=_("It seems that the packages were installed but the execution of EPI failed.\nIt may be necessary to run EPI for proper operation")
		elif code==37:
			msg=_("Checking if selected applications can be uninstalled...")
		elif code==38:
			msg=_("The selected applications cannot be uninstalled.\nIt is part of the system meta-package")
		elif code==39:
			msg=_("Some selected application successfully uninstalled.\nOthers not because they are part of the system's meta-package")
		return msg

	#def get_msg_text

	def create_process_token(self,command,action):

		if action=="keys":
			self.token_keys=tempfile.mkstemp('_keys')
			remove_tmp=' rm -f ' + self.token_keys[1] + ';'+'\n'
			
		elif action=="keyring":
			self.token_keyring=tempfile.mkstemp('_keyring')
			remove_tmp=' rm -f ' + self.token_keyring[1] + ';'+'\n'
		
		elif action=="download":
			self.token_download=tempfile.mkstemp('_download')
			remove_tmp=' rm -f ' + self.token_download[1] + ';'+'\n'

		elif action=="preinstall":
			self.token_preinstall=tempfile.mkstemp('_preinstall')	
			remove_tmp=' rm -f ' + self.token_preinstall[1] + ';'+'\n'
			
		elif action=="arquitecture":
			self.token_arquitecture=tempfile.mkstemp('_arquitecture')	
			remove_tmp=' rm -f ' + self.token_arquitecture[1] + ';'+'\n'	

		elif action=="updaterepos":
			self.token_updaterepos=tempfile.mkstemp('_updaterepos')	
			remove_tmp=' rm -f ' + self.token_updaterepos[1] + ';'+'\n'	
		
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

	def manage_feedback_box(self,hide,msg_type=None):

		if hide:
			self.feedback_box.set_name("HIDE_BOX")
			self.feedback_ok_img.hide()
			self.feedback_error_img.hide()
			self.feedback_info_img.hide()
			self.feedback_warning_img.hide()
			self.feedback_label.set_halign(Gtk.Align.CENTER)
			try:
				if self.load_epi_conf[0]["selection_enabled"]["active"]:
					self.main_window.resize(675,570)
				else:
					self.main_window.resize(675,550)
			except:
				pass

		else:
			self.feedback_label.set_halign(Gtk.Align.START)
			if self.load_epi_conf[0]["selection_enabled"]["active"] or msg_type=="warning":
				self.main_window.resize(675,571)
			else:
				self.main_window.resize(675,551)
	
			if msg_type=="error":
				self.feedback_ok_img.hide()
				self.feedback_error_img.show()
				self.feedback_info_img.hide()
				self.feedback_warning_img.hide()
				self.feedback_box.set_name("ERROR_BOX")
			elif msg_type=="info":
				self.feedback_ok_img.hide()
				self.feedback_error_img.hide()
				self.feedback_info_img.show()
				self.feedback_warning_img.hide()
				self.feedback_box.set_name("INFORMATION_BOX")
			elif msg_type=="success":
				self.feedback_ok_img.show()
				self.feedback_error_img.hide()
				self.feedback_info_img.hide()
				self.feedback_warning_img.hide()
				self.feedback_box.set_name("SUCCESS_BOX")
			elif msg_type=="warning":
				self.feedback_box.set_name("WARNING_BOX")
				self.feedback_ok_img.hide()
				self.feedback_error_img.hide()
				self.feedback_info_img.hide()
				self.feedback_warning_img.show()

	#def manage_feedback_box

	def quit(self,widget):

		msg_log='Quit'
		self.write_log(msg_log)
		self.core.epiManager.remove_repo_keys()
		Gtk.main_quit()		

	#def quit	

	def unable_quit(self,widget,event):

		if self.lock_quit:
			return True
		else:	
			return False
			
	#def unable_quit	

	def write_log_terminal(self,action):

		init_row=self.final_row
		init_column=self.final_column

		self.final_column,self.final_row = self.terminalBox.vterminal.get_cursor_position()
		log_text=self.terminalBox.vterminal.get_text_range(init_row,init_column,self.final_row,self.final_column)[0]

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
from . import Core
