from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import requests
import hashlib
from flask import Flask, render_template, request

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Đổi thành chuỗi bí mật mạnh hơn khi dùng thật

temp = 0.00
humi = 0.00
gas = 0.00
current = 0.00

# Firestore API config
projectID = "testappinc"
apiKey = "AIzaSyBOgR3ZiIXlPYIktsM3C3E8NST7nR-4qNU"
firestore_endpoint = f"https://firestore.googleapis.com/v1/projects/{projectID}/databases/(default)/documents/users?key={apiKey}"
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Đăng ký
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Kiểm tra user đã tồn tại chưa
        query_url = firestore_endpoint + f'&where=username=="{username}"'
        # Firestore REST không hỗ trợ where trực tiếp, nên ta sẽ lấy hết và lọc thủ công
        resp = requests.get(firestore_endpoint)
        exists = False
        if resp.ok:
            docs = resp.json().get('documents', [])
            for doc in docs:
                fields = doc.get('fields', {})
                if fields.get('username', {}).get('stringValue', '') == username:
                    exists = True
                    break
        if exists:
            return render_template('register.html', error='Tên đăng nhập đã tồn tại!')
        # Đăng ký user mới
        data = {
            "fields": {
                "username": {"stringValue": username},
                "password": {"stringValue": hash_password(password)}
            }
        }
        r = requests.post(firestore_endpoint, json=data)
        if r.ok:
            return render_template('register.html', success='Đăng ký thành công!')
        else:
            return render_template('register.html', error='Lỗi đăng ký!')
    return render_template('register.html')

# Đăng nhập
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        resp = requests.get(firestore_endpoint)
        if resp.ok:
            docs = resp.json().get('documents', [])
            for doc in docs:
                fields = doc.get('fields', {})
                if fields.get('username', {}).get('stringValue', '') == username and \
                   fields.get('password', {}).get('stringValue', '') == hash_password(password):
                    session['username'] = username
                    return redirect(url_for('show_data'))
        return render_template('login.html', error='Sai tên đăng nhập hoặc mật khẩu!')
    return render_template('login.html')

# Đăng xuất
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/postdata', methods=['POST'])
def get_sensor_data():
    global temp, humi, gas, current
    data = request.get_json()
    temp = float(data.get('temp'))
    humi = float(data.get('humi'))
    gas = float(data.get('gas'))
    current = float(data.get('current'))

    print(data.get('temp'))
    print(data.get('humi'))
    print(data.get('gas'))
    print(data.get('current'))
    return "OK", 200

@app.route('/api/sensordata')
def api_sensor_data():
    return jsonify({
        'temp': temp,
        'humi': humi,
        'gas': gas,
        'current': current
    })


@app.route('/')
def show_data():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', temp=temp, humi=humi, gas=gas, current=current)

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=8948,debug=True)
