# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- object tree
#--
#-- microelly 2015
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------

import FreeCAD
import PySide
from PySide import QtCore, QtGui, QtSvg
global QtGui,QtCore


global fullRefresh, parentsView, childrensView, familyView, renderWidget
global doSomething,search, createTree, sayWidgetTree,cm,vlines,TypeIcon
global w, refresh

import os

global __version__
__version__ = "(version 0.10 2015-06-18)"

from configmanager import ConfigManager




global AppHomePath
AppHomePath=FreeCAD.ConfigGet('AppHomePath')


cm=ConfigManager("ObjectTree")

def TypeIcon(typeId='Part::Cut'):
	
	typeIcons={
	'Part::MultiFuse' : "icons:Part_Fuse.svg",
	'Part::MultiCommon' : "icons:Part_Common.svg",
	'Sketcher::SketchObject' : "icons:Sketcher_Sketch.svg",
	#'Draft::Clone' : "Draft_Clone.svg",
	# 'App::DocumentObjectGroup' : icons:
	'Drawing::FeaturePage' : 'icons:Page.svg',
	'Drawing::FeatureViewPart' : 'icons:Draft_Drawing.svg'
	#'Drawing::FeatureViewPart' : 'icons:Drawing-orthoviews.svg',
	}

	tk=typeId.replace("::", "_");
	f2=QtCore.QFileInfo("icons:"+ tk + ".svg")
	if f2.exists():
		return QtGui.QIcon("icons:"+ tk + ".svg") 
	if typeIcons.has_key(typeId):
		f2=QtCore.QFileInfo(typeIcons[typeId])
		if f2.exists():
			return QtGui.QIcon(typeIcons[typeId])
	FreeCAD.Console.PrintError("TypeIcon: " + typeId + " - no Icon found \n")
	return QtGui.QIcon('icons:freecad.svg')


def createTree(obj,n,mode):
	if n<2: 
		tree={'obj':obj,'subs':[],'subtyp':n,'status':'normal','a_label':obj.Label,'a_typeId':obj.TypeId} 
	else:
		tree={'obj':obj,'subs':[],'subtyp':n,'status':'hide','a_label':obj.Label,'a_typeId':obj.TypeId} 
	
	print "--------------------"
	print obj.Label
	k=obj.OutList
	print "--------------------"
	for it in k:
		print it.Label, " => ",it.TypeId
	print "--------------------"
	
	if mode == 'parents':
		if obj.TypeId=='PartDesign::Mirrored' or obj.TypeId=='PartDesign::LinearPattern':
			k=obj.OutList
			for el in k:
				FreeCAD.Console.PrintMessage("\n: "+el.Label + "--"+el.TypeId + "\n")
			FreeCAD.Console.PrintMessage("\n size:" + str(len(k)) + "\n")
			#if len(k)>1:
			ske=k[-1]
			FreeCAD.Console.PrintMessage("Sonder: "+ske.Label)
			#else:
			#	stske=[]
			pad=k[0]
			stske=createTree(pad,n+2,mode)
			FreeCAD.Console.PrintMessage(" pad "+ pad.Label)
			tree1={'obj':ske,'subs':[stske],'subtyp':n+1,'status':'normal'} 
			tree['subs']=[tree1]
		elif obj.TypeId=='PartDesign::MultiTransform':
			k=obj.OutList
			for el in k:
				FreeCAD.Console.PrintMessage("\n: "+el.Label + "--"+el.TypeId + "\n")
			FreeCAD.Console.PrintMessage("\n size:" + str(len(k)) + "\n")
			#if len(k)>1:
			ske=k[0]
			FreeCAD.Console.PrintMessage("Sonder: "+ske.Label)
			# hier fehlt die hierarchie ...
			#else:
			#	stske=[]
			
			pad=k[-1]
			stske=createTree(pad,n+len(k)+0,mode)
			FreeCAD.Console.PrintMessage(" pad "+ pad.Label)
			treealt={'obj':ske,'subs':[stske],'subtyp':n+len(k)-1,'status':'normal'} 
			# tree['subs']=[treealt]
			k.pop()
			# k.reverse()
			
			# treealt=["intitree-----------------------------------"]
			print "#######"
			m=n+len(k)
			for it in k:
				print "++++++++++++++++"
				print it.Label," " ,it.TypeId," m",m
				treeneu={'obj':it,'subs':[treealt],'subtyp':m,'status':'normal','a_label':it.Label} 
				m -= 1
				treealt=treeneu
				import pprint
				pprint.pprint(treealt)
			print "########"
			tree['subs']=[treealt]
			tree['subtyp']=n



		else:
			for s in obj.OutList:
				st=createTree(s,n+1,mode)
				#st[s]['subtyp']=n
				tree['subs'].append(st)
	elif mode == 'children':
		for s in obj.InList:
			st=createTree(s,n+1,mode)
			#st[s]['subtyp']=n
			tree['subs'].append(st)
	else:
		FreeCAD.Console.PrintError("unknown mode:" + mode + "\n")
		raise Exception
	#FreeCAD.Console.PrintMessage(str(n) + " " + obj.Label +" typeId=")
	#FreeCAD.Console.PrintMessage(obj.TypeId +"\n")
	
	return tree

