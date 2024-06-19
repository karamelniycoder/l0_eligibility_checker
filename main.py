from loguru import logger
from sys import stderr

import settings
from browser import Browser
from excel import Excel

logger.remove()
logger.add(stderr, format="<white>{time:HH:mm:ss}</white> | <level>{message}</level>")


def checker(address: str, excel: Excel):

    status, tokens = Browser().get_eligibility(address=address)

    excel.edit_table(wallet_data=[address, status, tokens])
    return {"status": status, "tokens": tokens}


if __name__ == "__main__":
    logger.info(f'LayerZero Checker\n')
    if settings.PROXY in ["", "http://log:pass@ip:port"]:
        logger.warning(f'You will not using proxies!\n')
        input('\n> Start')

    with open('addresses.txt') as f: addresses = f.read().splitlines()

    excel = Excel(total_len=len(addresses), name="l0_checker")

    total_tokens = 0
    total_eligibility = 0
    for address in addresses:
        result = checker(address=address, excel=excel)
        if result["status"] == "Eligible":
            total_eligibility += 1
            total_tokens += result["tokens"]
    eligible_percent = round(total_eligibility / len(addresses) * 100, 2)

    excel.edit_table(wallet_data=[f"Total eligible addresses: [{total_eligibility}/{len(addresses)}]"])
    excel.edit_table(wallet_data=[f"Total tokens: {total_tokens} $ZRO"])

    print('\n')
    logger.success(f'Results saved in "results/{excel.file_name}"\n\nTotal eligibility: {eligible_percent}% [{total_eligibility}/{len(addresses)}] with {total_tokens} $ZRO\n\n')
    input('> Exit')
