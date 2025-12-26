# %%
from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from pathlib import Path
import pandas as pd
from tqdm import tqdm
import esv_ranges
import plotly.graph_objects as go

from book import Book

from sermonCounting.sermon import Sermon
from sermonCounting.getSermons import processMainPageByIdx, getPageCount

# %%
start = 1
end = getPageCount()

with tqdm(total=(end - start + 1) * 10) as pbar:
    sermons: 'set[Sermon]' = set()
    for num in range(start, end+1): # 141 pages to do
        sermons.update(processMainPageByIdx(num))
        pbar.update(10)

data = pd.DataFrame.from_records([s.to_dict() for s in sermons])


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
    'combined': data,
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
    mask = mask | ((data[f'book_{i}'] == Book.MATTHEW))
                #    & (data[f'chapter_start_{i}'] == 14))

mask = mask & (data.date >= datetime(2009, 1, 1))
mask = mask & (data.date < datetime(2010, 1, 1))
mask = mask & westburyMask

data[mask].sort_values(by='date')[['title', 'date']]

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

bible_data = {}

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
# Create with slider
def generateGraphData(data, idx, startYear=None, endYear=None):
    if startYear is None:
        startYear = data.date.min().year
    if endYear is None:
        endYear = data.date.max().year
    visited = pd.DataFrame(0, index=idx, columns=range(startYear, endYear+1))
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
# Create directory
BASE_DIR = Path("output")
BASE_DIR.mkdir(exist_ok=True, parents=True)

def generateFilename(church: str, type: str, base: Path = BASE_DIR):
    output = base.joinpath(church, type).with_suffix(".html")
    output.parent.mkdir(exist_ok=True, parents=True)
    return output