def sayTree(ot):
	'''	print output of the tree structure for testing'''
	
	ss="#"
	for k in ot.keys():
		if k=='subtyp': 
			ss= "* " * ot[k]
		if k == 'obj':
			name = ot[k].Label
#	print ss + name
	for s in ot['subs']:
			sayTree(s)

#------------------------------------------


import sys
from PySide import QtCore, QtGui



if False:
	try:
		import FreeCAD
		FreeCAD.open(u"/home/thomas/freecad_buch/b142_otreee/m02_mouse_events_testcase.fcstd")
		#FreeCAD.open(u"E:/freecadbuch_2/b142_otreee/m02_mouse_events_testcase.fcstd")
		App.setActiveDocument("m02_mouse_events_testcase")
		App.ActiveDocument=App.getDocument("m02_mouse_events_testcase")
		Gui.ActiveDocument=Gui.getDocument("m02_mouse_events_testcase")
		
		App.ActiveDocument.Torus.ViewObject.Visibility=True
		App.ActiveDocument.Sphere.ViewObject.Visibility=True
		App.ActiveDocument.Cylinder.ViewObject.Visibility=True
		FreeCADGui.Selection.clearSelection()
		for s in [App.ActiveDocument.Box001, App.ActiveDocument.Sphere001,App.ActiveDocument.Cone001]:
			FreeCADGui.Selection.addSelection(s)
	except:
		pass

if False:
	os=FreeCAD.ActiveDocument.Objects
	for obj in os:
		obj.ViewObject.Visibility=False
	App.ActiveDocument.Torus.ViewObject.Visibility=True
	App.ActiveDocument.Sphere.ViewObject.Visibility=True
	App.ActiveDocument.Cylinder.ViewObject.Visibility=True
	FreeCADGui.Selection.clearSelection()
	for s in [App.ActiveDocument.Box001, App.ActiveDocument.Sphere001,App.ActiveDocument.Cone001]:
		FreeCADGui.Selection.addSelection(s)

global buff

buff={}
def initBuff():
	
	os=FreeCAD.ActiveDocument.Objects
	for obj in os:
		try:
			v=obj.ViewObject.Visibility
			t=obj.ViewObject.Transparency
			buff[obj]=[v,t]
			say("!" +obj.Label + ":"+str(obj.ViewObject.Transparency) + "-- "+ str(obj.ViewObject.Visibility))
			v=obj.ViewObject.Visibility=False
		except:
			say (obj.Label + "not init buff") 

initBuff()

global context

context={}
os=FreeCADGui.Selection.getSelection()
for obj in os:
	context[obj]=True

global lastObj
lastObj=False

try:
	lastObj =[FreeCAD.ActiveDocument.ActiveObject,FreeCAD.ActiveDocument.ActiveObject.ViewObject.ShapeColor]
except:
	pass

class MyBut(QtGui.QPushButton):
	def __init__(self,icon,name):
		QtGui.QPushButton.__init__(self,icon,name)
		#QtGui.QPushButton.__init__(self,name)
		# self.obj=FreeCAD.ActiveDocument.Box

	def enterEvent(self,ev):
		global lastObj
		import random
		self.obvisi=self.obj.ViewObject.Visibility
		self.color=self.obj.ViewObject.ShapeColor
		self.obj.ViewObject.ShapeColor=(1.0,0.5,1.0)
		self.obj.ViewObject.Transparency=0
		self.obj.ViewObject.DisplayMode = "Flat Lines"
		self.obj.ViewObject.Visibility=True
		say("mouse enter A " + self.obj.Label)
		try:
			if lastObj:
				lo=lastObj[0]
				loc=lastObj[1]
				lo.ViewObject.ShapeColor=(random.random(),random.random(),random.random())
				lastObj=[self.obj,self.color]
				#FreeCADGui.SendMsgToActiveView("ViewFit")
				FreeCAD.ActiveDocument.recompute()
				say(lo.ViewObject.ShapeColor)
		except:
			sayexc("hk2")

	def leaveEvent(self,ev):
		say("mouse Leave A " + self.obj.Label) 
		try:
			self.obj.ViewObject.Visibility=False
			self.obj.ViewObject.ShapeColor=self.color
			self.obj.ViewObject.Transparency=90
			self.obj.ViewObject.DisplayMode = "Shaded"
			if context.has_key(self.obj) and context[self.obj]:
				pass
			self.obj.ViewObject.Visibility=True
		except:
			sayexc("hu44")
		FreeCAD.ActiveDocument.recompute()

	def mousePressEvent(self, ev):
		#FreeCAD.Console.PrintMessage("k mouse press")
		say("mouse Press A " + self.obj.Label) 
		#FreeCAD.Console.PrintMessage("Label clicked  " +  ot['obj'].Label + "\n")
		FreeCADGui.Selection.clearSelection()
		## FreeCADGui.Selection.addSelection(self.ot['obj'])
		FreeCADGui.Selection.addSelection(self.obj)
		fullRefresh('family')

	def eventFilter1(self,ev):
		FreeCAD.Console.PrintMessage("kgdfgfdk")
		say(" c gfgdfgfd nter event")
		say(ev)



