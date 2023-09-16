import pymysql
import discord
import json
import requests
import random
import redis
from database import host, user, password, db









redis_host = "localhost"
redis_port = 6379








file = open('config.json', 'r')
config = json.load(file)


#Создаем класс, работающий с дб
class Db_connect:

    #Получаем из дб начальный список ответов и заносим его в редис кеш
    def get_answers(self):
        with connection.cursor() as cursor:
            cursor.execute("SELECT answers FROM info")
            full_list = cursor.fetchall()
            answers = []
            for slovar in full_list:
                for k, v in slovar.items():
                    answers.append(v)

        redis_client = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=0)
        redis_client.set("answers", json.dumps(answers))
        answers_cash = redis_client.get("answers")
        redis_client.close()

        return json.loads(answers_cash)


    #Добовляем новый ответ пользователя в дб и обновляем текущий список
    def add_answers(new_answer):
        with connection.cursor() as cursor:
            insert_in = """INSERT INTO info (answers) VALUES (%s) """
            cursor.execute(insert_in, new_answer)
            connection.commit()
            Singleton().refresh_answers()



    #Удаляем выбранный пользователем ответ из дб и обновляем текущий список
    def delete_answers(index_new_answer):
        with connection.cursor() as cursor:
            delete_from = """DELETE FROM info WHERE id = %s """
            cursor.execute(delete_from, (index_new_answer, ))
            connection.commit()
            Singleton().refresh_answers()




#Создаем класс синглтона отвечающий за то что бы список был всегда один и тот же обьект и обновлялся при изменении
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

#Конектимся к дб
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

#Инициализируем синглтон и тем самым получаем начальный список с которым работаем
Singleton().refresh_answers()



#Класс для различных активностей через приложения
class AnswersService:

    #Апи на рандомные цитаты
    def get_quote(self):
        response = requests.get("https://zenquotes.io/api/random")
        json_data = json.loads(response.text)
        qoute = json_data[0]['q'] + " -" + json_data[0]['a']
        return (qoute)





intents = discord.Intents().all()
client = discord.Client(intents=intents)

words = ["плохо", "упал", "разбил",
         "грусно", "грустно", "скучно"] 


@client.event
async def on_ready():
    print(f'на месте')



#Класс для активностей связанных с сообщениями пользователей
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    msg = message.content
    #Запрос по апи цитат
    if msg.startswith('/цитата'):
        quote = AnswersService().get_quote()
        await message.channel.send(f'{message.author.mention}{quote}')

    #Проверка списка на совпадение и возвращение пользователю рандомного ответа из списка в кеше
    if any(word in msg for word in words):
        await message.channel.send(random.choice(Singleton().get_answers()))

    #Добавление пользователем ответа в дб
    if msg.startswith("/добавить"):
        answer_message = msg.split("/добавить ", 1)[1]
        Db_connect.add_answers(answer_message)
        await message.channel.send("Добавлен новый ответ.")

    #Удаление пользователем ответа из дб
    if msg.startswith("/удалить"):
        index_text = int(msg.split("/удалить ", 1)[1])
        Db_connect.delete_answers(index_text)
        await message.channel.send("Удалено")

#Токен - персональный ключ в дискорде(у меня находится в отдельном закрытом файле)
client.run(config['token'])
