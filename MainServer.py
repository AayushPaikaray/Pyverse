import socket
import threading
import pickle
import os
import shutil
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

HOST = socket.gethostbyname(socket.gethostname())
__PORT__ = 1010

INFOLAB_SERVER_DIRECTORY = r"C:\Users\chand\OneDrive\Desktop\Aayush Paikaray\Python\Cloud"

SERVER_ADDR = ("0.0.0.0", 9998)

PC = {}
currently_playing_counts = {}

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(SERVER_ADDR)
server.listen(5)
print("Server started...")

def load_user_data():
    if os.path.exists(r"C:\Users\chand\OneDrive\Desktop\Aayush Paikaray\Python\Project PYVERSE\SERVER\users.dat"):
        with open(r"C:\Users\chand\OneDrive\Desktop\Aayush Paikaray\Python\Project PYVERSE\SERVER\users.dat", "rb") as f:
            return pickle.load(f)
    return {}

def save_user_data(data):
    with open(r"C:\Users\chand\OneDrive\Desktop\Aayush Paikaray\Python\Project PYVERSE\SERVER\users.dat", "wb") as f:
        pickle.dump(data, f)


def load_games_data():
    if os.path.exists(r"C:\Users\chand\OneDrive\Desktop\Aayush Paikaray\Python\Project PYVERSE\SERVER\games.dat"):
        with open(r"C:\Users\chand\OneDrive\Desktop\Aayush Paikaray\Python\Project PYVERSE\SERVER\games.dat", "rb") as f:
            return pickle.load(f)
    return []

def load_groups_data() -> dict:
    if os.path.exists(r"C:\Users\chand\OneDrive\Desktop\Aayush Paikaray\Python\Project PYVERSE\SERVER\groups.dat"):
        with open(r"C:\Users\chand\OneDrive\Desktop\Aayush Paikaray\Python\Project PYVERSE\SERVER\groups.dat", "rb") as f:
            data = pickle.load(f)
            if data == None:return {}
            return data
    return {}

def save_groups_data(data):
    with open(r"C:\Users\chand\OneDrive\Desktop\Aayush Paikaray\Python\Project PYVERSE\SERVER\groups.dat", "wb") as f:
        pickle.dump(data, f)

def save_games_data(data):
    with open(r"C:\Users\chand\OneDrive\Desktop\Aayush Paikaray\Python\Project PYVERSE\SERVER\games.dat", "wb") as f:
        pickle.dump(data, f)

def handle_client(conn,addr):
    try:
        request = pickle.loads(conn.recv(4096))
        action = request.get("action")

        if action == "login":
            handle_login(conn, request, addr)
        elif action == "signup":
            handle_signup(conn, request)
        elif action == "upload":
            handle_upload(conn, request)
        elif action == "reupload":
            handle_reupload(conn, request)
        elif action == "delete":
            handle_delete(conn, request)
        elif action == "rename":
            handle_rename(conn, request)
        elif action == "get_games":
            handle_get_games(conn)
        elif action == "get_groups":
            handle_get_groups(conn,request)
        elif action == "get_players":
            handle_get_players(conn)        
        elif action == "get_playing_count":
            handle_get_playing_count(conn, request)
        elif action == "update_playing_count":
            handle_update_playing_count(conn, request)
        elif action == 'create_group':
            handle_create_group(conn,request)
        elif action == 'leave_group':
            handle_leave_group(conn,request)
        elif action == 'delete_group':
            handle_delete_group(conn,request)
        elif action == 'check':
            handle_check(conn,request)
        
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        conn.close()

def handle_get_players(conn):
    response = list(load_user_data())
    conn.send(pickle.dumps(response))

def handle_create_group(conn,request):
    response = 1; groups = list(load_groups_data().values())
    for group in groups:
        if group.get('group_name').lower() == request.get('group_name').lower():
            response=0
    if response:
        request.pop("action")
        grps=list(load_groups_data().values())
        func = lambda grp:grp.get('PORT')
        try:request['PORT']=max(map(func,grps))+1
        except:request['PORT'] = 1234
        data = load_groups_data()
        data[request['PORT']] = request
        save_groups_data(data)
        conn.send(pickle.dumps(request.get('PORT')))
    else:conn.send(pickle.dumps(0))