global hideall
def hideall():
	os=FreeCAD.ActiveDocument.Objects
	for obj in os:
		FreeCAD.Console.PrintMessage("!# ")
		obj.ViewObject.Transparency=90
		self.obj.ViewObject.DisplayMode = "Shaded"
		obj.ViewObject.Visibility=False


global showall2
def showall2():
	os=FreeCAD.ActiveDocument.Objects
	say("showall2")
	# say(os)
	for obj in os:
#		say("show all")
		obj.ViewObject.Visibility=buff[obj][0]
		obj.ViewObject.Transparency=buff[obj][1]
		obj.ViewObject.DisplayMode = "Flat Lines"
#		obj.ViewObject.Visibility=buff[obj][0]
#		say("!" +obj.Label + ":"+str(obj.ViewObject.Transparency) + "-- "+ str(obj.ViewObject.Visibility))
	#FreeCADGui.SendMsgToActiveView("ViewFit")
	

global MyWindow2
class MyWindow2(QtGui.QWidget) :
	def __init__(self):
		QtGui.QWidget.__init__(self)
		self.leaved=True
		layout2 = QtGui.QHBoxLayout()
		f=QtGui.QWidget()
		f=QtGui.QFrame()
		layout2.addWidget(f)
		self.f=f
		layout = QtGui.QHBoxLayout()
		self.framelayout=layout
		f.setObjectName("context")
		FreeCAD.f=f
		#self.f.setStyleSheet("{ background-color: yellow;padding:5px;margin:5px;border:2px solid red;}")
		self.f.setStyleSheet("{ background-color: yellow;padding:0px;margin:2px;border:2px solid red;}")

		f.setLayout(layout)
		# hier die vorselektierten objekte rein
		
		for obj in context.keys():
			if context[obj]:
				b=MyBut(TypeIcon(obj.TypeId),obj.Label)
				b.obj=obj
				layout.addWidget(b)
				lc=lambda: self.labelClick2(obj)
				b.clicked.connect(lc) 
				
#		b=MyBut(QtGui.QIcon('/usr/lib/freecad/Mod/mylib/icons/mars.png'),"Box")
#		b.obj=FreeCAD.ActiveDocument.Box
#		b2=MyBut(QtGui.QIcon('/usr/lib/freecad/Mod/mylib/icons/sun.png'),"cone")
#		b2.obj=FreeCAD.ActiveDocument.Cone
#		b3=MyBut(None,"Cut ")
#		b3.obj=FreeCAD.ActiveDocument.Cut001
#		b4=MyBut(None,"common ")
#		b4.obj=FreeCAD.ActiveDocument.Common
#		
#		layout.addWidget(b)
#		layout.addWidget(b2)
#		layout.addWidget(b3)
#		layout.addWidget(b4)

		self.setStyleSheet("\
				QWidget#context { background-color: orange;margin:0px;padding:0px;}\
				QPushButton { background-color: yellow;margin 30px;}\
				")


		self.setLayout(layout2)
		self.setMouseTracking(True)
		#f.setMouseTracking(True)

	def labelClick2(self,obj):
		FreeCAD.Console.PrintMessage("Label clicked 2 " +  obj.Label + "\n")
		FreeCADGui.Selection.clearSelection()
		FreeCADGui.Selection.addSelection(obj)
		fullRefresh('family')





	def enterEvent(self,ev):
		FreeCAD.Console.PrintMessage("++ ")
		hideall()

	def leaveEvent(self,ev):
		FreeCAD.Console.PrintMessage("#2# ")
		self.leaved=not self.leaved
		if self.leaved:
			pass
		#say("showall2")
		try: 
			#showall2()
			pass
		except:
			sayexc("huhu")
		for obj in context.keys():
			say("show all context -- " + obj.Label)
			obj.ViewObject.Visibility=True
			obj.ViewObject.Transparency=80
			obj.ViewObject.DisplayMode = "Shaded"

		say("showall2 done")


	def setMouseTracking(self, flag):
		def recursive_set(parent):
			for child in parent.findChildren(QtCore.QObject):
				try:
					child.setMouseTracking(flag)
				except:
					pass
				recursive_set(child)
		QtGui.QWidget.setMouseTracking(self, flag)
		recursive_set(self)

	def mouseMoveEvent(self, event):
		FreeCAD.Console.PrintMessage("--- ")
