import socket
import threading
import json
import requests  # 整合爬蟲需要用到 requests

BUFFER_SIZE = 4096
bind_ip = '0.0.0.0'
bind_port = 6543
client_list = []

# --- 爬蟲/API 整合區塊 ---
CWA_AUTHORIZATION_CODE = "CWA-D021145F-0782-4307-8469-9307991BEF4F"  # ⚠️ 請替換為您的授權碼
API_URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"

def fetch_weather_data(city_filter=""):
    """ 整合原本的氣象獲取邏輯 """
    if CWA_AUTHORIZATION_CODE == "YOUR_AUTHORIZATION_CODE":
        return {"error": "Server未設定授權碼"}
    
    params = {
        'Authorization': CWA_AUTHORIZATION_CODE,
        'format': 'JSON'
    }
    try:
        response = requests.get(API_URL, params=params, timeout=5)
        data = response.json()
        weather_list = []
        
        for location in data['records']['location']:
            loc_name = location['locationName']
            # 若有提供篩選字串，則進行比對
            if city_filter and city_filter not in loc_name:
                continue
                
            element = location['weatherElement']
            wx = element[0]['time'][0]['parameter']['parameterName']
            pop = element[1]['time'][0]['parameter']['parameterName']
            min_t = element[2]['time'][0]['parameter']['parameterName']
            max_t = element[4]['time'][0]['parameter']['parameterName']

            weather_list.append({
                "city": loc_name,
                "status": wx,
                "temp": f"{min_t}~{max_t}°C",
                "pop": f"{pop}%"
            })
        return {"type": 7, "data": weather_list} # type 7 定義為天氣回傳
    except Exception as e:
        return {"type": 7, "error": str(e)}

# --- Socket 連線處理執行緒 ---
def connection_thread(new_sock, sockname):
    global client_list
    nickname = ''
    while(True):
        f = new_sock.makefile(encoding='utf-8')
        try:
            text = f.readline()
            if text == '':
                # ... (原本的離線處理邏輯)
                if nickname != '':
                    new_client = {'nickname': nickname,'socket': new_sock}
                    if new_client in client_list:
                        client_list.remove(new_client)
                        print(f'{nickname} at {sockname} 已離線')
                new_sock.close()
                break
            
            print('The client at {} says {}'.format(sockname, text))
            message = json.loads(text)

            # type 1: 新Client加入
            if message['type'] == 1:
                nickname = message['nickname']
                new_client = {'nickname': nickname, 'socket': new_sock}
                client_list.append(new_client)
                msgdict = {"type": 2}
                data = (json.dumps(msgdict) + '\n').encode('utf-8')
                new_sock.sendall(data)

            # type 3: 聊天訊息轉送
            elif message['type'] == 3:
                # 送回確認
                new_sock.sendall((json.dumps({"type": 4}) + '\n').encode('utf-8'))
                # 轉發訊息
                transfer_msg = {
                    "type": 5,
                    "nickname": nickname,
                    "message": message['message']
                }
                data = (json.dumps(transfer_msg) + '\n').encode('utf-8')
                for client in client_list:
                    if client['socket'] != new_sock:
                        client['socket'].sendall(data)

            # --- 新增 type 6: 天氣查詢請求 ---
            elif message['type'] == 6:
                city_name = message.get('city', "") # Client可傳送想要篩選的縣市
                print(f'User {nickname} requested weather for: {city_name}')
                
                # 執行整合進來的爬蟲邏輯
                weather_res = fetch_weather_data(city_name)
                
                # 送回天氣結果給該 Client
                data = (json.dumps(weather_res) + '\n').encode('utf-8')
                new_sock.sendall(data)
                print(f'Sent weather data back to {nickname}')

        except (ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError):
            if nickname != '':
                new_client = {'nickname': nickname, 'socket': new_sock}
                if new_client in client_list:
                    client_list.remove(new_client)
            new_sock.close()
            break

# 伺服器主程式碼
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # 允許重新使用連接埠
sock.bind((bind_ip, bind_port))
sock.listen(5)
print('Weather Server Listening at {}'.format(sock.getsockname()))

while(True):
    new_sock, sockname = sock.accept()
    thread = threading.Thread(target=connection_thread, args=(new_sock, sockname))
    thread.start()