# %%
from __future__ import annotations

from datetime import datetime
import pandas as pd
import numpy as np
from tqdm import tqdm
import esv_ranges
import plotly.graph_objects as go

from importlib import reload

# reload(esv_ranges)
import book as BookEnum
# reload(BookEnum)
from book import Book

from sermonCounting.sermon import Sermon
from sermonCounting.getSermons import processMainPageByIdx

# %%
start = 1
end = 141
with tqdm(total=(end - start + 1) * 10) as pbar:
    sermons: 'set[Sermon]' = set()
    for num in range(start, end+1): # 141 pages to do
        sermons.update(processMainPageByIdx(num))
        pbar.update(10)

tags = set()
missingTagCount = 0
for sermon in sermons:
    if len(sermon.tags) == 0:
        missingTagCount += 1
    else:
        tags.update(sermon.tags)

data = pd.DataFrame.from_records([s.to_dict() for s in sermons])
data

# %%
# Sermon Counts
print("Sermon Counts")
westburyMask = (data['Emmanuel Westbury'] | data['EW Students'] | data['Weekend Away'] | data['audio_url'].str.contains('westbury', case=False))
westbury = data[westburyMask]
print(f"Westbury: {westbury.shape[0]}")

bishopstonMask = (data['Emmanuel Bishopston'] | data['audio_url'].str.contains('ashleydown', case=False))
bishopston = data[bishopstonMask]
print(f"Bishopston: {bishopston.shape[0]}")

eccMask = (data['Emmanuel City Centre'] | data['ECC'] | data['audio_url'].str.contains('ecc', case=False))
ecc = data[eccMask]
print(f"ECC: {ecc.shape[0]}")

unassigned = data[~(westburyMask | bishopstonMask | eccMask)]
print(f"unassigned: {unassigned.shape[0]}")

churches = {
    'all': data,
    'ECC': data[eccMask],
    'EW' : data[westburyMask], 
    'EB' : data[bishopstonMask],
}

# %%
# Find sermons from multiple churches
two = data[(westburyMask.astype(int) + bishopstonMask.astype(int) + eccMask.astype(int)) == 2]
three = data[(westburyMask.astype(int) + bishopstonMask.astype(int) + eccMask.astype(int)) == 3]

# %%
# Missing books
emptyBookMask = data['passage_count'] == 0
data[emptyBookMask]

# %%
# Missing Westbury Books
data[westburyMask & emptyBookMask]

# %%
data['passage_count'].plot.hist(bins=data['passage_count'].max()+1)

# %%
# Find specific book
mask = pd.Series(False, index=data.index)

for i in range(data['passage_count'].max()):
    mask = mask | (data[f'book_{i}'] == Book.HABAKKUK)

print(data[mask].title)

# %%
print("Unvisited books")
d = data[westburyMask & (data.date > datetime(2020,1,1))]
for book in Book:
    # Skip abreviated books
    mask = pd.Series(False, index=d.index)

    for i in range(d['passage_count'].max()):
        mask = mask | (d[f'book_{i}'] == book)
    if mask.sum() == 0:
        print(book.value[0].title())

# %%
# Create visited Series

bible_data = {
}

bookToIndex = {}
indexToBook = {}

chapVerse = {}

for i, (bookName, chapterCount, verseCounts) in enumerate(esv_ranges.passage_data[1:]):
    bookToIndex[bookName.name] = i
    indexToBook[i] = bookName
    # Remove None padding
    verseCounts = verseCounts[1:]
    chapVerse[bookName.name] = {}
    for chapterNum, chapterVerseCount in enumerate(verseCounts, start=1):
        chapVerse[bookName.name][chapterNum] = chapterVerseCount
        for verse in range(1, chapterVerseCount + 1):
            bible_data[(i, chapterNum, verse)] = 0

visited = pd.Series(bible_data)
visitedIdx = visited.index

