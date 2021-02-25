
# code to get crypto prices from api

from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import pandas as pd
import copy



def get_crypto_prices():
  
  url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
  parameters = {
    'start':'1',
    'limit':'5000',
    'convert':'USD'
  }
  headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': '604e968c-f220-42b5-8ce2-c7848c65edf4',
  }
  
  session = Session()
  session.headers.update(headers)
  
  try:
    response = session.get(url, params=parameters)
    data = json.loads(response.text)
  except (ConnectionError, Timeout, TooManyRedirects) as e:
    print(e)
    
  
  for i in range(len(data['data'])):
    sym = data['data'][i]['symbol']
    price = data['data'][i]['quote']['USD']['price']
    mcap = data['data'][i]['quote']['USD']['market_cap']
    pc24 = data['data'][i]['quote']['USD']['percent_change_24h']
    pc7 = data['data'][i]['quote']['USD']['percent_change_7d']
    v24 = data['data'][i]['quote']['USD']['volume_24h']
    
    coin_values = {'symbol': [sym], 'price': [float(price)], 'market_cap': [float(mcap)],
                          'price_change24': [float(pc24)], 'prince_change_week': [float(pc7)], 
                          'volume_24h': v24}
    coin_values = pd.DataFrame(data = coin_values)
    
    if i == 0:
      output = copy.deepcopy(coin_values)
    else:
      output = output.append(coin_values)
  
  output = output.drop_duplicates(subset = ['symbol'])
  output = output.sort_values(by = ['market_cap'], ascending = False)
  
  return(output)
  














