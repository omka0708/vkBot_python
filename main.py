# -*- coding: utf-8 -*-
import csv
import vk_api
from vk_api import VkUpload
import requests
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
from datetime import datetime
from random import randint

with open("C:\\Users\\mcsca\\token.txt", "r") as f:
    vk_session = vk_api.VkApi(
        token=f.readline())
longpoll = VkBotLongPoll(vk_session, '197126596')
vk = vk_session.get_api()
category = ["id", "firstname", "lastname", "regisration data", "nickname", "section"]  # для работы с DictWriter
users = {}  # словарь с ключами - id пользователя, со значениями объектов User, поля которого выгружаются из users.csv


class MainMenu:
    def __init__(self, user_id):
        self.text = "Главное меню\n" \
                    "_________________\n" \
                    "1. Настройки\n" \
                    "2. Игры"
        self.direction = {"games": Games(user_id), "weather": Weather(), "settings": Settings(user_id)}
        self.user_id = user_id

    def handler(self, msg):
        answer = users[self.user_id].current_dir.text
        if str(msg).lower() == "1" or str(msg).lower() == "настройки":
            answer = self.direction['settings'].text
            users[self.user_id].current_dir = self.direction['settings']
            users[self.user_id].section = "settings"
        if str(msg).lower() == "2" or str(msg).lower() == "игры":
            answer = self.direction['games'].text
            users[self.user_id].current_dir = self.direction['games']
            users[self.user_id].section = "games"
        return answer


class Games:
    def __init__(self, user_id):
        self.text = "Игры\n" \
                    "_________________\n" \
                    "1. Русская рулетка\n" \
                    "2. Назад"
        self.direction = {"game_rus_roulette": game_RusRoulette(user_id)}
        self.user_id = user_id

    def handler(self, msg):
        answer = users[self.user_id].current_dir.text
        if str(msg).lower() == "1" or str(msg).lower() == "русская рулетка":
            answer = self.direction['game_rus_roulette'].text
            users[self.user_id].current_dir = self.direction['game_rus_roulette']
            users[self.user_id].section = "game_rus_roulette"
        elif str(msg).lower() == "2" or str(msg).lower() == "назад":
            users[self.user_id].current_dir = MainMenu(self.user_id)
            answer = users[self.user_id].current_dir.text
            users[self.user_id].section = "main_menu"
        return answer


class game_RusRoulette:
    def __init__(self, user_id):
        self.text = "Русская рулетка (максимум очков можно набрать - 8)\n" \
                    "_________________\n" \
                    "Для выстрела напишите \"Выстрел\"\n" \
                    "Для выхода из игры напишите \"Назад\""
        self.user_id = user_id
        self.score = 0
        self.shots_left = 8

    def handler(self, msg):
        if str(msg).lower() == "выстрел":
            temp = randint(0, self.shots_left)
            if temp == 0:
                answer = f"Конец игры!\nВаш счёт: {self.score}\n" \
                         f"_________________\n" \
                         "Для новой игры выстрелите снова\n" \
                         "Для выхода из игры напишите \"Назад\""
                self.score = 0
                self.shots_left = 8
            else:
                self.score += 1
                answer = f"Выстрел!\nВаш счёт: {self.score}"
            self.shots_left -= 1
        elif str(msg).lower() == "назад":
            users[self.user_id].current_dir = Games(self.user_id)
            answer = users[self.user_id].current_dir.text
            users[self.user_id].section = "games"
        else:
            answer = "Выстрелите снова или напишите \"Назад\" для выхода из игры"
        return answer


class Weather:
    pass


class Settings:
    def __init__(self, user_id):
        self.text = "Настройки\n" \
                    "_________________\n" \
                    "1. Сменить ник (<никнейм \'...\'> без кавычек)\n" \
                    "2. Узнать данные\n" \
                    "3. Назад"
        self.user_id = user_id

    def handler(self, msg):
        answer = users[self.user_id].current_dir.text
        print(msg)
        if str(msg[:8]) == "никнейм ":
            print(f"Пользователь {users[self.user_id].nickname} (id {self.user_id}) сменил ник на {msg[8:]}")
            users[self.user_id].change_nickname(msg[8:])
            answer = f"Вы сменили ник на \"{msg[8:]}\"!\n" + users[self.user_id].current_dir.text[10:]
        elif str(msg).lower() == "2" or str(msg).lower() == "узнать данные":
            print(f"Пользователь {users[self.user_id].nickname} (id {self.user_id}) узнает данные")
            answer = users[self.user_id].get_stats() + "\n" + users[self.user_id].current_dir.text[10:]
        elif str(msg).lower() == "3" or str(msg).lower() == "назад":
            users[self.user_id].current_dir = MainMenu(self.user_id)
            answer = users[self.user_id].current_dir.text
            users[self.user_id].section = "main_menu"
        else:
            print("cringe1")
        return answer


