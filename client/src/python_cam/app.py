import cv2
import numpy as np
import requests
import time
import base64


class Camera:
    """
    カメラからフレームをキャプチャするためのカメラクラス。
    """

    def __init__(
        self,
        channel_id: int = 0,
        url: str = "http://localhost:8000/camera",
        send_sec: int = 10,  # 送信間隔（秒）
        extension: str = ".jpg",
    ) -> None:
        """
        カメラを初期化する。

        Args:
            channel_id (int, optional): _description_. Defaults to 0.
            url (_type_, optional): _description_. Defaults to "http://localhost:8000/api/camera".
            send_sec (int, optional): _description_. Defaults to 10.
        """
        self.cap = cv2.VideoCapture(channel_id)
        self.url = url
        self.send_sec = send_sec
        self.start_time = time.time()
        self.extension = extension

    def time_reset(self):
        """
        タイマーをセットする。
        """
        self.start_time = time.time()

    def encode_frame(self, frame: np.ndarray) -> str:
        """
        フレームをエンコードする。

        Args:
            frame (np.ndarray): エンコードするフレーム

        Returns:
            str: エンコードしたフレーム
        """
        _, enc_frame = cv2.imencode(self.extension, frame)  # フレームをエンコード
        # img_base64 = base64.b64encode(enc_frame).decode("utf-8")  # base64にエンコード
        tobytes = enc_frame.tobytes()
        return tobytes  # str

    def send_frame(self, frame: np.ndarray) -> bool:
        """
        フレームを送信する。

        Args:
            frame (np.ndarray): 送信するフレーム

        Returns:
            bool: 送信に成功した場合はTrue
        """
        enc_frame = self.encode_frame(frame)  # フレームをエンコードする
        try:
            res = requests.post(
                self.url,
                files={
                    "img": (
                        "img" + self.extension,
                        enc_frame,
                        "image/" + self.extension[1:],
                    )
                },
            )  # フレームを送信
            if res.status_code != 200:
                print(f"Error: {res.status_code}")
                return False
        except Exception as e:
            print(f"Error: {e}")
            return False
        return True

    def capture_frame(self) -> np.ndarray:
        """
        カメラからフレームをキャプチャする。（1フレームのみ）

        Returns:
            np.ndarray: キャプチャしたフレーム
        """
        ret, frame = self.cap.read()
        if not ret:
            print("Error: Could not read frame.")
            return None
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # グレースケールに変換
        return frame

    def release(self) -> bool:
        """
        カメラをリリースする。

        Returns:
            bool: 正常にリリースされた場合はTrue
        """
        try:
            self.cap.release()
            cv2.destroyAllWindows()  # windowを閉じる
        except Exception as e:
            print(f"Error: {e}")
            return False
        return True

    def show_time(self, frame: np.ndarray) -> np.ndarray:
        """
        シャッターまでの時間を表示する。
        """
        now = time.time()
        cv2.putText(
            frame,
            f"{self.send_sec - (now - self.start_time):.1f}",
            (20, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )
        return frame

    def __call__(self, *args, **kwds):
        """
        カメラからフレームをキャプチャし、指定した秒数ごとにフレームを送信する。
        """
        now = time.time()
        if now - self.start_time >= self.send_sec:
            # 送信する
            frame = self.capture_frame()
            if frame is not None:
                self.send_frame(frame)
            self.time_reset()
        else:
            # 送信しない
            frame = self.capture_frame()
            if frame is not None:
                frame = self.show_time(frame)

        return frame


if __name__ == "__main__":
    cam_channel_id = int(input("カメラIDを入力してください(int): "))  # 数値であること
    camera = Camera(
        # configration
        channel_id=cam_channel_id,
        url="http://localhost:8000/camera",
        send_sec=10,
        extension=".jpg",
    )

    while True:
        frame = (
            camera()
        )  # カメラからフレームをキャプチャし、指定した秒数ごとにフレームを送信する。
        if frame is not None:
            cv2.imshow("frame", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    camera.release()
