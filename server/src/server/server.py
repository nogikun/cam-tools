from fastapi import FastAPI, UploadFile
from pydantic import BaseModel
import uvicorn
from io import BytesIO
import matplotlib.pyplot as plt
import cv2
from PIL import Image

# FastAPIのインスタンスを作成
app = FastAPI()


# レスポンスデータのスキーマを定義
class ResponseModel(BaseModel):
    anomaly: int
    cause: str
    heartRate: int
    temprature: float
    spo2: int
    mame: str
    sex: str


# エンドポイントを定義
@app.get("/status")
async def get_status():
    return {
        "anomaly": 0,  # 0:異常なし, 1:異常あり
        "cause": "None",  # 異常の原因（heartRate, temprature, spo2）
        "heartRate": 75,
        "temprature": 36.5,
        "spo2": 98,
        "mame": "田中太郎",
        "sex": "M",
    }


# Postリクエストを受け取るエンドポイント
@app.post("/camera")
async def post_status(img: UploadFile = None):
    print(img.filename)  # 画像ファイル名を出力

    memory = await img.read()
    image = plt.imread(
        BytesIO(memory), format=img.filename.split(".")[-1]
    )  # image ･･･ 画像インスタンス。これをモデルの入力として使えるか要検証

    cv2.imwrite("test.jpg", image)  # 画像を保存

    # image.show()


# ローカルサーバの起動（このスクリプトを直接実行する場合）
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
