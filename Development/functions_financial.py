import datetime
import numpy
import pandas as pd
import utility as ut


def get_n_minute_candles(n_minutes, one_min_data):

    candles_to_return = int(len(one_min_data) / n_minutes)
    offset = len(one_min_data) % n_minutes

    candles = []
    start_of_n_min_candle = True
    open_time = 0
    open_price = 0
    high = 0
    low = 9999999
    close = 0
    volume = 0.0
    close_time = 0
    for i in range(0 + offset, candles_to_return * n_minutes):
        c = one_min_data[i]
        if start_of_n_min_candle:
            open_time = int(c[0])
            open_price = float(c[1])
            start_of_n_min_candle = False
        if float(c[2]) > high:
            high = float(c[2])
        if float(c[3]) < low:
            low = float(c[3])
        volume += float(c[5])

        if (i + 1) % n_minutes == 0:
            close_time = int(c[6])
            close = float(c[4])

            candle = [open_time, ut.float_to_str(open_price), ut.float_to_str(high), ut.float_to_str(low), ut.float_to_str(close), ut.float_to_str(volume), close_time, 'na', 'na', 'na', 'na', 'na']
            # candle = [open_time, open_price, high, low, close, volume, close_time]
            candles.append(candle)

            start_of_n_min_candle = True
            open_time = 0
            open_price = 0
            high = 0
            low = 9999999
            close = 0
            volume = 0.0
            close_time = 0
    return candles


def add_bollinger_bands_to_candles(candles):
    # create candles with bollinger bands

    # setup
    sma_interval = 20
    sma_array = []
    smart_candle_array = []
    last_open_close_center = 0
    consecutive_lower_open_close_centers = 0
    consecutive_higher_open_close_centers = 0
    last_boll_middle = 0

    # step through all candles
    for i in range(0, len(candles)):
        t = int(candles[i][0])
        o = float(candles[i][1])
        h = float(candles[i][2])
        l = float(candles[i][3])
        c = float(candles[i][4])
        v = float(candles[i][5])

        t_readable = datetime.datetime.fromtimestamp(t/1000).strftime('%Y-%m-%d %H:%M:%S')

        sma_array.append(c)

        # if 20+ periods of history, we calculate bollinger bands for all later candles
        if len(sma_array) > sma_interval:
            sma_array.pop(0)
            # Standard Deviation Calc
            # 1. Work out the Mean (the simple average of the numbers)
            # 2. Then for each number: subtract the Mean and square the result
            # 3. Then work out the mean of those squared differences.
            # 4. Take the square root of that and we are done!
            sma = sum(sma_array) / sma_interval
            stan_dev_array = [(n-sma)**2 for n in sma_array]
            stan_dev_mean = sum(stan_dev_array) / sma_interval
            stan_dev = stan_dev_mean**(0.5)
            # bollinger bands
            middle_band = sma
            upper_band = sma + stan_dev * 2.0
            lower_band = sma - stan_dev * 2.0
            # meta
            color = 'red'
            if c > o:
                color = 'green'
            open_close_center = (o + c) / 2.0
            if last_open_close_center == 0:
                last_open_close_center = open_close_center
            if open_close_center < last_open_close_center:
                consecutive_lower_open_close_centers += 1
                consecutive_higher_open_close_centers = 0
            if open_close_center >= last_open_close_center:
                consecutive_higher_open_close_centers += 1
                consecutive_lower_open_close_centers = 0
            # update candles passed in
                # candles[i][12] = upper_band
                # candles[i][13] = middle_band
                # candles[i][14] = lower_band
                # candles[i][15] = stan_dev
            candles[i].append(upper_band)
            candles[i].append(middle_band)
            candles[i].append(lower_band)
            candles[i].append(stan_dev)
            # update the candles as objects array (smart candles)
            smart_candle_array.append({
                'time_epoch': t,
                'time_human': t_readable,
                'volume': v,
                'open': o,
                'close': c,
                'high': h,
                'low': l,
                'boll_upper': upper_band,
                'boll_middle': middle_band,
                'boll_middle_change': middle_band - last_boll_middle,
                'boll_lower': lower_band,
                'color': color,
                'open_close_center': open_close_center,
                'high_low_center': (h + l) / 2,
                'consecutive_lower_open_close_centers': consecutive_lower_open_close_centers,
                'consecutive_higher_open_close_centers': consecutive_higher_open_close_centers
                })
    return candles, smart_candle_array

