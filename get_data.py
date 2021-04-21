import requests
import aiohttp
import asyncio
import math

base_url = 'https://api.covalenthq.com/v1/'
uniswap_block = '12273059'
sushiswap_block = '12273059'
token0 = ['WBTC', 'USDC','WETH', 'DAI']
token1 = ['WETH', 'USDT']
tx_hash = ""


def get_exchange_address_uniswap() :
  extend_url = '1/networks/uniswap_v2/assets/'
  url = base_url + extend_url
  raw = requests.get(url)
  raw = raw.json()
  data = raw['data']['items']
  uniswap_exchange = [x['exchange'] + " " + x['token_0']['contract_ticker_symbol'] + " " + x['token_1']['contract_ticker_symbol']  for x in data  if x['token_0']['contract_ticker_symbol'] in token0 and x['token_1']['contract_ticker_symbol'] in token1 ]
  return uniswap_exchange

# def get_exchange_address_sushiswap():
#   extend_url = '1/networks/sushiswap/assets/'
#   url = base_url + extend_url
#   raw = requests.get(url)
#   raw = raw.json()
#   data = raw['data']['items']
#   sushiswap_exchange = [x['exchange']  for x in data]
#   return sushiswap_exchange

def build_list(exchange, uni) : 
  extend_url = '1/events/address/'
  data = list(map(lambda x : base_url + extend_url + x.split(" ")[0] + '/', exchange))
  params = {
    'starting-block' : uni,
    'ending-block' : 'latest'
  }
  
  headers = {'Content-Type': 'application/json'}
  print(params)
  return data, params, headers

async def get_log(url, params, headers, session) :
    response = await session.get(url, params=params, headers=headers, raise_for_status=True)
    data = await response.json(content_type='application/json')
    return data

async def call_api(data, real_token, api) :
  async with aiohttp.ClientSession() as session:
      list_data = await asyncio.gather(*[get_log(endpoint_event, data[1], data[2], session) for endpoint_event in data[0]])
      return list_data
  
    


def extract_data_log(data, token, api, uniswap_block) :
  items = data['data']['items']
  token1 = ""
  token2 = ""
  
  for i in items :
    method = i['decoded']['name']
    params = i['decoded']['params']
    block = i['block_height']
    tx = i['tx_hash']
    if  method == 'Swap' :
      if params[1]['value'] != '0' :
        token1 = token[0]
        token2 = token[1]
        volume1 = params[1]['value']
        volume2 = params[4]['value']
        d =  get_swap(token1, token2, volume1, volume2, tx,api, block,uniswap_block)
      else :
        token1 = token[1]
        token2 = token[0]
        volume1 = params[2]['value']
        volume2 = params[3]['value']
        d = get_swap(token1, token2, volume1, volume2, tx, api, block,uniswap_block)
  return d

def get_swap(token1, token2, volume1, volume2,tx, api,block, uniswap_block):
  url = base_url + "pricing/tickers/"
  params = {
          'tickers' : token1
        }
  response = requests.get(url, params=params)
  raw = response.json()['data']['items']
  total1 = int(volume1)/math.pow(10, raw[0]['contract_decimals'])
  money1 = total1 * raw[0]['quote_rate']
  if total1 > 50000 :
      uniswap_block = str(block)
      print("new block " + uniswap_block)
      url = base_url + "pricing/tickers/"
      params = {
              'tickers' : token2
            }
      response = requests.get(url, params=params)
      raw2 = response.json()['data']['items']
      total2 = int(volume2)/math.pow(10, raw2[0]['contract_decimals'])
      money2 = total2 * raw2[0]['quote_rate']
      status = '🚨🚨🚨 Swap Alert!! \n#Uniswap 🦄 from {} ${} (~${:,.2f}) to {} ${} (~${:,.2f}) https://etherscan.io/tx/{}'.format(total1, token1, money1, total2, token2,money2, tx)
      api.update_status(status)
  return str(block)

  
    