##		print 'mouseMoveEvent: x=%d, y=%d' % (event.x(), event.y())






#----------------------
global MyBut
class MyButA(QtGui.QPushButton):
	
	def __init__(self,icon=None,label=''):
		#QtGui.QPushButton.__init__(self,icon,label)
		QtGui.QPushButton.__init__(self,label)
		self.obj=None
		self.active=False
		# self.active=True

	def enterEvent(self,ev):
		if not self.active:
			return
		self.obvisi=self.obj.ViewObject.Visibility
		self.color=self.obj.ViewObject.ShapeColor
		self.obj.ViewObject.ShapeColor=(1.0,0.0,1.0)
		self.obj.ViewObject.Visibility=True
		self.sel=FreeCADGui.Selection.getSelection()
		FreeCADGui.Selection.clearSelection()

	def leaveEvent(self,ev):
		if not self.active:
			return
		self.obj.ViewObject.Visibility=False
		self.obj.ViewObject.ShapeColor=self.color
		self.obj.ViewObject.Visibility=self.obvisi
		for s in self.sel:
			FreeCADGui.Selection.addSelection(s)
#--------------------------

class MyWidget(QtGui.QWidget):
	def __init__(self, master,*args):
		QtGui.QWidget.__init__(self, *args)
		
		self.master=master
		FreeCAD.mywidget=self
		self.printed=[]
		#self.printed2=[]
#		
#	def myinit(self):
		layout = QtGui.QGridLayout()
		
		self.layout=layout
		self.layout.setAlignment(QtCore.Qt.AlignLeft)
		line=4
		self.mw=QtGui.QWidget()
		layout.setSpacing(0)
		
		self.mw.setLayout(layout)
		self.setWindowTitle("Object Design Workflow Tree " + __version__)
		self.setStyleSheet("* {background-color:white;} *:focus { color:red;background-color:white;}")

		self.layout=layout
		self.line=line
		mlayout=QtGui.QVBoxLayout()
		self.mlayout=mlayout
		hlayout=QtGui.QHBoxLayout()
		self.hlayout=hlayout
		self.hw=QtGui.QWidget()
		self.hw.setLayout(self.hlayout)
		
		butti= QtGui.QPushButton(QtGui.QIcon('icons:view-refresh.svg'),"Refesh")
		butti.clicked.connect(fullRefresh) 
		self.hlayout.addWidget(butti)
		butti.clearFocus()
		butti= QtGui.QPushButton(QtGui.QIcon("icons:button_down.svg"),"Parents")
		butti.clicked.connect(parentsView) 
		self.hlayout.addWidget(butti)
		# butti= QtGui.QPushButton(QtGui.QIcon('/usr/lib/freecad/Mod/plugins/icons/web-refresh.png'),"View Children")
		butti= QtGui.QPushButton(QtGui.QIcon("icons:button_up.svg"),"Children")
		
		butti.clicked.connect(childrensView) 
		self.hlayout.addWidget(butti)
		butti= QtGui.QPushButton(QtGui.QIcon('/usr/lib/freecad/Mod/plugins/icons/web-refresh.png'),"Familiy")
		butti= QtGui.QPushButton(QtGui.QIcon('icons:Snap_Center.svg'),"Familiy")
		butti.clicked.connect(familyView) 
		self.hlayout.addWidget(butti)
		
		self.hw.setStyleSheet("QListWidget,QPushButton {border:none;text-align:left;}\
				QPushButton {border:0px solid red;text-align:left;}\
				QPushButton#mainLabel {border:0px solid green;text-align:left;background-color:yellow;padding:0px  5px 0px 0px;margin-right:10px;}\
				QPushButton#mainIcon {border:0px solid green;text-align:left;background-color:yellow;padding:0px  0px 0px 5px;}\
			QWidget2 {border:2px solid green;background-color:}")
		
		
		self.butti2= QtGui.QPushButton(QtGui.QIcon(AppHomePath+'/Mod/plugins/objecttree/icons/camera-photo.png'),"Snapshot")
		self.hlayout.addWidget(self.butti2)
		self.butti2.clicked.connect(renderWidget)
		
		self.butti2= QtGui.QPushButton(QtGui.QIcon('icons:Tree_Annotation.svg'),"Props")
		self.butti2.clicked.connect(doSomething)
		self.hlayout.addWidget(self.butti2)
		#self.butti2= QtGui.QPushButton(QtGui.QIcon('/usr/lib/freecad/Mod/plugins/icons/help.png'),"Search")
		#self.butti2= QtGui.QPushButton(QtGui.QIcon('/home/thomas/website_local/html/dokuwiki/data/media/story/ik.svg/view-select.svg'),"Search")
		self.butti2= QtGui.QPushButton(QtGui.QIcon("icons:"+ 'view-zoom-all.svg'),"Search")
		self.butti2.clicked.connect(search)
		
		self.hlayout.addWidget(self.butti2)
		butti= QtGui.QPushButton(QtGui.QIcon('icons:Part_Measure_Step_Done.svg'),"Close")
		butti.clicked.connect(self.hide) 
		butti.clicked.connect(showall2) 
		self.hlayout.addWidget(butti)
		self.mlayout.addWidget(self.hw)
		self.mlayout.addWidget(self.mw)
		
		window2 = MyWindow2()
		self.framelayout=layout
		self.mlayout.addWidget(window2)
