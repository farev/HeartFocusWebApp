from flask import Flask, request

app = Flask(__name__)

@app.route('/terra/webhook', methods=['POST'])
def handle_webhook():
    data = request.json
    # Process the received heart rate data here
    print(data)
    return 'OK', 200

if __name__ == '__main__':
    app.run(port=8000)
