# coding:utf-8
from feedparser import parse
from datetime import datetime as dt
import webbrowser
import pickle


def selectgenre(genretitles, genredata):
    while True:
        print(f"Genre:{genretitles}")
        try:
            genrenum = int(input("閲覧するFeed typeを番号で入力してください: "))
            ftype = genredata[genrenum]
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
def getentries(gurls, oldentry, checkedtitle, displaymode=True):
    getentry = oldentry

    # 除外する記事のキーワード
    exclusionword = ["セール情報", "閲覧注意"]

    for url in gurls:
        entrydic = parse(url).entries
        if displaymode:
            print(f"{url}の記事を{len(entrydic)}件取得")
        else:
            pass
        for entry in entrydic:
            kiji = {
                "title": entry["title"], "link": entry["link"],
                "date": parseDate(entry["updated_parsed"] or entry["published_parsed"]),
                "sourceurl": url
            }
            if True in [word in kiji["title"] for word in exclusionword]:
                continue
            elif True in [kiji["link"] == k["link"] for k in getentry]:
                continue
            elif True in [kiji["link"] == k["link"] for k in checkedtitle]:
                continue
            else:
                getentry.append(kiji)

    getentry.sort(key=lambda x: x['date'], reverse=True)
    return getentry


def readpickle(filename):
    pathname = './data_pickle'
    filename = f'{filename}.pickle'
    filepath = pathname+'/'+filename
    try:
        with open(filepath, 'rb') as f:
            variable = pickle.load(f)
    except FileNotFoundError:
        import os
        os.makedirs(pathname, exist_ok=True)
        variable = []
        with open(filepath, 'wb') as f:
            pickle.dump(variable, f)
    return variable


def writepickle(variable, filename):
    pathname = './data_pickle'
    filename = f'{filename}.pickle'
    filepath = pathname+'/'+filename
    with open(filepath, 'wb') as f:
        pickle.dump(variable, f)


def displayTitle(rssfeeds, maxcolumn, maxrow, searchword="", searchmode=False):
    pretitle = ""
    preday = ""
    if searchmode:
        import re
        # 検索パターンをコンパイル。大文字小文字を区別しない
        repatter = re.compile(searchword, re.IGNORECASE)
    for number, entry in enumerate(rssfeeds):
        # タイトルを表示
        thistitle = entry['title']
        sourceurl = entry["sourceurl"]
        lastday = "{0:%Y/%m/%d}".format(entry["date"])
        if searchmode:
            result = repatter.search(thistitle + sourceurl)
            if result:
                pass
            else:
                maxcolumn += 1
                continue
        elif pretitle == thistitle or thistitle == "":
            maxcolumn += 1
            continue
        if preday != lastday:
            print(lastday)
            preday = lastday
        pretitle = thistitle
        thistitle = thistitle.replace("&apos;", "")
        thistitle = thistitle.replace("Coronavirus", "Covid19")
        print(f"{number:0=2}: {thistitle[:maxrow]}")
        if number > maxcolumn:
            return None


def savefeed(rssfeeds, checkedfeeds, ftype):
    rssfeeds.sort(key=lambda x: x["date"], reverse=True)
    checkedfeeds.sort(key=lambda x: x["date"], reverse=True)
    writepickle(rssfeeds[:300], ftype+'oldentry')
    writepickle(checkedfeeds[:300], ftype+'checkedfeeds')


def readfeed(ftype):
    """return (checkedfeeds, oldentry)"""
    checked = readpickle(ftype+"checkedfeeds")
    old = readpickle(ftype+"oldentry")
    return checked, old


def readchecked(feeds, maxrow=37):
    print("   "*200)
    while True:
        print("    "*25)
        displayTitle(feeds, 37, maxrow)
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


def main():
    with open(file="feedurls.txt", mode="r", encoding="utf-8") as f:
        urlinfo = f.read()
    jogaimoji = (" ", "\n", "\t")

    for jmoji in jogaimoji:
        urlinfo = urlinfo.replace(jmoji, "")

    urlinfo = urlinfo.split("---")
    urls = {}

    for i in urlinfo:
        i = i.strip(",")
        a = i.split("@")
        feedurls = a[1].strip().split(",")
        urls[a[0]] = feedurls

    feed_genres = list(urls.keys())
    display_genres = "|"

    for n, s in enumerate(feed_genres):
        display_genres += f"{n}: {s}|"

    feedtype = selectgenre(display_genres, feed_genres)
    # 記事を取得する場合に各サイトの取得件数を表示する場合はTrue
    displaymode = True
    searchmode = False
    searchword = ""
    checkedtitle, oldentry = readfeed(feedtype)
    while True:
        rssentries = getentries(
            urls[feedtype], oldentry, checkedtitle, displaymode)
        # 2回目以降は取得件数を表示しない
        displaymode = False
        print("     "*25)
        print(f"Genre: {feedtype}")
        maxcol = 37
        if "english" in feedtype.lower():
            maxrow = 65
        else:
            maxrow = 37
        if searchmode:
            print("     "*25)
            print(f"検索ワード:{searchword}")
            displayTitle(rssentries, maxcol, maxrow, searchword, searchmode)
            print("""
            fq で通常モードに戻る
            """)
        else:
            displayTitle(rssentries, maxcol, maxrow, searchword, searchmode)
            print()
            print("g:ジャンルを変更する c:閲覧済記事を読む d:記事除外Mode f:検索モード q:終了")

        n = input("見たい記事の番号を入力: ")

        if n.lower() == "q":
            break
        elif searchmode:
            if n.lower() == "fq":
                searchmode = False
                continue
            else:
                pass

        elif n.lower() == "g":
            savefeed(rssentries, checkedtitle, feedtype)
            feedtype = selectgenre(display_genres, feed_genres)
            displaymode = True
            checkedtitle, oldentry = readfeed(feedtype)
            continue
        elif n.lower() == "c":
            readchecked(checkedtitle, maxrow)
            continue

        elif n.lower() == "f":
            searchmode = True
            searchword = input("検索ワード＝: ")
            continue

        try:
            n = int(n)
            webbrowser.open_new(rssentries[n]["link"])
            checked = rssentries.pop(n)
            checkedtitle.append(checked)
        except ValueError:
            print("ValueError")
            continue
        except IndexError:
            print("IndexError")
            continue

    savefeed(rssentries, checkedtitle, feedtype)


if __name__ == "__main__":
    main()
