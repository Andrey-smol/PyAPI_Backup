from datetime import datetime


class DateTime:

    @classmethod
    def get_date_time_now(cls):
        now = datetime.now()
        return f'[{now.day}-{now.month}-{now.year}__{now.hour}:{now.minute}:{now.second}]'
