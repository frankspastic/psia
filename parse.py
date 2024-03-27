from bs4 import BeautifulSoup
import csv
import requests


def parse_html(meet):
    response = requests.post(url="https://www.academicmeet.com/meet/show_results.php", data={"meet_id": meet["meet_id"]})
    source_code = response.content

    soup = BeautifulSoup(source_code,'html.parser')
    rows = soup.find(id="results_table").find_all('tr')

    results = []
    for row in rows:
        contest_rank = row.find("td", {"class": "contest_rank"})
        contest_title = row.find_previous_sibling("tr", {"class": "contest_title_row"})
        score = row.find("span", {"class": "contestant_score"})
        contestant_school = row.find("span", {"class": "contestant_school"})
        name = row.find("span", {"class": "contestant_name"})
        points = row.find("td", {"class": "contestant_points"})

        if contest_rank and contest_title and contestant_school and name and points and score:
            contestant_school = contestant_school.get_text().split(' / ')
            school = contestant_school[0]
            city = contestant_school[1]

            contestant_score = int(score.get_text()[3:],10) if len(score.get_text()) > 0 else 0
            contest_points = float(points.get_text()) if len(points.get_text()) > 0 else 0

            results.append({
                "district": meet["district"],
                "school": school,
                "city": city,
                "contest": contest_title.find("td").get_text(),
                "contest_rank": contest_rank.get_text().strip(' '),
                "name": name.get_text(),
                "contestant_score": contestant_score,
                "contest_points": contest_points
            })


    if len(results) > 0:
        with open(f'data/psia_2024.csv', 'a', ) as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(list(results[0].keys()))
            for result in results:
                writer.writerow(list(result.values()))


meet_info = [
    {"district": "31AA", "meet_id": 317},
    {"district": "32AA", "meet_id": 318},
    {"district": "33AA", "meet_id": 319},
    {"district": "34AA", "meet_id": 320},
    {"district": "35AA", "meet_id": 321},
    {"district": "36AA", "meet_id": 322},
    {"district": "37AA", "meet_id": 323},
    {"district": "38AA", "meet_id": 324},
    {"district": "39AA", "meet_id": 325},
    {"district": "40AA", "meet_id": 326},
    {"district": "41AA", "meet_id": 327},
    {"district": "42AA", "meet_id": 328},
]

for meet in meet_info:
    parse_html(meet)

