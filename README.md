# weather-reporting-system

專題名稱：[天氣回報系統]

作者: [林頎修] - [11103057a]、 [莊弘昇] - [11103113a]、[劉碩翰] - [11203120a] 、 [陳易謙] - [11303803a]

專題簡介:天氣回報系統
本專題為一個 Client–Server 架構的天氣回報系統。
系統以 Python Socket 為基礎，Server 端整合 中央氣象署（CWA）Open Data API 進行天氣資料擷取，Client 端透過圖形化介面輸入縣市名稱，向 Server 發送天氣查詢請求，並即時接收與顯示天氣資訊。

Client 端使用 Tkinter 建立完整操作介面，Server 端則採用 多執行緒 (Threading) 設計，可同時服務多位 Client。
功能特色:
✅ Client 端可輸入縣市名稱查詢即時天氣資訊

✅ 顯示天氣狀況、氣溫範圍與降雨機率

✅ Server 端整合氣象署 Open Data API，自動取得最新天氣資料

✅ 採用 TCP Socket 與 JSON 訊息格式進行通訊

✅ 圖形化使用者介面（GUI），操作直覺

✅ 支援多 Client 同時連線（Multi-thread Server）
系統架構
本系統採用 Client–Server 架構，整體流程如下：

1.	Client 端啟動後，透過 TCP Socket 與 Server 建立連線

2.	Client 先送出登入封包（Type 1）以符合 Server 協定

3.	使用者在 Client 端輸入欲查詢的縣市名稱

4.	Client 將天氣查詢請求（Type 6）送至 Server

5.	Server 接收到請求後，呼叫中央氣象署 Open Data API

6.	Server 將整理後的天氣資料封裝成回應封包（Type 7）

7.	Client 接收資料後，更新 GUI 表格顯示天氣資訊


協定設計
  傳輸方式

通訊協定：TCP

資料格式：JSON

編碼方式：UTF-8

每筆訊息以換行字元 \n 作為結束










  訊息類型定義
(1) Type 1：Client 登入請求

Client 連線後，首先送出登入訊息。

Client → Server

{
  "type": 1,
  "nickname": "Weather_User"
}


Server → Client

{
  "type": 2
}

(2) Type 6：天氣查詢請求

Client 端輸入縣市名稱後，送出查詢請求。

Client → Server

{
  "type": 6,
  "city": "臺北"
}


city 欄位可為空字串，表示查詢全台資料。









(3) Type 7：天氣資料回傳

Server 端查詢氣象署 API 後，回傳天氣資訊。

Server → Client


{
  "type": 7,
  "data": [
    {
      "city": "臺北市",
      "status": "多雲",
      "temp": "18~25°C",
      "pop": "20%"
    },
    {
      "city": "新北市",
      "status": "晴時多雲",
      "temp": "17~24°C",
      "pop": "10%"
    }
  ]
}


若發生錯誤，Server 會回傳錯誤訊息：

{
  "type": 7,
  "error": "API 連線失敗"
}
安裝與執行
需求
-Python 3.7 以上

套件：

requests

tkinter（Python 內建）

安裝方式
pip install requests

執行方式

先啟動 Server: python server.py
再啟動 Client: python client.py

測試結果:
Client 成功連線至 Server

可正確輸入縣市並顯示對應天氣資料

Server 可同時處理多位 Client 的請求

API 回傳資料正常，GUI 顯示正確

成果截圖於尾頁

未來改進方向
 改為 Web-based 系統（Flask / FastAPI）

 加入使用者帳號管理機制

 加入天氣預報圖與衛星雲圖顯示

 支援 HTTPS 與加密通訊

 將天氣資料快取以減少 API 請求次數
參考資料
- Foundations of Python Network Programming

-中央氣象署 Open Data API 官方文件

-Python Socket Programming Documentation 
