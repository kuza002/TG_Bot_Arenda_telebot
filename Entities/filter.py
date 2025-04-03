class Filter:
    def __init__(self, user_id, districts, min_price=0, max_price=10 ** 10):
        self.user_id = user_id
        self.districts = districts
        self.min_price = min_price
        self.max_price = max_price