from flask import Flask, render_template, request

app = Flask(__name__)

temp = 0.00
humi = 0.00
gas = 0.00
current = 0.00

@app.route('/postsensordata', methods=['POST'])
def get_sensor_data():
    global temp, humi, gas, current
    data = request.get_json()
    temp = float(data.get('temp'))
    humi = float(data.get('humi'))
    gas = float(data.get('gas'))
    current = float(data.get('current'))
    return "OK", 200


@app.route('/')
def show_data():
    return render_template('index.html', temp=temp, humi=humi, gas=gas, current=current)

if __name__ == '__main__':
    app.run(port=8948,debug=True)
