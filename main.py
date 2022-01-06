from flask import Flask
from flask_restful import Api, Resource
from flask_cors import CORS
import yfinance as yf

app = Flask(__name__)
api = Api(app)
CORS(app)

class Data(Resource):
    # Main get request function
    def get(self, ticker):
        data = yf.download(ticker, group_by="ticker", period='100d')
        result = []

        for date in data.index:
            result.append([date.timestamp()])

        for i in range(len(data)):
            row = data.iloc[i]
            result[i].extend([round(row['Open'], 2),round(row['High'], 2),round(row['Low'], 2),round(row['Close'], 2)])

        return {"data": result}

class Info(Resource):
    # Main get request function
    def get(self, ticker):
        info = yf.Ticker(ticker).get_info()
        return {"name": info}

api.add_resource(Data, "/data/<string:ticker>")
api.add_resource(Info, "/info/<string:ticker>")

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run(debug=True)