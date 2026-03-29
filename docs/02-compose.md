---
marp: true
theme: default
paginate: true
header: "Docker入門 - Docker Compose編"
footer: "FastAPI Hello World で学ぶ Docker"
---

# Docker入門 - Docker Compose編

**compose.yaml で複数コンテナをまとめて管理する**

---

## このスライドで学ぶこと

- Docker Compose とは何か
- compose.yaml の書き方と各設定の意味
- 昔の書き方（v2/v3）と今の書き方の違い
- よく使うコマンド

---

## Docker Compose とは？

- 複数のコンテナを **1つのファイルで定義・管理** するツール
- `docker run` の長いオプションを YAML に書いておける
- コンテナが1つでも便利（実行コマンドを覚えなくて済む）

```bash
# Compose なし（毎回これを打つ？）
docker run -p 8000:8000 -v ./:/app --name api fastapi-hello

# Compose あり
docker compose up
```

---

## 完成形の compose.yaml

```yaml
services:
  app:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app
```

たった6行。これだけで FastAPI アプリが起動する。

---

## ファイル名の変遷

| 時期 | ファイル名 | 備考 |
|------|-----------|------|
| 旧 | `docker-compose.yml` | ハイフン区切り、拡張子 `.yml` |
| 現在 | `compose.yaml` | **推奨**。シンプルな名前に統一 |

- Docker Compose V2 から `compose.yaml` が推奨
- `docker-compose.yml` も引き続き認識される（後方互換）
- 両方あれば `compose.yaml` が優先

---

## 昔の書き方 vs 今の書き方

<!--
_header: ""
-->

```yaml
# --- 旧: docker-compose.yml ---
version: "3.8"            # ← バージョン指定が必要だった

services:
  app:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app
```

```yaml
# --- 現在: compose.yaml ---
                           # ← version 不要

services:
  app:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app
```

---

## なぜ version が不要になったのか？

**旧仕様の問題:**
- `version: "2"` と `version: "3"` で使える機能が異なっていた
- バージョン番号を間違えるとエラーや意図しない動作に
- どのバージョンを書くべきか、常に混乱の原因だった

**現在の仕様:**
- Docker Compose V2 は **全ての機能を自動判定**
- `version` を書いても無視される（警告が出る場合あり）
- **書かないのが正解**

---

## コマンドの変遷

| 旧 | 現在 | 備考 |
|----|------|------|
| `docker-compose up` | `docker compose up` | ハイフンからスペースへ |
| `docker-compose down` | `docker compose down` | 同上 |
| `docker-compose build` | `docker compose build` | 同上 |

- 旧: `docker-compose` は別途インストールが必要な Python 製ツール
- 現在: `docker compose` は Docker CLI のプラグイン（Go製、標準同梱）
- **今から学ぶなら `docker compose`（スペース区切り）だけ覚えればよい**

---

## services - サービスの定義

```yaml
services:
  app:            # ← サービス名（自由に命名）
    ...
```

- `services` はcompose.yaml の **ルートキー**
- 各サービスが1つのコンテナに対応
- サービス名はコンテナ間通信のホスト名にもなる

```
例: services に "app" と "db" を定義すると
app コンテナから db:5432 でアクセスできる
```

---

## build - イメージのビルド設定

```yaml
services:
  app:
    build: .
```

- `.` = カレントディレクトリの Dockerfile を使ってビルド
- `docker compose up --build` でビルドしてから起動

```yaml
# より詳細に指定する場合
services:
  app:
    build:
      context: .                  # ビルドコンテキスト
      dockerfile: Dockerfile.dev  # 別名の Dockerfile を指定
```

---

## image - 既存イメージを使う場合

```yaml
services:
  app:
    image: python:3.13-slim
```

- `build` の代わりに `image` を指定すると、ビルドせず既存イメージを使う
- Docker Hub や他のレジストリからプルされる

```yaml
# build と image の両方を指定すると、ビルドしたイメージに名前を付けられる
services:
  app:
    build: .
    image: my-fastapi-app:latest
```

---

## ports - ポートの公開

```yaml
    ports:
      - "8000:8000"
```

```
"ホスト側ポート:コンテナ側ポート"

ホスト(自分のPC)          コンテナ
  :8000         →         :8000
  ブラウザから              uvicorn が
  アクセスする側            リッスンする側
```

```yaml
# 別のポート番号にマッピングすることも可能
    ports:
      - "3000:8000"   # localhost:3000 → コンテナの8000番
```

---

## volumes - ファイルのマウント

```yaml
    volumes:
      - .:/app
```

```
"ホスト側のパス:コンテナ側のパス"

ホスト(自分のPC)          コンテナ
  ./（プロジェクト）  ←→   /app
  ファイルを編集           リアルタイムで反映
```

- **バインドマウント**: ホストのディレクトリをコンテナに直結
- ソースコードの変更が即座にコンテナに反映される
- 開発時に便利（本番では使わない）

---

## volumes の種類

```yaml
services:
  app:
    volumes:
      # バインドマウント（開発向き）
      - .:/app                    # ホストのファイルを直接マウント

      # 名前付きボリューム（データ永続化向き）
      - app-data:/app/data        # Docker が管理するボリューム

volumes:
  app-data:                       # トップレベルで宣言が必要
```

| 種類 | 用途 | ホストから見える？ |
|------|------|-----------------|
| バインドマウント | ソースコード共有 | はい |
| 名前付きボリューム | DB データなど永続化 | Docker 経由で |

---

## environment - 環境変数

```yaml
services:
  app:
    environment:
      - APP_ENV=development
      - DEBUG=true
```

```yaml
# .env ファイルから読み込む場合
services:
  app:
    env_file:
      - .env
```

- コンテナ内のアプリが `os.environ["APP_ENV"]` で参照できる
- 秘密情報（APIキーなど）は `.env` ファイルに分離する

---

## 完成形のディレクトリ構成

```
project/
├── compose.yaml        # Docker Compose 設定
├── Dockerfile          # イメージのビルド定義
├── .dockerignore       # ビルド時に除外するファイル
├── .env                # 環境変数（git管理外）
├── requirements.txt    # Python 依存パッケージ
└── main.py             # FastAPI アプリケーション
```

---

## よく使うコマンド

```bash
# コンテナを起動（バックグラウンド）
docker compose up -d

# ビルドし直して起動
docker compose up -d --build

# ログを確認
docker compose logs -f

# コンテナを停止・削除
docker compose down

# コンテナの状態を確認
docker compose ps
```

---

## コマンド早見表

| コマンド | 説明 |
|---------|------|
| `docker compose up` | コンテナを起動 |
| `docker compose up -d` | バックグラウンドで起動 |
| `docker compose up --build` | リビルドして起動 |
| `docker compose down` | 停止してコンテナ削除 |
| `docker compose logs` | ログ表示 |
| `docker compose ps` | 状態確認 |
| `docker compose exec app bash` | コンテナ内でシェル起動 |

---

## まとめ

| キー | 役割 |
|------|------|
| `services` | コンテナの一覧を定義 |
| `build` | Dockerfile からイメージをビルド |
| `image` | 既存イメージを使用 |
| `ports` | ホストとコンテナのポートを接続 |
| `volumes` | ファイルやデータをマウント |
| `environment` | 環境変数を設定 |

**覚えること:**
- ファイル名は `compose.yaml`
- コマンドは `docker compose`（スペース区切り）
- `version` は書かない
