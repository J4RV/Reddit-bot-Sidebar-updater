# Info:: https://praw.readthedocs.org/en/stable/ ::

import schedule
import praw
import re
import time

import config

# Searches the two stickies in the subreddit
# Gets the current sidebar
# Updates the sidebar with the current urls of the sticky posts.
def update_sidebar():
    sidebar = get_sidebar()

    # Update sticky 1 in sidebar
    # Ugly IK
    try:
        sticky = reddit.subreddit(config.data["SUB"]).sticky(number=1)
    except:
        print("Couldnt update Sticky 1")
    else:
        if sticky.link_flair_text:
            section = sticky.link_flair_text
            url = sticky.url
            sidebar = update_sidebar_link(sidebar, section, url)

    # Update sticky 2 in sidebar
    try:
        sticky = reddit.subreddit(config.data["SUB"]).sticky(number=2)
    except:
        print("Couldnt update Sticky 2")
    else:
        if sticky.link_flair_text:
            section = "" + sticky.link_flair_text
            url = sticky.url
            sidebar = update_sidebar_link(sidebar, section, url)

    set_sidebar(sidebar)


# this function searches the current url from a section (ex: Ask CompHS) and replaces it with the newest url.
def update_sidebar_link(sidebar, section, url):
    if section == 'Ask CompHS':
        section = 'Ask /r/CompetitiveHS'

    section = section.replace('/', '\/')
    section = section.replace('?', '\?')

    pattern = '\[%s\]\((.+?)#dr\)' % section
    # note: re.match only matches at the start of the string FailFish
    results = re.search(pattern, sidebar)

    if results:
        old_url = results.group(1)
        sidebar = sidebar.replace(old_url, url)
        print("Replaced link: %s with %s." % (old_url, url))
    else:
        print("'%s' didn't match any link in the sidebar" % pattern)

    return sidebar


def get_sidebar():
    sidebar = reddit.subreddit(config.data["SUB"]).description

    return sidebar


def set_sidebar(sidebar):
    #r.update_settings(r.get_subreddit(config.SUB), description=sidebar)
    mod = reddit.subreddit(config.data["SUB"]).mod
    mod.update(description = sidebar)
    time_str = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.localtime())

    print("%s - %s's sidebar updated!" % (time_str, config.data["SUB"]))


if __name__ == '__main__':
    reddit = config.init()
    schedule.every().day.at("17:09").do(update_sidebar)

    update_sidebar()

    while True:
        schedule.run_pending()
        time.sleep(60)
