import sys
import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By

"""This code scrapes the leaderboard data of a given HackerRank contest, given contest URL, using selenium webdriver
and saves the leaderboard data to a csv file called "slug.csv" in Results folder. It can both scrape ACM type leaderboards as
well as list view leaderboards found commonly in HackerRank. The column names are same as HackerRank headers,
and questions are named Q[question number] for ACM type leaderboards. There is a maxPage limit set to 14; however,
this limit can be lifted easily by setting maxPage to a arbitrarily large number. In some cases, such as low
bandwidth and slow internet speed, script may fail to retrieve data. Rerunning the code will solve the problems in
most of the cases.

returns slug.csv
"""
def getLeaderBoard(slug):
    options = Options()
    options.add_argument('-headless')
    browser = webdriver.Firefox(options=options)


    url = 'https://www.hackerrank.com/'+slug+'/'  # Change the url of the contest
    maxPage = 14  # Set the maxPage limit

    if url[-11:] != "leaderboard":  # If only contest link is given, redirect to leaderboard link
        url = url + "leaderboard"


    def getPage(number):  # Return the leaderboard for given page number
        browser.get(url + "/" + str(number))
        browser.implicitly_wait(5)
        if len(browser.find_elements(By.CLASS_NAME,"acm-leaderboard-cell  ")) > 10:
            return 1, [x.text for x in browser.find_elements(By.CLASS_NAME,"acm-leaderboard-cell  ")]
        return 0, [x.text for x in browser.find_elements(By.CLASS_NAME,"leaderboard-list-view")]


    # columnLength = max(int(len(getPage(1)[1]) / 10), int(len(getPage(1)[1]) / 10)) if getPage(1)[0] else len(
    #     [text.split('\n') for text in getPage(1)[1]][0])
    columnLength = 0
    # print(getPage(1))
    if getPage(1)[0]:
        columnLength = max(int(len(getPage(1)[1]) / 10), int(len(getPage(1)[1]) / 10))
    else:
        # print([text.split('\n') for text in getPage(1)[1]])
        if(len(getPage(1)[1]) !=0):
            columnLength = len([text.split('\n') for text in getPage(1)[1]][0])

    if(columnLength == 0):
        print("No Submissions")
        return

    leaderboard = np.empty((0, columnLength))
    print("HackerRank scraping started.\n")
    number = 1  # Current page number

    # Loop over until there are no end page arrows
    while maxPage + 1 > number:
        try:
            pageType, pageList = getPage(number)
            if pageType:
                pageList = np.array(pageList).reshape(-1, columnLength)
            else:
                pageList = np.array([text.split('\n') for text in pageList])
            if pageList.shape[0] < 10:
                try:
                    browser.find_element(By.LINK_TEXT,str(number + 1))
                except NoSuchElementException:
                    #print(pageList)
                    if(len(pageList) != 0):leaderboard = np.append(leaderboard, pageList, axis=0)
                    break
                raise ZeroDivisionError("Could not get all in page {}".format(number))
            leaderboard = np.append(leaderboard, pageList, axis=0)
        except ZeroDivisionError:
            number -= 1
        finally:
            number += 1

    browser.close()

    # Convert the array to pandas DataFrame
    leaderboard = pd.DataFrame(leaderboard)
    leaderboard.rename(columns=lambda x: str(int(x)), inplace=True)
    leaderboard.drop_duplicates(keep='last', inplace=True)
    leaderboard["0"] = pd.to_numeric(leaderboard["0"])
    leaderboard.sort_values(by=['0'], inplace=True)
    leaderboard.reset_index(drop=True, inplace=True)

    leaderboard.rename(columns=lambda x: str(int(x) - 3), inplace=True)
    leaderboard = leaderboard.add_prefix('Q')
    leaderboard.rename(columns={'Q-3': 'rank', 'Q-2': 'user', 'Q-1': 'score', 'Q0': 'time'}, inplace=True)

    if leaderboard.shape[0] < 1:
        print("Could not find a leaderboard with this URL. Please check the URL and try again.")
    else:
        print("HackerRank scrape completed.\nScraped board length: ", leaderboard.shape[0])
        leaderboard.to_csv("./Results/"+slug+".csv", index=False)

if(__name__ == '__main__'):
    weekno = sys.argv[1]
    slugs = [
        'dsa-lab-d',
        'dsa-lab-e'
    ]

    for i in slugs:
        getLeaderBoard(i[:7]+weekno+i[7:])
    
