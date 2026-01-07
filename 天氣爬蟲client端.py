import threading
import socket
import json
import tkinter as tk
from tkinter import ttk, messagebox

# --- 設定連線資訊 ---
BUFFER_SIZE = 4096
remote_addr = ('192.168.1.108', 6543) # 請根據您的 Server IP 修改

class WeatherOnlyClient:
    def __init__(self, master):
        self.master = master
        self.master.title("CWA 縣市天氣查詢系統")
        self.master.geometry("600x450")
        
        # 1. 建立連線 (僅需基本登入，不需要綽號用於聊天，但 Server 協定仍要求 type 1)
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect(remote_addr)
            self.f = self.sock.makefile(encoding='utf-8')
            self.login_server()
        except ConnectionRefusedError:
            messagebox.showerror("連線失敗", "無法連接到伺服器，請確認 Server 已啟動。")
            self.master.destroy()
            return

        # 2. 建立 UI 介面
        self.setup_ui()

        # 3. 啟動接收天氣數據的執行緒
        self.receive_thread = threading.Thread(target=self.recv_handler, daemon=True)
        self.receive_thread.start()

    def login_server(self):
        """ 發送基本的進入請求 (配合原 Server 協定) """
        login_msg = {"type": 1, "nickname": "Weather_User"}
        data = (json.dumps(login_msg) + '\n').encode('utf-8')
        self.sock.sendall(data)
        # 讀取 type 2 回應
        self.f.readline()

    def setup_ui(self):
        """ 繪製純天氣查詢介面 """
        # 頂部查詢區
        header_frame = ttk.Frame(self.master, padding="10")
        header_frame.pack(fill=tk.X)

        ttk.Label(header_frame, text="請輸入縣市名稱 (如: 臺北):").pack(side=tk.LEFT)
        self.city_entry = ttk.Entry(header_frame)
        self.city_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        # 綁定 Enter 鍵直接查詢
        self.city_entry.bind('<Return>', lambda e: self.send_weather_request())

        search_btn = ttk.Button(header_frame, text="查詢天氣", command=self.send_weather_request)
        search_btn.pack(side=tk.LEFT, padx=5)

        # 中間表格區
        self.tree = ttk.Treeview(self.master, columns=("City", "Status", "Temp", "PoP"), show='headings')
        self.tree.heading("City", text="縣市")
        self.tree.heading("Status", text="天氣狀況")
        self.tree.heading("Temp", text="氣溫範圍")
        self.tree.heading("PoP", text="降雨機率")
        
        # 設定欄位寬度與對齊
        self.tree.column("City", width=100, anchor="center")
        self.tree.column("Status", width=150, anchor="center")
        self.tree.column("Temp", width=100, anchor="center")
        self.tree.column("PoP", width=100, anchor="center")
        
        self.tree.pack(pady=10, fill=tk.BOTH, expand=True, padx=10)

        # 狀態列
        self.status_var = tk.StringVar(value="準備就緒")
        status_bar = ttk.Label(self.master, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def send_weather_request(self):
        """ 發送天氣查詢請求 (Type 6) """
        city = self.city_entry.get().strip()
        msg = {"type": 6, "city": city}
        data = (json.dumps(msg) + '\n').encode('utf-8')
        try:
            self.sock.sendall(data)
            self.status_var.set(f"正在查詢 '{city if city else '全台'}' 的資料...")
        except Exception as e:
            messagebox.showerror("錯誤", f"發送失敗: {e}")

    def recv_handler(self):
        """ 專門處理天氣數據回傳 (Type 7) """
        while True:
            try:
                text = self.f.readline()
                if not text: break
                
                msgdict = json.loads(text)
                # 只處理 type 7 天氣資料
                if msgdict.get('type') == 7:
                    if 'data' in msgdict:
                        # 使用 after 安全更新 UI
                        self.master.after(0, self.refresh_table, msgdict['data'])
                    elif 'error' in msgdict:
                        self.master.after(0, lambda: messagebox.showwarning("API 錯誤", msgdict['error']))
            except:
                break

    def refresh_table(self, weather_data):
        """ 更新表格內容 """
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for info in weather_data:
            self.tree.insert("", tk.END, values=(
                info['city'],
                info['status'],
                info['temp'],
                info['pop']
            ))
        self.status_var.set(f"查詢完成，共 {len(weather_data)} 筆結果")

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherOnlyClient(root)
    root.mainloop()