# window.setGeometry(500, 300, 300, 400)
#window.show()

		
		
		self.setLayout(mlayout)
		self.mw.setStyleSheet("QListWidget,QPushButton {border:none;text-align:left;}\
				QPushButton {border:0px solid red;text-align:left;}\
				QPushButton#mainLabel {border:0px solid green;text-align:left;background-color:yellow;padding:0px  5px 0px 0px;margin-right:10px;}\
				QPushButton#mainIcon {border:0px solid green;text-align:left;background-color:yellow;padding:0px  0px 0px 5px;}\
			QWidget2 {border:2px solid green;background-color:transparent}")
		# self.butti2.installEventFilter(self)
		FreeCAD.Console.PrintMessage('myinint done installed ')

		self.setMouseTracking(True)
		#f.setMouseTracking(True)

	def close(self):
		showall2()
		self.hide()

	def enterEvent(self,ev):
		FreeCAD.Console.PrintMessage("++ ")
		hideall()

	def leaveEvent(self,ev):
		FreeCAD.Console.PrintMessage("#2# ")
		self.leaved=not self.leaved
		if self.leaved:
			pass
		showall2()





# button left right double clicks
	def eventFilter(self, obj, event):
			if event.type() == QtCore.QEvent.MouseButtonPress:
				if event.button() == QtCore.Qt.LeftButton:
					#If image is left clicked, display a red bar.
					FreeCAD.Console.PrintMessage('one left\n')
				elif event.button() == QtCore.Qt.RightButton:
					FreeCAD.Console.PrintMessage('one right\n')
			elif event.type() == QtCore.QEvent.MouseButtonDblClick:
				#If image is double clicked, remove bar.
				FreeCAD.Console.PrintMessage('two\n')
			return super(MyWidget, self).eventFilter(obj, event)




	def addObj(self,ot,obj,row,count,mode,dir):
		global filled
		
		ox=cm.get('ox',1000)
		oy=cm.get('oy',1000)
		ax=cm.get('ax',1)
		ay=cm.get('ay',1)
		
		
		if dir == '-x':
			ax=-1
		
#		pushButt = QtGui.QPushButton()
#		try:
#			butti= QtGui.QPushButton(QtGui.QIcon(obj.ViewObject.Proxy.getIcon()),"") 
#		except:
#			butti= QtGui.QPushButton(TypeIcon(obj.TypeId),"")


		pushButt = MyBut(None,"")
		pushButt.obj=obj
		pushButt.ot=ot
		try:
			butti= MyBut(QtGui.QIcon(obj.ViewObject.Proxy.getIcon()),"") 
		except:
			butti= MyBut(TypeIcon(obj.TypeId),"")
		butti.obj=obj

		tt="-: "+ str(oy+ay*self.line)
		tt=''
		if row==0:
			pushButt.setText(""+ obj.Label + "" + tt)
			pushButt.setObjectName("mainLabel")
			butti.setObjectName("mainIcon")
		else:
			pushButt.setText(obj.Label + tt)	
		
		lc=lambda: self.labelClick(ot)
		
		pushButt.clicked.connect(lc) 
		butti.clicked.connect(lc) 
		
		if obj in self.printed:
		#	pushButt.setText(obj.Label + "!")
			# butti= QtGui.QPushButton(QtGui.QIcon('/usr/lib/freecad/Mod/mylib/icons/mars.png'),"")
			
			pass 
		
		
		#pushButt.setStyleSheet("{border:2px solid green;color:green;}")
		
		self.printed.append(obj)
		if ax== -1:
			self.layout.addWidget(butti, oy+ay*self.line, ox+ax*3*row-1+1)
		else:
			self.layout.addWidget(butti, oy+ay*self.line, ox+ax*3*row)
		if ax== -1:
			self.layout.addWidget(pushButt, oy+ay*self.line, ox+ax*3*row+1)
		else:
			self.layout.addWidget(pushButt, oy+ay*self.line, ox+ax*3*row+1)
		subst=str(count)
