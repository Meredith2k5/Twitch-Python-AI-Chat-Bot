import irc.client
import random
import os
import json
import threading
import time
import cohere

########## Configuration ##########


# Twitch IRC server and port, do not change unless you know what you're doing
SERVER = "irc.chat.twitch.tv"
PORT = 6667 
# Your Twitch username and OAuth token, do not share this with anyone or show on stream
NICKNAME = "Tha_Dank_Joker"
# Your Twitch OAuth token here
TOKEN = "oauth:oauthhere"
#Channels you want the bot to be in
CHANNELS = ["#tha_dank_knight", "#djmerewolf", "#meredj"]
# Personality to use for chatbot, RPGGAME can be used as a secondary personality if you prefer
PERSONALITY = "Roleplay as Billy Butcher from The Boys. You have a very dry humour and love to pop a joke or pun whenever possible. You love drum & bass, DJing, gameing, metal gear solid, final fantasy 7, terrible jokes and puns, Tifa Lockheart, hardcore game mods and all things British. Use lots of emojis especially ' GlitchCat ', ' Kreygasm ' and ' Kappa '. ALWAYS reply in less than 300 characters and NEVER start a message with '/'. Now continue this conversation :" 
RPGGAME = "You are a dungeonmaster for a 18+ twitch chat based DnD game. Make the game interesting and include such topics as DJing, raving, Final Fantasy 7 8 or 9, Metal Gear Solid, German things, British things. Do not reply or make a move for the character as you are the dungeonmaster. Give things for people to roll for. Reply in less than 300 characters and use plenty of emojis such as ' Kappa ', ' Kreygasm ', ' LUL ', ' CoolCat '. Now start or continue this DnD game :"
# Cohere API key, do not share this with anyone or show on stream
COHERE_API_KEY = "CohereAPIkeyhere" # Cohere API key
# List of prefixes to trigger the chatbot
PREFIXES = ["chat", "ai ", "chatbot", "@botname", "!botname", "botname"]  
PREFIXES2= ["rpg", "!rpg", "roleplay", "role play", "role-play", "rpg ", "rpg", "roleplay ", "role play ", "role-play "] 
# Temperature for chatbot response. 0.3 is a good starting point, lower values are more conservative but accurate and higher values are more creative but less accurate
TEMPERATURE = 0.2
# Conversation ID for chatbot to remember context, memory will retain for future conversations. Change this up if the answers are getting stale
CONVERSATION_ID = "Con1" 
RPG_ID = "RPG1"
# Define the messages to send when joining the channel, leave blank for no message
INTROMESSAGE = " Wanna ask the me a question? Reply to me or type ai or chat at the start of your sentance. We also have a new RPG game! Start your sentance with RPG or roleplay to play!  "
########## END OF CONFIGURATION ############


#Connect to Cohere via your API key
co = cohere.Client(
    api_key=COHERE_API_KEY,
)



# Define names for later use

def on_connect(connection, event):
    print("Connected to server.")
    for channel in CHANNELS:
        connection.join(channel)
        connection.privmsg(channel, INTROMESSAGE)

def on_join(connection, event):
    print(f"Joined {event.target}")
    
def on_disconnect(connection, event):
    print("Disconnected from server.")

def on_pubmsg(connection, event):
    user = event.source.nick
    channel = event.target
    message = event.arguments[0]




    # Commands handling

    if any(message.lower().startswith(prefix) for prefix in PREFIXES):
        response = co.chat(
            message=PERSONALITY + message,
            model="command-r-plus",
            temperature=TEMPERATURE,
            conversation_id=CONVERSATION_ID,
            #frequency_penalty=0.30,    
            presence_penalty=0.6 
            
        )
        response_text = response.text.replace('\n', '. ').replace('\r', '. ')
        print(response_text)
        
        # Split response_text into multiple parts of 250 characters each
        parts = [response_text[i:i+250] for i in range(0, len(response_text), 250)]
        
        # Send each part as a separate message
        for i, part in enumerate(parts):
            time.sleep(5)
            connection.privmsg(channel, f"{part}")

    elif any(message.lower().startswith(prefix) for prefix in PREFIXES2):
        response = co.chat(
            message=RPGGAME + message,
            model="command-r-plus",
            temperature=TEMPERATURE,
            conversation_id=RPG_ID,
            #frequency_penalty=0.30,
            presence_penalty=0.9 
            
        )
        response_text = response.text.replace('\n', '. ').replace('\r', '. ')
        print(response_text)
        
        # Split response_text into multiple parts of 250 characters each
        parts = [response_text[i:i+250] for i in range(0, len(response_text), 250)]
        
        # Send each part as a separate message, wait 5 seconds between each
        for i, part in enumerate(parts):
            time.sleep(5)
            connection.privmsg(channel, f"{part}")

# Main loop 
def main():
    client = irc.client.Reactor()
    try:
        server = client.server()
        server.connect(SERVER, PORT, NICKNAME, TOKEN)
        server.add_global_handler("welcome", on_connect)
        server.add_global_handler("join", on_join)
        server.add_global_handler("disconnect", on_disconnect)
        server.add_global_handler("pubmsg", on_pubmsg)
        
        client.process_forever()
    except irc.client.ServerConnectionError as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    main()
