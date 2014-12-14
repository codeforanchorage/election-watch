# This is the script that handles the text messaging

import sys
from twilio.rest import TwilioRestClient
from auths import *
from sys import stdin
from time import sleep
from os import fork
from os import wait
from random import *
#numbers = ["+14155287986","+14159309679","+14159309577","+14154948207","+14159309709","+14154948205","+14159309382","+14159309616","+14159309327"]
numbers = ["add your numbers here"];
batches = []
for a in numbers[0:]:
	batches.append([])


def main(argv):
	# We could read from a file, but we're just using stdin....
#	f = open(argv,"r")
	f = stdin
	# Read in the file and split by "###"
	# Format:
	# 	phone number
	#	text message contents
	#	characters "###"
	for chunk in f.read().split("###\n"):
		chunks = chunk.split("\n")
		phone = chunks[0]
		if phone == "":
			break
		message = ""
		for line in chunks[1:]:
			message += line + "\n"
		# To ensure consistency in the origin phone number
		# when sending texts...
		# First, seed a random number generator with the dest phone num
		seed(phone)
		# Then, generate a random integer to select which number to use
		idx = randint(0, len(numbers) - 1)

		# Now, prepare data for a Twilio call
		struct = {} 
		struct["to"] = phone
		struct["body"] = message
#		print "idx = ", idx, "\n"

		# Finally, stick the data into the batch for the origin phone
		# number
		batches[idx].append(struct)
		
	print "len(batches) = ", len(batches);

	# Now that all the messages have been processed, for each origin
	# phone number...
	for i in range(0, len(batches)):
		# Start a new process for the phone number
		status = fork()
		if status > 0:
			number = numbers[i]
			print "len(batches[", i, "]) = ", len(batches[i]),"\n";
			for j in range(0, len(batches[i])):
				phone = batches[i][j]["to"]
				message = batches[i][j]["body"]
				print "to=", phone, " from_=", number, " body=", message, "\n";
				# To avoid errors that may crash the system,
				# the actual API call is made in a separate
				# process.
				#
				# TODO: Modify to use exception handling
				status2 = fork()
				if status2 > 0:
					# Connect to Twilio
					client=TwilioRestClient(ACCOUNT_SID,AUTH_TOKEN)
					# Send the text
					client.messages.create(
						to=phone,
						from_=number,
						body=message,
					)
					exit(0);
				# Reap excess zombie processes
				wait()
			sleep(3)
			exit(0)

	sleep(30)

main(sys.argv[1])
