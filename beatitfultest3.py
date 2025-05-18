from bs4 import BeautifulSoup
from config import config
from fp.fp import FreeProxy
import requests
import time


def _download_url(url="https://www.linkedin.com/jobs/view/4097292294/"):
    """Download the content of the URL and return it as a string.

    Args:
        url (str, optional): The URL to download. Defaults to None.

    Returns:
        bool: True if download was successful, False otherwise.
    """
    global job_post_html_data
    max_retries = config.MAX_RETRIES
    backoff_factor = config.BACKOFF_FACTOR
    use_proxy = False

    for attempt in range(max_retries):
        try:
            proxies = None
            if use_proxy:
                proxy = FreeProxy(rand=True).get()
                proxies = {"http": proxy, "https": proxy}

            response = requests.get(
                url, headers=config.REQUESTS_HEADERS, proxies=proxies
            )
            response.raise_for_status()
            job_post_html_data = response.text
            return True

        except requests.RequestException as e:
            if response.status_code == 429:
                config.logger.warning(
                    f"Rate limit exceeded. Retrying in {backoff_factor * 2 ** attempt} seconds..."
                )
                time.sleep(backoff_factor * 2**attempt)
                use_proxy = True
            else:
                config.logger.error(f"Failed to download URL {url}: {e}")
                return False

    config.logger.error(f"Exceeded maximum retries for URL {url}")
    return False


_download_url()
soup = BeautifulSoup(job_post_html_data, "html.parser")
job_post_raw = soup.get_text(separator=" ", strip=True)

print(job_post_raw)
