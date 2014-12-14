import sys
from twilio.rest import TwilioRestClient
from auths import *
from sys import stdin
from time import sleep
from os import fork
from os import wait
from random import *
numbers = ["+14155287986","+14159309679","+14159309577","+14154948207","+14159309709","+14154948205","+14159309382","+14159309616","+14159309327"]
batches = []
for a in numbers[0:]:
	batches.append([])


def main(argv):
#	f = open(argv,"r")
	f = stdin
	for chunk in f.read().split("###\n"):
		chunks = chunk.split("\n")
		phone = chunks[0]
		if phone == "":
			break
		message = ""
		for line in chunks[1:]:
			message += line + "\n"
		seed(phone)
		idx = randint(0, len(numbers) - 1)
		struct = {} 
		struct["to"] = phone
		struct["body"] = message
#		print "idx = ", idx, "\n"
		batches[idx].append(struct)
		
	print "len(batches) = ", len(batches);

	for i in range(0, len(batches)):
		status = fork()
		if status > 0:
			number = numbers[i]
			print "len(batches[", i, "]) = ", len(batches[i]),"\n";
			for j in range(0, len(batches[i])):
				phone = batches[i][j]["to"]
				message = batches[i][j]["body"]
				print "to=", phone, " from_=", number, " body=", message, "\n";
				status2 = fork()
				if status2 > 0:
					client=TwilioRestClient(ACCOUNT_SID,AUTH_TOKEN)
					client.messages.create(
						to=phone,
						from_=number,
						body=message,
					)
					exit(0);
				wait()
			sleep(3)
			exit(0)

	sleep(30)

main(sys.argv[1])
