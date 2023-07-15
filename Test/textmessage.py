# we import the Twilio client from the dependency we just installed
from twilio.rest import Client

# the following line needs your Twilio Account SID and Auth Token
client = Client("AC31efad981fbced849f8c8aee26aacea0", "7e64fef44079c2a9682c81ae5f2f8b4a")

# change the "from_" number to your Twilio number and the "to" number
# to the phone number you signed up for Twilio with, or upgrade your
# account to send SMS to any phone number
client.messages.create(to="+8615256215220",
                       from_="+8615256215220",
                       body="Hello from Python!")