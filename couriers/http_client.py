import time
import requests
from requests.exceptions import RequestException
import logging

logger = logging.getLogger(__name__)

class HttpClient:
    
    def __init__(self, max_retries=3, backoff_factor=0.5, timeout=30, default_headers=None):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.timeout = timeout
        self.default_headers = default_headers or {}
    
    def request(self, method, url, headers=None, params=None, data=None, json_data=None):
        merged_headers = {**self.default_headers, **(headers or {})}
        retries = 0
        
        while retries <= self.max_retries:
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=merged_headers,
                    params=params,
                    data=data,
                    json=json_data,
                    timeout=self.timeout
                )
                
                if 500 <= response.status_code < 600:
                    retries += 1
                    if retries > self.max_retries:
                        break
                    
                    backoff_time = self.backoff_factor * (2 ** (retries - 1))
                    logger.warning(f"Server error {response.status_code}, retrying in {backoff_time}s")
                    time.sleep(backoff_time)
                    continue
                
                return response
                
            except RequestException as e:
                retries += 1
                if retries > self.max_retries:
                    logger.error(f"Max retries reached for {url}: {str(e)}")
                    raise
                
                backoff_time = self.backoff_factor * (2 ** (retries - 1))
                logger.warning(f"Request failed, retrying in {backoff_time}s: {str(e)}")
                time.sleep(backoff_time)
        
        response.raise_for_status()
        return response