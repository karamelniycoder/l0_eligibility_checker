from tls_client import Session
from loguru import logger
from requests import get
from web3 import Web3
from time import sleep

from settings import *

from tls_client.exceptions import TLSClientExeption


class Browser:
    def __init__(self):

        if PROXY not in ['http://log:pass@ip:port', '']:
            self.change_ip()

        self.session = self.get_new_session()
        self.session.headers.update({
            "Origin": None,
            "Referer": None,
        })


    def get_new_session(self):
        session = Session(
            client_identifier="chrome_120",
            random_tls_extension_order=True
        )
        session.headers['user-agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

        if PROXY not in ['http://log:pass@ip:port', '']:
            session.proxies.update({'http': PROXY, 'https': PROXY})

        return session


    def change_ip(self):
        if CHANGE_IP_LINK not in ['https://changeip.mobileproxy.space/?proxy_key=...&format=json', '']:
            while True:
                try:
                    r = get(CHANGE_IP_LINK)
                    if 'mobileproxy' in CHANGE_IP_LINK and r.json().get('status') == 'OK':
                        print('') # empty string before next acc
                        logger.debug(f'[+] Proxy | Successfully changed ip: {r.json()["new_ip"]}')
                        return True
                    elif not 'mobileproxy' in CHANGE_IP_LINK and r.status_code == 200:
                        print('') # empty string before next acc
                        logger.debug(f'[+] Proxy | Successfully changed ip: {r.text}')
                        return True
                    logger.error(f'[-] Proxy | Change IP error: {r.text} | {r.status_code}')
                    sleep(10)

                except TLSClientExeption as err:
                    logger.error(f'[-] Browser | {err}')

                except Exception as err:
                    logger.error(f'[-] Browser | Cannot get proxy: {err}')


    def get_eligibility(self, address: str, retry: int = 0):
        try:
            r = self.session.get(f"https://www.layerzero.foundation/api/allocation/{address.lower()}")
            status = "Eligible" if r.json()["isEligible"] else "Not Eligible"
            tokens = float(r.json()["zroAllocation"]["asString"])

            if status == "Eligible":
                logger.success(f'[+] Browser | {address} ELIGIBLE | {tokens} $ZRO')
            else:
                logger.error(f'[+] Browser | {address} NOT ELIGIBLE')

            return status, tokens

        except Exception as err:
            logger.error(f"[-] Browser | Coudlnt get eligibility: {err} [{retry + 1}/{RETRY}]")
            if retry < RETRY:
                sleep(3)
                return self.get_eligibility(address=address, retry=retry + 1)
            else:
                return "Coudlnt get eligibility", 0