# %%
# Generate figures
for church, d in (pbar := tqdm(churches.items(), total=len(churches))):
    pbar.set_postfix_str(church)
    # Generate 
    fig = go.Figure()
    v = generateGraphData(d, visitedIdx)
    endYear = v.columns[-1]
    for year in v.columns:
        year_data = v.loc[:,v.columns == year]
        fig.add_trace(go.Scatter(
            x=year_data.index,
            y=year_data.squeeze(),
            mode='lines',
            name="",
            visible=(year==v.columns.max()),
            fill='tozeroy',
        ))

    # Add slider
    steps = []
    for i, year in enumerate(v.columns):
        step = dict(
            method="update",
            args=[{"visible": [False] * v.shape[1]}],
            label=year,
        )
        step["args"][0]["visible"][i] = True  # Toggle i'th trace to "visible"
        steps.append(step)

    sliders = [dict(
        currentvalue=dict(visible=False),
        active=len(v.columns) - 1,
        steps=steps,
        y=1.1,
        yanchor='bottom'
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
        margin=dict(t=140),
    )
    fig.update_xaxes(tickangle=45, automargin=True)

    fig.write_html(generateFilename(church, "line"))

    # Generate bar graphs
    total = pd.Series(-1, index=[b.getName() for b in Book])
    count = pd.DataFrame(-1, columns=v.columns, index=[b.getName() for b in Book])

    for b in Book:
        mask = v.index.str.startswith(b.getName())
        total.loc[b.getName()] = mask.sum()
        count.loc[b.getName()] = (v[mask] > 0).sum()

    perc = ((count.T / total).T * 100).round(2)

    fig = go.Figure()
    for year in perc.columns:
        year_data = perc.loc[:,perc.columns == year]
        fig.add_trace(go.Bar(
            x=year_data.index,
            y=year_data.squeeze(),
            name="",
            visible=(year==perc.columns.max()),
            text=[f'{x[0]}/{y} verses' for x, y in zip(count.loc[:,perc.columns == year].values, total.values)],
            textposition="none",
        ))

    # Add slider
    steps = []
    for i, year in enumerate(perc.columns):
        step = dict(
            method="update",
            args=[{"visible": [False] * perc.shape[1]}],
            label=year,
        )
        step["args"][0]["visible"][i] = True  # Toggle i'th trace to "visible"
        steps.append(step)

    sliders = [dict(
        currentvalue=dict(visible=False),
        active=len(perc.columns) - 1,
        steps=steps,
        y=1.1,
        yanchor='bottom'
    )]

    fig.update_layout(
        sliders=sliders, title="Percentage of verses covered for each book",
        yaxis_title="Percentage of book Covered", 
        yaxis_range=[0, 100],
        xaxis=dict(
            title="",
        ),
        margin=dict(t=140),
    )
    fig.update_xaxes(tickangle=45, automargin=True)

    # Show the plot
    fig.write_html(generateFilename(church, "bar"))

    # Generate stacked bar graphs
    total = pd.Series(-1, index=[b.getName() for b in Book])
    count = pd.DataFrame(-1, columns=v.columns, index=[b.getName() for b in Book])

    for b in Book:
        mask = v.index.str.startswith(b.getName())
        total.loc[b.getName()] = mask.sum()
        count.loc[b.getName()] = (v[mask] > 0).sum()

    bottom = count
    top = (total - count.T).T

    fig = go.Figure()
    for year in bottom.columns:
        bottom_year_data = bottom.loc[:,bottom.columns == year]
        top_year_data = top.loc[:,top.columns == year]
        fig.add_trace(go.Bar(
            x=bottom_year_data.index,
            y=bottom_year_data.squeeze(),
            name="Visited",
            visible=(year==bottom.columns.max()),
            offsetgroup=0,
        ))
        fig.add_trace(go.Bar(
            x=top_year_data.index,
            y=top_year_data.squeeze(),
            name="Unread",
            visible=(year==top.columns.max()),
            base=bottom_year_data.squeeze(),
            offsetgroup=0,
        ))

    # Add slider
    steps = []
    for i, year in enumerate(bottom.columns):
        step = dict(
            method="update",
            args=[{"visible": [False] * bottom.shape[1]*2}],
            label=year,
        )
        step["args"][0]["visible"][i*2] = True  # Toggle i'th trace to "visible"
        step["args"][0]["visible"][i*2+1] = True  # Toggle i'th trace to "visible"
        steps.append(step)

    sliders = [dict(
        currentvalue=dict(visible=False),
        active=len(perc.columns) - 1,
        steps=steps,
        y=1.1,
        yanchor='bottom'
    )]

    fig.update_layout(
        sliders=sliders, title="Split between number of verses covered for each book",
        yaxis_title="Number of verses", 
        xaxis=dict(
            title="",
        ),
        margin=dict(t=140),
    )
    fig.update_xaxes(tickangle=45, automargin=True)

    # Show the plot
    fig.write_html(generateFilename(church, "stacked_bar"))

    # Create raw count graphs
    sermonCount = pd.DataFrame(0, columns=v.columns, index=[b.getName() for b in Book])
    for year in v.columns:
        filtered = d[(datetime(year, 1, 1) < d['date']) & (d['date'] < datetime(year+1, 1, 1))]
        for _, sermon in filtered.iterrows():
            sermonBooks = []
            for i in range(sermon.passage_count):
                sermonBooks.append(sermon[f'book_{i}'].getName())
            sermonCount.loc[sermonBooks,:year] += 1

    fig = go.Figure()
    for year in sermonCount.columns:
        year_data = sermonCount.loc[:,sermonCount.columns == year]
        fig.add_trace(go.Bar(
            x=year_data.index,
            y=year_data.squeeze(),
            name="",
            visible=(year==sermonCount.columns.max()),
        ))

    # Add slider
    steps = []
    for i, year in enumerate(sermonCount.columns):
        step = dict(
            method="update",
            args=[{"visible": [False] * sermonCount.shape[1]}],
            label=year,
        )
        step["args"][0]["visible"][i] = True  # Toggle i'th trace to "visible"
        steps.append(step)

    sliders = [dict(
        currentvalue=dict(visible=False),
        active=len(sermonCount.columns) - 1,
        steps=steps,
        y=1.1,
        yanchor='bottom'
    )]

    fig.update_layout(
        sliders=sliders, title="Number of sermons in each book",
        yaxis_title="Number of Sermons", 
        yaxis_range=[0, round(sermonCount.max().max()+5, -1)],
        xaxis=dict(
            title="",
        ),
        margin=dict(t=140),
    )
    fig.update_xaxes(tickangle=45, automargin=True)

    # Show the plot
    fig.write_html(generateFilename(church, "count"))

# %%
# Find missing Romans verse
if 'yearData' not in locals():
    yearData = generateGraphData(churches['combined'], visitedIdx)[2007]
romans = yearData[yearData.index.str.startswith("Romans")]
romans[romans == 0]
