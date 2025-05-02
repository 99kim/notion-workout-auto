
import os
import requests
from collections import defaultdict

# 🔥 환경변수로부터 Token과 DB ID 읽어오기
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

def get_all_pages():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    pages = []
    has_more = True
    next_cursor = None

    while has_more:
        data = {"start_cursor": next_cursor} if next_cursor else {}
  #      response = requests.post(url, headers=headers, json=data).json()
  #      pages.extend(response["results"])

        res = requests.post(url, headers=headers, json=data)

        # ⬇️ 디버깅 출력 추가
        print("📦 API 상태 코드:", res.status_code)
        print("📦 API 응답 내용:", res.text)

        response = res.json()
        pages.extend(response["results"])

        has_more = response.get("has_more", False)
        next_cursor = response.get("next_cursor")

    return pages

def update_weekly_counts():
    pages = get_all_pages()

    # 작성자+주차 키별로 그룹화
    group_counts = defaultdict(list)
    for page in pages:
        try:
            key = page["properties"]["작성자+주차"]["formula"]["string"]
            page_id = page["id"]
            group_counts[key].append(page_id)
        except KeyError:
            continue

    # 각 그룹별로 운동 횟수 업데이트
    for key, page_ids in group_counts.items():
        count = len(page_ids)
        for pid in page_ids:
            update_url = f"https://api.notion.com/v1/pages/{pid}"
            update_data = {
                "properties": {
                    "주간 운동 횟수": {
                        "number": count
                    }
                }
            }
            res = requests.patch(update_url, headers=headers, json=update_data)
            print(f"Updated {pid} with count {count} - Status: {res.status_code}")

#if os.getenv("DRY_RUN") == "true":
#    print("🔧 DRY RUN MODE: Not calling Notion API.")
#    exit(0)


if __name__ == "__main__":
    update_weekly_counts()
