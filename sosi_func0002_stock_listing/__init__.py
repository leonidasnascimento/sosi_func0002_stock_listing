import datetime
import logging
import azure.functions as func
import json
import requests
import pathlib

from typing import List
from configuration_manager.reader import reader
from .crawler import stock_listing_crawler
from .models.stock import stock
from azure.storage.blob import (
    Blob,
    BlockBlobService,
    PublicAccess
)

SETTINGS_FILE_PATH = pathlib.Path(
    __file__).parent.parent.__str__() + "//local.settings.json"

def main(TimerJobSosiMs0002StockListing: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    try:
        logging.info("'TimerJobSosiMs0002StockListing' has begun")

        config_obj: reader = reader(SETTINGS_FILE_PATH, 'Values')
        next_service_url: str = config_obj.get_value("NEXT_SERVICE_URL")
        func_key_header: str = config_obj.get_value("X_FUNCTION_KEY")
        
        # Crawling
        logging.info("Getting stock list. It may take a while...")
        stock_list: list = stock_listing_crawler().get_stock_list()

        if not stock_list or len(stock_list) == 0:
            logging.warning("No stock code was found to process...")
        else:
            for s in stock_list:
                obj: stock = s 

                logging.info("Sending '{}' for next processing step...".format(obj.code))
                jsonAux = json.dumps(obj.__dict__)

                headers = {
                    'content-type': "application/json",
                    'x-functions-key': func_key_header,
                    'cache-control': "no-cache"
                }

                # Ain't gonna wait for any response. At first, we will not care about this. Just going forward
                requests.Response = requests.request("POST", next_service_url, data=jsonAux, headers=headers)
        logging.info("Timer job is done. Waiting for the next execution time")

        pass
    except Exception as ex:
        error_log = '{} -> {}'
        logging.exception(error_log.format(utc_timestamp, str(ex)))
        pass
    pass
