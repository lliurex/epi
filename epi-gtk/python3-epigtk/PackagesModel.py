#!/usr/bin/python3
import os
import sys
from PySide2 import QtCore, QtGui, QtQml

class PackagesModel(QtCore.QAbstractListModel):

	PkgIdRole= QtCore.Qt.UserRole + 1000
	PkgStatusRole = QtCore.Qt.UserRole + 1001
	CustomNameRole=QtCore.Qt.UserRole+1002
	IconRole=QtCore.Qt.UserRole+1003
	DefaultPkgRole=QtCore.Qt.UserRole+1004
	ShowCbRole=QtCore.Qt.UserRole+1005
	OrderRole=QtCore.Qt.UserRole+1006


	def __init__(self,parent=None):
		
		super(PackagesModel, self).__init__(parent)
		self._entries =[]
	#def __init__

	def rowCount(self, parent=QtCore.QModelIndex()):
		
		if parent.isValid():
			return 0
		return len(self._entries)

	#def rowCount

	def data(self, index, role=QtCore.Qt.DisplayRole):
		
		if 0 <= index.row() < self.rowCount() and index.isValid():
			item = self._entries[index.row()]
			if role == PackagesModel.PkgIdRole:
				return item["pkgId"]
			elif role == PackagesModel.PkgStatusRole:
				return item["pkgStatus"]
			elif role == PackagesModel.CustomNameRole:
				return item["customName"]
			elif role == PackagesModel.IconRole:
				return item["icon"]
			elif role == PackagesModel.DefaultPkgRole:
				return item["defaultPkg"]
			elif role == PackagesModel.ShowCbRole:
				return item["showCb"]
			elif role == PackagesModel.OrderRole:
				return item["order"]
	
		#def data

	def roleNames(self):
		
		roles = dict()
		roles[PackagesModel.PkgIdRole] = b"pkgId"
		roles[PackagesModel.PkgStatusRole] = b"pkgStatus"
		roles[PackagesModel.CustomNameRole] = b"customName"
		roles[PackagesModel.IconRole] = b"icon"
		roles[PackagesModel.defaultPkgRole] = b"defaultPkg"
		roles[PackagesModel.ShowCbRole] = b"showCb"
		roles[PackagesModel.OrderRole] = b"order"

		return roles

	#def roleName

	def appendRow(self,pkgid,pkgst,cn,ic,dp,shc,o):
		
		self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(),self.rowCount())
		self._entries.append(dict(pkgId=pkgid, pkgstatus=pkgst, customName=cn, icon=ic, defaultPkg=dp, showCb=shc,order=o))
		self.endInsertRows()

	#def appendRow

	def setData(self, index, param, value, role=QtCore.Qt.EditRole):
		
		if role == QtCore.Qt.EditRole:
			row = index.row()
			if param in ["pkgStatus","icon"]:
				self._entries[row][param]=value
				self.dataChanged.emit(index,index)
				return True
			else:
				return False
	
	#def setData

	def clear(self):
		
		count=self.rowCount()
		self.beginRemoveRows(QtCore.QModelIndex(), 0, count)
		self._entries.clear()
		self.endRemoveRows()
	
	#def clear
	
#class PackagesModel
