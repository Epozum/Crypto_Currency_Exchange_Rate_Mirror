import json
import threading
import telebot
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

checker_token = "****************************"

tf = open('telegram.txt', 'r')
telegram_file = tf.read()
telegram_array = telegram_file.strip().split('\n')
telegram_token = telegram_array[0]
telegram_chat = telegram_array[1]
bot = telebot.TeleBot(telegram_token)

chrm_options = Options()
chrm_options.add_argument("--headless")
chrm_options.add_argument("window-size=1024,768")
chrm_options.add_argument("--no-sandbox")
chrm_caps = webdriver.DesiredCapabilities.CHROME.copy()
chrm_caps['goog:loggingPrefs'] = {'performance': 'ALL'}

driver = webdriver.Chrome(executable_path='/usr/bin/chromedriver', chrome_options=chrm_options,
                          desired_capabilities=chrm_caps)  # Linux
data = {}


def find_trade_socket():
    try:
        for ws_data in driver.get_log('performance'):
            ws_json = json.loads((ws_data['message']))
            if ws_json["message"]["method"] == "Network.webSocketFrameReceived":
                socket = json.loads(ws_json["message"]["params"]["response"]["payloadData"])
                body = socket["body"]
                topic = socket["topic"]

                if topic == 'requestAccountTradeList' and type() is list and len() != 0:
                    return filter(lambda s: "status" in s and s["status"] == "open", )
        return -1
    except Exception as e:
        print("FindTradeSocket Function: ")
        print(e)
        try:
            r = requests.get(
                "https://***********************************", params={
                    "message": "FindTradeSocket Function: " + str(e),
                    "token": checker_token
                })
        except:
            pass
        return -1


def socket_data(socket_body):
    try:
        size = socket_body["size"][:-30]
        account = socket_body["account"]
        token = socket_body["indexToken"]
        collateral_token = socket_body["collateralToken"]
        if token == "0x82af49447d8a07e3bd95bd0d56f35241523fbab1":
            currency = "ethereum"
        elif token == "0xf97f4df75117a78c1a5a0dbb814af92458539fb4":
            currency = "link"
        elif token == "0xfa7f8980b0f1e64a2062791cc3b0871572f1f7f0":
            currency = "uni"
        elif token == "0x2f2a2543b76a4166549f7aab2e75bef0aefc5b0f":
            currency = "bitcoin"
        else:
            currency = token

        if token == collateral_token:
            market = 'bull'
        else:
            market = 'bear'


        return {
            'size': size,
            'account': account,
            'currency': currency,
            'market': market
        }
    except Exception as e:
        print("SocketData Function: ")
        print(e)
        try:
            r = requests.get(
                "https://***********************************", params={
                    "message": "SocketData Function: " + str(e),
                    "token": checker_token
                })
        except:
            pass
        return -1


def load_web_driver():
    try:
        f = open('links.txt', 'r')
        links_file = f.read()
        links_array = links_file.strip().split('\n')
        for link in links_array:
            driver.get(link)
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "canvas"))
                )
                web_socket_log(link)
            except Exception as e:
                print("LoadWebDriver Function: ")
                print(link + " => Unable to load page")
    except Exception as e:
        print("LoadWebDriver Function: ")
        print(e)
        try:
            r = requests.get(
                "https://***********************************", params={
                    "message": "LoadWebDriver Function: " + str(e),
                    "token": checker_token
                })
        except:
            pass


def web_socket_log(link):
    try:
        account = link.split("/")[-1]
        open_currency = find_trade_socket()
        if open_currency == -1:
            return

        prev_currency = []
        exist_currency = []

        for s in open_currency:
            socket_data = socket_data(s)
            if socket_data == -1:
                continue

            size = socket_data['size']
            account = socket_data['account']
            currency = socket_data['currency']
            market = socket_data['market']

            exist_currency.append(market + " " + currency)
            record_data(account, market + " " + currency, size)

        for c in data[account].keys():
            prev_currency.append(c)

        difference = set(prev_currency) - set(exist_currency)
        for d in difference:
            record_data(account, d, '0')

    except Exception as e:
        print("WebSocketLog Function: ")
        print(e)
        try:
            r = requests.get(
                "https://***********************************", params={
                    "message": "WebSocketLog Function: " + str(e),
                    "token": checker_token
                })
        except:
            pass


