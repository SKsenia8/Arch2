import socket  # Импортируем модуль socket, который предоставляет интерфейс для работы с сетевыми соединениями
import time    # Импортируем модуль time для работы с временными задержками, например, для паузы между отправками сообщений
import os      # Импортируем модуль os для взаимодействия с операционной системой, в частности для работы с файлами
import fcntl   # Импортируем модуль fcntl для управления файловыми дескрипторами, что позволяет устанавливать блокировки на файлы
import errno    # Импортируем модуль errno, который содержит коды ошибок, используемые для обработки исключений

''' 
Тесты:
- Просто клиент (запустили без сервера) - обработано в ошибке мейна, сразу умирает.
- Клиент, но не сервер (убили сервер) - обработано в ошибке отправления пинга, клиент пытается отправить и получить, но не может.
- 1+ клиент - обработано в открытии файла, нельзя.
- 1+ сервер - обработано в мейне, нельзя.
- Убиваем клиента - сервер тоже умирает.
'''

def start_client(host='127.0.0.1', port=65432):
    # Функция для запуска клиента
    # host: адрес сервера, к которому будет подключаться клиент. '127.0.0.1' - это локальный адрес (localhost)
    # port: номер порта, на котором сервер слушает входящие соединения. 65432 - это произвольный порт

    # Имя файла блокировки, который будет использоваться для предотвращения запуска нескольких экземпляров клиента
    lock_file = "client_lock.txt"

    try:
        # Пытаемся открыть файл блокировки в режиме записи ('w')
        fp = open(lock_file, 'w')
        # Устанавливаем эксклюзивную неблокирующую блокировку на файл
        # Это предотвращает запуск другого экземпляра клиента, пока этот экземпляр работает
        #fcntl.LOCK_EX - установка эксклюзивной блокировки на файл, зн. что только один процесс может получить доступ к файлу в данный момент времени
        #fcntl.LOCK_NB - флаг, который указывает, что мы хотим установить неблокирующую блокировку. Если файл уже заблокирован другим процессом, то вместо этого он немедленно вызовет исключение
        fcntl.flock(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        # Если не удалось установить блокировку (например, файл уже заблокирован другим процессом), выводим сообщение и завершаем работу
        print("Процесс одного клиента уже запущен. Завершение работы.")
        return  # Завершаем выполнение функции, чтобы не продолжать работу клиента

    try:
        # Создаем сокет для TCP-соединения
        # socket.AF_INET указывает, что мы используем IPv4
        # socket.SOCK_STREAM указывает, что мы используем TCP (ориентированный на соединение)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Подключаемся к серверу по указанному адресу и порту
            s.connect((host, port))

            # Получаем адрес клиента (локальный адрес и порт)
            client_address = s.getsockname()
            # Формируем строку с кодом клиента в формате "IP:PORT"
            client_code = f"{client_address[0]}:{client_address[1]}"

            # Открываем файл client_code.txt в режиме записи ('w') для сохранения кода клиента
            with open('client_code.txt', 'w') as f:
                f.write(client_code)  # Записываем код клиента в файл

            # Выводим сообщение о том, что код клиента сохранен
            print(f"Код клиента сохранен в файле: {client_code}")

            # Запускаем бесконечный цикл для отправки и получения сообщений
            while True:
                try:
                    request = "ping"  # Формируем сообщение для отправки серверу
                    print(f"Отправка сообщения: {request}")  # Выводим сообщение о том, что отправляем
                    s.sendall(request.encode())  # Отправляем сообщение серверу, кодируя его в байты

                    # Получаем ответ от сервера (максимум 1024 байта)
                    data = s.recv(1024)
                    response = data.decode()  # Декодируем ответ из байтов в строку
                    print(f"Получен ответ: {response}")  # Выводим полученный ответ

                    # Проверяем, является ли ответ "pong"
                    if response == "pong":
                        print("Успешный обмен сообщениями")  # Если ответ "pong", выводим сообщение об успешном обмене
                    else:
                        print("Ошибка: непредвиденный ответ")  # Если ответ не "pong", выводим сообщение об ошибке

                    time.sleep(1)  # Задержка в 1 секунду перед следующей отправкой, чтобы не перегружать сервер

                except IOError as e:
                    # Обрабатываем ошибки ввода-вывода, которые могут возникнуть при отправке или получении данных
                    if e.errno == errno.EPIPE:
                        # Если возникает ошибка EPIPE, это означает, что соединение с сервером было разорвано
                        # Это может произойти, если сервер закрыл соединение или был остановлен
                        print(
                            "На другом конце конвейера нет считывания процесса")  # Выводим сообщение о разрыве соединения
                        break  # Выходим из цикла, так как дальнейшие попытки общения с сервером бессмысленны

                except Exception as e:
                    # Обрабатываем любые другие исключения, которые могут возникнуть
                    # Это может быть полезно для отладки, если возникла непредвиденная ошибка
                    print(f"Произошла ошибка: {e}")  # Выводим сообщение об ошибке
                    break  # Выходим из цикла, чтобы завершить работу клиента

    finally:
        # Блок finally выполняется в любом случае, даже если произошли исключения в блоке try
        # Это гарантирует, что файл блокировки будет удален, чтобы другие экземпляры клиента могли быть запущены
        os.unlink(lock_file)  # Удаляем файл блокировки, когда клиент завершает работу
        print(
            "Client finished and lock released")  # Выводим сообщение о завершении работы клиента и освобождении блокировки



if __name__ == "__main__":
    try:
        start_client()  # Вызываем функцию для запуска клиента с параметрами по умолчанию (localhost и порт 65432)
    except ConnectionRefusedError:
        # Обрабатываем исключение, если не удалось подключиться к серверу
        # Это может произойти, если сервер не запущен или недоступен
        print("Невозможно подключиться к серверу")  # Выводим сообщение о том, что подключение не удалось
