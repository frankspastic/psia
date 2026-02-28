from bs4 import BeautifulSoup
import requests
import gspread
from google.oauth2.service_account import Credentials

SPREADSHEET_ID = "1S8WFyNBxthx_41aF54x5zMFrqedDN8YPK2h_5VT9DUk"

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
client = gspread.authorize(creds)


def parse_html(meet):
    response = requests.post(url="https://www.academicmeet.com/meet/show_results.php", data={"meet_id": meet["meet_id"]})
    source_code = response.content

    soup = BeautifulSoup(source_code,'html.parser')
    results_table = soup.find(id="results_table")
    if not results_table:
        print(f"No results table found for {meet['district']} (meet_id={meet['meet_id']}), skipping.")
        return
    rows = results_table.find_all('tr')

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

    if results:
        sheet = client.open_by_key(SPREADSHEET_ID).sheet1
        existing = sheet.get_all_values()
        kept = [row for row in existing if row and row[0] != meet["district"]]
        new_rows = [list(result.values()) for result in results]
        all_rows = (kept if kept else [list(results[0].keys())]) + new_rows
        sheet.clear()
        sheet.update(all_rows, "A1")
        print(f"{meet['district']}: wrote {len(results)} rows.")


meet_info = [
    # {"district": "31AA", "meet_id": 317},
    # {"district": "32AA", "meet_id": 318},
    # {"district": "33AA", "meet_id": 319},
    # {"district": "34AA", "meet_id": 320},
    # {"district": "35AA", "meet_id": 321},
    {"district": "36AA", "meet_id": 373},
    # {"district": "37AA", "meet_id": 323},
    # {"district": "38AA", "meet_id": 324},
    # {"district": "39AA", "meet_id": 325},
    # {"district": "40AA", "meet_id": 326},
    {"district": "41AA", "meet_id": 377},
    # {"district": "42AA", "meet_id": 328},
]

for meet in meet_info:
    parse_html(meet)

