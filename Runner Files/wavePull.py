import os
import bs4
import requests
import xarray as xr
import pandas as pd
import numpy as np
import sys


def make_url_list():
    url_list = []
    name_list = []
    url_gen = pd.read_csv("data/url_gen.csv")
    for ind in url_gen.index:
        for i in range(url_gen["Min"][ind], url_gen["Max"][ind] + 1):
            level = url_gen["World"][ind]
            time = url_gen["Time"][ind]

            url_string = "https://reflourished.fandom.com/wiki/{0}_-_{1}_{2}".format(
                level.replace(" ", "_"), time, i
            )
            url_list.append(url_string)

            name_string = "{0} {1} {2}".format(level, time, i)
            name_list.append(name_string)

    return url_list, name_list


def pull_wave(src):
    dfs = pd.read_html(io=src, flavor="bs4")
    return dfs[3]


def make_dataset():
    url_list, name_list = make_url_list()
    dfs = []
    error_file = open("data/errors.txt", "w")
    error_file.write("")
    error_file.close()
    error_file = open("data/errors.txt", "a")

    for url in url_list:
        sys.stdout.write(url + "\r")
        df = pull_wave(url)
        dfs.append(df)
        if list(df.columns)[0] != "Waves":
            error_file.write(url)
            error_file.write(df.to_string())

    error_file.close()

    ds = xr.concat([df.to_xarray() for df in dfs], dim=name_list)
    # ds = df.to_xarray()
    ds = ds.rename({"index": "wave", "concat_dim": "level"})
    df = ds.to_dataframe(("level", "wave"))
    df.to_csv("data/waves.csv")


def xpath_method():
    url_list, name_list = make_url_list()
    # levels = np.array([[[]]])
    levels = []
    error_file = open("data/errors.txt", "w")

    for url in url_list:
        # waves_list = np.array([[]])
        waves_list = [url[37:]]
        print(url, end="\r")
        html = requests.get(url).text
        site = bs4.BeautifulSoup(html, "html.parser")
        waves = site.find("table", class_="wavestable")  # .td.a.get("title")
        try:
            rows = waves.find_all("tr")
            for row in rows:
                # zombies_list = np.array([])
                zombies_list = []
                wave_num = row.find("th").text
                # print("\n" + wave_num[:-1])
                zombies = row.find_all("a")
                for zombie in zombies:
                    # zombies_list = np.append(zombies_list, zombie.get("title"))
                    zombies_list.append(zombie.get("title"))
                # waves_list = np.append(waves_list, zombies_list[1:])
                waves_list.append(zombies_list)
            # levels = np.append(levels, waves_list)
            levels.append(waves_list)
        except:
            error_file.write(url + "\n")
            levels.append(["boss level"])
            continue
    print(levels)
    # np_levels = np.asarray(levels)
    # print(np_levels)
    df_levels = pd.DataFrame(levels)
    print(df_levels)
    df_levels.to_csv("waves.csv")


xpath_method()


# rows = waves.find_all("td")
