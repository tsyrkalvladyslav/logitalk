import socket
import threading
import struct

HOST = "localhost"
PORT = 8080

# Список усіх активних клієнтів
clients = []
clients_lock = threading.Lock()

def broadcast(packet):
    """Розсилає готовий бінарний пакет усім підключеним клієнтам."""
    with clients_lock:
        # Створюємо копію списку для безпечної ітерації
        for client in list(clients):
            try:
                client.sendall(packet)
            except:
                # Якщо відправка не вдалася, видаляємо клієнта
                print("Не вдалося відправити пакет клієнту. Видаляємо зі списку.")
                if client in clients:
                    clients.remove(client)

def handle_client(client_socket):
    """Обробка кожного окремого клієнта у своєму потоці."""
    print("Новий користувач приєднався до сервера!")
    with clients_lock:
        clients.append(client_socket)
        
    while True:
        try:
            # 1. Читаємо заголовок пакета (4 байти типу + 4 байти довжини)
            header = recv_all(client_socket, 8)
            if not header:
                break  # Клієнт відключився
            
            p_type = header[:4].decode('utf-8', errors='ignore').strip()
            # Розпаковуємо 4 байти довжини назад в ціле число (int)
            p_len = struct.unpack('!I', header[4:])[0]
            
            # 2. Читаємо тіло пакета на основі отриманої довжини
            payload = recv_all(client_socket, p_len)
            if not payload:
                break
            
            print(f"Сервер обробив пакет: {p_type} | Розмір даних: {p_len} байтів")
            
            # 3. Склеюємо заголовок та дані назад і транслюємо УСІМ клієнтам у чаті
            full_packet = header + payload
            broadcast(full_packet)
            
        except Exception as e:
            print(f"Помилка під час обробки даних клієнта: {e}")
            break
            
    # Очищення при відключенні
    print("Користувач покинув чат.")
    with clients_lock:
        if client_socket in clients:
            clients.remove(client_socket)
    client_socket.close()

def recv_all(sock, n):
    """Допоміжна функція, яка гарантує, що ми зчитаємо рівно n байтів з сокета."""
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

def start_server():
    """Запуск сервера."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Дозволяємо повторне використання порту після перезапуску
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind((HOST, PORT))
        server.listen()
        print(f"=== Сервер LogiTalk запущено на {HOST}:{PORT} ===")
    except Exception as e:
        print(f"Не вдалося запустити сервер: {e}")
        return
    
    while True:
        try:
            client_sock, addr = server.accept()
            # Для кожного клієнта запускаємо окремий потік
            threading.Thread(target=handle_client, args=(client_sock,), daemon=True).start()
        except KeyboardInterrupt:
            print("\nСервер зупинено.")
            break

if __name__ == "__main__":
    start_server()