#		if False and count >0:
#			butte= QtGui.QPushButton(QtGui.QIcon('/usr/lib/freecad/Mod/mylib/icons/mars.png'),subst)
#			self.layout.addWidget(butte, oy+self.line, ox+3*row+2)

		
		say(AppHomePath)
		if row >0:
			if mode ==1  :
				butte= QtGui.QPushButton(QtGui.QIcon(AppHomePath+'/Mod/plugins/objecttree/icons/single.png'),"")
			elif mode ==0 :
				butte= QtGui.QPushButton(QtGui.QIcon(AppHomePath+'/Mod/plugins/objecttree/icons/start.png'),"")
			elif mode == -1:
				if ax== -1:
					butte= QtGui.QPushButton(QtGui.QIcon(AppHomePath+'/Mod/plugins/objecttree/icons/end2.png'),"")
				else:
					butte= QtGui.QPushButton(QtGui.QIcon(AppHomePath+'/Mod/plugins/objecttree/icons/end.png'),"")
			else:
				if ax== -1:
					butte= QtGui.QPushButton(QtGui.QIcon(AppHomePath+'/Mod/plugins/objecttree/icons/downl-l.png'),"" )
				else:
					butte= QtGui.QPushButton(QtGui.QIcon(AppHomePath+'/Mod/plugins/objecttree/icons/downl-r.png'),"" )
			if ax== -1:
				self.layout.addWidget(butte, oy+ay*self.line, ox+ax*3*row-1+2+1)
			else:
				self.layout.addWidget(butte, oy+ay*self.line, ox+ax*3*row-1)
			
			f=lambda: self.collapsTree(ot)
			
			if len(ot['subs']) >0 :
				butte.clicked.connect(f) 

			g=lambda: self.expandTree(ot)
			if ot['status'] == 'hide' and dir != '-x':
				if len(ot['subs']):
					buttx= QtGui.QPushButton(QtGui.QIcon('icons:add.svg'),"" )
					self.layout.addWidget(buttx, oy+ay*self.line, ox+ax*3*row+2)
					buttx.clicked.connect(g) 
			if ot['status'] == 'hide' and dir == '-x':
				if len(ot['subs']):
					buttx= QtGui.QPushButton(QtGui.QIcon('icons:add.svg'),"" )
					self.layout.addWidget(buttx, oy+ay*self.line, ox+ax*3*row+2-4)
					#buttx.clicked.connect(g) 
					buttx.clicked.connect(lc) 
			
			filled[self.line][3*row-1]=1
	
	def collapsTree(self,ot):
		ot['status']='hide'
		FreeCAD.Console.PrintMessage("collapsTree " +  ot['obj'].Label + "\n")
		FreeCAD.Console.PrintMessage("collapsTree " +  ot['status'] + "\n")
		refresh()

	def expandTree(self,ot):
		ot['status']='normal'
		FreeCAD.Console.PrintMessage("expandTree " +  ot['obj'].Label + "\n")
		FreeCAD.Console.PrintMessage("expandTree " +  ot['status'] + "\n")
		refresh()

	def labelClick(self,ot):
		FreeCAD.Console.PrintMessage("Label clicked  " +  ot['obj'].Label + "\n")
		FreeCADGui.Selection.clearSelection()
		FreeCADGui.Selection.addSelection(ot['obj'])
		fullRefresh('family')

vlines={}
vflines={}

def sayWidgetTree(w,ot,mode=0,dir='+x'):
	pos=ot['subtyp']
	
	w.addObj(ot,ot['obj'],pos,len(ot['subs']),mode,dir)
	#if obj in w.printed2:
	#	return
	#	pass
	# w.printed2.append(obj)
	for p in vlines.keys():
		if vlines[p]:
			if vlines[p]==1 and filled[w.line][3*p+2]<>1:
				butte= QtGui.QPushButton(QtGui.QIcon(AppHomePath+'/Mod/plugins/objecttree/icons/down.png'),"" )
	anz=len(ot['subs'])
	startline=w.line
	if ot['status']=='normal':
		for s in range(anz):
			# print (s)
			if s==0 and anz==1:
				mode2=1
				vlines[pos]=0
			elif s ==0: 
				mode2=0
				vlines[pos]=1
			elif s == anz -1:
				mode2= -1
				vlines[pos]=0
				w.line += 1
			else:
				mode2 = 2
				vlines[pos]=22
				w.line += 1
			sayWidgetTree(w,ot['subs'][s],mode2,dir)
			#w.line += 1
			endline=w.line
	


