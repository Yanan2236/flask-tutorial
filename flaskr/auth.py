import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

# Blueprint クラスのインスタンスを作成する
# auth という名前の Blueprint 
# flaskr.auth モジュールに属する Blueprint
# この Blueprint に属する URL は、/auth を先頭につける
bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method =='POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        
        if error is None:
            try:
                db.execute(
                    # username と password を SQL に渡すときは、SQL インジェクション攻撃を防ぐために、? プレースホルダを使う。
                    # generate_password_hash() でパスワードをハッシュ化して保存する。
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),          
                )
                # DBの変更の確定
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                # url_for() は、引数に指定した関数が呼び出される URL を返す。
                return redirect(url_for('auth.login'))
            
        # session にエラーメッセージを保存する。次の画面で get_flashed_messages() で取り出せる。
        flash(error)
    
    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()
        
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'
        
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        
        flash(error)
    
    return render_template('auth/login.html')


# リクエストが来るたびに、ログイン中ユーザーを session から g.user に読み込む
# g は、リクエストごとに保存される特殊なオブジェクトで、リクエストの間だけデータを保存するために使う。
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()
        
        
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    # functools.wraps() は、デコレータが元の関数の名前やドキュメンテーションを保持するためのデコレータ
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)
    
    return wrapped_view