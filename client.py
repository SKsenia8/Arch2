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
    lock_file = "client_lock.txt"

    try:
        fp = open(lock_file, 'w')
        fcntl.flock(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        print("Процесс одного клиента уже запущен. Завершение работы.")
        return

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))

            client_address = s.getsockname()
            client_code = f"{client_address[0]}:{client_address[1]}"

            with open('client_code.txt', 'w') as f:
                f.write(client_code)

            print(f"Код клиента сохранен в файле: {client_code}")

            while True:
                try:
                    request = "ping"
                    print(f"Отправка сообщения: {request}")
                    s.sendall(request.encode())

                    data = s.recv(1024)
                    response = data.decode()
                    print(f"Получен ответ: {response}")

                    if response == "pong":
                        print("Успешный обмен сообщениями")
                    else:
                        print("Ошибка: непредвиденный ответ")

                    time.sleep(1)
                except IOError as e:
                    if e.errno == errno.EPIPE:
                        print("На другом конце конвейера нет считывания процесса")
                        break

                except Exception as e:
                    print(f"Произошла ошибка: {e}")
                    break

    finally:
        # Always release the lock file, even if exceptions occur.
        os.unlink(lock_file)  #remove the lock file when finished
        print("Client finished and lock released.")


if __name__ == "__main__":
    try:
        start_client()

    except ConnectionRefusedError:
        print("Невозможно подключиться к серверу")