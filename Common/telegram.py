#This module is used for telegram reporting
#you can use if for checking whether automated batch job is well done 


chat_id = '562514449:AAFeCYAM77N_xe220ZE7Ee3MCx0TymUjD80' #Bot ID
bot = telepot.Bot(chat_id) #Activate
bot.getUpdates() 
my_id = '455038539' #My ID

msg = "Hello World!"
bot.sendMessage(my_id, msg) #Messaging