def refresh():
	#global otlist
	for k in w.mw.findChildren(QtGui.QPushButton):
		k.deleteLater()
	w.line=4
	#for ot in otlist:
	sayWidgetTree(w,w.ot,0)
	w.hide();w.show()


def fullRefresh(mode='parents'):
	global w,filled,ot,otlist
	ot=None
	w.ot=None
	w.printed=[]
	#w.printed2=[]
	w.line=4
	filled={}
	
	for x in range(100):
		filled[x]={}
		for y in range(100):
			#print x,y
			filled[x][y]=0
	
	for k in w.mw.findChildren(QtGui.QPushButton):
		k.deleteLater()
	#obs= [App.ActiveDocument.Fusion002,App.ActiveDocument.Cut001]
	#obs= [App.ActiveDocument.Cut001]
	#obs= [App.ActiveDocument.Fusion]
	obs= Gui.Selection.getSelection()
	if len(obs)<1:
			obs=[FreeCAD.ActiveDocument.ActiveObject]
			#w.layout.setAlignment(QtCore.Qt.AlignCenter)
			#butte= QtGui.QPushButton(QtGui.QIcon('icons:freecad.svg'),"Error: Select your object of interest!" )
			#butte.setObjectName("mainLabel")
			#w.layout.addWidget(butte, 1,1)
			#return
		
	#obs=obs[0:1]

	otlist=[]
	#for ob1 in obs:
		
		#otlist.append(ot)
		# import pprint;pprint.pprint(ot)
	ob1=obs[len(obs)-1]
	if True:
		if mode== 'children':
			ot=createTree(ob1,0,mode)
			dir = '-x'
			w.layout.setAlignment(QtCore.Qt.AlignLeft)
			sayWidgetTree(w,ot,0,dir)
		elif mode == 'parents':
			ot=createTree(ob1,0,mode)
			dir = '+x'
			w.layout.setAlignment(QtCore.Qt.AlignRight)
			sayWidgetTree(w,ot,0,dir)
		else:
			ot=createTree(ob1,0,'parents')
			sayWidgetTree(w,ot,0,'+x')
			ot2=createTree(ob1,0,'children')
			w.line=4
			w.printed=[]
			#w.printed2=[]
			w.layout.setAlignment(QtCore.Qt.AlignCenter)
			sayWidgetTree(w,ot2,0,'-x')
	w.ot=ot
	# w.hide();w.show()
	w.update()
	
	for obj in context.keys():
		say("show all context -- " + obj.Label)
		obj.ViewObject.Visibility=True
		obj.ViewObject.Transparency=30




def parentsView():
	fullRefresh('parents')
	w.setWindowTitle("Object Design Workflow Tree - Parents View ")

def childrensView():
	fullRefresh('children')
	w.setWindowTitle("Object Design Workflow Tree - Children View ")

def familyView():
	fullRefresh('family')
	w.setWindowTitle("Object Design Workflow Tree - Children and Parents ")

#-----------------------

import re


