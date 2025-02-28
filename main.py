import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import logging
import datetime
import requests

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("bot.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Загрузка переменных окружения (пока хардкодим)
VK_TOKEN = "vk1.a.RJkt5FrdwTztrEw-kkRHOCNueykXsItHnvUPZqDT7p0YvDcxippRBw_q8iLgmYGbNgm-K_N-N3BRjoRfZqow-CGtw-0FsObp3Hn2fOlnbaMZD1KcoWuadNnX0z5jqV0Vdjs_76OamaCfcDjxfSsmLx50YuhTU2aOWE8ht0JTbPjS6GEeJ0UOsWYm2gfT8TyTjgPIV-SVLxhIH1wfnH4gBQ"
VK_GROUP_ID = "229535000"

# Создание клавиатуры (функция остается без изменений)
def create_keyboard(start=False, search=False, favorites=False):
    keyboard = VkKeyboard(one_time=True)
    if start:
        keyboard.add_button("Начать", color=VkKeyboardColor.PRIMARY)
    elif search or favorites:
        if search:
            keyboard.add_button("Поиск", color=VkKeyboardColor.PRIMARY)
        if favorites:
            keyboard.add_button("Избранное", color=VkKeyboardColor.SECONDARY)
    return keyboard.get_keyboard()

# Функция для отправки сообщения (изменена!)
def send_message(vk, user_id, message, keyboard=None):  # Добавлен параметр vk
    params = {
        "user_id": user_id,
        "message": message,
        "random_id": 0,
    }
    if keyboard:
        params["keyboard"] = keyboard
    try:
        vk.messages.send(**params)
        logging.info(f"Sent message to user {user_id}: {message}")
    except vk_api.exceptions.ApiError as e:
        logging.error(f"VK API Error sending message to user {user_id}: {e}")
    except Exception as e:
        logging.exception(f"An unexpected error occurred while sending message to user {user_id}: {e}")


class VK_get:
        
    def __init__(self, VK_TOKEN, version='5.199'):
        self.base_address = 'https://api.vk.com/method/'
        self.params = {
            'access_token': VK_TOKEN,
            'v': version
        }

    def get_user_info(self, user_id, fields='bdate,sex,city'):  # Получить информацию о пользователе
        url = f'{self.base_address}users.get'
        params = {
            'user_ids': user_id,
            'fields': fields
        }
        params.update(self.params)
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # Проверка на HTTP ошибки
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при выполнении запроса: {e}")
            return None  # Или выбросить исключение, если это необходимо
        except ValueError as e:
            print(f"Ошибка при разборе JSON: {e}")
            return None # Или выбросить исключение, если это необходимо    


# Основная функция для запуска бота
def main():
    try:
        vk_session = vk_api.VkApi(token=VK_TOKEN)
        longpoll = VkLongPoll(vk_session)
        vk = vk_session.get_api()
        vk_get = VK_get(VK_TOKEN)  # Инициализируем VK_get здесь
        logging.info("VK API session initialized successfully.")
    except vk_api.exceptions.ApiError as e:
        logging.error(f"Failed to initialize VK API: {e}")
        return

    logging.info("Bot started listening for events.")
    for event in longpoll.listen():
        user_info = None  # Инициализируем user_info по умолчанию
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            user_id = event.user_id
            message_text = event.text
            logging.info(f"Received message from user {user_id}: {message_text}")

            try:
                if message_text.lower() == "начать":
                    send_message(vk, user_id, "Привет! Выбери действие:", keyboard=create_keyboard(search=True, favorites=True))
                elif message_text.lower() in ["поиск", "избранное"]: # Улучшенная проверка
                    if message_text.lower() == "поиск":
                        send_message(vk, user_id, "Функция поиска ещё не реализована.", keyboard=create_keyboard(search=True, favorites=True))
                    else:  # Это будет "избранное"
                        send_message(vk, user_id, "Функция избранного ещё не реализована.", keyboard=create_keyboard(search=True, favorites=True))
                else:
                    user_info = vk_get.get_user_info(user_id)  # Получаем информацию о пользователе
                    if user_info:
                        # Обрабатываем user_info здесь
                        print(f"Информация о пользователе {user_id}: {user_info}")
                    else:
                        print(f"Не удалось получить информацию о пользователе {user_id}")
                        send_message(vk, user_id, "Не удалось получить информацию о вас. Попробуйте позже.")

            except Exception as e:
                logging.exception(f"An unexpected error occurred while processing message from user {user_id}: {e}")

# Запуск бота только при прямом запуске файла
if __name__ == "__main__":
    main()

