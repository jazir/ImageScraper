import os
import time
import requests
import shutil
from selenium import webdriver

# My Chrome Version 85.0.4183.121 (Official Build) (64-bit)
DRIVER_PATH = './chromedriver'


def fetch_image_urls(query: str, max_links_to_fetch: int, wd: webdriver, sleep_between_interactions: float = 1):
    def scroll_to_end(wd):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(sleep_between_interactions)

     # build the google query
    search_url = f"https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={query}&oq={query}&gs_l=img"

    # load the page
    wd.get(search_url)

    image_urls = set()
    image_count = 0
    results_start = 0
    while image_count < max_links_to_fetch:
        scroll_to_end(wd)

        # get all image thumbnail results
        thumbnail_results = wd.find_elements_by_css_selector("img.Q4LuWd")
        number_results = len(thumbnail_results)

        print(f"Found: {number_results} search results. Extracting links from {results_start}:{number_results}")

        for img in thumbnail_results[results_start:number_results]:
            # try to click every thumbnail such that we can get the real image behind it
            try:
                img.click()
                time.sleep(sleep_between_interactions)
            except Exception:
                continue

            # extract image urls
            actual_images = wd.find_elements_by_css_selector('img.n3VNCb')
            for actual_image in actual_images:
                if actual_image.get_attribute('src') and 'http' in actual_image.get_attribute('src'):
                    image_urls.add(actual_image.get_attribute('src'))

            image_count = len(image_urls)

            if len(image_urls) >= max_links_to_fetch:
                print(f"Found: {len(image_urls)} image links, done!")
                break
        else:
            print("Found:", len(image_urls), "image links, looking for more ...")
            time.sleep(30)

            load_more_button = wd.find_element_by_css_selector(".mye4qd")
            if load_more_button:
                wd.execute_script("document.querySelector('.mye4qd').click();")

        # move the result start point further down
        results_start = len(thumbnail_results)

    return image_urls


def persist_image(folder_path: str, filename: str, url: str, counter):
    try:
        image_content = requests.get(url).content

    except Exception as e:
        print(f"ERROR - Could not download {url} - {e}")

    try:
        f = open(os.path.join(folder_path, filename + "_" + str(counter) + ".jpg"), 'wb')
        f.write(image_content)
        f.close()
        print(f"SUCCESS - saved {url} - as {folder_path}")
    except Exception as e:
        print(f"ERROR - Could not save {url} - {e}")


def search_and_download(search_term: str, driver_path: str, save_path='./images', number_images=10):
    save_loc = os.path.join(save_path, '_'.join(search_term.lower().split(' ')))

    if not os.path.exists(save_loc):
        os.makedirs(save_loc)
    else:  # if that folder already exits, clear its contents
        shutil.rmtree(save_loc)
        os.mkdir(save_loc)

    with webdriver.Chrome(executable_path=driver_path) as wd:
        res = fetch_image_urls(search_term, number_images, wd=wd, sleep_between_interactions=0.5)

    counter = 0
    for elem in res:
        persist_image(save_loc, search_term, elem, counter)
        counter += 1


if __name__ == '__main__':
    searchItem = input('Input the search item: ')
    imagesCount = int(input('Number of images: '))
    # To be added: check validity of imagesCount
    if imagesCount <= 0:
        print("Invalid number")
    else:
        search_and_download(search_term=searchItem, number_images=imagesCount, driver_path=DRIVER_PATH)