class searchWidget(QtGui.QWidget):
	def __init__(self, *args):
		QtGui.QWidget.__init__(self, *args)
		self.vollabel = QtGui.QLabel('2. Select Object by Label ...')
		self.vollabel2 = QtGui.QLabel('1. Preselect Filter for Label ...')
	
		self.listWidget = QtGui.QListWidget() 
		#self.listWidget.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
		self.pat = QtGui.QLineEdit(self)
		self.pat.setText(".*")
		self.getlist()
		self.pat.textChanged.connect(self.run)

		for k in self.res:
			#if not self.config[k]['status'] == "ignore":
			
				# item = QtGui.QListWidgetItem(QtGui.QIcon('/usr/lib/freecad/Mod/plugins/icons/master.png'),k.Label)
				
				try:
					item= QtGui.QListWidgetItem(QtGui.QIcon(k.ViewObject.Proxy.getIcon()),k.Label) 
				except:
					item= QtGui.QListWidgetItem(TypeIcon(k.TypeId),k.Label)
				
				
				
				self.listWidget.addItem(item)
		layout = QtGui.QGridLayout()
		
		layout.addWidget(self.vollabel2, 1, 0,1,4)
		layout.addWidget(self.vollabel, 3, 0,1,4)
		
		layout.addWidget(self.listWidget, 4, 0,1,4)
		
		
		layout.addWidget(self.pat, 2, 0,1,4)
		
		self.pus = QtGui.QPushButton()
		self.pus.clicked.connect(self.runresult) 
		self.pus.setText("Set Selection")
		
		layout.addWidget(self.pus, 5, 0,1,4)
		self.setLayout(layout)
		self.setWindowTitle("Object Selector")



	def getlist(self):
		os=FreeCAD.ActiveDocument.Objects
		res=[]
		FreeCAD.Console.PrintMessage("pat:+++++++++++++\n")
		pat=str(self.pat.text())
		FreeCAD.Console.PrintMessage("pat:"+pat+"!\n")
		for oj in os:
			# print oj.Label
			
			
			if re.search(pat, oj.Label):
				FreeCAD.Console.PrintMessage(oj.Label)
				print oj.Label," okay" 
				res.append(oj)
		self.res=res


	def run(self):
		FreeCAD.Console.PrintMessage("k--------------- \n")
		# self.res=self.res[0]
		FreeCAD.Console.PrintMessage("k--------------- \n")
		k=True
		while  k:
			k=None
			k=self.listWidget.takeItem(0)
			
			
		#		FreeCAD.Console.PrintMessage("yy--------------- \n")
		#		FreeCAD.Console.PrintMessage(k)
		#		k.deleteLater()
		FreeCAD.Console.PrintMessage("k----dfd----------- \n")
		self.getlist()
		# self.res=[self.res[0]]
		for k in self.res:
			#if not self.config[k]['status'] == "ignore":
				# item = QtGui.QListWidgetItem(k.Label )
				
				try:
					item= QtGui.QListWidgetItem(QtGui.QIcon(k.ViewObject.Proxy.getIcon()),k.Label) 
				except:
					item= QtGui.QListWidgetItem(TypeIcon(k.TypeId),k.Label)
				
				
				self.listWidget.addItem(item)
		self.hide()
		self.show()

	def runresult(self):
		
		FreeCAD.Console.PrintMessage("k----dfd---runresult 1-------- \n")
		FreeCADGui.Selection.clearSelection()
		
		ll=self.listWidget.selectedItems()
		ls=ll[0].text()
		for s in self.res:
			if s.Label==ls:
				FreeCAD.Console.PrintMessage("k----dfd---runresult 1a-------- \n")
				FreeCADGui.Selection.addSelection(s)
		FreeCAD.Console.PrintMessage("k----dfd---runresult 2-------- \n")
		self.hide()
		fullRefresh('family')



def search():
	global searchWidget,w
	FreeCAD.Console.PrintMessage("Search -----------!!--------\n")
	try:
		t=searchWidget()
		FreeCAD.Console.PrintMessage("t:" +str(t))
		w.searchw=t
		t.show()
	except:
		FreeCAD.Console.PrintMessage("Fehler")




#-----------------------


def renderWidget():
	child=w
	child=w.mw
	image = QtGui.QPixmap(child.size())
	child.render(image)
	imagename=cm.get('imageName','c:/t2.jpg')
	imageformat=cm.get('imageFormat','JPG')
	image.save( 'c:/t.jpg', 'JPG')
	
	#displaymode=cm.get('displayMode','extern')
	displaymode=cm.get('displayMode','intern')
	displayCmd=cm.get('displayCmd','eog')
	
	displaymode='intern'
	displayCmd="c:/i_view32.exe"
	
	if displaymode=='intern':
		import os, tempfile
		d=tempfile.mktemp()
		os.makedirs(d)
		imagename = d + '/tree.' + imageformat
		FreeCAD.Console.PrintMessage("tempfile !" + imagename +'!\n')
		
	image.save(imagename,imageformat)
	
	if displaymode == 'extern':
		image.save( '/tmp/snapshot.png', 'PNG')
		import os
		#os.system("eog /tmp/snapshot.png &")
		import subprocess
		DETACHED_PROCESS = 0x00000008

		pid = subprocess.Popen([displayCmd,"c:\\t3.jpg"],creationflags=DETACHED_PROCESS).pid
		#subprocess.call(["c:/i_view32.exe","c:\\t3.jpg"])
		
		
	else:
		import ImageGui
		ImageGui.open(imagename)
		FreeCAD.Console.PrintMessage("Image saved to:" +str(imagename))
	
 
	

import PySide

def doSomething():
	# display the properties dock window in foreground 
	mw=FreeCAD.Gui.getMainWindow()
	cn=mw.children()
	for c in cn:
		#FreeCAD.Console.PrintMessage(c.__class__)
		if c.__class__ == QtGui.QDockWidget:
			#FreeCAD.Console.PrintMessage(c.windowTitle())
			#print c, c.objectName(), c.windowTitle()
			if str(c.objectName())=="Property view":
				c.show()
				c.raise_()

# main 
if 1 or False:
	w=MyWidget(None)
	w.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
	w.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
	#fullRefresh('parents')
	#fullRefresh('children')
	fullRefresh('family')
	w.show()

if False:
	ob1= App.ActiveDocument.MultiTransform
	mode='parents'
	ot=createTree(ob1,0,mode)
	print ot
	sayTree(ot)
	import pprint
	pprint.pprint(ot)