# %%
# Mark books we have been to
for church, d in churches.items():
    church = 'all'
    visited = pd.Series(0, index=visited.index)
    for i, sermonData in tqdm(d.iterrows(), total=d.shape[0]):
        for i in range(sermonData['passage_count']):
            sliceStart = (
                bookToIndex[sermonData[f'book_{i}'].name],
                sermonData[f'chapter_start_{i}'],
                max(sermonData[f'verse_start_{i}'], 0),
            )
            sliceEnd = (
                bookToIndex[sermonData[f'book_{i}'].name],
                sermonData[f'chapter_end_{i}'],
                max(sermonData[f'verse_end_{i}'], chapVerse[sermonData[f'book_{i}'].name][sermonData[f'chapter_end_{i}']]),
            )
            visited[sliceStart:sliceEnd] += 1

    visited.sum()

    v = visited.T.copy()
    v.index = [f'{indexToBook[x[0]]} {x[1]}:{x[2]}' for x in v.index.to_flat_index()]
    v

    pd.set_option('plotting.backend', 'plotly')
    fig = v.plot.line()
    fig.write_html(f'output/{church}.html')
    fig

# %%
# Create with slider
def generateGraphData(data, idx):
    visited = pd.DataFrame(0, index=idx, columns=range(data.date.min().year, data.date.max().year+1))
    for year in visited.columns:
        filtered = data[(datetime(year, 1, 1) < data['date']) & (data['date'] < datetime(year+1, 1, 1))]
        for i, sermonData in filtered.iterrows():
            for i in range(sermonData['passage_count']):
                sliceStart = (
                    bookToIndex[sermonData[f'book_{i}'].name], 
                    sermonData[f'chapter_start_{i}'], 
                    sermonData[f'verse_start_{i}'],
                )
                sliceEnd = (
                    bookToIndex[sermonData[f'book_{i}'].name], 
                    sermonData[f'chapter_end_{i}'], 
                    sermonData[f'verse_end_{i}'],
                )
                visited.loc[sliceStart:sliceEnd,:year] += 1

    v = visited.copy()
    v.index = [f'{indexToBook[x[0]].getName()} {x[1]}:{x[2]}' for x in v.index.to_flat_index()]
    return v


# %%
# Generate figures
for church, d in (pbar := tqdm(churches.items(), total=len(churches))):
    pbar.set_postfix_str(church)
    # Generate 
    fig = go.Figure()
    v = generateGraphData(d, visitedIdx)
    for year in v.columns:
        year_data = v.loc[:,v.columns == year]
        fig.add_trace(go.Scatter(
            x=year_data.index,
            y=year_data.squeeze(),
            mode='lines',
            name="",
            visible=(year==v.columns.max()),
        ))

    # Add slider
    steps = []
    for i, year in enumerate(v.columns):
        step = dict(
            method="update",
            args=[{"visible": [False] * v.shape[1]}],
            label=str(year),
        )
        step["args"][0]["visible"][i] = True  # Toggle i'th trace to "visible"
        steps.append(step)

    sliders = [dict(
        active=len(v.columns) - 1,
        steps=steps,
        y=0
    )]

    fig.update_layout(
        sliders=sliders, title="",
        yaxis_title="Number of Visits", 
        yaxis_range=[0, v.max().max()+1],
        xaxis=dict(
            title="",
            nticks=10
            # tickmode='array',
            # tickvals=tickPositions,
            # ticktext=[b.getName() for b in Book],
        ),
    )

    fig.write_html(f'output/animated_line_{church}.html')

    # Generate bar graphs
    total = pd.Series(-1, index=[b.getName() for b in Book])
    count = pd.DataFrame(-1, columns=v.columns, index=[b.getName() for b in Book])

    for b in Book:
        mask = v.index.str.startswith(b.getName())
        total.loc[b.getName()] = mask.sum()
        count.loc[b.getName()] = (v[mask] > 0).sum()

    perc = (count.T / total).T

    fig = go.Figure()
    for year in perc.columns:
        year_data = perc.loc[:,perc.columns == year]
        fig.add_trace(go.Bar(
            x=year_data.index,
            y=year_data.squeeze(),
            name="",
            visible=(year==perc.columns.max()),
        ))

    # Add slider
    steps = []
    for i, year in enumerate(perc.columns):
        step = dict(
            method="update",
            args=[{"visible": [False] * perc.shape[1]}],
            label=str(year),
        )
        step["args"][0]["visible"][i] = True  # Toggle i'th trace to "visible"
        steps.append(step)

    sliders = [dict(
        active=len(perc.columns) - 1,
        steps=steps,
        y=0
    )]

    fig.update_layout(
        sliders=sliders, title="",
        yaxis_title="Percentage of book Covered", 
        yaxis_range=[0, 1],
        xaxis=dict(
            title="",
        ),
    )

    # Show the plot
    fig.write_html(f'output/animated_bar_{church}.html')
