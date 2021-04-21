import tweepy
from os import environ
import get_data
import asyncio
import time
#config credentials
API_KEY = environ["API_KEY"]
API_SECRET_KEY = environ["API_SECRET_KEY"]
ACCESS_TOKEN = environ["ACCESS_TOKEN"]
ACCESS_SECRET_TOKEN = environ["ACCESS_SECRET_TOKEN"]
uniswap_block = '12273059'
#make a connection to twitter
def connect_to_twitter() :
  auth = tweepy.OAuthHandler(API_KEY, API_SECRET_KEY)
  auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET_TOKEN)
  api = tweepy.API(auth, wait_on_rate_limit=True,
      wait_on_rate_limit_notify=True)
  return api

#crate tweet
def tweet(api, status) :
  api.update_status(status)

#run bot
while True :
    print('bot is running')
    print(uniswap_block)
    try :
      api = connect_to_twitter()
      data_uni = get_data.get_exchange_address_uniswap()
      data = get_data.build_list(data_uni, uniswap_block)
      count = 0
      real_token = [x.split(" ")[1:3] for x in data_uni]
      asyncio.set_event_loop(asyncio.new_event_loop())
      loop = asyncio.get_event_loop()
      list_data = loop.run_until_complete(get_data.call_api(data, real_token, api))
      loop.close()
      for i in range(len(list_data)) :
        d = get_data.extract_data_log(list_data[i], real_token[i], api,uniswap_block)
        uniswap_block = d
      time.sleep(60)
    except :
      print('Oops.. something went wrong!')
  
  




