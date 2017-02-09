#!/usr/bin/env python
##
## $Id: iosswitch.py,v 1.3 2016/03/28 15:07:15 weiwang Exp $
##
## This program is licensed under the GPL v3.0, which is found at the URL below:
##	http://opensource.org/licenses/gpl-3.0.html

import re, time
import device

import re
xpat = re.compile('/no\s+such\s/', re.I)


class IOSSwitch(device.SNMPDevice):
	'''Class implementing a Cisco IOS switch that uses CISCO-CONFIG-COPY-MIB to save configuration.
	'''
	def set_int (xoid, xvalue):
		return self.set(xoid, "i", xvalue)


	def save_config():
		'''
		'''
		xrow = rand(1, 100)

		## CISCO-CONFIG-COPY-MIB::ccCopySourceFileType.15
		self.set_int(".1.3.6.1.4.1.9.9.96.1.1.1.1.3.xrow", "4") ## set source as running
		## CISCO-CONFIG-COPY-MIB::ccCopyDestFileType.15
		self.set_int(".1.3.6.1.4.1.9.9.96.1.1.1.1.4.xrow", "3") ## set dest as startup
		## CISCO-CONFIG-COPY-MIB::ccCopyEntryRowStatus.15
		self.set_int(".1.3.6.1.4.1.9.9.96.1.1.1.1.14.xrow", "1") ## set transfer to active

		xsuccess = false
		for xix in range(0, 9): # Number of retries
			## check if finished
			## CISCO-CONFIG-COPY-MIB::ccCopyState.15
			xtransferflag = self.get(".1.3.6.1.4.1.9.9.96.1.1.1.1.10.xrow").split(' ')[:-1]
			if xtransferflag == 'successful' or xtransferflag == '3':
				xsuccess = true
				break
			if xtransferflag == 'failed' or xtransferflag == '4':
				break
			time.sleep(1)

		## CISCO-CONFIG-COPY-MIB::ccCopyEntryRowStatus.15
		self.set_int(".1.3.6.1.4.1.9.9.96.1.1.1.1.14.xrow", "6") ## destroy entry
		return xsuccess

	def get_model ():
		'''
		'''
		if not getattr('mode', self):
			#		CISCO-STACK-MIB::chassisModel
			xmodel = self.get('.1.3.6.1.4.1.9.5.1.2.16.0')
			if xpat.match(xmodel): ## ENTITY-MIB::entPhysicalModelName
				xmodel = self.get(".1.3.6.1.2.1.47.1.1.1.1.13.1")
				if xpat.match(xmodel):
					return ''
			self.model = xmodel
		return self.model