def handle_login(conn, request, addr):
    username = request.get("username")
    password = request.get("password")
    users = load_user_data()
    if users.get(username) == password:
        response = {"status": "success"}
        PC[addr[0]]=username
        
    else:
        response = {"status": "failure"}
    conn.send(pickle.dumps(response))

def handle_signup(conn, request):
    username = request.get("username")
    password = request.get("password")
    users = load_user_data()
    if username in users:
        response = {"status": "failure"}
    else:
        users[username] = password
        save_user_data(users)
        response = {"status": "success"}
    conn.send(pickle.dumps(response))

def handle_upload(conn, request):
    game_name = request.get("game_name")
    username = request.get("username")
    game_main_file = request.get("game_main_file")
    game_icon = request.get("game_icon")
    description = request.get("description")
    download = request.get('download')
    view = request.get('view')

    games = load_games_data()
    games.append({
        "game_name": game_name,
        "username": username,
        "main_file": game_main_file,
        "icon": game_icon,
        "description":description,
        'download':download,
        'view':view
    })
    save_games_data(games)
    response = {"status": "success"}
    conn.send(pickle.dumps(response))

def handle_reupload(conn, request):
    game_name = request.get("game_name")
    username = request.get("username")
    game_main_file = request.get("game_main_file")
    game_icon = request.get("game_icon")

    games = load_games_data()
    for game in games:
        if game["game_name"] == game_name and game["username"] == username:
            game["main_file"] = game_main_file
            game["icon"] = game_icon
            save_games_data(games)
            response = {"status": "success"}
            conn.send(pickle.dumps(response))
            return
    response = {"status": "failure"}
    conn.send(pickle.dumps(response))

def handle_delete(conn, request):
    game_name = request.get("game_name")
    username = request.get("username")

    games = load_games_data()
    games = [game for game in games if not (game["game_name"] == game_name and game["username"] == username)]
    save_games_data(games)

    game_dir = os.path.join(INFOLAB_SERVER_DIRECTORY, game_name)
    if os.path.exists(game_dir):
        shutil.rmtree(game_dir)

    response = {"status": "success"}
    conn.send(pickle.dumps(response))

def handle_rename(conn, request):
    old_game_name = request.get("old_game_name")
    new_game_name = request.get("new_game_name")
    username = request.get("username")

    games = load_games_data()
    for game in games:
        if game["game_name"] == old_game_name and game["username"] == username:
            game["game_name"] = new_game_name
            save_games_data(games)

            old_game_dir = os.path.join(INFOLAB_SERVER_DIRECTORY, old_game_name)
            new_game_dir = os.path.join(INFOLAB_SERVER_DIRECTORY, new_game_name)
            if os.path.exists(old_game_dir):
                os.rename(old_game_dir, new_game_dir)

            response = {"status": "success"}
            conn.send(pickle.dumps(response))
            return
    response = {"status": "failure"}
    conn.send(pickle.dumps(response))