def make_smart_candles(candles):
    # create candles with bollinger bands

    # setup
    calculation_periods = 27
    bollinger_periods = 20
    sma_array = []
    smart_candle_array = []
    last_open_close_center = 0
    consecutive_lower_open_close_centers = 0
    consecutive_higher_open_close_centers = 0
    last_boll_middle = 0

    # step through all candles
    for i in range(0, len(candles)):
        t = int(candles[i][0])
        o = float(candles[i][1])
        h = float(candles[i][2])
        l = float(candles[i][3])
        c = float(candles[i][4])
        v = float(candles[i][5])

        t_readable = datetime.datetime.fromtimestamp(t/1000).strftime('%Y-%m-%d %H:%M:%S')

        sma_array.append(c)

        # once we have all periods to calc SMA, we calculate technical indicators for all later candles
        if len(sma_array) > calculation_periods:
            sma_array.pop(0)
            # Bollinger Bands
                # 1. Work out the Mean (the simple average of the numbers)
                # 2. Then for each number: subtract the Mean and square the result
                # 3. Then work out the mean of those squared differences.
                # 4. Take the square root of that and we are done!
            boll_sma_array = sma_array[calculation_periods-bollinger_periods:calculation_periods]
            boll_sma = sum(boll_sma_array) / bollinger_periods
            stan_dev_array = [(n-boll_sma)**2 for n in boll_sma_array]
            stan_dev_mean = sum(stan_dev_array) / bollinger_periods
            stan_dev = stan_dev_mean**(0.5)
            middle_band = boll_sma
            upper_band = boll_sma + stan_dev * 2.0
            lower_band = boll_sma - stan_dev * 2.0


            # EMA (exponential moving average)
            macd_12_sma_array = sma_array[calculation_periods-12-1:calculation_periods-1]
            macd_12_sma = float(sum(macd_12_sma_array) / 12.0)
            macd_12_ema = (c - macd_12_sma) * float(2.0 / (12.0 + 1.0)) + macd_12_sma
            # macd_12_ema = (c - macd_12_sma) * float(2.0 / (12.0 + 1.0))
            # macd_12_ema = (c - macd_12_ema) * (2 / (12 + 1)) + macd_12_ema

            df = pd.DataFrame(macd_12_sma_array)
            macd_12_ema_2 = float(pd.ewma(df, span=12, adjust=False).mean())
            the_12_2 = c - macd_12_ema_2
            the_12 = c - macd_12_ema

            macd_26_sma_array = sma_array[calculation_periods-26-1:calculation_periods-1]
            macd_26_sma = float(sum(macd_26_sma_array) / 26.0)
            macd_26_ema = (c - macd_26_sma) * float(2.0 / (26.0 + 1.0)) + macd_26_sma
            # macd_26_ema = (c - macd_26_sma) * float(2.0 / (26.0 + 1.0))
            # macd_26_ema = (c - macd_26_ema) * (2 / (26 + 1)) + macd_26_ema

            df = pd.DataFrame(macd_26_sma_array)
            macd_26_ema_2 = float(pd.ewma(df, span=26, adjust=False).mean())
            the_26_2 = c - macd_26_ema_2
            the_26 = c - macd_26_ema
            the_9 = the_26 + the_12
            the_9_2 = the_26_2 + the_12_2

            macd_line = float(macd_12_ema - macd_26_ema)
            macd_line_2 = float(macd_12_ema_2 - macd_26_ema_2)

            macd_signal_line = (c - macd_line) * float(2.0 / (9.0 + 1.0)) + macd_line
            # macd_signal_line = (c - macd_line) * float(2.0 / (9.0 + 1.0))
            # macd_signal_array = sma_array[calculation_periods-9:calculation_periods]
            # df = pd.DataFrame(macd_signal_array)
            # macd_signal_line_2 = float(pd.ewma(df, span=9, adjust=False).mean())
            macd_signal_line_2 = (c - macd_line_2) * float(2.0 / (9.0 + 1.0)) + macd_line_2


            macd_9_sma_array = sma_array[calculation_periods-9:calculation_periods]
            macd_9_sma = float(sum(macd_9_sma_array) / 9.0)
            macd_9_ema = (c - macd_9_sma) * float(2.0 / (9.0 + 1.0)) + macd_9_sma
            macd_9_ema = (c - macd_26_sma) * float(2.0 / (9.0 + 1.0))

            macd_histogram = macd_line - macd_signal_line
            macd_histogram = macd_line - macd_9_ema

            macd_histogram_positive = macd_histogram >= 0
            macd_histogram_2 = float(macd_line_2 - macd_signal_line_2)
            macd_histogram_positive_2 = macd_histogram_2 >= 0

            # MACD
                # The Chart
                # The MACD Line is the 12-day Exponential Moving Average (EMA) less the 26-day EMA. Closing prices are used for these moving averages.
                # A 9-day EMA of the MACD Line is plotted with the indicator to act as a signal line and identify turns.
                # The MACD Histogram represents the difference between MACD and its 9-day EMA, the Signal line.
                # The histogram is positive when the MACD Line is above its Signal line and negative when the MACD Line is below its Signal line.

                # An EMA is calculated as follows:
                # Calculate the simple moving average (SMA) for the chosen number of time periods. (The EMA uses an SMA as the previous period's EMA to start its calculations.) To calculate a 12-period EMA, this would simply be the sum of the last 12 time periods, divided by 12.
                # Calculate the weighting multiplier using this equation: 2 / (12 + 1) ) = 0.1538
                # Calculate the 12 EMA itself as {Close - EMA(previous time period)} x 0.1538 + EMA(previous time period)

                # Putting together the MACD requires simply doing all of the following EMA calculations for any given market instrument (a stock, future, currency pair, or market index):
                # 1. Calculate a 12-period EMA of price for the chosen time period.
                # 2. Calculate a 26-period EMA of price for the chosen time period.
                # 3. Subtract the 26-period EMA from the 12-period EMA.
                # 4. Calculate a nine-period EMA of the result obtained from step 3.
                # This nine-period EMA line is overlaid on a histogram that is created by subtracting the nine-period EMA from the result in step 3, which is called the MACD line, but it is not always visibly plotted on the MACD representation on a chart.

                # The MACD also has a zero line to indicate positive and negative values. The MACD has a positive value whenever the 12-period EMA is above the 26-period EMA and a negative value when the 12-period EMA is below the 26-period EMA.

            # meta
            color = 'red'
            if c > o:
                color = 'green'
            open_close_center = (o + c) / 2.0
            if last_open_close_center == 0:
                last_open_close_center = open_close_center
            if open_close_center < last_open_close_center:
                consecutive_lower_open_close_centers += 1
                consecutive_higher_open_close_centers = 0
            if open_close_center >= last_open_close_center:
                consecutive_higher_open_close_centers += 1
                consecutive_lower_open_close_centers = 0
            # update candles passed in
                # candles[i][12] = upper_band
                # candles[i][13] = middle_band
                # candles[i][14] = lower_band
                # candles[i][15] = stan_dev
                # candles[i][16] = macd_line
                # candles[i][17] = macd_signal_line
                # candles[i][18] = macd_histogram
                # candles[i][19] = macd_histogram_positive
            candles[i].append(upper_band)
            candles[i].append(middle_band)
            candles[i].append(lower_band)
            candles[i].append(stan_dev)
            candles[i].append(macd_line)
            candles[i].append(macd_signal_line)
            candles[i].append(macd_histogram)
            candles[i].append(macd_histogram_positive)
            candles[i].append(macd_line_2)
            candles[i].append(macd_signal_line_2)
            candles[i].append(macd_histogram_2)
            candles[i].append(macd_histogram_positive_2)
            candles[i].append(macd_12_ema)
            candles[i].append(macd_26_ema)
            candles[i].append(macd_9_ema)
            candles[i].append(macd_12_ema_2)
            candles[i].append(macd_26_ema_2)
            candles[i].append(macd_signal_line_2)
            candles[i].append(the_12)
            candles[i].append(the_26)
            candles[i].append(the_9)
            candles[i].append(the_12_2)
            candles[i].append(the_26_2)
            candles[i].append(the_9_2)
            #candles[i].append(macd)
            # update the candles as objects array (smart candles)
            smart_candle_array.append({
                'time_epoch': t,
                'time_human': t_readable,
                'volume': v,
                'open': o,
                'close': c,
                'high': h,
                'low': l,
                'boll_upper': upper_band,
                'boll_middle': middle_band,
                'boll_middle_change': middle_band - last_boll_middle,
                'boll_lower': lower_band,
                'color': color,
                'open_close_center': open_close_center,
                'high_low_center': (h + l) / 2,
                'consecutive_lower_open_close_centers': consecutive_lower_open_close_centers,
                'consecutive_higher_open_close_centers': consecutive_higher_open_close_centers
                })
    return candles, smart_candle_array


def print_ascii():
    longstring = """\

       ______________________
     .'   __                 `.
     |  .'__`.    = = = =     |_.-----._                          .---.
     |  `.__.'    = = = =     | |     | \ _______________        / .-. \
     |`.                      | |     |  |  ````````````,)       \ `-' /
     |  `.                    |_|     |_/~~~~~~~~~~~~~~~'         `---'
     |    `-;___              | `-----'                   ___
     |        /\``---..._____.'               _  _...--'''   ``-._
     |       |  \                            /\\`                 `._
     |       |   )              __..--''\___/  \\     _.-'```''-._   `;
     |       |  /              /       .'       \\_.-'            ````
     |       | /              |_.-.___|  .-.   .'~
     |       `(               | `-'      `-'  ;`._
     |         `.     jgs      \__       ___.'  //`-._          _,,,
     |           )                ``--./home/ec2-user/environment/botfarming/Development/   \  //     `-.,,,..-'    `;
     `----------'                            \//,_               _.-'
                                              ^   ```--...___..-'

    """
    print(longstring)
