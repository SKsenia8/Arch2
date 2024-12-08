import socket
import time
import os
import fcntl
import errno

'''тесты:
просто клиент (запустили без сервера) - обработано в ошибке мейна, сразу умирает
клиент, но не сервер (убили сервер) - обработано в ошибке отправления пинга, клиент пытается отправить и получить, но не может
1+ клиент - обработано в открытии файла, нельзя
1+ сервер - обработано в мейне, нельзя
убиваем клиента - сервер тоже умирает
'''

def start_client(host='127.0.0.1', port=65432):
    # Функция для запуска клиента
    lock_file = "client_lock.txt"

    try:
        fp = open(lock_file, 'w')
        fcntl.flock(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        print("Процесс одного клиента уже запущен. Завершение работы.")
        return

    try:
        # Создаем сокет для TCP-соединения
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Подключаемся к серверу по указанному адресу и порту
            s.connect((host, port))

            # Получаем адрес клиента
            client_address = s.getsockname()
            client_code = f"{client_address[0]}:{client_address[1]}"

            # Записываем код клиента в файл
            with open('client_code.txt', 'w') as f:
                f.write(client_code)

            print(f"Код клиента сохранен в файле: {client_code}")

            while True:
                try:
                    # Отправляем сообщение серверу
                    request = "ping"
                    print(f"Отправка сообщения: {request}") 
                    s.sendall(request.encode()) 

                    # Получаем ответ от сервера
                    data = s.recv(1024)
                    response = data.decode()
                    print(f"Получен ответ: {response}")

                    # Проверяем, является ли ответ "pong"
                    if response == "pong":
                        print("Успешный обмен сообщениями")
                    else:
                        print("Ошибка: непредвиденный ответ")

                    time.sleep(1)
                except IOError as e:
                    if e.errno == errno.EPIPE:
                        # Если ошибка о потеряне соединения
                        print("На другом конце конвейера нет считывания процесса")
                        break

                except Exception as e:
                    # Обрабатываем любые другие исключения
                    print(f"Произошла ошибка: {e}")
                    break

    finally:
        # Удаляем файл блокировки, когда клиент завершает работу
        os.unlink(lock_file)
        print("Client finished and lock released.")


if __name__ == "__main__":
    try:
        # Вызываем функцию для запуска клиента
        start_client()
    except ConnectionRefusedError:
        # Обрабатываем исключение, если не удалось подключиться к серверу
        print("Невозможно подключиться к серверу")