class User:
    def __init__(self, id_, firstname_, lastname_, registration_data_, nickname_, section_):
        self.id = id_
        self.firstname = firstname_
        self.lastname = lastname_
        self.registration_data = registration_data_
        self.nickname = nickname_
        self.section = section_
        if self.section == "main_menu":
            self.current_dir = MainMenu(self.id)
        elif self.section == "settings":
            self.current_dir = Settings(self.id)
        elif self.section == "games":
            self.current_dir = Games(self.id)
        elif self.section == "game_rus_roulette":
            self.current_dir = game_RusRoulette(self.id)
        else:
            print("cringe2")

    def change_nickname(self, nickname_):
        self.nickname = nickname_

    def get_stats(self):
        return f"Имя: {self.firstname}\n" \
               f"Фамилия: {self.lastname}\n" \
               f"Ник: {self.nickname}\n" \
               f"Дата регистрации: {self.registration_data}"


def register(_users):  # регистрация пользователя (если он не зарегистрирован)
    with open("users.csv", "a") as w_file:
        writer = csv.DictWriter(w_file, lineterminator="\r", fieldnames=category)
        is_registered = False
        with open("users.csv", "r") as r_file:
            for r_row in r_file:
                if str(r_row.strip().split(",")[0]) == str(_users["id"]):
                    is_registered = True
                    break
        if not is_registered:
            _users["regisration data"] = str(datetime.now()).replace('-', '.')[:-7]
            _users["nickname"] = _users["firstname"] + ' ' + _users["lastname"]
            _users["section"] = "main_menu"
            users[str(_users["id"])] = User(str(_users["id"]),
                                            _users["firstname"],
                                            _users["lastname"],
                                            _users["regisration data"],
                                            _users["nickname"],
                                            _users["section"])
            writer.writerow(_users)


def download_users_from_file():  # выгрузка данных о пользователе из users.csv в виде объектов класса User
    with open("users.csv", "r") as file:
        for row in file:
            _id, _firstname, _lastname, _registration_data, _nickname, _section = row.strip().split(",")
            print(_id)
            users[_id] = User(_id, _firstname, _lastname, _registration_data, _nickname, _section)
            print(users[_id])


def upload_user_to_file():  # загрузка данных о пользователе в файл (обновление users.csv)
    with open("users.csv", "w") as file:
        writer = csv.DictWriter(file, lineterminator="\r", fieldnames=category)
        for value in users.values():
            writer.writerow({"id": value.id,
                             "firstname": value.firstname,
                             "lastname": value.lastname,
                             "regisration data": value.registration_data,
                             "nickname": value.nickname,
                             "section": value.section})


def main():
    download_users_from_file()  # выгружаю данные из users.csv
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            user_dict = {"id": event.obj.from_id,
                         "firstname": vk.users.get(user_id=event.obj.from_id)[0]['first_name'],
                         "lastname": vk.users.get(user_id=event.obj.from_id)[0]['last_name']}
            register(user_dict)  # регистрирую

            # json_data = requests.post(vk.photos.getMessagesUploadServer()['upload_url'],
            #                           files={'photo': open('image1.png', 'rb')}).json()  # загружает фотографию на сервер
            # photo_data = vk.photos.saveMessagesPhoto(photo=json_data['photo'],
            #                                          server=json_data['server'],
            #                                          hash=json_data['hash'])[0]  # возврат данных загруженной фотографии
            # photo = "photo{}_{}".format(photo_data["owner_id"], photo_data["id"])

            vk.messages.send(
                user_id=event.obj.from_id,
                random_id=get_random_id(),
                message=users[str(event.obj.from_id)].current_dir.handler(event.obj.text),
                attachment=None
            )
            upload_user_to_file()
        else:
            # print(event.type)
            pass


if __name__ == '__main__':
    main()
