###############################################################################
#                       README for infection.py                               #
#                       Written by Henry Zhou                                 #
#                       Date: 10/15/15                                        #      
###############################################################################


Interface usage:

usage: infection.py [-h] [--limit [LIMIT]] user_data infect_user

Emulate infection of users and collect data regarding the
positional arguments:

  user_data        File containing user relationships - see readme for data
                   formatting

  infect_user      User to start infection from

optional arguments:
  -h, --help       show this help message and exit
  
  --limit [LIMIT]  Number of users to limit in infection. Halts infection if
                   number of infections from current user will make total
                   infections exceed limit



Example data and tests to run:
###############################################################################
classroom.txt:
	Represents a classroom of 30 students and 1 teacher where one teacher coaches 
	the rest of the students.

	Tests:
	$ python infection.py classroom.txt 0
		Infect teacher - All students infected in first wave
	
	$ python infection.py classroom.txt 30
		Infect a student. Student infects teacher in first wave, and teacher
		infects remaining students in second wave.

	$ python infection.py classroom.txt 0 --limit 1 
		Limit infection point to initial user

	$ python infection.py classroom.txt 0 --limit 30 
		Limit infection due to teacher infecting 1 too many students than limit

	$ python infection.py classroom.txt  0 --limit 31
		Ensure that limit is inclusive
###############################################################################
4classrooms.txt:
	Represents 4 different classrooms of 30 students and one teacher. 
	All the teachers are coached by one central user.

	$ python infection.py 4classrooms.txt 0
		Check to see that BFS is functioning properly. Infection should spread from
		central user, to 4 teachers, to each teacher's students in 2 waves.
	$ python infection.py 4classrooms.txt 0 --limit 35
		Withhold infection to all the teachers and one class
	$ python infection.py 4classrooms.txt 124 
		Start infection from a student in one classroom, infect that classroom's 
		teacher, the teacher infects the rest of the students and the head teacher, 
		who then infects the other teachers, and lastly the other 3 classrooms. 
		Expect 4 waves.
###############################################################################
2_separate_classrooms:
	Two discrete classrooms of 30 students and 1 teacher. Teacher coaches all 
	the students

	$ python infection.py 2_separate_classrooms.txt 31
	  python infection.py 2_separate_classrooms.txt 0

	  Make sure the infections stay separate. 
###############################################################################
series.txt:
	101 users where each user coaches subsequent next user. 

	$ python infection.py series.txt 0
		Sanity check to see that waves and infections are working properly. 
		Expect only 1 user to be infected per wave. Check if coaches are 
		infecting students properly

	$ python infection.py series.txt 100
		Same as previous test, check if students are infecting coaches properly.

	$ python infection.py series.txt 50
		Expect half as many waves and double the infection rate since infection 
		starts from middle user.

	$ python infection.py series.txt 50 --limit 10
		Ensure that infection stops halfway in wave 5 and revokes wave 5's 
		infections.
###############################################################################
pyramid.txt:
	User data where the current user coaches the previous user's students as 
	well as the subsequent user.
	ex: user 5 coaches users 1,2,3,4,5 from previous and user 6. Checks 
	for corner case where user coaches itself

	$ python infection.py pyramid.txt 0
		Check that first infection infects only user 1, and second wave consists 
		of user 1 infectings users 2 through 98 due to student to coach transmission. 
		Also check that user 99 is infected only by user 98.

	$ python infection.py pyramid.txt 99
		Vice versa test of previous test. 
	
	$ python infection.py pyramid.txt range(1 to 98)
		Ensures that if infection starts at a user that infects itself, it 
		doesn't reinfect itself
###############################################################################
pairs.txt:
	5 pairs of coach/student user pairs. 

	$ python infection.py pairs.txt range(0 to 9)
		Isolated way to test student/coach infection behavior only between 
		connected users.
################################################################################
singles.txt
	5 singleton users. Checks corner case for patient zero having no relations

	$ python infection.py singles.txt range(0 to 4)
		Check to see that only initial user is infected and no
		other users are infected.


