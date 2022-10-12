class IndicatorPipeline(object):
    def __init__(self):
        self.indicators = []
        pass

    def add_indicator(self, indicator):
        self.indicators.append(indicator)
        pass


class BaseIndicator(object):
    def __init__(self):
        pass

    def calc(self, instance, prices):
        return prices


class MovingAverage(BaseIndicator):
    """
    Moving Average Class

    """

    def __init__(self, window):
        self.window = window

    def calc(self, instance, prices):
        return prices.rolling(self.window).mean()


if __name__ == '__main__':
    indicator_pipeline = IndicatorPipeline()
    base_indicator = BaseIndicator()

    for indicator in indicator_pipeline.indicators:
        indicator.calc()
