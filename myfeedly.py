# coding:utf-8
from feedparser import parse
from datetime import datetime as dt
import webbrowser
import pickle

with open(file="feedurls.txt", mode="r") as f:
    urlinfo = f.read()
jogaimoji = (" ", "\n", "\t")
for jmoji in jogaimoji:
    urlinfo = urlinfo.replace(jmoji, "")
urlinfo = urlinfo.split("---")
urls = {}
for i in urlinfo:
    a = i.split("@")
    feedurls = a[1].strip().split(",")
    urls[a[0]] = feedurls
    for prurl in feedurls:
        print(prurl)


feed_genres = tuple(urls.keys())
display_genres = ""

for n, s in enumerate(feed_genres):
    display_genres += f"|{n}: {s} |"


def selectgenre(d_genres, f_genres):
    while True:
        print(f"Feed types are {d_genres}")
        try:
            genrenum = int(input("閲覧するFeed typeを番号で入力してください: "))
            ftype = f_genres[genrenum]
            break
        except ValueError:
            print("Value Errorです")
        except TypeError:
            print("Type Errorです")
        except IndexError:
            print("Index Errorです")
    return ftype


def parseDate(dateData):
    """日付のパース用関数"""
    return dt(
        dateData.tm_year, dateData.tm_mon, dateData.tm_mday,
        dateData.tm_hour, dateData.tm_min, dateData.tm_sec)


# 取得&整形
def getentries(gurls, oldentry=[], checkedtitle=[]):
    getentry = oldentry
    # 除外する記事のキーワード
    exclusionword = ["セール情報", "閲覧注意"]

    for url in gurls:
        for entry in parse(url).entries:
            kiji = {
                "title": entry["title"], "link": entry["link"],
                "date": parseDate(entry["updated_parsed"] or entry["published_parsed"])
            }
            if True in [word in kiji["title"] for word in exclusionword]:
                continue
            elif kiji not in getentry and kiji not in checkedtitle:
                getentry.append(kiji)
    return getentry


def readpickle(filename):
    try:
        with open(f'{filename}.pickle', 'rb') as f:
            variable = pickle.load(f)
    except FileNotFoundError:
        variable = []
        with open(f'{filename}.pickle', 'wb') as f:
            pickle.dump(variable, f)
    return variable


def writepickle(variable, filename):
    with open(f'{filename}.pickle', 'wb') as f:
        pickle.dump(variable, f)


def displayTitle(rssfeeds, maxcolumn):
    for number, entry in enumerate(rssfeeds[:maxcolumn]):
        # タイトルを表示
        pretitle = entry['title']
        thistitle = pretitle[:36]
        print(f'{number:0=2}: {thistitle}')


def savefeed(rssfeeds, checkedfeeds):
    checkedfeeds.sort(key=lambda x: x["date"], reverse=True)
    writepickle(rssentries[:500], feedtype+'oldentry')
    writepickle(checkedfeeds[:500], feedtype+'checkedfeeds')


def readfeed(ftype):
    """return (checkedfeeds, oldentry)"""
    checked = readpickle(ftype+"checkedfeeds")
    old = readpickle(ftype+"oldentry")
    return checked, old


def readchecked(feeds):
    print("   "*200)
    while True:
        print("    "*25)
        displayTitle(feeds, 37)
        print("閲覧済モード")
        print("閲覧済モードを終える場合はqを入力")
        n = input("みたい記事の番号を入力: ")
        if n.lower() == "q":
            break
        else:
            try:
                n = int(n)
                webbrowser.open_new(feeds[n]["link"])
            except ValueError:
                print("適切な数値を入力してください")
                continue
            except IndexError:
                print("IndexError")
                continue


feedtype = selectgenre(display_genres, feed_genres)
checkedtitle, oldentry = readfeed(feedtype)
print("input Q or q for exit.", end="\n")
input("press Enter key: ")
ischecked = False

while True:

    rssentries = getentries(urls[feedtype], oldentry, checkedtitle)

    # 日付順でソート
    rssentries.sort(key=lambda x: x["date"], reverse=True)
    print("     "*25)
    displayTitle(rssentries, 37)
    print()
    print("記事のジャンルを変更する場合はgを入力してください")
    print("閲覧済みの記事を読みたい場合はcを入力してください")
    n = input("見たい記事の番号を入力: ")
    if n.lower() == "q":
        break
    elif n.lower() == "g":
        savefeed(rssentries, checkedtitle)
        feedtype = selectgenre(display_genres, feed_genres)
        checkedtitle, oldentry = readfeed(feedtype)
        continue
    elif n.lower() == "c":
        readchecked(checkedtitle)
        continue
    else:
        try:
            n = int(n)
            webbrowser.open_new(rssentries[n]["link"])
            checked = rssentries.pop(n)
            checkedtitle.append(checked)
        except ValueError:
            print("適切な数値を入力してください。終了する場合は q か Qを入力してください")
            continue
        except IndexError:
            print("IndexError")
            continue


savefeed(rssentries, checkedtitle)
