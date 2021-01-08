import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from dateutil.parser import *
from collections import Counter
from wordcloud import WordCloud
import html
import json
import re

def gender(x):
    return {"M": "male", "F": "female"}.get(x, "Undefined")


def npmax(l):
    max_idx = np.argmax(l)
    max_val = l[max_idx]
    return (max_idx, max_val)


with open("data.json") as f:
    data = json.load(f)

usage = pd.DataFrame(data['Usage']).drop(columns=['advertising_id', 'idfa'])
usage['encounters'] = usage['swipes_likes'] + usage['swipes_passes']
usage.index = pd.to_datetime(usage.index)

print(f"{data['User']['name']}'s Tinder Overview")
print(
    f"Account created on: {parse(data['User']['create_date']):%d %B, %Y at %H:%M}")
print(
    f"Last active at: {parse(data['User']['active_time']):%d %B, %Y at %H:%M}")
print(f"Linked phone number: +{data['User']['phone_id']}\n")

print(f"Bio: {html.unescape(data['User']['bio'])}\n")

print(f"Born on: {parse(data['User']['birth_date']):%d %B, %Y}")
print(f"Gender: {gender(data['User']['gender']).capitalize()}")
if 'instagram' in data['User']:
    print(
        f"Linked to the Instagram profile: {data['User']['instagram']['username']} with {data['User']['instagram']['media_count']} photos/videos")

print(
    f"Looking for {data['User']['age_filter_min']} to {data['User']['age_filter_max']} year old {gender(data['User']['gender_filter'])}s in {data['User']['city']['name']}, {data['User']['city']['region']}\n"
)

likes = usage['swipes_likes'].sum()
passes = usage['swipes_passes'].sum()
matches = usage['matches'].sum()
encounters = usage['encounters'].sum()

messages = [message for matches in data['Messages']
            for message in matches['messages'] if matches['messages'] != []]
matchesMessaged = Counter([x['to'] for x in messages])


print(
    f"Total app opens: {usage['app_opens'].sum()} with a max of {usage['app_opens'].max()} on {usage['app_opens'].idxmax():%d %B, %Y}")
print(
    f"Total encounters: {encounters} with a max of {usage['encounters'].max()} on {usage['encounters'].idxmax():%d %B, %Y}")
print(
    f"Average encounters per session: {(encounters)/usage['app_opens'].sum():.2f}\n")

print(
    f"Total likes: {likes} with a max of {usage['swipes_likes'].max()} on {usage['swipes_likes'].idxmax():%d %B, %Y}")
print(
    f"Total passes: {passes} with a max of {usage['swipes_passes'].max()} on {usage['swipes_passes'].idxmax():%d %B, %Y}")
print(
    f"Total matches: {matches} with a max of {usage['matches'].max()} on {usage['matches'].idxmax():%d %B, %Y}")
print(
    f"Match rate: {matches/likes:.4%} or 1 in {1/(matches/likes):.0f} people")
print(
    f"Matches out of all encounters: {matches/encounters:.4%} or 1 in {1/(matches/encounters):.0f} people\n")

print(
    f"Messages sent: {usage['messages_sent'].sum()} with a max of {usage['messages_sent'].max()} on {usage['messages_sent'].idxmax():%d %B, %Y}")
print(
    f"Messages received: {usage['messages_received'].sum()} with a max of {usage['messages_received'].max()} on {usage['messages_received'].idxmax():%d %B, %Y}")
print(
    f"Matches messaged: {len(matchesMessaged)} ({len(matchesMessaged)/matches:.2%})\n")

print(
    f"Images sent: {len([images for images in messages if images.get('type', '') == 'image'])}")
print(
    f"GIFs sent: {len([gifs for gifs in messages if gifs.get('type', '') == 'gif'])}")
print(
    f"Reactions sent: {len([reactions for reactions in messages if reactions.get('type', '') == 'activity'])}")

words = [html.unescape(message['message'])
         for message in messages if message.get('type', '') == '']

wc = WordCloud(background_color="white", width=1600, height=900,
               regexp="(?:(?<=\s)|(?<=^)|(?<=\b))(?:[-'’.%$#&\/]\b|\b[-.'%$#&\/]|[:;]+[\"^-]*[(\/)]+|[A-Za-z0-9]|\([A-Za-z0-9]+\))+(?=\s|$|\b)", collocations=False).generate(' '.join(words))
plt.imshow(wc, interpolation="bilinear")
plt.axis("off")
plt.tight_layout(pad=0)
plt.show()

frequencies = pd.Series(Counter([len(re.findall(
    "(?:(?<=\s)|(?<=^)|(?<=\b))(?:[-'’.%$#&\/]\b|\b[-.'%$#&\/]|[:;]+[\"^-]*[(\/)]+|[A-Za-z0-9]|\([A-Za-z0-9]+\))+(?=\s|$|\b)", sentence)) for sentence in words])).sort_index().drop(0)
plt.scatter(frequencies.index, frequencies)
plt.xlabel('Message Length')
plt.ylabel('Frequency')
plt.title('Word Count Distribution')
plt.show()

plt.plot(usage.index, usage['swipes_passes'], 'r', label='Passes')
plt.plot(usage.index, usage['swipes_passes'].rolling(
    7, center=True).mean(), 'm--', label="Passes 7-day rolling average")
plt.plot(usage.index, usage['swipes_likes'], 'g', label='Likes')
plt.plot(usage.index, usage['swipes_likes'].rolling(
    7, center=True).mean(), 'b--', label="Likes 7-day rolling average")
ax = plt.gca()
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
plt.legend()
plt.ylabel('Swipe Trend')
plt.title('Likes vs Passes')
plt.tight_layout()
plt.show()

monthly = usage.resample('MS').sum()

plt.bar(monthly.index, monthly['matches'], width=25)
plt.ylabel('Monthly Matches')
ax = plt.gca()
ax2 = ax.twinx()
ax2.plot(monthly.index, monthly['matches']/monthly['swipes_likes'], 'r')
ax2.set_ylabel('Monthly Match Rate')
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
plt.title('Monthly Matches')
plt.tight_layout()
plt.show()
