from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
from roulette_analyzer import RouletteAnalyzer
import json

app = Flask(__name__)
socketio = SocketIO(app)
analyzer = RouletteAnalyzer()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_number', methods=['POST'])
def add_number():
    data = request.get_json()
    number = int(data.get('number'))
    if 0 <= number <= 36:
        analyzer.add_number(number)
        prediction = analyzer.predict_next()
        return jsonify({
            'status': 'success',
            'prediction': prediction,
            'numbers': list(reversed(analyzer.numbers))
        })
    return jsonify({'status': 'error', 'message': 'Invalid number'})

@app.route('/get_history')
def get_history():
    prediction = analyzer.predict_next()
    return jsonify({
        'numbers': list(reversed(analyzer.numbers)),
        'prediction': prediction
    })

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5001)
