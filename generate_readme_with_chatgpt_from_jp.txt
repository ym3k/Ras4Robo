Github のレポジトリにREADME.md をかきたい。
下記の特徴やセットアップの方法、使用方法をまとめて英語で出力してほしい。
ITの基本的な知識がある読者を対象にする。
表現がわかりにくいところを補完してほしい。


＝＝＝＝ここから＝＝＝＝

# Ras4Robo

## 特徴
1. ラズパイ3またはラズパイ4で動作する。
1. ラズパイのGPIOにつながった以下のデバイスをジョイスティックからリモート操作できる。
  - 2つのDCモータドライバによる2輪ホイール
  - ２つのサーボモーターによるラズパイカメラのパンチルト
1. i2c/シリアル通信のセンサーからの値の取得
  - ToF or LiDAR
1. カメラから動画、静止画を取得
1. mqtt によるメッセージングにより、遠隔から操縦したりセンサーからデータを取得したりできる。
1. 将来的にはROS2をサポート予定

## 動作環境
### OS
- raspberry pi OS (64bit)
- Ubuntu 22.04 LTS(64bit)
どちらでも動作するがraspberry pi OS をおすすめする。

### デバイス
- サーボモーター： SG90 ２個
- DCモータードライバー： DRV8835 2個
- モーター：　タミヤミニ四駆　トルクチューン２モーター　２個
- LiDAR：　YDLIDAR GS2(808nm) １個

## 準備
### インストールソフトウェア
docker compose でアプリケーション動作管理させる。
ただし、pigpiodだけはOSで起動する。
- docker
- pigpiod

### dockerインストール
ROS2 のドキュメント（https://docs.ros.org/en/foxy/How-To-Guides/Installing-on-Raspberry-Pi.html)にあるように、
ここ（https://docs.docker.com/engine/install/debian/#install-using-the-convenience-script）の手順で
docker をインストールする。
pi ユーザで docker を操作できるように以下のコマンドを実行しておく
```
usermod -aG docker $USER
```

### pigpiod 設定
pigpiod を ホストで動作中の docker コンテナからアクセスできるようにする。

systemd の起動スクリプトを override する。
```bash
sudo systemctl edit pigpiod.service
```

下記内容を追記する。
```
[Service]
ExecStart=
ExecStart=/usr/bin/pigpiod -n localhost
```
１行目の`ExecStart=` は忘れず書くこと

### docker image 作成
```
docker build -t ras4robo:0.1 .
```

## プロセス起動
```
docker compose up -d
```

## リモートホストから操作
mqttのおかげでリモートPCからも移動やカメラのパンチルト操作できる。
遠隔のWIndowsPCにジョイスティックを接続する場合は
- python 3.10 以上
- pygame
をインストールし、
```
python joypad_pygame.py --host <hostname>
```
を実行する。

＝＝＝＝ここまで＝＝＝＝
