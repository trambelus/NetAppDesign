# NB: this was written for Python 3.
# Might take a little tweaking for 2.
import time
from threading import Thread

FLASH_DELAY = 1 # flash delay in seconds

# This function will be run in the thread.
def flash(is_active):
	c = 0
	while True:
		c = 1-c
		if len(is_active) == 0: # empty list means exit, for our purposes
			break # jump out of this infinite while loop and exit this thread
		if is_active[0]:
			if c:
				pass # turn LED on here
			else:
				pass # turn LED off here
			print("Flash!") # so you can see what's going on here in this example

		time.sleep(FLASH_DELAY)

is_active = [False] # It's a list because it'll get passed to the thread by reference this way, not by value.
# If we just passed False as an argument, changing the local variable here wouldn't change the thread's variable.
# There are many ways to implement this, but I like this list-singleton method. It's simple.
Thread(target=flash, args=(is_active,)).start() # start the thread
# sorry about that messy syntax, can't be helped
while True:
	command = raw_input() # Just for this example, typing "go" enables the flashing and "stop" disables it.
	if command == "go":
		is_active[0] = True # Turns the flashing on
	if command == "stop":
		is_active[0] = False # Turns the flashing off
	if command == "exit":
		is_active.remove(0) # Clear the list. This will signal the thread to break and exit.
		break # jump out of this infinite while loop and exit