# import requests

# # API endpoint URL
# url = "https://api.twelvedata.com/time_series"

# # Parameters for the request
# params = {
#     "start_date": "2023-08-15",
#     "end_date": "2023-08-31",
#     "symbol": "xauusd",
#     "interval": "1day",
#     "apikey": "9134ab7cb1ed4db09c8c2f0688419b51"
# }

# # Make the GET request
# response = requests.get(url, params=params)

# # Check if the request was successful (status code 200)
# if response.status_code == 200:
#     data = response.json()  # Parse the JSON response
#     print(data)
# else:
#     print("Request failed with status code:", response.status_code)


from twelvedata import TDClient

# Initialize client - apikey parameter is requiered
td = TDClient(apikey="9134ab7cb1ed4db09c8c2f0688419b51")

# Construct the necessary time series
ts = td.time_series(
    symbol="USD/JPY",
    interval="1h",
    outputsize=10,
    timezone="UTC",
    start_date="2012-01-01",
    end_date="2020-08-31 02:00:00",
    order="asc"
)
# 1min, 5min, 15min, 30min, 45min, 1h, 2h, 4h, 8h, 1day, 1week, 1month
# Returns pandas.DataFrame
# print(ts.as_pandas().head())
print(len(ts.as_pandas()))
print(ts.as_pandas())
tt = ts.as_pandas()
# Remove the last row of the dataframe
# tt = tt[:-1]

# Get the first datetime of the dataframe
first_datetime = tt.index[0]

import pdb; pdb.set_trace()