def handle_get_games(conn):
    games = load_games_data()
    conn.send(pickle.dumps(games[:len(games)//2]))
    conn.send(pickle.dumps(games[len(games)//2:]))

def handle_leave_group(conn, request):
    Room.allrooms[request.get('PORT')].SEND(f"SERVER:{request.get('username')} exited the group...")
    groups = load_groups_data()
    groups[request.get('PORT')]['group_members'].remove(request.get('username'))
    save_groups_data(groups)

def handle_delete_group(conn, request):
    Room.allrooms[request.get('PORT')].END()
    groups = load_groups_data()
    r=groups.pop(request.get('PORT'))
    save_groups_data(groups)
    print('GROUP',r)
    
def handle_get_groups(conn,request):
    groups = list(load_groups_data().values()) ; user = request.get('username')
    def filter_by(group):
        if user in group.get('group_members'):return True
        return False
    
    groups = list(filter(filter_by,groups))
    print(groups)
    conn.send(pickle.dumps(groups[:len(groups)//2]))
    conn.send(pickle.dumps(groups[len(groups)//2:]))

def handle_get_playing_count(conn, request):
    game_name = request.get("game_name")
    count = currently_playing_counts.get(game_name, 0)
    conn.send(pickle.dumps(count))
    
def handle_update_playing_count(conn, request):
    game_name = request.get("game_name")
    count_change = request.get("count_change", 0)
    if game_name in currently_playing_counts:
        currently_playing_counts[game_name] += count_change
    else:
        currently_playing_counts[game_name] = count_change
    conn.send(pickle.dumps({"status": "success"}))

def handle_check(conn, request):
    code = request.get('lines')
    if open(r'C:\Users\chand\OneDrive\Desktop\Aayush Paikaray\Python\Project PYVERSE\SERVER\Pycrium.py','r+').read() != code:
        conn.send(pickle.dumps({"status": "fail","message": open(r'C:\Users\chand\OneDrive\Desktop\Aayush Paikaray\Python\Project PYVERSE\SERVER\Pycrium.py','r+').read()}))
    else:
        conn.send(pickle.dumps({"status": "success","message": None}))

def rmain():
    while True:
        conn, addr = server.accept()
        print(f"Connection from {addr}")
        threading.Thread(target=handle_client, args=(conn,addr)).start()

if __name__ == "__main__":
    threading.Thread(target=rmain).start()

lobby = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
random_user = 1
try:
    lobby.bind((HOST, __PORT__))
    print(f'Created Lobby {HOST} {__PORT__}')
except Exception as e:
    print('Error creating Lobby:', e)
    exit(1)
lobby.listen()

class Room:
    codes = []
    allrooms = {}

    def __init__(self, PORT):
        global HOST
        self.PORT = PORT
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.server.bind((HOST, PORT))
            print(f'Created server {HOST} {PORT}')
        except Exception as e:
            print(f'Error Creating Server {HOST} {PORT}:', e)
        self.server.listen()
        self.run = True
        self.allclients = []
        self.alladdress = {}
        self.chathistory = load_groups_data()[PORT]['chat_history']
        Room.allrooms[PORT] = self
        Room.codes.append(PORT)
        threading.Thread(target=self.getclient).start()

    def getclient(self):
        while self.run:
            try:
                client, address = self.server.accept()
                self.alladdress[client] = address
                client.sendall(pickle.dumps(self.chathistory))
                print(f'Connected {PC.get(address[0], address[0])} to {self.PORT}')
                self.allclients.append(client)
                self.update_online_players()
                self.SEND(f'server:{PC.get(address[0], address[0])} has joined the chat',False)
                threading.Thread(target=self.RECIEVE, args=(client,)).start()
            except OSError:
                break
            except Exception as e:
                print(f'Error accepting client: {e}')

    def update_online_players(self):
        onlineplayers = 'online:'
        for clts in self.allclients:
            onlineplayers = f'{onlineplayers}{PC.get(self.alladdress[clts][0], self.alladdress[clts][0])},'
        self.SEND(onlineplayers,False)

    def SEND(self, message:str,b=True):
        if b:
            if self.chathistory:self.chathistory = f'{self.chathistory}\n{message}'
            else:self.chathistory = message
        groups_dat = load_groups_data();groups_dat[self.PORT]['chat_history'] = self.chathistory
        save_groups_data(groups_dat)
        for client in self.allclients:
            try:
                client.sendall(pickle.dumps(f'{message}'))
            except:
                self.allclients.remove(client)

    def RECIEVE(self, client):
        while self.run:
            try:
                message = pickle.loads(client.recv(2048))
                if message:
                    self.SEND(f'{PC.get(self.alladdress[client][0], self.alladdress[client][0])} : {message}')
            except:
                self.allclients.remove(client)
                self.SEND(f'server:{PC.get(self.alladdress[client][0], self.alladdress[client][0])} went offline.',False)
                self.update_online_players()
                break

    def END(self):
        self.run = False
        self.SEND('SERVER: Group deleted by admin...')
        self.allclients.clear()
        self.server.close()
        del self

    def history(self):
        return self.chathistory

def commands(client, address):
    global random_user;run=True
    while run:
        try:
            while True:
                try:
                    code = pickle.loads(client.recv(2048))
                    print(f'Request {PC.get(address[0], address[0])} to PORT {code}')
                    if code in Room.codes:
                        print(f'Connecting {PC.get(address[0], address[0])} to {code}')
                        break
                    else:Room(code)

                except:
                    print(f'Disconnected {address[0]}')
                    client.close();run=False;break
        except:client.close()
def RunLobby():
    while True:
        try:
            client, address = lobby.accept()
            threading.Thread(target=commands, args=(client, address)).start()
        except Exception as e:
            print(f'Error in lobby: {e}')
            break

def chat(message:str):
    for code in Room.codes:
        Room.allrooms[code].SEND(message)

class AdminUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Admin Control Panel")

        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.tab_control = ttk.Notebook(self.main_frame)
        self.tab_control.pack(fill=tk.BOTH, expand=True)

        self.server_tabs = {}
        self.user_listbox = tk.Listbox(self.main_frame, selectmode=tk.SINGLE)

        self.create_command_frame()
        self.update_server_list()

        threading.Thread(target=self.update_server_tabs).start()

    def create_command_frame(self):
        command_frame = ttk.Frame(self.main_frame)
        command_frame.pack(fill=tk.X, side=tk.BOTTOM)

        kick_button = ttk.Button(command_frame, text="Kick User", command=self.kick_user)
        kick_button.pack(side=tk.LEFT)

        broadcast_button = ttk.Button(command_frame, text="Broadcast", command=self.broadcast_message)
        broadcast_button.pack(side=tk.LEFT)

        refresh_button = ttk.Button(command_frame, text="Refresh Users", command=self.refresh_user_list)
        refresh_button.pack(side=tk.LEFT)

        self.user_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def update_server_list(self):
        for port in Room.codes:
            if port not in self.server_tabs:
                tab = ttk.Frame(self.tab_control)
                self.tab_control.add(tab, text=f"Port {port}")
                chat_display = tk.Text(tab, state=tk.DISABLED, wrap=tk.WORD)
                chat_display.pack(fill=tk.BOTH, expand=True)
                self.server_tabs[port] = chat_display

    def update_server_tabs(self):
        while True:
            try:
                self.update_server_list()
                for port, chat_display in self.server_tabs.items():
                    chat_display.config(state=tk.NORMAL)
                    chat_display.delete(1.0, tk.END)
                    chat_display.insert(tk.END, Room.allrooms[port].history())
                    chat_display.config(state=tk.DISABLED)
                self.root.after(1000, self.update_server_list)
            except: pass
    def kick_user(self):
        port = self.get_selected_port()
        if port is None:
            messagebox.showinfo("Error", "No server selected")
            return

        selected_user = self.user_listbox.get(tk.ACTIVE)
        if not selected_user:
            messagebox.showinfo("Error", "No user selected")
            return

        user_ip = self.get_ip_from_name(selected_user)
        if user_ip is None:
            messagebox.showinfo("Error", "User not found")
            return

        room = Room.allrooms.get(port)
        if room:
            for client, address in room.alladdress.items():
                if address[0] == user_ip:
                    room.SEND(f'{PC[user_ip]} was kicked from the server.')
                    client.close()
                    room.allclients.remove(client)
                    self.refresh_user_list()
                    break

    def broadcast_message(self):
        message = simpledialog.askstring("Input", "Enter message to broadcast:")
        if message:
            chat(f'ADMIN: {message}')

    def refresh_user_list(self):
        self.user_listbox.delete(0, tk.END)
        port = self.get_selected_port()
        if port is not None:
            room = Room.allrooms.get(port)
            if room:
                for client in room.allclients:
                    user_name = PC[room.alladdress[client][0]]
                    self.user_listbox.insert(tk.END, user_name)

    def get_ip_from_name(self, name):
        for ip, user_name in PC.items():
            if user_name == name:
                return ip
        return None

    def get_selected_port(self):
        tab_index = self.tab_control.index(self.tab_control.select())
        tab_text = self.tab_control.tab(tab_index, "text")
        if tab_text.startswith("Port "):
            return int(tab_text.split(" ")[1])
        return None

def main():
    threading.Thread(target=RunLobby).start()

    root = tk.Tk()
    admin_ui = AdminUI(root)
    
    root.mainloop()
if __name__ == "__main__":
    main()

