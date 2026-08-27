from datetime import datetime

def get_current_time():
    current_datetime = datetime.now()
    current_hour = current_datetime.hour
    current_minute = current_datetime.minute
    return f"{current_hour}:{current_minute}"

def get_current_date():
    current_datetime = datetime.now()

    current_day = current_datetime.day
    current_month = current_datetime.month
    current_year = current_datetime.year

    return f"{current_day}/{current_month}/{current_year}"

print(get_current_date())