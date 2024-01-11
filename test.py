import shelve
import datetime
from datetime import time, timedelta, timezone

with shelve.open('next_wm_time') as shelf_file:
  # 変数を取得する
  day = shelf_file['day']
  hour = shelf_file['hour']
  min = shelf_file['min']
  print(day)
  print(hour)
  print(min)
  d_today = datetime.date.today().strftime('%m-%d')
  print(d_today)
  print(datetime.datetime.strptime(day, '%m/%d').strftime('%m-%d'))
  print(datetime.datetime.strptime(day, '%m/%d').strftime('%m-%d') == d_today)

with shelve.open('next_fl_time') as shelf_file:
  # 変数を取得する
  day = shelf_file['day']
  hour = shelf_file['hour']
  min = shelf_file['min']
  print(day)
  print(hour)
  print(min)
  day_op = datetime.datetime.strptime(day,
                                      '%m/%d') - datetime.timedelta(days=2)
  print(day_op.strftime('%m-%d'))
