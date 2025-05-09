import csv

def cleanup_billboard_csv():
    rows = []
    with open('billboardProject/billboard2.csv', 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            title = row['title']
            while title and (title[0] == '"' or title[-1] == '"'):
                if title and title[0] == '"':
                    title = title[1:]
                if title and title[-1] == '"':
                    title = title[:-1]
            row['title'] = title
            rows.append(row)

    seen_titles = {}
    for row in rows:
        title = row['title']
        if title in seen_titles:
            row['url'] = seen_titles[title]['url']
        else:
            seen_titles[title] = row

    with open('billboardProject/billboardFixed.csv', 'w', newline='', encoding='utf-8') as file:
        fieldnames = ['title', 'artist', 'year', 'era', 'url']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def consolidate():

    rows = []
    with open('billboardProject/billboardFixed.csv', 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            rows.append(row)

    song_counts = {}
    for row in rows:
        title = row['title']
        if title in song_counts:
            song_counts[title] += 1
        else:
            song_counts[title] = 1

    seen_titles = {}
    for row in rows:
        title = row['title']
        if title in seen_titles:
            seen_titles[title]['count'] += 1
        else:
            seen_titles[title] = row
            seen_titles[title]['count'] = 1

    with open('billboard/billboardConsolidated.csv', 'w', newline='', encoding='utf-8') as file:
        fieldnames = ['title', 'artist', 'year', 'era', 'count','url']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(seen_titles.values())




cleanup_billboard_csv()
consolidate()

