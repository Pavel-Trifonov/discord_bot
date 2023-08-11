import pymysql
import discord
import json
import requests
import random
from database import host, user, password, db


file = open('config.json', 'r')
config = json.load(file)

class Db_connect:
    def get_answers(self):
        with connection.cursor() as cursor:
            cursor.execute("SELECT answers FROM info")
            full_list = cursor.fetchall()
            answers = []
            for slovar in full_list:
                for k, v in slovar.items():
                    answers.append(v)
        return answers
    def add_answers(new_answer):
        with connection.cursor() as cursor:
            insert_in = """INSERT INTO info (answers) VALUES (%s) """
            cursor.execute(insert_in, new_answer)
            connection.commit()
            Singleton().refresh_answers()




    def delete_answers(index_new_answer):
        with connection.cursor() as cursor:
            delete_from = """DELETE FROM info WHERE id = %s """
            cursor.execute(delete_from, (index_new_answer, ))
            connection.commit()
            Singleton().refresh_answers()





class Singleton:
    __instance = None

    answers = []

    def __new__(cls, *args, **kwargs):
        if cls.__instance is not None:
            return cls.__instance
        cls.__instance = super(Singleton, cls).__new__(cls)
        return cls.__instance

    def get_answers(self):
        return self.answers
    def refresh_answers(self):
        self.answers = Db_connect().get_answers()
        return self.answers


try:
    connection = pymysql.connect(
        host=host,
        port=3306,
        user=user,
        password=password,
        database=db,
        cursorclass=pymysql.cursors.DictCursor
    )
    print("Законектилось")

except Exception as ex:
    print("Не законектилось")
    print(ex)


Singleton().refresh_answers()




class AnswersService:


    def get_quote(self):
        response = requests.get("https://zenquotes.io/api/random")
        json_data = json.loads(response.text)
        qoute = json_data[0]['q'] + " -" + json_data[0]['a']
        return (qoute)





intents = discord.Intents().all()
client = discord.Client(intents=intents)

words = ["хуево", "плохо", "упал", "разбил",
         "грусно", "грустно", "скучно"] 


@client.event
async def on_ready():
    print(f'на месте')




@client.event
async def on_message(message):
    if message.author == client.user:
        return

    msg = message.content

    if msg.startswith('/цитата'):
        quote = AnswersService().get_quote()
        await message.channel.send(f'{message.author.mention}{quote}')


    if any(word in msg for word in words):
        await message.channel.send(random.choice(Singleton().get_answers()))


    if msg.startswith("/добавить"):
        answer_message = msg.split("/добавить ", 1)[1]
        Db_connect.add_answers(answer_message)
        await message.channel.send("Добавлен новый ответ.")


    if msg.startswith("/удалить"):
        index_text = int(msg.split("/удалить ", 1)[1])
        Db_connect.delete_answers(index_text)
        await message.channel.send("Удалено")


client.run(config['token'])
