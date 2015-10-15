# File name: infection.py
# Author: Henry Zhou
# Date created: 10/9/15
# Date last modified: 10/14/15
# Python Version: 2.7.6

# Description - userGraph is a class that can emulate an infection.
#               userGraph has a bunch of goodies that can track
#               analytics such as average users infected per 
#               wave, number users infected by previous wave
#               current number of users current wave is infecting
#               number of users a user infects, etc. 

# Begin code
import sys
import argparse
from Queue import Queue
from sets import Set

############################################################
class userGraph():
	def __init__(self):
		self.users                            = dict() # key = user #
	                                                   # value = (coaches, students, Bool infected, int user_id)
		
		self.total_users                      = 0      #count of total users                              
		self.total_infected                   = 0      #total infected users - incremented by wave
		self.currently_infected               = 0      #currently infected users - incremented by each infection 
		self.previous_wave_users_count        = 0      #tracks count of prev waves users                   
		self.current_wave_infected_user_count = 0      #number of users infected by prev wave
		self.current_user_infected_user_count = 0      #number of users current user will infect                          
		self.current_wave                     = 1      #infection waves 1 indexed     
		self.limit                            = 0      #tracks limit if set
		self.infected                         = Set() #dictionary of infected users - prevents cycles in traversal
		self.infected_by_user                 = dict() #dictionary of students a user infected  

	############################################################
	def loadUsers(self, user_data):
		target = open(user_data, 'r')
		users = target.readlines()

		for ii in range(len(users)):
			students = users[ii].split('=')
			current_user = int(students[0])
			students = students[1].split('\n')
			students = map( int, students[0].split(','))
			if students[0] != -1:
				#add currents users students in self.users
				if self.users.has_key(current_user):
					for student in students:        
						self.users[current_user][1].add(student)
				else:
					self.users[current_user] = [ set(), set(students), False , ii]
					self.total_users += 1  #current coach not in users yet
				#add current user as coach of students
				for student in students:
					if self.users.has_key(student):
						self.users[student][0].add(current_user)  #currently only adding students
					else: 
						self.users[student] = [ set(), set(), False, student ]
						self.users[student][0].add(current_user)
						self.total_users += 1
			else:
				#-1 indicates user has no students or coaches
				if not self.users.has_key(current_user):
					self.users[current_user] = [ set(), set(), False, ii ]
					self.total_users += 1 

	############################################################
	def printUsers(self):
		print self.total_users
		for user in self.users:
			print "User: %s" % user
			print "Coaches: ", self.users[user][0]
			print "Students ", self.users[user][1]
			print "Infected: ", self.users[user][2]
	############################################################
	def setLimit(self, limit):
		self.limit = limit

	############################################################
	def evaluateNextUser(self, next_wave_queue, current_user, limited = False):
		self.total_infected += self.current_user_infected_user_count
		if limited:
			if self.total_infected > self.limit:
				print ""
				print "~~~~~~~~~~~Limit breached~~~~~~~~~~~"
				print "Current user:" , current_user, "will infect" ,  self.current_user_infected_user_count , "users"
				print "Total infected will increment to", self.total_infected , ", which will exceed limit:" \
				       , self.limit , "by" , self.total_infected - self.limit , "users"
				#revoke infection
				self.total_infected -= self.current_user_infected_user_count
				self.current_wave -= 1
				return False	
		if self.current_user_infected_user_count > 0:
			print "Total infected by user" , current_user , "               :" , self.current_user_infected_user_count
			#self.previous_wave_users_count += self.current_user_infected_user_count
			print "Total users currently infected          :" , self.total_infected
			self.current_user_infected_user_count = 0
		return True

	############################################################
	def evaluateNextWave(self, next_wave_queue, limited = False):
		#Commented out code is behavior available if one wanted to limit by next wave instead
		#if limited:
		#	if self.total_infected + self.current_wave_infected_user_count  > self.limit:  	#of next user
		#		print "Limit breached"
		#		print "Current Wave:" , self.current_wave , "infected" ,  self.current_wave_infected_user_count , "users"
		#		#revoke infection
		#		self.total_infected -= self.current_wave_infected_user_count
		#		self.current_wave -= 1
		#		return False	
		# Don't count as a wave if at leaf wave
		if not next_wave_queue.empty(): 
			print "WAVE COMPLETE: Total infected by wave" , self.current_wave , ":" \
			       , self.current_wave_infected_user_count
		self.previous_wave_users_count = self.current_wave_infected_user_count 
		#print "Total users currently infected          :" , self.total_infected
		print ""
		if not next_wave_queue.empty():
			self.current_wave += 1
		if self.current_wave_infected_user_count == 0:  #Found leaf (last) wave
			self.current_wave -= 1
		self.current_wave_infected_user_count = 0
		return True
	############################################################	
	def infectInit(self, patient_zero, next_wave_queue, limited = False):
		print "~~~~~~~Infection point: " , patient_zero , "~~~~~~~~"
		print ""

		self.infected.add(patient_zero)
		self.currently_infected += 1

		for student in self.users[patient_zero][1]:
			if student not in self.infected:	#in case user self coaches
				next_wave_queue.put(student)
				self.infected.add(student)
				self.currently_infected += 1
				self.previous_wave_users_count += 1 # number of people infected by patient zero
		for coach in self.users[patient_zero][0]:
			if coach not in self.infected:
				next_wave_queue.put(coach)
				self.infected.add(coach)
				self.currently_infected += 1
				self.previous_wave_users_count += 1

		if limited:
			if self.currently_infected > self.limit:
				print ""
				print "~~~~~~~~~~Limit breached~~~~~~~~~~~"
				print "Current user:" , patient_zero, "will infect" ,  self.currently_infected - 1 , "users"
				print "Total infected will increment to", self.currently_infected , ", which will exceed limit:" , self.limit , "by" , \
				       self.currently_infected - self.limit , "users"
				self.current_wave -= 1
				self.total_infected = 1
				self.printInfectionResults(patient_zero)
				return False


		print "~~~~~~~~~~START INFECTION~~~~~~~~~~"

		print "Total infected by infection point" , patient_zero , "    :" , self.currently_infected - 1
		print "Total users currently infected          :" , self.currently_infected 
		print "WAVE COMPLETE: Total infected by wave" , self.current_wave , ":" , self.currently_infected - 1
		self.total_infected += self.currently_infected
		if self.currently_infected > 1:  #Corner case: patient zero infects no one
			self.current_wave += 1
		return True
		
	############################################################
	def infect(self, patient_zero, limited = False):
		"""
		Use BFS traversal to infect other users
		Keep track of users infected per infection wave
		Print out total infected after each round
		Print out data summary after infection ends 
		"""

		if not self.users.has_key(patient_zero):
			print "ERROR Infection Point User:" , patient_zero , "does not exist!"
			return

		print "WAVE TRACKING INITIALIZED"
		self.current_wave = 1
		next_wave_queue = Queue()
		self.users[patient_zero][2] = True		
		#initialize infection - take care of initial wave
		if not self.infectInit(patient_zero, next_wave_queue, limited):
			return

		print ""
		while not next_wave_queue.empty():
			#dequeue infected user
			current_user = next_wave_queue.get()
			self.current_user_infected_users = 0
			#infect
			self.users[current_user][2] = True #set infected to True
			#queue current_user's students if not infected yet
			for student in self.users[current_user][1]:
				if student not in self.infected:
					self.infected.add(student)
					next_wave_queue.put(student)
					self.current_wave_infected_user_count += 1
					self.current_user_infected_user_count += 1
					self.currently_infected += 1
			#queue current_user's coaches if not infected yet
			for coach in self.users[current_user][0]:
				#print current_user
				#print coach
				#print coach in self.infected
				if coach not in self.infected:
					self.infected.add(coach)
					next_wave_queue.put(coach)
					self.current_wave_infected_user_count += 1
					self.current_user_infected_user_count += 1
					self.currently_infected += 1
			
			self.previous_wave_users_count -= 1
			if not self.evaluateNextUser(next_wave_queue, current_user, limited):
					break
			if self.previous_wave_users_count == 0: #evaluate previous waves
				self.evaluateNextWave(next_wave_queue, limited)

		self.printInfectionResults(patient_zero)

	############################################################		
	def printInfectionResults(self, patient_zero):
		print ""
		print "~~~~~~~~~INFECTION COMPLETE~~~~~~~~~"
		print ""
		print "~~~~~~~~~Infection Results~~~~~~~~~~"
		print "Infection started by user      :" , patient_zero 
		print "Total completed waves          :" , self.current_wave
		print "Total users infected           :" , self.total_infected
		print "Uninfected users               :" , self.total_users - self.total_infected
		print "Total users                    :" , self.total_users
		if self.current_wave != 0:            
			if self.current_wave == 1:  
				self.total_infected -= 1          #Ignore patient zero 
			print "Average users infected per wave:" , float(self.total_infected / (self.current_wave) )
		else:
			print "Users Infection point infected :" , self.total_infected - 1
		#print "Average users infected per wave:"
		#print "Max users infected of every wave:"	

	############################################################
	def printCurrentUserGraphInfo():
		"""
		Print the status of the users in the graph
		Useful for examining state of users at various points
		"""
		print "Total Users              " , self.total_users                              
		print "Total Users infected     " , self.total_infected  
		print "Users Currently Infected " , self.currently_infected                    
		print "Current Infection Wave   " , self.current_wave   		
		print "Current Wave: " , self.current_wave , "has infected" , "self.current_wave_infected_user_count" , "so far"
	############################################################
	def resetInfection():
		self.total_infected                   = 0
		self.currently_infected               = 0 
		self.previous_wave_users_count        = 0                
		self.current_wave_infected_user_count = 0
		self.current_user_infected_user_count = 0                         
		self.current_wave                     = 1      #infection waves 1 indexed     
		self.infected                         = Set()

############################################################
def main():
	parser = argparse.ArgumentParser(description='Emulate infection of users and collect data regarding the ')
	parser.add_argument('user_data', help='File containing user relationships - see readme for data formatting')
	parser.add_argument('infect_user', type=int, help='User to start infection from')
	parser.add_argument('--limit', nargs='?', type=int, help='Number of users to limit in infection. Halts infection if ' 
		                "number of infections from current user will make total infections exceed limit")
	args = parser.parse_args()

	graph = userGraph()
	graph.loadUsers(args.user_data)

	if args.limit == 0:
		print "ERROR: Limit must be whole number greater than 0"
		return

	patient_zero = int(args.infect_user)

	if args.limit:
		graph.setLimit(args.limit)
		graph.infect(patient_zero, limited = True)
	else:
		graph.infect(patient_zero)


############################################################
main()