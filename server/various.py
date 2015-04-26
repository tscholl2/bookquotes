import threading

class SafeList:
	def __init__(self):
		self.lock = threading.Lock()
		self.list = []
	
	def append(self,item):
		with self.lock:
			return self.list.append(item)
	
	def remove(self,item):
		with self.lock:
			return self.list.remove(item)
	
	#if you want to go through the list and don't allow anyeone else to do anything
	def lockedIter(self):
		with self.lock:
			for item in self.list:
				yield item
	
	#if you want to add something and do something with the lock still
	def appendPlus(self,item,callback,**kwargs):
		with self.lock:
			self.list.append(item)
			callback(**kwargs)
	
	def __iter__(self):
		with self.lock:
			new_list = [item for item in self.list]
			return new_list.__iter__()
			
	def __len__(self):
		with self.lock:
			return len(self.list)