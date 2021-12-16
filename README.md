# Restaurary Rest API
---
「Restaurary」にデータを渡すためのRest API  
グルメサイトの口コミデータをスクレイピングにより取得  
<br>

# データ取得方法
---
seleniumでのスクレイピングにより以下の情報を取得
* エリア情報
* 店舗情報(店名、よみがな、電話番号、料理カテゴリ、URL)
* 口コミ情報(評価点、投稿日、口コミ本文)  
<br>

取得したデータをjsonファイルで保存(これによりGoogle Colab等のの外部サービスからでもデータ収集が可能に)

insert_from_json_run.pyスクリプトでjsonファイルを読み取り、データごとに整理してDBへ格納  


# データ出力方法
---
Django Rest FrameworkによりRest APIしてあり、HTTPリクエストで取得