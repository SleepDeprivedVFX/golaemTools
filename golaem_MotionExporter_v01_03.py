from maya import cmds
import os.path
from functools import partial

__author__ = 'Adam Benson'
__version__ = '1.03.01'


class golaem_MotionExporter(object):
	"""
	docstring for golaem_MotionExporter

	Written by: Adam Benson for The Third Floor, 2016

	v01.03

	This script creates a .gmo Golaem Motion File from an existing animation on the Snarlies.
	It requires that a Golaem rig be parented to the master animation rig.
	"""
	def __init__(self):
		super(golaem_MotionExporter, self).__init__()
		self.root = 'root_golaem'

	def ui(self):
		start = 1
		end = 25
		#check for existing windows
		if cmds.window('golaemMotionExportUI', ex=True):
			cmds.deleteUI('golaemMotionExportUI')
		gmo = cmds.window('golaemMotionExportUI', rtf=True, wh=(300, 200), t='Golaem Motion Exporter - version %s' % __version__)
		#start tabs layout
		formTabs = cmds.formLayout()
		tabs = cmds.tabLayout(innerMarginWidth=5, innerMarginHeight=5)
		cmds.formLayout(formTabs, edit=True, attachForm=((tabs, 'top', 0), (tabs, 'left', 0), (tabs, 'bottom', 0), (tabs, 'right', 0)) )
		#Motion Exporter Tab Setup
		form = cmds.formLayout(nd=100)
		charFile = cmds.textFieldButtonGrp('charFile', l='Golaem Character File', text='', buttonLabel='Get File', pht='Golaem Char File (.gcha) must be loaded', bc=partial(self.getCharFile))
		motionFile = cmds.textFieldButtonGrp('motionFile', l='Export Motion File To', text='', buttonLabel='Set File Path', pht='Export Path for Motion (.gmo) file', bc=partial(self.setMotionPath))
		startEnd = self.getStartEndTimes()
		start = startEnd[0]
		end = startEnd[1]
		startText = cmds.text(label='Start Time')
		endText = cmds.text(l='End Time')
		startTime = cmds.textField('startTime', tx=start, w=50)
		endTime = cmds.textField('endTime', tx=end, w=50)
		rootText = cmds.text(l='Root Joint')
		rootJoint = cmds.textField('rootJoint', tx=self.root, w=150)
		header = cmds.text(l='Golaem Motion Exporter')
		runBtn = cmds.button(l='Run', w=100, c=partial(self.confirmCommand))
		cmds.formLayout(form, edit=True, attachForm=[(header, 'top', 15), (header, 'left', 15), (charFile, 'top', 45), (charFile, 'left', 15), (motionFile, 'top', 75), (motionFile, 'left', 15), (startText, 'top', 125), (startText, 'left', 47), (endText, 'top', 125), (endText, 'left', 165), (startTime, 'top', 145), (startTime, 'left', 47), (endTime, 'top', 145), (endTime, 'left', 165), (rootText, 'top', 170), (rootText, 'left', 47), (rootJoint, 'top', 190), (rootJoint, 'left', 47), (runBtn, 'bottom', 25), (runBtn, 'right', 10)], attachControl=[(header, 'bottom', 5, charFile), (charFile, 'bottom', 5, motionFile), (motionFile, 'bottom', 5, startTime), (motionFile, 'bottom', 5, endTime), (startTime, 'bottom', 5, rootText), (rootText, 'bottom', 5, rootJoint)])
		cmds.setParent('..')
		#Rig Repair Tab Setup
		fixForm = cmds.formLayout(nd=100)
		fixHeader = cmds.text(l='These tools can help repair some rig issues that may arise with the golaem rigs.\n Many of these should be used directly on the master file, and not on a reference.')
		segmentScaleText = cmds.text(l='Segment Scale Patch')
		segmentScaleBtn = cmds.button(l='Fix Segment Scale', w=100, c=partial(self.segmentScalePatch))
		countBones = cmds.button(l='Count Rig Bones', w=100, c=partial(self.countBones))
		attachGolaemRig = cmds.button(l='Attach Golaem Rig', w=100, c=partial(self.attachBones))
		cmds.formLayout(fixForm, edit=True, attachForm=[(fixHeader, 'top', 15), (fixHeader, 'left', 15), (segmentScaleText, 'top', 55), (segmentScaleText, 'left', 15), (segmentScaleBtn, 'top', 75), (segmentScaleBtn, 'left', 15), (countBones, 'top', 115), (countBones, 'left', 15), (attachGolaemRig, 'top', 155), (attachGolaemRig, 'left', 15)])
		cmds.setParent('..')	
		#Package Tabs and open window
		cmds.tabLayout(tabs, edit=True, tabLabel=((form, 'Motion Export'), (fixForm, 'Rig Toolbox')))
		cmds.showWindow('golaemMotionExportUI')
		cmds.setFocus('rootJoint')
		
	def confirmCommand(self, *args):
		#Check information correctness
		motionsCorrect = cmds.confirmDialog(m='Golaem animations, like walk/run cycles, \nrequire forward translation, and should not\nbe running in place.  Is your animation\nready for Golaem?', b=['Yes, Do it!', 'Oops, let me fix that!'], cb='Oops, let me fix that!', db='Yes, Do it!', t='Ready for Golaem?')
		if motionsCorrect == 'Yes, Do it!':
			charFile = cmds.textFieldButtonGrp('charFile', q=True, tx=True)
			motionFile = cmds.textFieldButtonGrp('motionFile', q=True, tx=True)
			startTime = cmds.textField('startTime', q=True, tx=True)
			endTime = cmds.textField('endTime', q=True, tx=True)
			rootJoint = cmds.textField('rootJoint', q=True, tx=True)
			if charFile == '' or '.gcha' not in charFile or motionFile == '' or startTime == '' or endTime == '' or rootJoint == '' or self.checkNumeric(startTime) == False or self.checkNumeric(endTime) == False:
				if charFile == '' or '.gcha' not in charFile:
					cmds.confirmDialog(m='Your Golaem Character File must be a proper .gcha file!')
				elif motionFile == '':
					cmds.confirmDialog(m='Your Motion File must have a proper output path!')
				elif startTime == '' or self.checkNumeric(startTime) == False:
					cmds.confirmDialog(m='Your start time must be a numeric value!')
				elif endTime == '' or self.checkNumeric(endTime) == False:
					cmds.confirmDialog(m='Your end time must be a numeric value!')
				elif rootJoint == '':
					cmds.confirmDialog(m='Your root joint must be listed!')
			else:
				self.bakeExistingAnimations(startTime, endTime, charFile, motionFile, rootJoint)
	
	def checkNumeric(self, var):
		try:
			float(var)
			return True
		except ValueError:
			return False
		
	def getCharFile(self):
		#get the character file
		projRoot = '%s/scenes/Assets/' % self.getSystemInfo()[0]
		charFile = cmds.fileDialog2(cap='Get Golaem Char File', okc='Get', fm=1, rf=True, dir=projRoot)
		cmds.textFieldButtonGrp('charFile', e=True, tx=charFile[0])
		
	def setMotionPath(self):
		#Get the motion file output path
		projRoot = '%s/scenes/Assets/' % self.getSystemInfo()[0]
		motionPath = cmds.fileDialog2(cap='Set Output Path', okc='Set', fm=3, rf=True, dir=projRoot)
		cmds.textFieldButtonGrp('motionFile', e=True, tx=motionPath[0])
		
	
	def getStartEndTimes(self):
		#this will collect the current start and end times
		start = cmds.playbackOptions(q=True, min=True)
		end = cmds.playbackOptions(q=True, max=True)
		return start, end
			
	def getSystemInfo(self):
		#This will collect all of the filename and folder structure info and return it to the UI
		projectRoot = cmds.workspace(q=True, rd=True)
		currentFileName = cmds.file(q=True, sn=True, shn=True).rsplit('.', 1)[0]
		fullFilePath = cmds.file(q=True, sn=True)
		return projectRoot, currentFileName, fullFilePath

	def selectRoot(self, root):
		#select the golaem root joint
		cmds.namespace(set=':')
		getNamespaces = self.parseNamespaces()
		try:
			cmds.select(root, r=True)
			rootFound = cmds.ls(sl=True)[0]
		except:
			for ns in getNamespaces:
				cmds.namespace(set=ns)
				try:
					cmds.select('%s:%s' % (ns, root), r=True)
					rootFound = cmds.ls(sl=True)[0]
					break
				except:
					rootFound = False
				cmds.namespace(set=':')
		if rootFound != False:
			return rootFound
		else:
			return False
		cmds.namespace(set=':')
		

	def parseNamespaces(self):
		#Collect all namespaces
		baseNS = cmds.namespaceInfo(lon=True, r=True)
		return baseNS
		
	def bakeExistingAnimations(self, start, end, char, motion, root):
		#Select the hierarchy and bake the animation
		getRoot = self.selectRoot(root)
		if getRoot != False:
			cmds.select(hi=True)
			bakeTheseJoints = cmds.ls(sl=True)
			cmds.bakeResults(bakeTheseJoints, t=(start, end), simulation=True)
			self.exportGolaemMotion(char, motion, start, end, root)
		else:
			cmds.confirmDialog(m='The Root Joint Cannot be found!')
	
	def exportGolaemMotion(self, char, motion, start, end, root):
		#Create the golaem .gmo file
		getRoot = self.selectRoot(root)
		motionPath = motion
		mainFile = self.getSystemInfo()[1].rsplit('.', 1)[0]
		motionFile = '%s.gmo' % mainFile
		motionOutput = '%s/%s' % (motionPath, motionFile)
		try:
			cmds.glmExportMotion(outputFile=motionOutput, fromRoot=getRoot, characterFile=char, automaticFootprints=True, ftf=start, ltf=end)
			cmds.select(cl=True)
			cmds.deleteUI('golaemMotionExportUI')
			cmds.confirmDialog(m='Success!\nIf you undo the script immediately, it will remove the baking for future editing!  You can also simply not save the baked animations.  If you save it, the baking is permanent!', b='Gotcha!')
		except:
			cmds.confirmDialog(m='The Goleam Export has failed.  Please check the rig and .gcha files to make sure that the number of bones is correct and that there are no other inconsistencies between the hero rig and the Golaem rig.')
			
	
	def segmentScalePatch(self, *args):
		#This will turn segmentScaleCompensate values on joints of the Golaem rig to 0
		getRoot = cmds.textField('rootJoint', q=True, tx=True)
		root = self.selectRoot(getRoot)
		cmds.select(hi=True)
		bones = cmds.ls(sl=True)
		for x in bones:
			try:
				if cmds.nodeType(x) == 'joint':
					cmds.setAttr('%s.segmentScaleCompensate' % x, 0)
					print '************\n%s successfully patched!\n------------------------' % x
			except:
				print '%s couldn\'t be found' % x
				
	
	def countBones(self, *args):
		#Returns the number of bones in a Golaem rig.  This is important when the rig fails because the number of joints differs in the GCHA file list.
		getRoot = cmds.textField('rootJoint', q=True, tx=True)
		root = self.selectRoot(getRoot)
		cmds.select(hi=True)
		bones = cmds.ls(sl=True)
		count = 0
		for bone in bones:
			if cmds.nodeType(bone) == 'joint':
				count += 1
		cmds.confirmDialog(m='Total Golaem Rig bones: %i' % count)


	def attachBones(self, *args):
		#This will parent constrain a golaem rig to a master rig for later animation baking.
		rigCorrect = cmds.confirmDialog(m='For Golaem to function properly, the Golaem Rig, must have a different name than the parent rig.  Currently, this setup is using the following name convention:\nMain Rig = "root"\nGolaem Rig = "root_golaem"\n\nMain Rig = "hips_bind"\nGolaem Rig = "hips_golaem".\n\nIs your Golaem Rig following this format?', b=['Yes, let\'s go!', 'Nope, let me fix that'], cb='Nope, let me fix that', db='Yes, let\'s go!', t='Is the Rig Named Correctly?')
		if rigCorrect == 'Yes, let\'s go!':
			golaemRoot = self.selectRoot(cmds.textField('rootJoint', q=True, tx=True))
			cmds.select(hi=True)
			golaemSkeleton = cmds.ls(sl=True)
			badConnections = []
			for thisJoint in golaemSkeleton:
				getBaseName = thisJoint.split('_golaem')[0]
				if '_jnt' not in getBaseName and 'root' not in getBaseName:
					newName = '%s_bind' % getBaseName
				elif 'root' in getBaseName:
					newName = 'root'
				else:
					newName = getBaseName
				parentJoint = self.findParentJoint(newName)
				jointsConnected = self.connectTheseJoints(parentJoint, thisJoint)
				if jointsConnected == False:
					badConnections.append('%s to %s' % (thisJoint, parentJoint))
		cmds.select(golaemRoot)
		if badConnections != []:
			badList = 'THE FOLLOWING CONNECTIONS COULD NOT BE MADE!\n'
			for bad in badConnections:
				badList = badList + '\n%s' % bad
			cmds.confirmDialog(m=badList, b='Gotcha')


	def findParentJoint(self, jointName):
		cmds.namespace(set=':')
		getNamespaces = cmds.namespaceInfo(lon=True, r=True)
		try:
			cmds.select(jointName, r=True)
			foundJoint = cmds.ls(sl=True)[0]
		except:
			for ns in getNamespaces:
				cmds.namespace(set=ns)
				try:
					cmds.select('%s:%s' % (ns, jointName), r=True)
					foundJoint = cmds.ls(sl=True)[0]
					break
				except:
					foundJoint = ''
				cmds.namespace(set=':')
		
		if foundJoint != '':
			return foundJoint

	#Attempt to parent constrain 2 matching joints
	def connectTheseJoints(self, parentJoint, childJoint):
		try:
			cmds.select(parentJoint, r=True)
			cmds.select(childJoint, tgl=True)
			cmds.parentConstraint(parentJoint, childJoint)
			print '%s was successfully connected to %s' % (childJoint, parentJoint)
			status = True
			return status
		except:
			print '%s failed to connect or find %s' % (childJoint, parentJoint)
			status = False
			return status
			

run = golaem_MotionExporter()
run.ui()