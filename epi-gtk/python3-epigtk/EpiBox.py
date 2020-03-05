#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Vte', '2.91')
from gi.repository import Gtk, Pango, GdkPixbuf, Gdk, Gio, GObject,GLib,Vte

import copy

import sys
import os
import html2text

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

		self.package_availabled=self.core.rsrc_dir+"package.svg"
		self.package_availabled_dep=self.core.rsrc_dir+"package_dep.svg"
		self.package_installed=self.core.rsrc_dir+"package_install.svg"
		self.package_installed_dep=self.core.rsrc_dir+"package_install_dep.svg"
		self.info_image=self.core.rsrc_dir+"info.svg"
		self.initial=self.core.rsrc_dir+"initial.svg"
		self.terminal_config=self.core.rsrc_dir+"terminal.conf"


		self.main_box=builder.get_object("epi_data_box")
		self.epi_list_label=builder.get_object("epi_list_label")
		self.epi_box=builder.get_object("epi_box")
		self.scrolledwindow=builder.get_object("scrolledwindow")
		self.epi_list_box=builder.get_object("epi_list_box")
		self.epi_list_vp=builder.get_object("epi_list_viewport")
		self.epi_depend_label=builder.get_object("epi_depend_label")

		self.terminal_box=builder.get_object("terminal_box")
		self.terminal_label=builder.get_object("terminal_label")
		self.viewport=builder.get_object("viewport")
		self.terminal_scrolled=builder.get_object("terminalScrolledWindow")
		self.vterminal=Vte.Terminal()
		self.vterminal.spawn_sync(
			Vte.PtyFlags.DEFAULT,
			os.environ['HOME'],
			#["/usr/sbin/dpkg-reconfigure", "xdm"],
			["/bin/bash","--rcfile",self.terminal_config],
			[],
			GLib.SpawnFlags.DO_NOT_REAP_CHILD,
			None,
			None,
		)
		font_terminal = Pango.FontDescription("monospace normal 9")
		self.vterminal.set_font(font_terminal)
		self.vterminal.set_scrollback_lines(-1)
		self.vterminal.set_sensitive(True)
		self.terminal_scrolled.add(self.vterminal)
		self.pbar_label=builder.get_object("pbar_label")
		self.pbar=builder.get_object("pbar")


		self.pack_start(self.main_box,True,True,0)
		self.set_css_info()
		

				
	#def __init__

	def set_css_info(self):
		
		self.style_provider=Gtk.CssProvider()

		f=Gio.File.new_for_path(self.css_file)
		self.style_provider.load_from_file(f)

		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),self.style_provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		self.epi_list_label.set_name("OPTION_LABEL")
		self.terminal_label.set_name("MSG_LABEL")
		self.epi_depend_label.set_name("DEPEND_LABEL")
				
	#def set_css_info			
			
	def load_info(self,info):
		
		show_cb=False
		default_checked=False

		if info[0]["available_selection"]["active"]:
			self.epi_list_label.set_text(_("Select the applications to install"))
			

		for item in info:
			show_cb=False
			order=item
			#if info[item]["type"]!="file":
			if info[item]["available_selection"]["active"]:
				show_cb=True
				if info[item]["available_selection"]["all_selected"]:
					default_checked=True

			for element in info[item]["pkg_list"]:
				name=element["name"]
				self.new_epi_box(name,order,show_cb,default_checked)

			'''	
			else:
				name=info[item]["name"]
				self.new_epi_box(name,order)
			'''
		self.get_icon_toupdate()	

	#def load_info				

	
	def new_epi_box(self,name,order,show_cb,default_checked):
		
		hbox=Gtk.HBox()
		if self.core.epiManager.pkg_info[name]["status"]=="installed":
			img=Gtk.Image.new_from_file(self.package_installed)
		else:
			if order==0:
				img=Gtk.Image.new_from_file(self.package_availabled)
			else:
				img=Gtk.Image.new_from_file(self.package_availabled_dep)
		
		

		application_cb=Gtk.CheckButton()
		application_cb.connect("toggled",self.on_checked)
		application_cb.set_margin_left(10)
		application_cb.set_halign(Gtk.Align.CENTER)		
		application_cb.set_valign(Gtk.Align.CENTER)
		application_cb.id=name
		application_cb.pkg=False
		application_cb.status=False
		application_cb.order=order		
		
		application_image=img
		application_image.set_margin_left(10)
		application_image.set_halign(Gtk.Align.CENTER)
		application_image.set_valign(Gtk.Align.CENTER)
		application_image.id=name
		application_image.pkg=True
		application_image.status=False
		application_image.order=order
		application_info="<span font='Roboto'><b>"+name+"</b></span>"
		application=Gtk.Label()
		application.set_markup(application_info)
		application.set_margin_left(10)
		application.set_margin_right(15)
		application.set_margin_top(21)
		application.set_margin_bottom(21)
		application.set_width_chars(25)
		application.set_max_width_chars(25)
		application.set_xalign(-1)
		application.set_ellipsize(Pango.EllipsizeMode.END)
		application.id=name
		application.pkg=False
		application.status=False
		application.order=order
		
		info=Gtk.Button()
		info_image=Gtk.Image.new_from_file(self.info_image)
		info.add(info_image)
		info.set_halign(Gtk.Align.CENTER)
		info.set_valign(Gtk.Align.CENTER)
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
		
		state=Gtk.Image()
		state=Gtk.Image.new_from_file(self.initial)
		state.set_halign(Gtk.Align.CENTER)
		state.set_valign(Gtk.Align.CENTER)
		state.id=name
		state.pkg=False
		state.status=True
		state.order=order
		
		hbox.pack_start(application_cb,False,False,0)
		hbox.pack_start(application_image,False,False,0)
		hbox.pack_start(application,False,False,0)
		hbox.pack_end(info,False,False,10)
		hbox.pack_end(state,False,False,10)
		hbox.show_all()
		if show_cb:
			application_cb.set_visible(True)
			if default_checked:
				application_cb.set_active(True)
		else:
			application_cb.set_visible(False)
			self.core.epiManager.packages_selected.append(application_cb.id)	

		hbox.set_name("APP_BOX")
		self.epi_list_box.pack_start(hbox,False,False,5)
		self.epi_list_box.queue_draw()
		hbox.queue_draw()
		
	#def new_epi_box

	def on_checked(self,widget):

		if widget.get_active():
			self.core.epiManager.packages_selected.append(widget.id)

		else:
			self.core.epiManager.packages_selected.remove(widget.id)

	#def on_checked		
			
	def get_icon_toupdate(self):

		self.update_icons={}

		for item in self.epi_list_box.get_children():
			tmp={}			
			for element in item.get_children():
				if element.id in self.core.epiManager.packages_selected:
					if element.order not in self.update_icons:
						self.update_icons[element.order]=[]
					if element.pkg:
						tmp['icon_package']=element

					if element.status:
						tmp['icon_status']=element

					
			if len(tmp)>0:
				self.update_icons[element.order].append(tmp)


	#def get_icon_toupdate				


	def show_info_clicked(self,button,hbox):

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

			icon=self.core.get_icons.get_icon(debian_name,icon,component)
			
			self.core.infoBox.icon.set_from_file(icon)
			self.core.infoBox.name_label.set_text(name)
			self.core.infoBox.summary_label.set_text(summary)
			self.core.infoBox.description_label.set_text(txt)
			self.core.mainWindow.apply_button.hide()
			self.core.mainWindow.uninstall_button.hide()
			self.core.mainWindow.return_button.show()
			self.core.mainWindow.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
			self.core.mainWindow.stack.set_visible_child_name("infoBox")


	#def show_info_clicked

	def manage_vterminal(self,enabled_input,sensitive):

		self.vterminal.set_input_enabled(enabled_input)
		self.vterminal.set_sensitive(sensitive)	

	#def manage_vterminal		

	def manage_application_cb(self,active):

		for item in self.epi_list_box.get_children():
			item.get_children()[0].set_sensitive(active)

	#def manage_application_cb		


#class EpiBox

from . import Core