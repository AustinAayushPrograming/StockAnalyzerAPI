from flask import Flask
from flask_restful import Api, Resource
from flask_cors import CORS
import yfinance as yf

app = Flask(__name__)
api = Api(app)
CORS(app)

class Data(Resource):
    def getEMA(self, last_100):
        previousfiftyday = 0
        previousTwentyDay = 0
        previousTenDay = 0
        previousFiveDay = 0

        dayfiftytohundredSMA = 0
        daytwentytofourtySMA = 0
        daytentotwentySMA = 0
        dayfivetotenSMA = 0

        ema_list = []

        x = len(last_100) - 6
        while x >= 90:
            dayfivetotenSMA += last_100[x]
            x -= 1
        dayfivetotenSMA = dayfivetotenSMA / 5

        x = len(last_100) - 11
        while x >= 80:
            daytentotwentySMA += last_100[x]
            x -= 1
        daytentotwentySMA = daytentotwentySMA / 10

        x = len(last_100) - 21
        while x >= 60:
            daytwentytofourtySMA += last_100[x]
            x -= 1
        daytwentytofourtySMA = daytwentytofourtySMA / 20

        x = len(last_100) - 51
        while x >= 0:
            dayfiftytohundredSMA += last_100[x]
            x -= 1
        dayfiftytohundredSMA = dayfiftytohundredSMA / 50

        fivedaysmoothingConstant = 2 / (5 + 1)
        tendaysmoothingConstant = 2 / (10 + 1)
        twentydaysmoothingConstant = 2 / (20 + 1)
        fiftydaysmoothingConstant = 2 / (50 + 1)

        fiftydayEMA = (last_100[51] - dayfiftytohundredSMA) * \
                      fiftydaysmoothingConstant + dayfiftytohundredSMA
        twentydayEMA = (last_100[81] - daytwentytofourtySMA) * \
                       twentydaysmoothingConstant + daytwentytofourtySMA
        tendayEMA = (last_100[91] - daytentotwentySMA) * \
                    tendaysmoothingConstant + daytentotwentySMA
        fivedayEMA = (last_100[96] - dayfivetotenSMA) * \
                     fivedaysmoothingConstant + dayfivetotenSMA

        x = len(last_100) - 48
        while x < len(last_100):
            fiftydayEMA = (last_100[x] - fiftydayEMA) * fiftydaysmoothingConstant + fiftydayEMA
            x += 1

        x = len(last_100) - 18
        while x < len(last_100):
            twentydayEMA = (last_100[x] - twentydayEMA) * twentydaysmoothingConstant + twentydayEMA
            x += 1

        x = len(last_100) - 8
        while x < len(last_100):
            tendayEMA = (last_100[x] - tendayEMA) * tendaysmoothingConstant + tendayEMA
            x += 1

        x = len(last_100) - 3
        while x < len(last_100):
            fivedayEMA = (last_100[x] - fivedayEMA) * fivedaysmoothingConstant + fivedayEMA
            x += 1

        ema_list.append(fivedayEMA)
        ema_list.append(tendayEMA)
        ema_list.append(twentydayEMA)
        ema_list.append(fiftydayEMA)

        return ema_list

    # -- END OF EMA FUNCTION ----------------------------------------------------------------------------------------------------#

    ######################
    ## GET RSI FUNCTION ##
    ######################
    def getRSI(self, last_15):
        averageUp = 0
        totalUp = 0
        averageDown = 0
        totalDown = 0
        n = 15
        rsi = 0
        x = 1
        y = 0

        while x <= len((last_15)) - 1:
            if last_15[x] > last_15[y]:
                totalUp += (last_15[x] - last_15[y] / last_15[y])
            else:
                totalDown += (last_15[x] - last_15[y] / last_15[y])
            x += 1
            y += 1

        averageUp = totalUp / n
        averageDown = totalDown / n

        rsi = 100 - (100 / ((1 + (averageUp / averageDown))))

        return rsi

    # -- END OF RSI FUNCTION ----------------------------------------------------------------------------------------------------#

    # 5 diff functions for 5 diff indicators
    # function 1 which takes in SMA, EMA. Function determines when a crossover happens between the moving averages (SMA and EMA) For example if 5 day SMA crosses over 10 day SMA
    # it is bullish (strong uptrend) or 10 day crosses 15 day (bullish), etc. If it goes down that is 5 day doesnt cross the 10 day moving averages it is downtrend
    def crossover(self, SMAvalues, EMAvalues):
        crossover_trendpoints = 0

        # upside EMA points
        if EMAvalues[0] > EMAvalues[1]:
            crossover_trendpoints += 0.3

        if EMAvalues[1] > EMAvalues[2]:
            crossover_trendpoints += 0.2

        if EMAvalues[2] > EMAvalues[3]:
            crossover_trendpoints += 0.1

        # downside EMA points
        if EMAvalues[0] < EMAvalues[1]:
            crossover_trendpoints -= 0.3

        if EMAvalues[1] < EMAvalues[2]:
            crossover_trendpoints -= 0.2

        if EMAvalues[2] < EMAvalues[3]:
            crossover_trendpoints -= 0.1

        # upside SMA points
        if SMAvalues[0] > SMAvalues[1]:
            crossover_trendpoints += 0.2

        if SMAvalues[1] > SMAvalues[2]:
            crossover_trendpoints += 0.125

        if SMAvalues[2] > SMAvalues[3]:
            crossover_trendpoints += 0.075

        # downside SMA points
        if SMAvalues[0] < SMAvalues[1]:
            crossover_trendpoints -= 0.2

        if SMAvalues[1] < SMAvalues[2]:
            crossover_trendpoints -= 0.125

        if SMAvalues[2] < SMAvalues[3]:
            crossover_trendpoints -= 0.075

        return crossover_trendpoints

    # function 2 to find price above average (takes in closing price, SMA, EMA) i.e. if the closing price is above the 10 day SMA, EMA good if below bad
    def price_above_average(self, price, EMAvalues, SMAvalues):
        price_above_average_points = 0

        # upside EMA trend
        if price > EMAvalues[0]:
            price_above_average_points += 0.225

        if price > EMAvalues[1]:
            price_above_average_points += 0.175

        if price > EMAvalues[2]:
            price_above_average_points += 0.125

        if price > EMAvalues[3]:
            price_above_average_points += 0.075

        # downside EMA trends
        if price < EMAvalues[0]:
            price_above_average_points -= 0.225

        if price < EMAvalues[1]:
            price_above_average_points -= 0.175

        if price < EMAvalues[2]:
            price_above_average_points -= 0.125

        if price < EMAvalues[3]:
            price_above_average_points -= 0.075

        # upside SMA trend
        if price > SMAvalues[0]:
            price_above_average_points += 0.175

        if price > SMAvalues[1]:
            price_above_average_points += 0.125

        if price > SMAvalues[2]:
            price_above_average_points += 0.075

        if price > SMAvalues[3]:
            price_above_average_points += 0.025

        # downside SMA trend
        if price < SMAvalues[0]:
            price_above_average_points -= 0.175

        if price < SMAvalues[1]:
            price_above_average_points -= 0.125

        if price < SMAvalues[2]:
            price_above_average_points -= 0.075

        if price < SMAvalues[3]:
            price_above_average_points -= 0.025

        return price_above_average_points

    # funtion 3 that takes in rsi value, tells you whether stock is over bought or over sold. A stock over 70 RSI is overbought, stock below 30 is beneficial, between 30 and 70 is meh
    def rsi(self, RSIvalue):

        rsi_trendpoints = 0
        givenrsi = RSIvalue

        if givenrsi < 50:
            rsi_trendpoints = (1 - (givenrsi / 100) * 2) * 1

        if givenrsi >= 50:
            rsi_trendpoints = (1 - (givenrsi / 100) * 2) * 1

        return rsi_trendpoints

    # function 4 that takes in roc, which says the closert the roc is to 0 and positive/negative, the less strong it is, if roc >> 0 then strong, if roc << 0 then bad
    def roc(self, ROCvalues):

        day5_trendpoint = 0
        day10_trendpoint = 0
        day15_trendpoint = 0
        roc_trendpoints = 0
        roc_dayFive = 0
        roc_dayTen = 0
        roc_dayFifteen = 0

        roc_dayFive = ROCvalues[0]
        roc_dayTen = ROCvalues[1]
        roc_dayFifteen = ROCvalues[2]

        day5_trendpoint = roc_dayFive * 0.5
        day10_trendpoint = roc_dayTen * 0.3
        day15_trendpoint = roc_dayFifteen * 0.2

        roc_trendpoints = day5_trendpoint + day10_trendpoint + day15_trendpoint

        return roc_trendpoints

    # function 5 that takes in closing price, EMA, SMA, average volumes, current volume. if input from function 1 is uptrend with low volume not good, if above uptrend with strong volume good
    # downtrend on weaker volume then good, downtrend on strong volume then bad

    def average_volume(self, price, SMAvalues, EMAvalues, currentvolume, averagevolume):

        trend = (self.price_above_average(price, SMAvalues, EMAvalues) +
                 self.crossover(SMAvalues, EMAvalues)) / 2
        total = 0
        total_points = 0

        if currentvolume > averagevolume[2]:
            total += 0.5
        if currentvolume > averagevolume[1]:
            total += 0.3
        if currentvolume > averagevolume[0]:
            total += 0.2

        if currentvolume < averagevolume[2]:
            total -= 0.5
        if currentvolume < averagevolume[1]:
            total -= 0.3
        if currentvolume < averagevolume[0]:
            total -= 0.2

        total_points = trend * total

        return total_points

    def get_total_trend_points(self, ticker):
        totalTrendpoints = 0

        closeByDay = ticker['Close']
        volumeByDay = ticker['Volume']

        lastClosingPrice = closeByDay[-1]
        lastVolume = volumeByDay[-1]
        avgVolume_5 = sum(volumeByDay[-5:]) / 5
        avgVolume_10 = sum(volumeByDay[-10:]) / 10
        avgVolume_15 = sum(volumeByDay[-15:]) / 15
        SMA_5 = sum(closeByDay[-5:]) / 5
        SMA_10 = sum(closeByDay[-10:]) / 10
        SMA_20 = sum(closeByDay[-20:]) / 20
        SMA_50 = sum(closeByDay[-50:]) / 50
        ROC_5 = (lastClosingPrice - closeByDay[-6]) / closeByDay[-6]
        ROC_10 = (lastClosingPrice - closeByDay[-11]) / closeByDay[-11]
        ROC_15 = (lastClosingPrice - closeByDay[-16]) / closeByDay[-16]
        RSIvalue = self.getRSI(closeByDay[-15:])

        SMAvalues = [SMA_5, SMA_10, SMA_20, SMA_50]
        EMAvalues = self.getEMA(closeByDay[-100:])
        ROCvalues = [ROC_5, ROC_10, ROC_15]
        avgVolumes = [avgVolume_5, avgVolume_10, avgVolume_15]

        # call to crossover function which returns crossover trend points
        totalTrendpoints += self.crossover(SMAvalues, EMAvalues)
        # call to price_above_average function which returns price_above_average trend points
        totalTrendpoints += self.price_above_average(
            lastClosingPrice, EMAvalues, SMAvalues)
        # call to rsi function which returns rsi trend points
        totalTrendpoints += self.rsi(RSIvalue)
        # call to roc function which returns roc trend points
        totalTrendpoints += self.roc(ROCvalues)
        # call to average_volume function which returns average volume points
        totalTrendpoints += self.average_volume(lastClosingPrice, SMAvalues,
                                           EMAvalues, lastVolume, avgVolumes)
        return totalTrendpoints

    def hillClimbTop(self, dict, x):
        top_x = []
        while len(top_x) < x:
            highest_value = None
            for key in dict:
                if highest_value == None:
                    highest_value = key
                else:
                    if dict[key] > dict[highest_value]:
                        highest_value = key
            top_x.append((highest_value, dict[highest_value]))
            del dict[highest_value]

        return top_x

    def hillClimbBottom(self, dict, x):
        bottom_x = []
        while len(bottom_x) < x:
            lowest_value = None
            for key in dict:
                if lowest_value == None:
                    lowest_value = key
                else:
                    if dict[key] < dict[lowest_value]:
                        lowest_value = key
            bottom_x.append((lowest_value, dict[lowest_value]))
            del dict[lowest_value]

        return bottom_x

    # Main get request function
    def get(self, ticker):
        data = yf.download(ticker, group_by="ticker", period='100d')
        info = yf.Ticker(ticker).info
        points = self.get_total_trend_points(data)
        temp = data.to_dict('series')
        dictionary = temp['Close']
        resultPrice = []
        resultDate = []
        resultInfo = []

        for key in info.keys():
            resultInfo.append([key,info[key]])

        for key in dictionary.keys():
            key = key.strftime("%d %B, %Y")
            resultDate.append(key[0:len(key) - 6])
            resultPrice.append(dictionary[key])

        return {"trendPoints": points, "datePrice": [resultDate, resultPrice], "info": resultInfo}

class Info(Resource):

    # Main get request function
    def get(self, ticker):
        info = yf.Ticker(ticker).info
        resultInfo = []

        for key in info.keys():
            resultInfo.append([key, info[key]])

        return {"info": resultInfo}

api.add_resource(Data, "/data/<string:ticker>")
api.add_resource(Info, "/info/<string:ticker>")

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run(debug=True)