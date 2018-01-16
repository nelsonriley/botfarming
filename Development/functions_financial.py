import datetime
import numpy
import pandas as pd


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
    macd_periods_big = 26
    macd_periods_small = 12
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
            macd_small_sma_array = sma_array[calculation_periods-macd_periods_small:calculation_periods]
            macd_small_sma = sum(macd_small_sma_array) / macd_periods_small
            macd_small_weighted_multiplier = 2 / (macd_periods_small + 1)
            macd_small_ema = (c - macd_small_sma) * macd_small_weighted_multiplier + macd_small_sma

            df = pd.DataFrame(macd_small_sma_array)
            macd_small_ema_2 = pd.ewma(df, span=macd_periods_small, adjust=False).mean()

            macd_big_sma_array = sma_array[calculation_periods-macd_periods_big:calculation_periods]
            macd_big_sma = sum(macd_big_sma_array) / macd_periods_big
            macd_big_weighted_multiplier = 2 / (macd_periods_big + 1)
            macd_big_ema = (c - macd_big_sma) * macd_big_weighted_multiplier + macd_big_sma

            df = pd.DataFrame(macd_big_sma_array)
            macd_big_ema_2 = pd.ewma(df, span=macd_periods_big, adjust=False).mean()

            diff_ema = macd_small_ema - macd_big_ema
            macd_diff_weighted_multiplier = 2 / (9 + 1)
            macd_mid_ema = (c - diff_ema) * macd_diff_weighted_multiplier + diff_ema
            macd = diff_ema - macd_mid_ema

            macd_positive_2 = macd_small_ema_2 > macd_big_ema_2
            macd_positive = macd_small_ema > macd_big_ema
            # MACD
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
                # candles[i][16] = macd_small_ema
                # candles[i][17] = macd_big_ema
                # candles[i][18] = macd
            candles[i].append(upper_band)
            candles[i].append(middle_band)
            candles[i].append(lower_band)
            candles[i].append(stan_dev)
            candles[i].append(macd_small_ema_2)
            candles[i].append(macd_big_ema_2)
            candles[i].append(macd_positive)
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