def record_data(account, market_currency, size):
    try:
        if not market_currency in data[account] or data[account][market_currency] != size:
            if not market_currency in data[account]:
                data[account][market_currency] = 0
            prev_size = data[account][market_currency]
            data[account][market_currency] = size
            send_message(account, market_currency, size, prev_size)
    except Exception as e:
        print("RecordData Function: ")
        print(e)
        try:
            r = requests.get(
                "https://***********************************", params={
                    "message": "RecordData Function: " + str(e),
                    "token": checker_token
                })
        except:
            pass


def send_message(account, market_currency, size, prev_size):
    try:
        market_currency_arr = market_currency.split(' ')
        market = market_currency_arr[0]
        currency = market_currency_arr[1]

        link = "https://***********************************" + account
        bot.send_message(telegram_chat,
                         "[ " + currency + " | " + market + " market ]: " + prev_size + " --->> " + size + "\n" + link)
        print("[ " + currency + " | " + market + " market ]: " + prev_size + " --->> " + size + "\n" + link)
    except Exception as e:
        print("SendMessage Function: ")
        print(e)
        try:
            r = requests.get(
                "https://***********************************", params={
                    "message": "SendMessage Function: " + str(e),
                    "token": checker_token
                })
        except:
            pass


def init_load_web_driver():
    try:
        f = open('links.txt', 'r')
        links_file = f.read()
        links_array = links_file.strip().split('\n')
        inited = []
        for link in links_array:
            try:
                driver.get(link)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "canvas"))
                )
                init_data(link)
                inited.append(link)
            except:
                print("Failed load: " + link)
                pass
        print("Data is initialized [ " + str(len(inited)) + " / " + str(len(links_array)) + " ]")
        if len(inited) != len(links_array):
            exit()
    except Exception as e:
        print("InitLoadWebDriver Function: ")
        print(e)
        try:
            r = requests.get(
                "https://***********************************", params={
                    "message": "InitLoadWebDriver Function: " + str(e),
                    "token": checker_token
                })
        except:
            pass


def init_data(link):
    try:
        account = link.split("/")[-1]
        data[account] = {}

        open_currency = find_trade_socket()
        if open_currency == -1:
            return

        for s in open_currency:
            socket_data = socket_data(s)
            if socket_data == -1:
                continue

            size = socket_data['size']
            account = socket_data['account']
            currency = socket_data['currency']
            market = socket_data['market']

            data[account][market + " " + currency] = size
    except Exception as e:
        print("InitData Function: ")
        print(e)
        try:
            r = requests.get(
                "https://***********************************", params={
                    "message": "InitData Function: " + str(e),
                    "token": checker_token
                })
        except:
            pass


def main():
    try:
        print("Data initialization....")
        init_load_web_driver()
        print("Start watching....")

        while True:
            load_web_driver()
    except Exception as e:
        print("Main Function: ")
        print(e)
        try:
            r = requests.get(
                "https://***********************************", params={
                    "message": "Main Function: " + str(e),
                    "token": checker_token
                })
        except:
            pass


def checker_function():
    try:
        r = requests.get("https://***********************************" + checker_token)
        sec = (int(r.text))
        if sec == -1:
            return

        def func_wrapper():
            checker_function()

        t = threading.Timer(sec, func_wrapper)
        t.start()
    except Exception as e:
        print("CheckerFunction Function: ")
        print(e)


if __name__ == "__main__":
    checker_function()
    main()
