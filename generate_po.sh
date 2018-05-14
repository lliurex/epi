#!/bin/bash

xgettext --join-existing ./epi-gtk/python3-epigtk/MainWindow.py -o ./translations/epi-gtk.pot
xgettext --join-existing ./epi-gtk/python3-epigtk/EpiBox.py -o ./translations/epi-gtk.pot
xgettext --join-existing ./epi-gtk/python3-epigtk/LoadingBox.py -o ./translations/epi-gtk.pot
xgettext --join-existing ./epi-gtk/python3-epigtk/InfoBox.py -o ./translations/epi-gtk.pot
xgettext --join-existing ./epi-gtk/python3-epigtk/ChooserBox.py -o ./translations/epi-gtk.pot
xgettext --join-existing ./epi-gtk/python3-epigtk/rsrc/epi-gtk.ui -o ./translations/epi-gtk.pot