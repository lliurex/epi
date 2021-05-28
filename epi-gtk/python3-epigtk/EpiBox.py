#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Vte', '2.91')
gi.require_version('PangoCairo', '1.0')

import cairo
from gi.repository import Gtk, Pango, PangoCairo,GdkPixbuf, Gdk, Gio, GObject,GLib,Vte

import copy

import sys
import os
import html2text
import threading


from . import settings
import gettext
gettext.textdomain(settings.TEXT_DOMAIN)
_ = gettext.gettext


class EpiBox(Gtk.VBox):
	
	def __init__(self):
		
		Gtk.VBox.__init__(self)
		
		self.core=Core.Core.get_core()
		
		builder=Gtk.Builder()
		builder.set_translation_domain(settings.TEXT_DOMAIN)
		ui_path=self.core.ui_path
		builder.add_from_file(ui_path)

		self.css_file=self.core.rsrc_dir+"epi-gtk.css"

		self.package_availabled=self.core.rsrc_dir+"package.png"
		self.package_availabled_dep=self.core.rsrc_dir+"package_dep.png"
		self.package_installed=self.core.rsrc_dir+"package_install.png"
		self.package_installed_dep=self.core.rsrc_dir+"package_install_dep.png"
		self.info_image=self.core.rsrc_dir+"info.png"
		self.initial=self.core.rsrc_dir+"initial.png"
		self.check_image=self.core.rsrc_dir+"check.png"
		self.run_image=self.core.rsrc_dir+"run.png"

		self.main_box=builder.get_object("epi_data_box")
		self.epi_list_label=builder.get_object("epi_list_label")
		
		self.search_entry=builder.get_object("search_entry")
		self.search_entry.connect("changed",self.search_entry_changed)

		self.epi_box=builder.get_object("epi_box")
		self.scrolledwindow=builder.get_object("scrolledwindow")
		self.epi_list_box=builder.get_object("epi_list_box")
		self.epi_list_vp=builder.get_object("epi_list_viewport")
		self.select_pkg_btn=builder.get_object("select_pkg_btn")
		self.select_pkg_btn.connect("clicked",self.select_all_pkg)
		self.epi_depend_label=builder.get_object("epi_depend_label")
		self.view_terminal_btn=builder.get_object("view_terminal_btn")
		self.view_terminal_btn.connect("clicked",self.view_terminal)
		self.monitoring=True
		self.show_terminal=False

		self.search_list=[]
		self.update_icons={}
		self.main_box.set_valign(Gtk.Align.FILL)

		self.pack_start(self.main_box,True,True,0)
		self.set_css_info()
		

				
	#def __init__

	def set_css_info(self):
		
		self.style_provider=Gtk.CssProvider()

		f=Gio.File.new_for_path(self.css_file)
		self.style_provider.load_from_file(f)

		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),self.style_provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		self.epi_list_label.set_name("OPTION_LABEL")
		#self.terminal_label.set_name("MSG_LABEL")
		self.epi_depend_label.set_name("DEPEND_LABEL")
		self.search_entry.set_name("CUSTOM-ENTRY")
		self.epi_list_box.set_name("LIST_BOX")
				
	#def set_css_info			
			
	def load_info(self):
		
		self.info=copy.deepcopy(self.core.mainWindow.load_epi_conf)
		
		if self.info[0]["selection_enabled"]["active"]:
			self.epi_list_label.set_text(_("Select the applications to install"))
			self.epi_list_label.set_halign(Gtk.Align.START)
		self.draw_pkg_list()

	#def load_info

	def draw_pkg_list(self):

		show_cb=False
		default_checked=False
		self.are_depends=False
		info=self.info
		
		if len(info)>1:
			self.are_depends=True

		for item in info:
			pkg_order=0
			show_cb=False
			order=item
			#if info[item]["type"]!="file":
			if order==0:
				if info[item]["selection_enabled"]["active"]:
					self.search_entry.show()
					self.select_pkg_btn.set_visible(True)
					self.core.mainWindow.main_window.resize(675,570)

					show_cb=True
					if info[item]["selection_enabled"]["all_selected"]:
						default_checked=True
						self.uncheck_all=True
						self.select_pkg_btn.set_label(_("Uncheck all packages"))
					else:
						self.uncheck_all=False
						self.select_pkg_btn.set_label(_("Check all packages"))
				else:
					self.select_pkg_btn.set_visible(False)
					self.search_entry.hide()

			count=len(info[item]["pkg_list"])
			self.number_pkg=count
			for element in info[item]["pkg_list"]:
				params_to_draw=[]
				name=element["name"]
				if order!=0:
					custom_name=_("Previous actions: executing ")+info[item]["zomando"]
				else:
					try:
						custom_name=element["custom_name"]
					except:
						custom_name=""
				try:
					debian_name=self.core.epiManager.pkg_info[name]["debian_name"]
					component=self.core.epiManager.pkg_info[name]["component"]
					custom_icon=self.core.iconsManager.search_icon(debian_name,info[item]["custom_icon_path"],element["custom_icon"],component)
				except:
					custom_icon=""	

				try:
					entrypoint=element["entrypoint"]
				except:
					entrypoint=""				
				
				if not default_checked:
					try:
						default_pkg=element["default_pkg"]
					except:
						default_pkg=False
				else:
					default_pkg=False			

				params_to_draw=[name,order,show_cb,default_checked,custom_name,custom_icon,pkg_order,entrypoint,default_pkg,count]
				self.new_epi_box(params_to_draw)
				pkg_order+=1
				count-=1

			'''	
			else:
				name=info[item]["name"]
				self.new_epi_box(name,order)
			'''
		#self.get_icon_toupdate()	
		
	#def draw_pkg_list				

	def hide_non_search(self):

		for item in self.epi_list_box.get_children():
			for element in item.get_children()[0].get_children():
				if element.id in self.search_list:
					item.hide()
				else:
					if element.order==0:
						item.show()
					else:
						item.hide()	
	
	#def hide_non_search	

	def show_depend_box(self):

		for item in self.epi_list_box.get_children():
			for element in item.get_children()[0].get_children():
				if element.order!=0 and element.pkg_order==0:
					item.show()

	#def show_depend_box			

	def new_epi_box(self,params_to_draw):

		name=params_to_draw[0]
		order=params_to_draw[1]
		show_cb=params_to_draw[2]
		default_checked=params_to_draw[3]
		custom_name=params_to_draw[4]
		custom_icon=params_to_draw[5]
		pkg_order=params_to_draw[6]
		entrypoint=params_to_draw[7]
		default_pkg=params_to_draw[8]
		count=params_to_draw[9]
		#search=params_to_draw[6]
		
		vbox=Gtk.VBox()
		hbox=Gtk.HBox()

		aditional_params=self._get_aditional_params(name,order,custom_icon)

		custom=aditional_params[0]
		icon=aditional_params[1]
		icon_installed=aditional_params[2]
		img=aditional_params[3]
		img_state=aditional_params[4]
					
		application_cb=Gtk.CheckButton()
		application_cb.connect("toggled",self.on_checked)
		application_cb.set_margin_left(10)
		application_cb.set_halign(Gtk.Align.CENTER)		
		application_cb.set_valign(Gtk.Align.CENTER)
		application_cb.id=name
		application_cb.pkg=False
		application_cb.status=False
		application_cb.order=order
		application_cb.pkg_order=pkg_order
		application_cb.info=False
		application_cb.run=False		
		
		application_image=img
		application_image.set_margin_left(10)
		application_image.set_halign(Gtk.Align.CENTER)
		application_image.set_valign(Gtk.Align.CENTER)
		application_image.id=name
		application_image.pkg=True
		application_image.status=False
		application_image.order=order
		application_image.icon=icon
		application_image.icon_installed=icon_installed
		application_image.custom=custom
		application_image.pkg_order=pkg_order
		application_image.info=False
		application_image.run=False
		#application_image.installed=installed

		if custom_name=='':
			application_info="<span font='Roboto'><b>"+name+"</b></span>"
		else:
			if order==0:
				application_info="<span font='Roboto'><b>"+custom_name+"</b></span>"
			else:
				if pkg_order==0:
					application_info="<span font='Roboto'><b>"+custom_name+"</b></span>"
				else:
					application_info="<span font='Roboto'><b>"+name+"</b></span>"
	
		application=Gtk.Label()
		application.set_markup(application_info)
		application.set_margin_left(10)
		application.set_margin_right(15)
		application.set_margin_top(21)
		application.set_margin_bottom(21)
		application.set_width_chars(50)
		#application.set_max_width_chars(50)
		application.set_xalign(-1)
		application.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
		application.id=name
		application.pkg=False
		application.status=False
		application.order=order
		application.pkg_order=pkg_order
		application.info=False
		application.run=False
		
		info=Gtk.Button()
		info_image=Gtk.Image.new_from_file(self.info_image)
		info.add(info_image)
		info.set_halign(Gtk.Align.CENTER)
		info.set_valign(Gtk.Align.CENTER)
		if self.number_pkg>2:
			info.set_margin_right(10)
		else:
			info.set_margin_right(5)

		info.set_name("INFO_APP_BUTTON")
		info.connect("clicked",self.show_info_clicked,hbox)
		if self.core.epiManager.pkg_info[name]["summary"]!="":
			info.set_tooltip_text(_("Press to view application information"))
		else:
			info.set_tooltip_text(_("Info not availabled"))
	
		info.id=name
		info.pkg=False
		info.order=order
		info.status=False
		info.pkg_order=pkg_order
		info.info=True
		info.run=False

		if entrypoint!="":
			run=Gtk.Button()
			run_image=Gtk.Image.new_from_file(self.run_image)
			run.add(run_image)
			run.set_halign(Gtk.Align.CENTER)
			run.set_valign(Gtk.Align.CENTER)
			run.set_name("RUN_APP_BUTTON")
			run.set_tooltip_text(_("Click to launch the application"))
			run.connect("clicked",self.run_app,entrypoint)
			if self.number_pkg>2:
				run.set_margin_right(10)
			else:
				run.set_margin_right(5)
	
			run.id=name
			run.pkg=False
			run.order=order
			run.status=False
			run.pkg_order=pkg_order
			run.info=False
			run.run=True
		
		#state=Gtk.Image()
		state=img_state
		state.set_halign(Gtk.Align.CENTER)
		state.set_valign(Gtk.Align.CENTER)
		state.id=name
		state.pkg=False
		state.status=True
		state.order=order
		state.pkg_order=pkg_order
		state.info=False
		state.run=False
		
		hbox.pack_start(application_cb,False,False,0)
		hbox.pack_start(application_image,False,False,0)
		hbox.pack_start(application,False,False,0)
		hbox.pack_end(info,False,False,10)
		
		if entrypoint!="":
			hbox.pack_end(run,False,False,10)
		
		hbox.pack_end(state,False,False,10)
		hbox.show_all()

		list_separator=Gtk.Separator()
		if show_cb:
			list_separator.set_margin_left(40)
		else:
			list_separator.set_margin_left(20)

		if self.number_pkg>2:
			list_separator.set_margin_right(20)
		else:
			list_separator.set_margin_right(15)
		

		if count!=1:
			if order>0:
				list_separator.set_name("WHITE_SEPARATOR")
			else:
				list_separator.set_name("SEPARATOR")
			
		else:
			if order==0:
				if not self.are_depends:
					list_separator.set_name("WHITE_SEPARATOR")
				else:
					list_separator.set_name("SEPARATOR")
				
			else:
				list_separator.set_name("WHITE_SEPARATOR")
		
		vbox.pack_start(hbox,False,False,5)
		vbox.pack_end(list_separator,False,False,0)
		vbox.show_all()

		
		if show_cb:
			application_cb.set_visible(True)
			if name in self.core.epiManager.packages_selected:
				application_cb.set_active(True)
			else:	
				if default_checked:
					application_cb.set_active(True)
				else:
					if default_pkg:
						application_cb.set_active(True)
					else:
						application_cb.set_active(False)	
		else:
			application_cb.set_visible(False)
			self.core.epiManager.packages_selected.append(application_cb.id)	

		if entrypoint!="":
			if self.core.epiManager.pkg_info[name]["status"]=="installed":
				info.set_visible(False)
			else:
				run.set_visible(False)	
		
		#hbox.set_name("APP_BOX")

		self.epi_list_box.pack_start(vbox,False,False,0)
		self.epi_list_box.queue_draw()
		self.epi_list_box.set_valign(Gtk.Align.FILL)
		
		vbox.queue_draw()
		if order!=0:
			vbox.hide()
		
	#def new_epi_box

	def _get_aditional_params(self,name,order,custom_icon):

		aditional_params=[]

		if custom_icon=="":
			custom=False
			icon=self.package_availabled
			icon_installed=self.package_installed
		else:
			custom=True
			image=Gtk.Image.new_from_file(custom_icon)
			pixbuf=image.get_pixbuf()
			icon=pixbuf.scale_simple(48,48,GdkPixbuf.InterpType.BILINEAR)
			
			icon_installed=self.core.iconsManager.create_pixbuf(custom_icon)
			if icon_installed=="":
				custom=False
				icon=self.package_availabled
				icon_installed=self.package_installed


		img_state=Gtk.Image.new_from_file(self.initial)

				
		if self.core.epiManager.pkg_info[name]["status"]=="installed":
			if not custom:
				img=Gtk.Image.new_from_file(icon_installed)
			else:
				img=Gtk.Image.new_from_pixbuf(icon_installed)	
		else:
			if order==0:
				if not custom:
					img=Gtk.Image.new_from_file(icon)
				else:
					img=Gtk.Image.new_from_pixbuf(icon)	
			else:
				img=Gtk.Image.new_from_file(self.package_availabled_dep)

		img_state=Gtk.Image.new_from_file(self.initial)	

		aditional_params=[custom,icon,icon_installed,img,img_state]

		return aditional_params

	# _get_aditional_params

	def on_checked(self,widget):

		if widget.get_active():
			if widget.id not in self.core.epiManager.packages_selected:
				self.core.epiManager.packages_selected.append(widget.id)

		else:
			if widget.id in self.core.epiManager.packages_selected:
				self.core.epiManager.packages_selected.remove(widget.id)

		self.manage_state_select_pkg_btn()

	#def on_checked		
			
	def get_icon_toupdate(self):

		self.update_icons={}
		
		for item in self.epi_list_box.get_children():
			tmp={}			
			for element in item.get_children()[0].get_children():
				if element.id in self.core.epiManager.packages_selected:
					if element.order not in self.update_icons:
						self.update_icons[element.order]=[]
					if element.pkg:
						tmp['icon_package']=element
						tmp['icon']=element.icon
						tmp["icon_installed"]=element.icon_installed
						tmp["custom"]=element.custom
						
					if element.status:
						tmp['icon_status']=element

					if element.info:
						tmp["icon_info"]=element

					if element.run:
						tmp["icon_run"]=element		

					
			if len(tmp)>0:

				self.update_icons[element.order].append(tmp)

	#def get_icon_toupdate				


	def show_info_clicked(self,button,hbox):

		try:
			app=hbox.get_children()[2].id
		except:	
			app=hbox.get_children()[2].get_text()

		summary=self.core.epiManager.pkg_info[app]["summary"]

		if summary!="":
			debian_name=self.core.epiManager.pkg_info[app]["debian_name"]
			component=self.core.epiManager.pkg_info[app]["component"]

			name=self.core.epiManager.pkg_info[app]["name"]
			icon=self.core.epiManager.pkg_info[app]["icon"]
			description=self.core.epiManager.pkg_info[app]["description"]

			h=html2text.HTML2Text()
			h.body_width=400
			txt=h.handle(description)
			txt=txt.replace("&lt;", "<")
			txt=txt.replace("&gt;", ">")
			txt=txt.replace("&amp;", "&")

			icon=self.core.iconsManager.get_icon(debian_name,icon,component)
			image=Gtk.Image.new_from_file(icon)
			pixbuf=image.get_pixbuf()
			pixbuf=pixbuf.scale_simple(64,64,GdkPixbuf.InterpType.BILINEAR)
			self.core.infoBox.icon.set_from_pixbuf(pixbuf)
			self.core.infoBox.name_label.set_text(name)
			self.core.infoBox.summary_label.set_text(summary)
			self.core.infoBox.description_label.set_text(txt)
			self.core.mainWindow.apply_button.hide()
			self.core.mainWindow.uninstall_button.hide()
			self.core.mainWindow.return_button.show()
			self.core.mainWindow.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
			self.core.mainWindow.stack.set_visible_child_name("infoBox")


	#def show_info_clicked
	
	def manage_application_cb(self,active):

		for item in self.epi_list_box.get_children():
			item.get_children()[0].get_children()[0].set_sensitive(active)
			try:
				item.get_children()[0].get_children()[4].set_sensitive(active)
			except:
				pass	


	#def manage_application_cb		

	def select_all_pkg(self,widget):

		self.monitoring=False

		if self.uncheck_all:
			active=False
			self.select_pkg_btn.set_label(_(_("Check all packages")))
			self.core.mainWindow._get_label_install_button("install")	
			self.uncheck_all=False
		else:
			active=True
			self.select_pkg_btn.set_label(_(_("Uncheck all packages")))
			self.uncheck_all=True
			if len(self.core.mainWindow.required_eula)>0:
				self.core.mainWindow._get_label_install_button("eula")	
			else:
				self.core.mainWindow._get_label_install_button("install")	

		for item in self.epi_list_box.get_children():
			if item.get_children()[0].get_children()[0].order==0:
				item.get_children()[0].get_children()[0].set_active(active)

		self.monitoring=True

	#def select_all_pkg	

	def manage_state_select_pkg_btn(self):
		
		if self.monitoring:
			count_ck=0
			count_uck=0
			count_eula=0

			for item in self.core.mainWindow.load_epi_conf[0]["pkg_list"]:
				if item["name"] in self.core.epiManager.packages_selected:
					count_ck+=1

				else:
					count_uck+=1	
			
			for item in self.core.mainWindow.required_eula:
				if item["pkg_name"] in self.core.epiManager.packages_selected:
					count_eula+=1

			if count_ck==len(self.core.mainWindow.load_epi_conf[0]["pkg_list"]):
				self.select_pkg_btn.set_label(_(_("Uncheck all packages")))
				self.uncheck_all=True

			if count_uck==len(self.core.mainWindow.load_epi_conf[0]["pkg_list"]):
				self.select_pkg_btn.set_label(_(_("Check all packages")))
				self.uncheck_all=False
		
			if count_eula>0:
				self.core.mainWindow._get_label_install_button("eula")	
			else:
				self.core.mainWindow._get_label_install_button("install")	
	
	#def manage_select_pkg_btn

	def search_entry_changed(self,widget):

		self.search_list=[]
		
		search=self.search_entry.get_text().lower()

		if search=="":
			self.hide_non_search()
		else:
			for item in self.info:
				tmp_pkg=self.info[item]["pkg_list"].copy()
				for element in range(len(tmp_pkg)-1, -1, -1):
					try:
						name=tmp_pkg[element]["custom_name"].lower()
					except:
						name=tmp_pkg[element]["name"].lower()
				
					if search in name:
						pass
					else:
						self.search_list.append(tmp_pkg[element]["name"])
						tmp_pkg.pop(element)

			if len(self.search_list)>0:
				self.hide_non_search()

	#search_entry_changed

	def view_terminal(self,widget):

		self.show_terminal=True
		self.core.mainWindow.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
		self.core.mainWindow.stack.set_visible_child_name("terminalBox")
		self.core.mainWindow.return_button.show()
		self.core.mainWindow.apply_button.hide()
		if self.core.mainWindow.remove_btn:
			self.core.mainWindow.uninstall_button.hide()

	# def view_terminal		

	def run_app(self,widget,entrypoint):

		self.launch_app_t=threading.Thread(target=self.launch_app)
		self.launch_app_t.daemon=True
		self.launch_cmd=entrypoint
		GObject.threads_init()
		
		self.launch_app_t.start()
		
		self.core.mainWindow.quit(widget)

	#def run_app

	def launch_app(self):
	
		os.system(self.launch_cmd)

	#def launch_app	
	'''
#class EpiBox

from . import Core
