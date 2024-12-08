import socket
import json

def start_server(host='127.0.0.1', port=65432):
    # Функция для запуска сервера, принимает адрес хоста и порт в качестве аргументов

    # Создаем словарь с информацией о сервере
    server_info = {'host': host, 'port': port}

    with open('server_info.json', 'w') as f:
        json.dump(server_info, f)

    # Создаем сокет для TCP-соединения
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Проверяем, занят ли указанный порт
        result = s.connect_ex((host, port))
        if result == 0:
            # Если порт занят, выводим сообщение и выходим из функции
            print(f"Порт {port} уже занят.")
            return

        try:
            # Привязываем сокет к указанному адресу и порту
            s.bind((host, port))
            print(f"Порт {port} открыт и сервер запущен.")
        except OSError as e:
            # Если произошла ошибка при привязке, выводим сообщение об ошибке
            print(f"Ошибка привязки порта {port}: {e}")
            return

        s.listen()
        print(f"Сервер запущен на {host}:{port}. Ожидание соединения...")

        # Принимаем входящее соединение
        conn, addr = s.accept()
        with conn:
            # Выводим информацию о подключенном клиенте
            print(f"Подключено к {addr}")
            while True:
                # Получаем данные от клиента (максимум 1024 байта)
                data = conn.recv(1024)
                if not data:
                    # Если данные не получены, выходим из цикла
                    break

                message = data.decode()
                print(f"Получено сообщение: {message}")

                # Проверяем содержимое сообщения и формируем ответ
                response = "pong" if message == "ping" else "Ошибка: неизвестное сообщение"

                # Отправляем ответ клиенту
                conn.sendall(response.encode())
                print(f"Отправлено сообщение: {response}")


if __name__ == "__main__":
    try:
        # Запуск сервера
        start_server()
    except Exception as e:
        print(f"Ошибка: {e}")
