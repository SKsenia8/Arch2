import socket
import json

def start_server(host='127.0.0.1', port=65432):
    server_info = {'host': host, 'port': port}

    with open('server_info.json', 'w') as f:
        json.dump(server_info, f)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        result = s.connect_ex((host, port))
        if result == 0:
            print(f"Порт {port} уже занят.")
            return

        try:
            s.bind((host, port))
            print(f"Порт {port} открыт и сервер запущен.")
        except OSError as e:
            print(f"Ошибка привязки порта {port}: {e}")
            return

        s.listen()
        print(f"Сервер запущен на {host}:{port}. Ожидание соединения...")

        conn, addr = s.accept()
        with conn:
            print(f"Подключено к {addr}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break

                message = data.decode()
                print(f"Получено сообщение: {message}")
                response = "pong" if message == "ping" else "Ошибка: неизвестное сообщение"
                conn.sendall(response.encode())
                print(f"Отправлено сообщение: {response}")


if __name__ == "__main__":
    try:
        start_server()
    except Exception as e:
        print(f"Ошибка: {e}")
