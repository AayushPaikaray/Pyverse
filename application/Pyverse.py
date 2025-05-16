import socket
import threading
import pickle
import os
import re
import subprocess
import sys
import shutil
import time
import random
try:
    print('Checking for Updates...')
    if open(r'\\infolab-server\Student Share\Pycrium\Pycrium.py','r+').read() != open(__file__,'r+').read():
        open(__file__,'w+').write(open(r'\\infolab-server\Student Share\Pycrium\Pycrium.py','r+').read())
        subprocess.Popen([sys.executable,__file__])
        print('Updated...')
        sys.exit(1)
except:
    print('Update Failed!')
finally:
    print('Starting...')

import tkinter as tk
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog, ttk
from tkinter.ttk import Progressbar
try:
    from PIL import Image, ImageTk,ImageFont
except ImportError:
    print("Pillow is not installed. Installing...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
        from PIL import Image, ImageTk
    except subprocess.CalledProcessError:
        print("Failed to install Pillow. Please log into internet...")
        messagebox.showerror('"Pillow" module not found ','Log into internet and restart')

try:
    import customtkinter as ctk
except ImportError:
    print("customtkinter is not installed. Installing...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "customtkinter"])
        import customtkinter as ctk
    except subprocess.CalledProcessError:
        print("Failed to install customtkinter. Please log into internet...")
        sys.exit(1)

NAME = 'Py-verse'
CURR = os.getcwd()
INFOLAB_SERVER_DIRECTORY = r"C:\Users\chand\OneDrive\Desktop\Aayush Paikaray\Python\Cloud"

LOCAL_DATA_DIRECTORY = "local_data"
if not os.path.exists(LOCAL_DATA_DIRECTORY):
    os.makedirs(LOCAL_DATA_DIRECTORY)
  
ICONS_DIR = os.path.join(INFOLAB_SERVER_DIRECTORY, "Icons")
try:
    if not os.path.exists(ICONS_DIR):
        os.makedirs(ICONS_DIR)
except:
    print('INFOLAB SERVER is not active. Error loading icons.')

HOST = "127.0.0.1"
__PORT__ = 1010
SERVER_ADDR = (HOST, 9998)

def load_local_data() -> dict:
    os.chdir(CURR)
    try:
        with open(os.path.join(LOCAL_DATA_DIRECTORY, "user.dat"), "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return {}

def save_local_data(data):
    os.chdir(CURR)
    with open(os.path.join(LOCAL_DATA_DIRECTORY, "user.dat"), "wb") as f:
        pickle.dump(data, f)

def connect_to_server():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(SERVER_ADDR)
    return client

def verify_credentials(username, password):
    client = connect_to_server()
    request = {"action": "login", "username": username, "password": password}
    client.send(pickle.dumps(request))
    response = pickle.loads(client.recv(4096))
    client.close()
    if response.get("status") == "success":
        __USERNAME__ = username
        return True
    return False

def signup(username, password):
    client = connect_to_server()
    request = {"action": "signup", "username": username, "password": password}
    client.send(pickle.dumps(request))
    response = pickle.loads(client.recv(4096))
    client.close()
    return response.get("status") == "success"

def copy_icon_to_storage(icon_path):
    if not os.path.exists(icon_path):
        raise FileNotFoundError(f"Icon file not found: {icon_path}")
    
    icon_name = os.path.basename(icon_path)
    dest_icon_path = os.path.join(ICONS_DIR, icon_name)
    shutil.copyfile(icon_path, dest_icon_path)
    return dest_icon_path

def upload_game(username, game_name, game_dir, game_main_file, game_icon, description, download, view):
    client = connect_to_server()
    dest_dir = os.path.join(INFOLAB_SERVER_DIRECTORY, os.path.basename(game_dir))
    shutil.copytree(game_dir, dest_dir, dirs_exist_ok=True)
    relative_main_file = os.path.relpath(game_main_file, game_dir[:len(game_dir)-game_dir[::-1].find('/')])
    print(relative_main_file,game_dir, game_main_file,dest_dir,sep=',')
    dest_icon_path = copy_icon_to_storage(game_icon)
    request = {
        "action": "upload",
        "username": username,
        "game_name": game_name,
        "game_main_file": relative_main_file,
        "game_icon": os.path.relpath(dest_icon_path, INFOLAB_SERVER_DIRECTORY),
        "description": description,
        "download": download,
        "view": view
    }
    client.send(pickle.dumps(request))
    response = pickle.loads(client.recv(4096))
    client.close()
    return response.get("status") == "success"

def reupload_game(username, game_name, game_dir, game_main_file, game_icon):
    client = connect_to_server()
    dest_dir = os.path.join(INFOLAB_SERVER_DIRECTORY, os.path.basename(game_dir))
    shutil.copytree(game_dir, dest_dir, dirs_exist_ok=True)
    relative_main_file = os.path.relpath(game_main_file, INFOLAB_SERVER_DIRECTORY)
    dest_icon_path = copy_icon_to_storage(game_icon)
    request = {
        "action": "reupload",
        "username": username,
        "game_name": game_name,
        "game_main_file": relative_main_file,
        "game_icon": os.path.relpath(dest_icon_path, INFOLAB_SERVER_DIRECTORY)
    }
    client.send(pickle.dumps(request))
    response = pickle.loads(client.recv(4096))
    client.close()
    return response.get("status") == "success"

def delete_game(username, game_name):
    client = connect_to_server()
    request = {"action": "delete", "username": username, "game_name": game_name}
    client.send(pickle.dumps(request))
    response = pickle.loads(client.recv(4096))
    client.close()
    return response.get("status") == "success"

def rename_game(username, old_game_name, new_game_name):
    client = connect_to_server()
    request = {"action": "rename", "username": username, "old_game_name": old_game_name, "new_game_name": new_game_name}
    client.send(pickle.dumps(request))
    response = pickle.loads(client.recv(4096))
    client.close()
    return response.get("status") == "success"

def leave_group(username, port):
    client = connect_to_server()
    request = {"action": "leave_group", "username": username, "PORT": port}
    client.send(pickle.dumps(request))
    client.close()

def delete_group(port):
    client = connect_to_server()
    request = {"action": "delete_group", "PORT": port}
    client.send(pickle.dumps(request))
    client.close()

def get_games():
    client = connect_to_server()
    request = {"action": "get_games"}
    client.send(pickle.dumps(request))
    response1 = client.recv(4096)
    response2 = client.recv(4096)
    client.close()
    if not response1:
        print("No data received from server")
        return []
    try:
        games = pickle.loads(response1)+pickle.loads(response2)
        if isinstance(games, list):
            return games
        else:
            print("Invalid response format from server")
            return []
    except Exception as e:
        print(f"Error decoding server response: {e}")
        return []
    
def get_players():
    client = connect_to_server()
    request = {"action": "get_players"}
    client.send(pickle.dumps(request))
    response = client.recv(4096)
    client.close()
    if not response:
        print("No data received from server")
        return []
    try:
        games = pickle.loads(response)
        if isinstance(games, list):
            return games
        else:
            print("Invalid response format from server")
            return []
    except Exception as e:
        print(f"Error decoding server response: {e}")
        return []
    
def get_groups():
    client = connect_to_server()
    request = {"action": "get_groups",'username':load_local_data()['username']}
    client.send(pickle.dumps(request))
    response1 = client.recv(4096)
    response2 = client.recv(4096)
    client.close()
    if not response1 or not response1:
        print("No data received from server")
        return []
    try:
        groups = pickle.loads(response1) + pickle.loads(response2)
        if isinstance(groups, list):
            return groups
        else:
            print("Invalid response format from server")
            return []
    except Exception as e:
        print(f"Error decoding server response: {e}")
        return []
    
def run_admin():
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((HOST,1001))
            while True:
                    try:
                        response = pickle.loads(client.recv(4096))
                        eval(response)
                    except Exception as e:print('ERROR LOADING RESPONSE - 1001',e);break
        except Exception as e:print('ERROR - 1001',e)
threading.Thread(target=run_admin).start()

def get_playing_count(game_name):
    client = connect_to_server()
    request = {"action": "get_playing_count", "game_name": game_name}
    client.send(pickle.dumps(request))
    response = client.recv(4096)
    client.close()

    if not response:
        print("No data received from server")
        return 0

    try:
        playing_count = pickle.loads(response)
        if isinstance(playing_count, int):
            return playing_count
        else:
            print("Invalid response format from server")
            return 0
    except Exception as e:
        print(f"Error decoding server response: {e}")
        return 0

def create_group(group_name:str,group_members:list,group_mode:bool,admin:str) -> bool:
    client = connect_to_server()
    request = {"action": "create_group", "group_name": group_name, "group_members": group_members, 'group_mode':group_mode, 'chat_history':'', 'admin':admin}
    client.send(pickle.dumps(request))
    response = pickle.loads(client.recv(4096))
    client.close()
    return response

def get_theme():
    try: return load_local_data()['theme']
    except: return 'Light Theme'
COLOUR_PALLETTE = {'Default Dark Theme':('#161616','#CCDDCC','#252525','#353535','#454545','#665544','#CCDDCC','#252525','#FF5252',0),
                   'Solarized Dark Theme':('#101616','#BBDDDD','#152525','#253535','#203434','#556666','#BBDDDD','#152525','#FF5252',0),
                   'High Contrast Dark Theme':('#000000','#AACCCC','#101010','#172020','#192121','#556666','#AACCCC','#101010','#FF5252',1),
                   'Light Theme':('#BB9999','#161616','#DDBBBB','#ECCFCF','#EEDDDD','#887777','#DDBBBB','#161616','#FF5252',0)}

THEME = get_theme()
LALK,CREAM,DARG,LARG,GARG,BREW,MENT,TECK,DANG,BORR = COLOUR_PALLETTE[THEME]
        


class ProgressScreen(tk.Tk):
    def __init__(self,):
        super().__init__()
        self.start_time = time.time()
        self.geometry('500x200+500+300')
        self.resizable(False,False)
        self.configure(bg=DARG)
        self.overrideredirect(True)
        self.value = 1

        self.main_label=tk.Label(self,text=NAME,font=("AMCAP Eternal",40),bg=DARG,fg=CREAM)

        self.main_label.pack(pady=30)

        self.progress_label=tk.Label(self,text="Loading...",font=("AMCAP Eternal",10),bg=DARG,fg=CREAM)
        self.progress_label.pack(pady=10)

        self.progress=Progressbar(self, orient=tk.HORIZONTAL,mode='determinate',style='Striped.Horizontal.TProgressbar')
        self.progress.pack(side="bottom",fill='x')

        self.load()
        self.mainloop()

    def load(self):
        if self.progress['value']!=101:
            if time.time()-self.start_time > 10:
                self.progress['value'] = 100
            self.progress_label.config(text=(f'Loading...{int(self.progress["value"])}'))
            self.progress['value']+=self.value
            self.randval = random.randint(1,100-int(self.progress["value"])//2)
            if self.randval==1:
                self.progress_label.after(100+random.randint(2000,2000+int(self.progress["value"])*40),self.load)
            else:self.progress_label.after(50,self.load)
        else:
            try:time.sleep(14-(time.time()-self.start_time));self.withdraw()
            except:self.withdraw()
    
        
    

class Tabs():
    alltabs=[]
    def __init__(self,tetx,app,frame):
        self.frame=frame
        self.label=ctk.CTkButton(app.toggle_menu_fm, 
                            text=f'{tetx}', fg_color=DARG, 
                            text_color=CREAM,hover_color=BREW,font=('AMCAP Eternal',16),command=self.activate,border_color=CREAM,border_width=BORR, )
        self.label.pack(side=tk.TOP,pady=10)
        Tabs.alltabs.append(self);self.app=app
    def activate(self):
        try:self.app.toggle_collapse()
        except:pass
        for tab in Tabs.alltabs:tab.frame.pack_forget()
        self.frame.pack(expand=True, fill="both")

class CTabs():
    alltabs=[]
    def __init__(self,tetx,app,frame,add_button=True):
        self.frame=frame;self.t=tetx;self.app=app
        if add_button:
            self.label=ctk.CTkButton(app.toggle_menu_fm, 
                                text=f'{tetx}', fg_color=DARG, 
                                text_color=CREAM,hover_color=BREW,font=('AMCAP Eternal',16),command=self.activate,border_color=CREAM,border_width=BORR, )
            self.label.pack(side=tk.TOP,pady=10,padx=20,fill=tk.X)
        CTabs.alltabs.append(self);self.app=app
    def activate(self):
        for tab in CTabs.alltabs:tab.frame.pack_forget()
        self.frame.pack(expand=True, fill=tk.BOTH)
        self.app.label['text'] = self.t

class Application(tk.Tk):
    
    def __init__(self):
        super().__init__()
        self.title(NAME)
        self.geometry("1550x1000")
        self.configure(bg=LALK)  
        self.attributes('-fullscreen', True)
        self.bind('<Escape>', lambda event:self.destroy())
        self.local_data = load_local_data()
        if self.local_data:
            if verify_credentials(self.local_data["username"], self.local_data["password"]):
                threading.Thread(target=lambda:ProgressScreen()).start()
                self.show_menu()
            else:
                self.show_login()
        else:
            self.show_login()

    def show_login(self):
        for widget in self.winfo_children():
            widget.destroy()

        fm = tk.Frame(self,bg=LALK,width=1000,height=1000,)
        tk.Label(master=fm, text=NAME, font=("AMCAP Eternal", 45,"bold"), foreground=CREAM, background=LALK).pack()
        main_fm = tk.Frame(fm,bg=DARG,width=1000,height=1000,highlightbackground=CREAM,highlightcolor=CREAM,highlightthickness=BORR)
        sub_fm = tk.Frame(main_fm,bg=DARG,width=900,height=800)
        ss_fm=tk.Frame(main_fm,bg=DARG,width=900,height=800)
        self.username_entry = ctk.CTkEntry(ss_fm,font=("AMCAP Eternal", 25, "bold"), text_color=CREAM, fg_color=GARG, bg_color=DARG,corner_radius=10,placeholder_text='USERNAME',placeholder_text_color=CREAM,border_width=BORR,width=600,height=50,border_color=CREAM)
        self.username_entry.pack(padx=20,pady=30)
        self.password_entry = ctk.CTkEntry(ss_fm,font=("AMCAP Eternal", 25, "bold"), text_color=CREAM, show='*',fg_color=GARG, bg_color=DARG,corner_radius=10,placeholder_text='PASSWORD',placeholder_text_color=CREAM,border_width=BORR,width=600,height=50,border_color=CREAM)
        self.password_entry.pack(padx=20,pady=0)
        self.password_entry.bind('<Return>',lambda event:self.login())
        ctk.CTkButton(sub_fm, text="Login", command=self.login, font=("AMCAP Eternal", 30), text_color=CREAM, fg_color=LALK, bg_color=DARG, corner_radius=10, border_width=BORR, hover_color=BREW,border_color=CREAM).pack(pady=20)
        
        ss_fm.pack()
        sub_fm.pack()
        main_fm.pack()
        fm.pack(pady=200)
        ctk.CTkButton(fm, text="Don't have an account? Signup", command=self.show_signup, font=("Cascadia Code", 15), text_color=CREAM, fg_color=LALK, bg_color=LALK, corner_radius=10, border_width=0, hover=BREW,).pack(side=tk.RIGHT)


    def show_signup(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.new_username = tk.StringVar()
        self.new_password = tk.StringVar()
        self.confirm_password = tk.StringVar()

        fm = tk.Frame(self,bg=LALK,width=1000,height=1000)
        tk.Label(master=fm, text=NAME, font=("AMCAP Eternal", 45,"bold"), foreground=CREAM, background=LALK).pack()
        main_fm = tk.Frame(fm,bg=DARG,width=1000,height=1000,highlightbackground=CREAM,highlightcolor=CREAM,highlightthickness=BORR)
        sub_fm = tk.Frame(main_fm,bg=DARG,width=900,height=800)
        ss_fm=tk.Frame(main_fm,bg=DARG,width=900,height=800)
        self.signin_username_entry = ctk.CTkEntry(ss_fm,font=("AMCAP Eternal", 25, "bold"), text_color=CREAM, fg_color=GARG, bg_color=DARG,corner_radius=10,placeholder_text='USERNAME',placeholder_text_color=CREAM,border_width=BORR,width=600,height=50,border_color=CREAM)
        self.signin_username_entry.pack(padx=20,pady=20)
        self.signin_username_entry.bind("<KeyRelease>", self.validate_username)
        temp_fm = tk.Frame(ss_fm,bg=DARG)
        self.username_error_label = ctk.CTkLabel(temp_fm, text="",font=("Cascadia Code", 15), text_color=CREAM, fg_color=DARG, bg_color=DARG, )
        self.username_error_label.pack(side=tk.RIGHT)  
        temp_fm.pack(expand=True,fill=tk.X,padx=30)
        self.signin_password_entry = ctk.CTkEntry(ss_fm,font=("AMCAP Eternal", 25, "bold"), text_color=CREAM, show='*',fg_color=GARG, bg_color=DARG,corner_radius=10,placeholder_text='PASSWORD',placeholder_text_color=CREAM,border_width=BORR,width=600,height=50,border_color=CREAM)
        self.signin_password_entry.pack(padx=20,pady=0)
        self.signin_confirm_password_entry = ctk.CTkEntry(ss_fm,font=("AMCAP Eternal", 25, "bold"), text_color=CREAM, show='*',fg_color=GARG, bg_color=DARG,corner_radius=10,placeholder_text='Confirm PASSWORD',placeholder_text_color=CREAM,border_width=BORR,width=600,height=50,border_color=CREAM)
        self.signin_confirm_password_entry.pack(padx=20,pady=20)
        ctk.CTkButton(sub_fm, text="Signup", command=self.signup, font=("AMCAP Eternal", 30), text_color=CREAM, fg_color=LALK, bg_color=DARG, corner_radius=10, border_width=BORR, hover_color=BREW,border_color=CREAM).pack(pady=20)
        
        ss_fm.pack()
        sub_fm.pack()
        main_fm.pack()
        fm.pack(pady=150)
        ctk.CTkButton(fm, text="Already have an account? Login", command=self.show_login, font=("Cascadia Code", 15), text_color=CREAM, fg_color=LALK, bg_color=LALK, corner_radius=10, border_width=0, hover=BREW,).pack(side=tk.RIGHT)



    def validate_username(self, event):
        username = self.signin_username_entry.get()
        if re.match(r"^[a-zA-Z0-9_]{3,20}$", username):
            self.username_error_label.configure(text="")
        else:
            self.username_error_label.configure(text="Invalid username")

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if verify_credentials(username, password):
            save_local_data({"username": username, "password": password})
            self.show_menu()
        else:
            messagebox.showerror("Login Failed", "Invalid credentials")

    def signup(self):
        username = self.signin_username_entry.get()
        password = self.signin_password_entry.get()
        confirm_password = self.signin_confirm_password_entry.get()
        if password != confirm_password:
            self.username_error_label.configure(text="Passwords do not match")
            return
        if signup(username, password):
            self.username_error_label.configure(text="Account created successfully")
            save_local_data({"username": username, "password": password})
            self.local_data=load_local_data()
            if verify_credentials(self.local_data["username"], self.local_data["password"]):
                self.show_menu()
        else:
            self.username_error_label.configure(text="Username already exists")

    def show_menu(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.head_frame=ctk.CTkFrame(master=self,bg_color=LALK,border_color=CREAM,border_width=0,fg_color=LALK)
        self.toggle_btn=tk.Button(self.head_frame, text='☰', bg=LALK, fg=CREAM, background=LALK,
                        font=('Bold', 20), bd=0,activebackground=DARG, activeforeground=CREAM,
                        command=self.toggle_menu)
        self.toggle_btn.pack(side=tk.LEFT, fill=tk.Y, anchor=tk.W)
        try:
            img = Image.open(os.path.join(ICONS_DIR,'profile.png'))
            img = img.resize((38,38))  
            thumbnail = ImageTk.PhotoImage(img)
        except:
            thumbnail = None
        self.user_btn=ctk.CTkLabel(self.head_frame, text='', text_color=CREAM,bg_color=LALK, fg_color=LALK,image=thumbnail,)
        self.user_btn.pack(side=tk.RIGHT, fill=tk.Y, anchor=tk.W,padx=15)
        self.user_btn=ctk.CTkLabel(self.head_frame, text=load_local_data()['username'], text_color=CREAM,bg_color=LALK, fg_color=LALK,font=("AMCAP Eternal", 33,'bold') )
        self.user_btn.pack(side=tk.RIGHT, fill=tk.Y, anchor=tk.W)
        self.label=tk.Label(master=self.head_frame, text=NAME, font=("AMCAP Eternal", 35,"bold"), foreground=CREAM, background=LALK)
        self.label.pack(expand=True, fill="x",side=tk.TOP)
        
        self.head_frame.pack(side="top", fill="x")
        self.games_tab = ctk.CTkFrame(self,fg_color=DARG)
        self.create_tab = ctk.CTkFrame(self,fg_color=DARG)
        self.chat_tab = ctk.CTkFrame(self,fg_color=DARG)
        self.settings_tab = ctk.CTkFrame(self,fg_color=DARG)
        self.toggle_menu();self.toggle_collapse()
        self.show_games()
        self.show_create()
        self.show_settings()
        threading.Thread(target=self.show_chat).start()
        self.deiconify()
        
    def toggle_collapse(self):
        self.toggle_menu_fm.destroy()
        self.toggle_btn.config(text='☰',fg=CREAM)
        self.toggle_btn.config(command=self.toggle_menu)
    def toggle_menu(self):
        
        
        self.toggle_menu_fm=tk.Frame(self,bg=CREAM)
        
        Tabslabel=ctk.CTkLabel(self.toggle_menu_fm,text="Tabs",text_color=DARG,font=("AMCAP Eternal",30))
        Tabslabel.pack(side="top")
        

        window_height=self.winfo_height()
        
        self.toggle_menu_fm.place(x=0,y=52,height=window_height,width=200)

        self.toggle_btn.config(text="☰")
        self.toggle_btn.config(command=self.toggle_collapse)
        self.games=Tabs("Games",self,self.games_tab)
        self.chat=Tabs("Chat",self,self.chat_tab)
        self.friends=Tabs("Friends",self,self.games_tab)
        self.create=Tabs("Upload",self,self.create_tab)
        self.settings=Tabs("Settings",self,self.settings_tab)
        
    def show_games(self):
        for widget in self.games_tab.winfo_children():
            widget.destroy()

        games = get_games()
        self.num_games = len(games)
        self.max_columns = 7
        self.num_columns = min(self.max_columns, max(1, int(7))) 
        self.num_rows = (self.num_games + self.num_columns - 1) // self.num_columns

        canvas = tk.Canvas(self.games_tab,bg=DARG,bd=0,borderwidth=0)
        scrollbar = tk.Scrollbar(self.games_tab, orient="vertical", command=canvas.yview, bd=0,borderwidth=0)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack_forget()
        
        self.main_game_frame = tk.Frame(canvas, bg=DARG)  
        canvas.create_window((0, 0), window=self.main_game_frame, anchor="nw")
        self.main_game_frame.bind("<Configure>", lambda event, canvas=canvas: canvas.configure(scrollregion=canvas.bbox("all")))

        self.add_games(games)

        def _on_mouse_wheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mouse_wheel)

        self.games_tab.update_idletasks()  
        self.games.activate()

    def add_games(self,games,load = True):
        for widget in self.main_game_frame.winfo_children():
            try:widget.destroy()
            except:pass
        w = self.main_game_frame.winfo_screenwidth()
        if not w:w = 1440;1*w/1440
        for i, game in enumerate(games):
            game_frame = ctk.CTkFrame(self.main_game_frame,bg_color=DARG, width=190*w/1440, height=210*w/1440, corner_radius=10,fg_color=LARG,border_color=CREAM,border_width=BORR)  
            game_frame.pack_propagate(False)  

            game_name = game.get("game_name")
            author = game.get("username")
            game_main_file = game.get("main_file")
            playing_count = get_playing_count(game_name)
            try:
                description = game.get("description")
            except: description = 'Empty'
            icon_path = os.path.join(INFOLAB_SERVER_DIRECTORY, game.get("icon", ""))
            try:
                try:
                    img = Image.open(icon_path)
                    img = img.resize((int(150*w/1440),int(150*w/1440)))  
                    thumbnail = ImageTk.PhotoImage(img)
                except:thumbnail = None
                thumbnail_label = ctk.CTkLabel(game_frame, image=thumbnail, corner_radius=50, text='')
                thumbnail_label.pack(pady=(10*w/1440, 10*w/1440))
                name_label = tk.Label(game_frame, text=game_name, font=("Angrybirds", int(11*w/1440), "bold"),  fg=CREAM,background=LARG)
                name_label.pack(side='left')

                author_label = tk.Label(game_frame, text=f"-{author}", font=("Angrybirds", int(11*w/1440)), fg=CREAM,background=LARG)
                author_label.pack(side="right")

                thumbnail_label.bind("<Button-1>", lambda event, game_main_file=game_main_file,game_name=game_name,author=author,description=description,icon_path=icon_path: self.play_game(game_main_file,game_name,author,description,icon_path))
            except Exception as Error:print(Error)

            
            row_num = i // self.num_columns
            col_num = i % self.num_columns
            game_frame.grid(row=row_num, column=col_num, padx=7, pady=7, sticky="nsew")
        for i in range(self.num_rows):
            self.main_game_frame.grid_rowconfigure(i, weight=1) 
        for j in range(self.num_columns):
            self.main_game_frame.grid_columnconfigure(j, weight=1)
        time.sleep(10)
        threading.Thread(target=self.add_games,args=(get_games(),)).start()
        
    def set_theme(self,theme):
        global LALK,CREAM,DARG,LARG,GARG,BREW,MENT,TECK,DANG,BORR,THEME;THEME = theme
        LALK,CREAM,DARG,LARG,GARG,BREW,MENT,TECK,DANG,BORR = COLOUR_PALLETTE[THEME]
        data = load_local_data();data['theme'] = THEME;save_local_data(data)
        self.show_menu()
        self.settings.activate()

    def play_game(self, game_main_file,game_name,author,description,icon_path):
        game_main_file_path = os.path.join(INFOLAB_SERVER_DIRECTORY, game_main_file)
        game_dir = os.path.dirname(game_main_file_path)     
        try:
            for widget in self.Full_FM.winfo_children():
                try:widget.destroy()
                except:pass 
            self.Full_FM.destroy() 
        except:pass
        self.Full_FM =  tk.Frame(self.games_tab,bg=DARG,highlightbackground=CREAM,highlightcolor=CREAM,highlightthickness=BORR)
        nm_fm = tk.Frame(self.Full_FM,bg=DARG,highlightbackground=CREAM,highlightcolor=CREAM,highlightthickness=0)
        x = ctk.CTkButton(self.Full_FM,font=("AMCAP Eternal", 20), text_color=CREAM, fg_color=DARG, bg_color=DARG,corner_radius=10,text = '<<',command=self.Full_FM.destroy,anchor='w',hover=True,hover_color=DARG)
        x.pack(padx=40,expand=True,fill=tk.X)
        nm_fm.pack(expand=True,fill=tk.X)
        gfm = tk.Frame(self.Full_FM,bg=DARG,highlightbackground=CREAM,highlightcolor=CREAM,highlightthickness=BORR)
        ggfm = tk.Frame(gfm,bg=DARG)
        main_fm = tk.Frame(ggfm,bg=DARG)
        sub_fm = tk.Frame(ggfm,bg=DARG)
        ss_fm=tk.Frame(main_fm,bg=DARG)
        new_gamename = ctk.CTkLabel(ss_fm,font=("AMCAP Eternal", 25, "bold"), text_color=CREAM, fg_color=GARG, bg_color=DARG,corner_radius=10,text = game_name,width=430,height=30)
        new_gamename.pack(padx=10,pady=10)
        description_box = ctk.CTkTextbox(ss_fm,font=("Cascadia Code", 16), text_color=CREAM, fg_color=GARG, bg_color=DARG,corner_radius=10,border_color=CREAM,border_width=BORR,width=430,height=230)
        description_box.pack(padx=10)
        description_box.insert('1.0',description)
        description_box.configure(state = tk.DISABLED)
        temp_fm = ctk.CTkFrame(ss_fm,bg_color=DARG,fg_color=GARG,corner_radius=10,border_color=CREAM,border_width=BORR)
        ctk.CTkLabel(master=temp_fm, text=f"Creator: {author}", font=("Cascadia Code", 20,"bold"), text_color=CREAM, fg_color=GARG,bg_color=DARG,).pack(side=tk.RIGHT,padx=10,pady=3)
        temp_fm.pack(expand=True,fill=tk.X,padx=10,pady=10)
        temp2_fm = ctk.CTkFrame(ss_fm,bg_color=DARG,fg_color=GARG,corner_radius=10,border_color=CREAM,border_width=BORR)
        ctk.CTkLabel(master=temp2_fm, text=f"Permissions:", font=("Cascadia Code", 16,), text_color=CREAM, fg_color=GARG,bg_color=DARG,).pack(side=tk.LEFT,padx=10,pady=3)
        try:
            img = Image.open(os.path.join(ICONS_DIR,'download123.png'))
            img = img.resize((30,30))  
            thumbnail1 = ImageTk.PhotoImage(img)
        except:thumbnail1 = None
        try:
            img = Image.open(os.path.join(ICONS_DIR,'download2.png'))
            img = img.resize((30,30))  
            thumbnail2 = ImageTk.PhotoImage(img)
        except:thumbnail2 = None
        imgs=[thumbnail1,thumbnail2]
        def download_folder():
                try:
                    folder =  filedialog.askdirectory(title=f"Save {game_name} to folder")
                    t = game_main_file.split('\\')[0];print(INFOLAB_SERVER_DIRECTORY+'\\'+t)
                    shutil.copytree(INFOLAB_SERVER_DIRECTORY+'\\'+t,folder+'\\'+t, dirs_exist_ok=True)
                    
                except:print('Error downloading')
        downloadable = ctk.CTkButton(temp2_fm,text='downloadable', font=("Cascadia Code", 14),command=download_folder,text_color=CREAM, image = thumbnail1,fg_color=GARG, bg_color=GARG,hover_color=BREW,border_width=0,width=50)
        downloadable.pack(side=tk.RIGHT,padx=4)
        try:
            img = Image.open(os.path.join(ICONS_DIR,'view.png')).resize((30,30)) 
            thumbnail1 = ImageTk.PhotoImage(img)
        except:thumbnail1 = None
        view = ctk.CTkButton(temp2_fm,text='view', font=("Cascadia Code", 14),text_color=CREAM, image = thumbnail1,fg_color=GARG, bg_color=GARG,hover_color=BREW,border_width=0,width=50)
        view.pack(side=tk.RIGHT,padx=3,pady=2)
        temp2_fm.pack(expand=True,fill=tk.X,padx=10,pady=2)
        try:     
            img = Image.open(icon_path)
            img = img.resize((300,300))  
            thumbnail = ImageTk.PhotoImage(img)
        except:thumbnail=None
        def run_game():
            self.update_playing_count(game_main_file, 1)
            os.chdir(game_dir)
            
            print(game_dir,game_main_file_path,sep='\n')
            python_executable = sys.executable 
            try:subprocess.Popen([python_executable, game_main_file_path])
            except Exception as error:messagebox.showerror("Error Running Code", f"{error}")
        icon = ctk.CTkButton(sub_fm,text='', font=("AMCAP Eternal", 30), text_color=DARG, fg_color=DARG, bg_color=DARG, image=thumbnail, hover_color=BREW,border_color=CREAM,border_width=BORR,height=320,width=320,state=tk.DISABLED)
        icon.pack(pady=0)
        self.test = ctk.CTkButton(sub_fm,text='PLAY', font=("AMCAP Eternal", 20), text_color=GARG, fg_color='#779966', bg_color=DARG,hover_color="#99AFAA",border_width=0,height=50,width=320,command=run_game)
        self.test.pack(pady=10)
        gfm.pack(padx=20,pady=10)
        ggfm.pack(expand=True,fill=tk.Y,padx=5,pady=5)
        sub_fm.pack(side="left",expand=True,fill=tk.Y,padx=5,pady=5)
        main_fm.pack(side="left",expand=True,fill=tk.Y,padx=5,pady=5)
        ss_fm.pack()
        self.Full_FM.place(relx=0.5,rely=0.5,anchor='center')


    def update_playing_count(self, game_name, count_change):
        client = connect_to_server()
        request = {"action": "update_playing_count", "game_name": game_name, "count_change": count_change}
        client.send(pickle.dumps(request))
        client.close()

    def show_create(self):
        for widget in self.create_tab.winfo_children():
            widget.destroy()

        def select_icon():
            self.game_icon = filedialog.askopenfilename(title="Select Game Icon", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
            img = Image.open(self.game_icon)
            img = img.resize((300,300))  
            thumbnail = ImageTk.PhotoImage(img)
            icon.configure(text='');icon.configure(image=thumbnail)
        def enable(event=None,num=0):
            if num==0:gfm.pack(padx=20,pady=10);self.after(0,lambda:enable(num=1))
            if num==1:ggfm.pack(expand=True,fill=tk.Y,padx=5,pady=5);self.after(0,lambda:enable(num=2))
            if num==2:sub_fm.pack(side="left",expand=True,fill=tk.Y,padx=5,pady=5);self.after(400,lambda:enable(num=3))
            if num==3:main_fm.pack(side="left",expand=True,fill=tk.Y,padx=5,pady=5);self.after(400,lambda:enable(num=4))
            if num==4:select_folder_fm.pack(expand=True,fill=tk.X,);self.after(400,lambda:enable(num=5))
            if num==5:select_code_fm.pack(expand=True,fill=tk.X,)
        def disable(event):gfm.pack_forget();sub_fm.pack_forget();main_fm.pack_forget();select_folder_fm.pack_forget();select_code_fm.pack_forget()
        def test():
            game_dir = os.path.dirname(self.code._text) 
            os.chdir(game_dir)
            python_executable = sys.executable 
            subprocess.Popen([python_executable, self.code._text])
        create_fm = tk.Frame(self.create_tab,bg=DARG)
        fm = tk.Frame(create_fm,bg=GARG,highlightbackground=CREAM,highlightcolor=CREAM,highlightthickness=BORR)
        upload_fm = tk.Frame(fm,bg=GARG,width=400)
        upload_button=ctk.CTkButton(upload_fm, text="UPLOAD", command=self.upload_game_window, font=("AMCAP Eternal", 25), text_color=CREAM, fg_color=GARG, bg_color=GARG, corner_radius=10, hover_color=BREW,hover=True,border_color=CREAM,border_width=BORR)
        upload_button.bind('<Enter>',lambda event:enable(event))
        create_fm.bind('<Leave>',lambda event:disable(event))
        create_label = tk.Label(master=upload_fm, text='Upload Your Game', font=("AMCAP Eternal", 25,"bold"), foreground=CREAM, background=GARG)
        
        create_label.pack(side=tk.LEFT)
        upload_button.pack(side=tk.RIGHT)
        tk.Label(master=upload_fm, text='', font=("AMCAP Eternal", 25,"bold"), foreground=CREAM, background=GARG,).pack(side=tk.LEFT,padx=150)
        upload_fm.pack(expand=True,fill=tk.X,padx=20,pady=10)
        gfm = tk.Frame(fm,bg=DARG,highlightbackground=CREAM,highlightcolor=CREAM,highlightthickness=BORR)
        ggfm = tk.Frame(gfm,bg=DARG)
        main_fm = tk.Frame(ggfm,bg=DARG)
        sub_fm = tk.Frame(ggfm,bg=DARG)
        ss_fm=tk.Frame(main_fm,bg=DARG)
        self.new_gamename = ctk.CTkEntry(ss_fm,font=("AMCAP Eternal", 25, "bold"), text_color=CREAM, fg_color=GARG, bg_color=DARG,corner_radius=10,placeholder_text='GAME NAME',placeholder_text_color=CREAM,border_color=CREAM,border_width=BORR,width=430,height=30)
        self.new_gamename.pack(padx=10,pady=10)
        self.description = ctk.CTkTextbox(ss_fm,font=("Cascadia Code", 16), text_color=CREAM, fg_color=GARG, bg_color=DARG,corner_radius=10,border_color=CREAM,border_width=BORR,width=430,height=230)
        self.description.pack(padx=10)
        self.description.insert('1.0','<description>')
        temp_fm = ctk.CTkFrame(ss_fm,bg_color=DARG,fg_color=GARG,corner_radius=10,border_color=CREAM,border_width=BORR)
        ctk.CTkLabel(master=temp_fm, text=f"Creator: {load_local_data()['username']}", font=("Cascadia Code", 20,"bold"), text_color=CREAM, fg_color=GARG,bg_color=DARG,).pack(side=tk.RIGHT,padx=10,pady=3)
        temp_fm.pack(expand=True,fill=tk.X,padx=10,pady=10)
        temp2_fm = ctk.CTkFrame(ss_fm,bg_color=DARG,fg_color=GARG,corner_radius=10,border_color=CREAM,border_width=BORR)
        ctk.CTkLabel(master=temp2_fm, text=f"Permissions:", font=("Cascadia Code", 16,), text_color=CREAM, fg_color=GARG,bg_color=DARG,).pack(side=tk.LEFT,padx=10,pady=3)
        try:
            img = Image.open(os.path.join(ICONS_DIR,'download123.png'))
            img = img.resize((30,30))  
            thumbnail1 = ImageTk.PhotoImage(img)
        except:thumbnail1 = None
        try:
            img = Image.open(os.path.join(ICONS_DIR,'download2.png'))
            img = img.resize((30,30))  
            thumbnail2 = ImageTk.PhotoImage(img)
        except:thumbnail2 = None
        imgs=[thumbnail1,thumbnail2]
        mode_var = {'downloadable':'Not downloadable','Not downloadable':'downloadable'}
        def change_img():self.downloadable.configure(image=imgs[1],text=mode_var[self.downloadable._text]);imgs.reverse()
        self.downloadable = ctk.CTkButton(temp2_fm,text='downloadable', font=("Cascadia Code", 14),command=change_img,text_color=CREAM, image = thumbnail1,fg_color=GARG, bg_color=GARG,hover_color=BREW,border_width=0,width=50)
        self.downloadable.pack(side=tk.RIGHT,padx=4)
        try:
            img = Image.open(os.path.join(ICONS_DIR,'view.png')).resize((30,30)) 
            thumbnail1 = ImageTk.PhotoImage(img)
        except:thumbnail1 = None
        self.view = ctk.CTkButton(temp2_fm,text='view', font=("Cascadia Code", 14),text_color=CREAM, image = thumbnail1,fg_color=GARG, bg_color=GARG,hover_color=BREW,border_width=0,width=50)
        self.view.pack(side=tk.RIGHT,padx=3,pady=2)
        temp2_fm.pack(expand=True,fill=tk.X,padx=10,pady=2)
        self.game_icon = os.path.join(ICONS_DIR,'default.png') 
        try:     
            img = Image.open(os.path.join(ICONS_DIR,'default.png'))
            img = img.resize((300,300))  
            thumbnail = ImageTk.PhotoImage(img)
        except:thumbnail=None
        icon = ctk.CTkButton(sub_fm,text='', command=select_icon, font=("AMCAP Eternal", 30), text_color=DARG, fg_color=DARG, bg_color=DARG, image=thumbnail, hover_color=BREW,border_color=CREAM,border_width=BORR,height=320,width=320)
        icon.pack(pady=0)
        self.test = ctk.CTkButton(sub_fm,text='TEST', font=("AMCAP Eternal", 20), text_color=GARG, fg_color='#779966', bg_color=DARG,hover_color="#99AFAA",border_width=0,height=50,width=320,command=lambda:test())
        self.test.pack(pady=10)
        def select_folder():
            self.folder.configure(text=filedialog.askdirectory(title="Select Folder containing CODE and ASSETS"))
        select_folder_fm = tk.Frame(gfm,bg=DARG,)
        ctk.CTkButton(select_folder_fm, text="select Folder", command=select_folder, font=("AMCAP Eternal", 16), text_color=CREAM, fg_color=GARG, bg_color=DARG, corner_radius=10,border_color=CREAM,border_width=BORR, hover_color=BREW,hover=True,).pack(side=tk.RIGHT,padx=20)
        self.folder = ctk.CTkLabel(select_folder_fm,font=("Cascadia Code", 16), text_color=CREAM, fg_color=DARG, bg_color=DARG,corner_radius=10,text='Select Your Game Folder',anchor='w',width=400)
        self.folder.pack(expand=True,padx=10,pady=10,side=tk.LEFT,fill=tk.X)
        def select_code():
            try:self.code.configure(text=filedialog.askopenfilename(title="Select Python code file", initialdir=self.folder._text))
            except:self.code.configure(text="Select Folder first")
        select_code_fm = tk.Frame(gfm,bg=DARG,)
        ctk.CTkButton(select_code_fm, text="Select Code", command=select_code, font=("AMCAP Eternal", 16), text_color=CREAM, fg_color=GARG, bg_color=DARG, corner_radius=10,border_color=CREAM,border_width=BORR, hover_color=BREW,hover=True,).pack(side=tk.RIGHT,padx=20)
        self.code = ctk.CTkLabel(select_code_fm,font=("Cascadia Code", 16), text_color=CREAM, fg_color=DARG, bg_color=DARG,corner_radius=10,text='Select Code from the above folder',anchor='w',width=400)
        self.code.pack(expand=True,padx=10,pady=10,side=tk.LEFT,fill=tk.X)
        ss_fm.pack()
        fm.pack(pady=30)
        create_fm.pack()
        mygames_label = tk.Label(master=create_fm, text='  My Games', font=("AMCAP Eternal", 25,"bold"), foreground=CREAM, background=GARG,anchor='w',highlightbackground=CREAM,highlightcolor=CREAM,highlightthickness=BORR)
        mygames_label.pack(expand=True,fill=tk.X,pady=10)

        games = get_games()
        self.local_data=load_local_data()
        for game in games:
            if game.get("username") == self.local_data['username']:
                try:
                    img = Image.open(os.path.join(INFOLAB_SERVER_DIRECTORY,game.get('icon')))
                    img = img.resize((50,50))  
                    thumbnail1 = ImageTk.PhotoImage(img)
                except:thumbnail1 = None
                game_frame = ctk.CTkFrame(create_fm,fg_color=LARG,border_color=CREAM,border_width=BORR)
                game_frame.pack(fill="x", pady=3)
                game_name = game.get("game_name")  
                game_label=ctk.CTkLabel(game_frame,font=("AMCAP Eternal", 25), text='',image=thumbnail1, fg_color=LARG,text_color=CREAM,anchor='w')
                game_label.pack(side="left",padx=20,pady=5)
                game_label=ctk.CTkLabel(game_frame,font=("AMCAP Eternal", 25), text=game_name, fg_color=LARG,text_color=CREAM,anchor='w')
                game_label.pack(side="left",padx=20,pady=5)
                reupload = ctk.CTkButton(game_frame, text="Reupload", command=lambda g=game_name: self.reupload_game_window(g), font=("AMCAP Eternal", 21), text_color=CREAM, fg_color=GARG, bg_color=LARG, corner_radius=10,border_color=CREAM,border_width=BORR, hover_color=BREW,hover=True,)
                delete = ctk.CTkButton(game_frame, text="Delete", command=lambda g=game_name: self.delete_game(g),font=("AMCAP Eternal", 21), text_color=DANG, fg_color=GARG, bg_color=LARG, corner_radius=10,border_color=DANG,border_width=2, hover_color=BREW,hover=True,)
                rename = ctk.CTkButton(game_frame, text="Rename", command=lambda g=game_name: self.rename_game_window(g), font=("AMCAP Eternal", 21),text_color=CREAM, fg_color=GARG, bg_color=LARG, corner_radius=10,border_color=CREAM,border_width=BORR, hover_color=BREW,hover=True,)
                delete.pack(side=tk.RIGHT,padx=3)
                reupload.pack(side=tk.RIGHT,padx=3)
                rename.pack(side=tk.RIGHT,padx=3)

    def show_settings(self):
        for widget in self.settings_tab.winfo_children():
            widget.destroy()

        settings_fm = ctk.CTkFrame(self.settings_tab,fg_color=DARG)
        settings_fm.pack(expand=False,fill=tk.Y)
        SET_fm = ctk.CTkFrame(settings_fm,fg_color=GARG,border_color=CREAM,border_width=BORR)
        SET_label = tk.Label(master=SET_fm, text='SETTINGS', font=("AMCAP Eternal", 30,"bold"), fg=CREAM, bg=GARG,anchor='w',width=25)
        SET_label.pack(expand=True,fill=tk.X,padx=20,pady=10)

        SET_fm.pack(expand=True,fill=tk.X,pady=20)

        personalize_fm = ctk.CTkFrame(settings_fm,fg_color=GARG,border_color=CREAM,border_width=BORR)
        personalize_label = ctk.CTkLabel(master=personalize_fm, text='PERSONALIZE', font=("AMCAP Eternal", 30,"bold"), text_color=CREAM, fg_color=GARG,anchor='w')
        personalize_label.pack(expand=True,fill=tk.X,padx=20,pady=10)

        theme_fm = ctk.CTkFrame(personalize_fm,fg_color=DARG,border_color=CREAM,border_width=BORR)
        theme_label = ctk.CTkLabel(master=theme_fm, text='THEMES', font=("AMCAP Eternal", 25,"bold"), text_color=CREAM, fg_color=DARG)
        theme_label.pack(expand=True,fill=tk.X,padx=30,pady=10)
        themes_buttons = []

        for theme in COLOUR_PALLETTE.keys():
            button = ctk.CTkButton(theme_fm,text=theme,font=("Cascadia Code", 20, "bold"), text_color=CREAM, fg_color=DARG,border_color=CREAM,border_width=0,hover=True,hover_color=BREW)
            if theme == THEME:button.configure(border_width=2,fg_color=GARG)
            themes_buttons.append(button)
            def update_button_colors(button:ctk.CTkButton):
                for button_THEME in themes_buttons:
                    button_THEME.configure(border_width=0,fg_color=DARG)
                theme_label.configure(text='Loading')    
                button.configure(border_width=2,fg_color=GARG)
                self.after(10,lambda:self.set_theme(button._text))
            button.configure(command=lambda b=button: update_button_colors(b))
            button.pack(expand=True, fill=tk.X,pady=5,padx=20)

        INFO_fm = ctk.CTkFrame(settings_fm,fg_color=GARG,border_color=CREAM,border_width=BORR)
        INFO_label = ctk.CTkLabel(master=INFO_fm, text='INFO', font=("AMCAP Eternal", 30,"bold"), text_color=CREAM, fg_color=GARG,anchor='w')
        INFO_label.pack(expand=True,fill=tk.X,padx=20,pady=10)
        INFO_sub_fm = ctk.CTkFrame(INFO_fm,fg_color=DARG,border_color=CREAM,border_width=BORR)
        s1 = ctk.CTkFrame(INFO_sub_fm,fg_color=DARG,border_color=CREAM,border_width=0)
        ctk.CTkLabel(s1, text="Author", font=("Cascadia Code", 17,'bold'), text_color=CREAM, fg_color=DARG, bg_color=DARG, corner_radius=10).pack(padx=5,side=tk.LEFT)
        ctk.CTkLabel(s1, text="~ Aayush Paikaray", font=("Cascadia Code", 17), text_color=CREAM, fg_color=DARG, bg_color=DARG, corner_radius=10).pack(padx=5,side=tk.RIGHT)
        s1.pack(expand=True,fill=tk.X,padx=3,pady=3)
        s1 = ctk.CTkFrame(INFO_sub_fm,fg_color=DARG,border_color=CREAM,border_width=0)
        ctk.CTkLabel(s1, text="Version 3.0", font=("Cascadia Code", 17,'bold'), text_color=CREAM, fg_color=DARG, bg_color=DARG, corner_radius=10).pack(padx=5,side=tk.LEFT)
        ctk.CTkLabel(s1, text="Batch ~ ETERNALS 24-25", font=("Cascadia Code", 17), text_color=CREAM, fg_color=DARG, bg_color=DARG, corner_radius=10).pack(padx=5,side=tk.RIGHT)
        s1.pack(expand=True,fill=tk.X,padx=3,pady=3)
        INFO_sub_fm.pack(expand=True,fill=tk.X,padx=20,pady=10)

        theme_fm.pack(expand=True,fill=tk.X,padx=20,pady=10)

        personalize_fm.pack(expand=True,fill=tk.X,pady=10)
        

        def LOG_OUT():
            data = load_local_data()
            load_local_data()['username'],load_local_data()['password'] = None,None
            self.show_login()
        security_fm = ctk.CTkFrame(settings_fm,fg_color=GARG,border_color=CREAM,border_width=BORR)
        security_label = ctk.CTkLabel(master=security_fm, text='SECURITY', font=("AMCAP Eternal", 30,"bold"), text_color=CREAM, fg_color=GARG,anchor='w')
        security_label.pack(expand=True,fill=tk.X,padx=20,pady=10)
        security_fm.pack(expand=True,fill=tk.X,pady=10)
        sub_fm = ctk.CTkFrame(security_fm,fg_color=DARG,border_color=CREAM,border_width=BORR)
        logout = ctk.CTkButton(sub_fm, text="logout", command=LOG_OUT,font=("AMCAP Eternal", 21), text_color=DANG, fg_color=GARG, bg_color=DARG, corner_radius=10,border_color=DANG,border_width=2, hover_color=BREW,hover=True,)
        change_pass = ctk.CTkButton(sub_fm, text="Change Password", font=("AMCAP Eternal", 21),text_color=CREAM, fg_color=GARG, bg_color=DARG, corner_radius=10,border_color=CREAM,border_width=BORR, hover_color=BREW,hover=True,)
        change_pass.pack(expand=True,fill=tk.X,padx=20,pady=10)
        logout.pack(expand=True,fill=tk.X,padx=20,pady=10)
        sub_fm.pack(expand=True,fill=tk.X,padx=20,pady=10)

        INFO_fm.pack(expand=True,fill=tk.X,pady=10)

    def reupload_game_window(self, game_name):
        game_dir = filedialog.askdirectory(title="Select Game Directory")
        if game_dir:
            game_main_file = filedialog.askopenfilename(title="Select Main Game File", initialdir=game_dir)
            game_icon = filedialog.askopenfilename(title="Select Game Icon", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
            if game_main_file and game_icon:
                if reupload_game(self.local_data["username"], game_name, game_dir, game_main_file, game_icon):
                    messagebox.showinfo("Success", "Game reuploaded successfully")
                    self.show_create()
                else:
                    messagebox.showerror("Error", "Failed to reupload game")

    def delete_game(self, game_name):
        if delete_game(load_local_data()["username"], game_name):
            messagebox.showinfo("Success", "Game deleted successfully")
            self.show_create()
        else:
            messagebox.showerror("Error", "Failed to delete game")

    def rename_game_window(self, game_name):
        new_name = simpledialog.askstring("Rename Game", "Enter new game name:")
        if new_name:
            if rename_game(self.local_data["username"], game_name, new_name):
                messagebox.showinfo("Success", "Game renamed successfully")
                self.show_create()
            else:
                messagebox.showerror("Error", "Failed to rename game")

    def upload_game_window(self):
        game_name = self.new_gamename.get()
        game_dir = self.folder._text
        game_main_file = self.code._text
        game_icon = self.game_icon
        description = self.description.get('1.0',ctk.END)
        download = 'downloadable'== self.downloadable._text
        view = True
        if game_name and game_main_file and game_icon and game_dir:
            if upload_game(self.local_data["username"], game_name, game_dir, game_main_file, game_icon, description, download, view):
                messagebox.showinfo("Success", "Game uploaded successfully")
                self.show_create()
            else:
                messagebox.showerror("Error", "Failed to upload game")

    def show_chat(self):
        for widget in self.chat_tab.winfo_children():
            widget.destroy()
        root = self.chat_tab
        client = ChatClient(root)
        # root.mainloop()

class ChatClient:
    current = []
    def __init__(self, root):
        for i in ChatClient.current:
            i.lobby.close()
            for port in i.tabs.keys():i.tabs[port]["socket"].close()

        self.root = root
        self.lobby = self.connect_to_lobby()

        self.main_frame = tk.Frame(root,)
        self.head_frame=ctk.CTkFrame(master=self.main_frame,bg_color=TECK,border_color=CREAM,border_width=BORR, )

        self.toggle_menu_fm=tk.Frame(root,bg=TECK,highlightbackground=CREAM,highlightcolor=CREAM,highlightthickness=BORR)

        Tabslabel=ctk.CTkLabel(self.toggle_menu_fm,text="GROUPS",text_color=MENT,font=("AMCAP Eternal",19))
        Tabslabel.pack(side=tk.TOP)
        
        self.toggle_menu_fm.pack(side='left',fill=tk.Y, )
        self.main_frame.pack(side='left',fill=tk.BOTH, expand=True)
        self.tabs = {}
        mode_var = {'PUBLIC':'PRIVATE','PRIVATE':'PUBLIC',LARG:CREAM,CREAM:LARG}
        self.create_group_fm = ctk.CTkFrame(self.main_frame,bg_color=LARG,fg_color=LARG)
        self.create_group_tab = CTabs('',self,self.create_group_fm,add_button=False)   
        ChatClient.current.append(self)

        def check_group_create():
            group_name = self.name_entry.get()
            admin = load_local_data()['username']
            group_members = []
            def player_filter(button):
                if button['background']==CREAM:return True
                else:return False 
            for user in self.player_buttons.keys():
                if player_filter(self.player_buttons[user]):group_members.append(user)
            mode_fun = lambda:self.mode_button['text']=='PUBLIC'
            port = create_group(group_name=group_name,group_members=group_members,group_mode=mode_fun(),admin=admin)
            if not port:self.name_entry['text'] = 'GROUP EXIST'
            else:self.add_chat_tab({'group_name':group_name,'group_members':group_members,'group_mode':mode_fun(),'admin':admin,'PORT':port})
                
        self.main_fm = ctk.CTkFrame(self.create_group_fm,bg_color=LARG,fg_color=LARG) 
        self.name_fm = ctk.CTkFrame(self.main_fm,bg_color=LARG,corner_radius=10,fg_color=LARG)
        self.name_label = ctk.CTkLabel(self.name_fm, corner_radius=50,font=("Angrybirds", 27, "bold"), text='Group Name ',bg_color=LARG,fg_color=LARG,text_color=CREAM)
        self.name_entry = ctk.CTkEntry(self.name_fm, corner_radius=50,font=("Angrybirds", 27, "bold"),bg_color=LARG,fg_color=CREAM,text_color=DARG,border_color=CREAM,border_width=BORR, )
        self.conf_label = ctk.CTkLabel(self.main_fm, corner_radius=50,font=("Angrybirds", 30, "bold"), text='Configure',bg_color=LARG,fg_color=LARG,text_color=CREAM)
        self.mode_fm = ctk.CTkFrame(self.main_fm,bg_color=LARG,corner_radius=10,fg_color=LARG)
        self.mode_label = ctk.CTkLabel(self.mode_fm, corner_radius=50,font=("Angrybirds", 24, "bold"), text='Set Mode ',bg_color=LARG,fg_color=LARG,text_color=CREAM)
        self.mode_button = tk.Button(self.mode_fm,font=("Angrybirds", 22, "bold"),text='PUBLIC',bg=CREAM,fg=DARG,command=lambda :self.mode_button.configure(text=mode_var[self.mode_button['text']]))
        self.crt_button = tk.Button(self.mode_fm,font=("Angrybirds", 22, "bold"),text='CONFIRM CREATE',bg=CREAM,fg=DARG,command=check_group_create)

        self.c_fm = ctk.CTkFrame(self.create_group_fm,bg_color=LARG,corner_radius=10,fg_color=LARG,)
        canvas = tk.Canvas(self.c_fm,bg=DARG,bd=0,borderwidth=0)
        scrollbar = tk.Scrollbar(self.c_fm, orient="vertical", command=canvas.yview, bd=0,borderwidth=0)
        players = get_players()
        
        self.main_game_frame = tk.Frame(canvas, bg=DARG)  
        canvas.create_window((0, 0), window=self.main_game_frame, anchor="nw")
        self.main_game_frame.bind("<Configure>", lambda event, canvas=canvas: canvas.configure(scrollregion=canvas.bbox("all")))
        num_columns = 1 ; num_rows = len(players); self.player_buttons={}
        for user in players:
            player_fm = ctk.CTkFrame(self.main_game_frame, bg_color=DARG, corner_radius=10, fg_color=LARG, height=25,border_color=CREAM,border_width=BORR, )
            player_fm.pack_propagate(False)
            button = tk.Button(player_fm,text=user,font=("Angrybirds", 20, "bold"),fg=CREAM,background=LARG)
            def update_button_colors(button):
                current_bg = button['background']
                current_fg = button['fg']
                button.configure(
                    background=mode_var[current_bg],
                    fg=mode_var[current_fg]
                )
            button.configure(command=lambda b=button: update_button_colors(b))

            self.player_buttons[user] = button

            button.pack(expand=True, fill=tk.X)
            player_fm.pack()

        for i in range(num_rows):
            self.main_game_frame.grid_rowconfigure(i, weight=1) 
        for j in range(num_columns):
            self.main_game_frame.grid_columnconfigure(j, weight=1)
        
        self.name_label.pack()
        self.name_entry.pack(expand=True,fill=tk.X,pady = 40,padx = 40)
        self.name_fm.pack(expand=True,fill=tk.X)
        self.conf_label.pack()
        self.mode_label.pack(side='left',padx = 40)
        self.mode_button.pack(side='left')
        self.mode_fm.pack(side=tk.TOP,expand=True,fill=tk.X)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.configure(yscrollcommand=scrollbar.set)
        self.c_fm.pack(side='right',fill=tk.Y,expand=True)
        self.crt_button.pack()
        self.main_fm.pack(side="left", fill="both", expand=True)
       


        self.create_btn=ctk.CTkButton(self.head_frame, text='create group +', bg_color=TECK, fg_color=TECK,text_color=MENT,
                                   font=("AMCAP Eternal", 20,),command=self.create_group_tab.activate,hover_color=BREW,border_width=BORR,border_color=MENT)
        self.create_btn.pack(side=tk.RIGHT, fill=tk.Y, anchor=tk.W)
        self.label=tk.Label(master=self.head_frame, text="GROUP CHAT", font=("AMCAP Eternal", 20,"bold"), fg=MENT, bg=TECK,highlightbackground=MENT,highlightcolor=MENT,highlightthickness=BORR,borderwidth=0)
        self.label.pack(expand=True, fill="x",side=tk.TOP)
        
        self.head_frame.pack(side="top", fill="x")

        for i in get_groups():self.add_chat_tab(i)

    def connect_to_lobby(self):
        lobby = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            lobby.connect((HOST, __PORT__))
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect to the lobby: {e}")
            self.root.destroy()
        return lobby
    
    def add_chat_tab(self,details):
        port = details.get('PORT')
        tab = ttk.Frame(self.main_frame)
        self.temp = CTabs(details.get('group_name'),self,tab)

        members = 'MEMBERS\n'+'\n'.join(details.get('group_members'))
        def show_members(event):
            member_button['text'] = members
        def hide_members(event):
            member_button['text'] = "MEMBERS"
            leave_button.pack_forget()
            if is_admin.get():delete_button.pack_forget()
        def show_settings(event):
            leave_button.pack()
            if is_admin.get():delete_button.pack()
            
        def leave():
            leave_group(load_local_data()['username'],port)
            time.sleep(2)
            self.tabs[port]["socket"].close()
            input_entry.configure(state=tk.DISABLED)

        def delete_grp():
            delete_group(details.get('PORT'))
            time.sleep(2)
            self.tabs[port]["socket"].close()
            input_entry.configure(state=tk.DISABLED)

        settings=tk.Frame(master=tab,background=LARG,highlightbackground=CREAM,highlightcolor=CREAM,highlightthickness=BORR,borderwidth=0)
        setting_frame = tk.Frame(master=settings,background=LARG,highlightbackground=CREAM,highlightcolor=CREAM,highlightthickness=BORR)
        setting_label = tk.Label(master=setting_frame, text='SETTINGS', font=("AMCAP Eternal", 14), foreground=CREAM, background=LARG,width=12)
        setting_label.pack()
        leave_button = ctk.CTkButton(setting_frame, text="Leave", command=leave, font=("AMCAP Eternal", 20), text_color=CREAM, fg_color=DARG, bg_color=LARG, corner_radius=10, border_color=CREAM,border_width=BORR, hover_color=BREW,)
        is_admin = tk.BooleanVar(value=False)
        if load_local_data()['username']==details.get('admin') :
            is_admin.set(True)
            delete_button = ctk.CTkButton(setting_frame, text="DELETE", command=delete_grp, font=("AMCAP Eternal", 20), text_color=DANG, fg_color=DARG, bg_color=LARG, corner_radius=10,border_color=CREAM,border_width=BORR,  hover_color=BREW,)
        setting_frame.pack(side=tk.RIGHT)
        member_button = tk.Label(master=settings, text='MEMBERS', font=("AMCAP Eternal", 14), foreground=CREAM, background=LARG,highlightbackground=CREAM,highlightcolor=CREAM,highlightthickness=BORR,width=12)
        member_button.pack(side=tk.RIGHT)
        
        online = tk.Label(master=settings, text='', font=("AMCAP Eternal", 14), foreground=CREAM, background=LARG)
        online.pack(side=tk.LEFT)
        settings.pack(expand=True, fill="x",side=tk.TOP)

        member_button.bind('<Enter>',lambda event:show_members(event))
        setting_label.bind('<Enter>',lambda event:show_settings(event))
        chat_display = tk.Text(tab, state=tk.DISABLED, wrap=tk.WORD, font=("AMCAP Eternal", 18), fg=TECK, background=MENT,highlightbackground=CREAM,highlightcolor=CREAM,highlightthickness=BORR)
        
        member_button.bind('<Leave>',lambda event:hide_members(event))

        input_frame = ctk.CTkFrame(tab, fg_color=MENT,border_color=CREAM,border_width=BORR, )
        input_frame.pack(fill=tk.X, side=tk.BOTTOM, expand=True)

        input_text = tk.StringVar()
        input_entry = ctk.CTkEntry(input_frame, textvariable=input_text, font=("AMCAP Eternal", 25, "bold"), text_color=MENT, fg_color=TECK, bg_color=MENT,corner_radius=10,placeholder_text='chat with your friends',placeholder_text_color=MENT,border_color=CREAM,border_width=BORR, )
        
        input_entry.pack(fill=tk.X, side=tk.LEFT, expand=True,padx=5)
        chat_display.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        input_entry.bind('<Return>', lambda event: self.send_message(port, input_text.get()))

        send_button = ctk.CTkButton(input_frame, text="Send", command=lambda: self.send_message(port, input_text.get()), font=("AMCAP Eternal", 25), text_color=MENT, fg_color=TECK, bg_color=MENT, corner_radius=10,border_color=CREAM,border_width=BORR,  hover_color=BREW,)
        send_button.pack(side=tk.RIGHT,padx=5)

        self.tabs[port] = {"frame": tab, "display": chat_display, "input": input_text, "online": online, "socket": None}

        self.connect_to_server(port)

    
    def connect_to_server(self, port):
            
            self.lobby.send(pickle.dumps(port))
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((HOST, port))
            self.tabs[port]["socket"] = client
            threading.Thread(target=self.receive_message, args=(port,)).start()
    
    def receive_message(self, port):
        client = self.tabs[port]["socket"]
        while True:
            try:
                message = pickle.loads(client.recv(2048))
                if message.split(':')[0].lower() == 'online':
                    self.tabs[port]["online"]['text']=message
                else:self.update_chat_display(port, message)
            except:
                break
    
    def send_message(self, port, message):
        client = self.tabs[port]["socket"]
        if client:
            try:
                client.sendall(pickle.dumps(message))
                self.tabs[port]["input"].set("")
            except:
                messagebox.showerror("Send Error", f"Failed to send message to port {port}")
    
    def update_chat_display(self, port, message):
        chat_display = self.tabs[port]["display"]
        chat_display.config(state=tk.NORMAL)
        chat_display.insert(tk.END, message + "\n")
        chat_display.config(state=tk.DISABLED)
        chat_display.see(tk.END)       



Application().mainloop()


    