#!/usr/bin/python3

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtQuick import QQuickImageProvider
import os

class IconProvider(QQuickImageProvider):

	def __init__(self):

		super(IconProvider,self).__init__(QQuickImageProvider.Image)
		self.checkImage="/usr/lib/python3/dist-packages/epigtk/rsrc/check.png"
		self.localPackage="/usr/lib/python3/dist-packages/epigtk/rsrc/local_deb.png"

	#def __init__
	
	def requestImage(self,imagePath,size1,size2):

		return self.createIcon("/%s"%imagePath)

	#def requestImage

	def createIcon(self,imagePath):

		combineImage=QImage(48,48,QImage.Format_RGBA8888)
		destImage=QImage()

		if "_OK.png" in imagePath:
			isInstalled=True
			appIcon=imagePath.split("_OK.png")[0]+".png"
		else:
			isInstalled=False
			appIcon=imagePath

		if os.path.exists(appIcon):
			destImage.load(appIcon,"png")
		else:
			destImage.load(self.localPackage,"png")
		
		s=QSize(48,48)
		destImage=destImage.scaled(s,aspectRatio=Qt.KeepAspectRatio,mode=Qt.FastTransformation)
		lastImage=QImage()
		lastImage.load(self.checkImage,"png")
		p=QPainter()
		p.begin(combineImage)
		p.drawImage(0,0,destImage)
		if isInstalled:
			p.drawImage(30,30,lastImage)
		p.end()

		return combineImage
		
	#def createIcon

#clas IconProvider
