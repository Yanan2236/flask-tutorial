import os 

from flask import Flask

def create_app(test_config=None):
    # Flask クラスから app インスタンスを作成する。
    # __name__は、現在のモジュール名を表す特殊変数で、Flask がアプリのルートパスや各種リソースの基準を決めるために使う。
    #
    # instance_relative_config=True:
    #   設定ファイルを相対パスで読み込むときの基準を、
    #   アプリケーションルートではなく instance フォルダに切り替える。
    #   つまり from_pyfile('config.py') のような処理で、
    #   instance/config.py を読む構成にしやすくするための指定。
    app = Flask(__name__, instance_relative_config=True)
    
    # アプリの初期設定をまとめて登録する。
    app.config.from_mapping(
        # 開発用秘密鍵
        SECRET_KEY='dev',
        # instance フォルダ内の SQlite ファイルの保存先
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
    
    # テスト時に外から設定値を渡せる
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)
        
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Flask のルーティングのやり方。/hello という URL にアクセスしたときに hello() が呼び出される。
    @app.route('/hello')
    def hello():
        return 'Hello, World!'
    
    return app