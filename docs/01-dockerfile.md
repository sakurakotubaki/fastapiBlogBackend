---
marp: true
theme: default
paginate: true
header: "Docker入門 - Dockerfile編"
footer: "FastAPI Hello World で学ぶ Docker"
---

# Docker入門 - Dockerfile編

**FastAPI Hello World で学ぶコンテナの基礎**

---

## このスライドで学ぶこと

- Dockerfileとは何か
- 主要な命令（FROM / WORKDIR / COPY / RUN / EXPOSE / CMD）の意味
- FastAPI の Hello World をコンテナ化する流れ

---

## 前提：今回作るアプリ

```python
# main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def hello():
    return {"message": "Hello, World!"}
```

これを Docker コンテナで動かすのがゴール。

---

## Dockerfile とは？

- コンテナイメージの **設計図**（レシピ）
- テキストファイルに「どんな環境を作るか」を命令として記述
- `docker build` で読み込まれ、イメージが生成される

```
Dockerfile  →  docker build  →  イメージ  →  docker run  →  コンテナ
（設計図）       （ビルド）       （成果物）      （起動）       （実行環境）
```

---

## 完成形の Dockerfile

```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

ここから各行を解説していく。

---

## FROM - ベースイメージの指定

```dockerfile
FROM python:3.13-slim
```

| 要素 | 説明 |
|------|------|
| `FROM` | 全ての Dockerfile の **最初の命令**（必須） |
| `python` | Docker Hub で公開されている公式 Python イメージ |
| `3.13-slim` | タグ。バージョンとバリアント（slim = 軽量版）を指定 |

---

## FROM - イメージの選び方

| タグ例 | サイズ目安 | 特徴 |
|--------|-----------|------|
| `python:3.13` | ~900MB | フル機能。C拡張のビルドに便利 |
| `python:3.13-slim` | ~150MB | 最小限のパッケージ。本番向き |
| `python:3.13-alpine` | ~50MB | 超軽量だが musl libc のため互換性注意 |

**slim がバランスが良く、最初の選択肢としておすすめ。**

---

## WORKDIR - 作業ディレクトリの設定

```dockerfile
WORKDIR /app
```

- コンテナ内の作業ディレクトリを `/app` に設定
- 以降の `COPY`, `RUN`, `CMD` はこのディレクトリを基準に実行される
- ディレクトリが存在しなければ **自動で作成** される

```
# WORKDIR を設定しないと…
# 全て / (ルート) で実行され、ファイルが散らかる
```

---

## COPY - ファイルをコンテナへコピー

```dockerfile
COPY requirements.txt .
```

| 要素 | 説明 |
|------|------|
| `COPY` | ホストマシンのファイルをコンテナへコピー |
| `requirements.txt` | コピー元（ホスト側のファイル） |
| `.` | コピー先（WORKDIR = `/app`） |

**なぜ先に requirements.txt だけコピーするのか？**
→ Docker のレイヤーキャッシュを活用するため（次ページで解説）

---

## レイヤーキャッシュの仕組み

```dockerfile
COPY requirements.txt .          # レイヤー1: 依存定義だけコピー
RUN pip install -r requirements.txt  # レイヤー2: インストール
COPY . .                             # レイヤー3: ソースコード全体をコピー
```

- Dockerfile の各命令は **レイヤー**（層）としてキャッシュされる
- ファイルに変更がなければ、そのレイヤーは **再利用** される
- ソースコードを変更しても、依存関係のインストールはスキップできる

```
ソース変更時: レイヤー1 ✅キャッシュ → レイヤー2 ✅キャッシュ → レイヤー3 🔄再実行
依存追加時:   レイヤー1 🔄再実行   → レイヤー2 🔄再実行   → レイヤー3 🔄再実行
```

---

## RUN - コマンドの実行

```dockerfile
RUN pip install --no-cache-dir -r requirements.txt
```

| 要素 | 説明 |
|------|------|
| `RUN` | ビルド時にコンテナ内でコマンドを実行 |
| `pip install` | Python パッケージをインストール |
| `--no-cache-dir` | pip のキャッシュを保存しない（イメージサイズ削減） |

**RUN はイメージのビルド時に1回だけ実行される。**
コンテナ起動時に毎回実行されるわけではない。

---

## COPY . . - ソースコード全体のコピー

```dockerfile
COPY . .
```

- ホスト側のカレントディレクトリの **全ファイル** をコンテナへコピー
- `.dockerignore` に記載したファイルは除外される

```
# .dockerignore の例
__pycache__
.venv
.git
.env
```

**`.dockerignore` は必ず作成すること。** 不要なファイルがイメージに含まれると、サイズ増大やセキュリティリスクになる。

---

## EXPOSE - ポートの宣言

```dockerfile
EXPOSE 8000
```

- コンテナが **リッスンするポート番号** をドキュメントとして宣言
- 実際のポート公開は `docker run -p` や compose.yaml で行う
- EXPOSE だけでは外部からアクセスできない

```
EXPOSE = 「このコンテナは8000番で待ち受けます」という宣言
docker run -p 8000:8000 = 実際にホストの8000番とつなぐ設定
```

---

## CMD - コンテナ起動時のコマンド

```dockerfile
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

| 要素 | 説明 |
|------|------|
| `CMD` | コンテナ **起動時** に実行されるデフォルトコマンド |
| `["...", "..."]` | exec形式（推奨）。各引数を配列で指定 |

---

## CMD の2つの書き方

```dockerfile
# exec形式（推奨）- シェルを介さず直接実行
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]

# shell形式 - /bin/sh -c 経由で実行
CMD uvicorn main:app --host 0.0.0.0
```

| | exec形式 | shell形式 |
|---|----------|----------|
| シグナル | プロセスに直接届く | シェルが受け取る |
| 終了 | 正常にシャットダウン | 強制終了になりがち |
| 推奨度 | **推奨** | 非推奨 |

---

## CMD vs ENTRYPOINT

| 命令 | 役割 | `docker run` で上書き |
|------|------|----------------------|
| `CMD` | デフォルトのコマンド | 引数を指定すると **全て** 上書きされる |
| `ENTRYPOINT` | 固定のコマンド | 引数は CMD や実行時引数で **追加** される |

```dockerfile
# ENTRYPOINT + CMD の組み合わせ例
ENTRYPOINT ["uvicorn"]
CMD ["main:app", "--host", "0.0.0.0", "--port", "8000"]

# docker run <image> main:app --port 9000
# → uvicorn main:app --port 9000 （CMD部分だけ上書き）
```

---

## ビルドと実行

```bash
# イメージをビルド
docker build -t fastapi-hello .

# コンテナを起動
docker run -p 8000:8000 fastapi-hello
```

ブラウザで http://localhost:8000 にアクセスすると

```json
{"message": "Hello, World!"}
```

---

## requirements.txt

今回のサンプルに必要な内容:

```
fastapi
uvicorn[standard]
```

**ディレクトリ構成:**

```
project/
├── Dockerfile
├── .dockerignore
├── requirements.txt
└── main.py
```

---

## まとめ

| 命令 | タイミング | 役割 |
|------|-----------|------|
| `FROM` | ビルド開始 | ベースイメージの指定 |
| `WORKDIR` | ビルド時 | 作業ディレクトリの設定 |
| `COPY` | ビルド時 | ファイルをコンテナへコピー |
| `RUN` | ビルド時 | コマンドの実行（パッケージインストールなど） |
| `EXPOSE` | 宣言 | ポートのドキュメント |
| `CMD` | コンテナ起動時 | デフォルト実行コマンド |

**次のスライド → compose.yaml 編へ**
