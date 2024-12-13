from datetime import datetime
import requests
import json
from creds import TOKEN_USER

def get_posts(domain, date_start, date_end=int(datetime.now().timestamp()), token=TOKEN_USER, version=5.199, COUNT=100):
    posts = []
    offset = 0
    date_start = int(date_start)
    while True:
        # Запрос к API
        response = requests.get(
            "https://api.vk.com/method/wall.get",
            params={
                "count": COUNT,
                "offset": offset,
                "access_token": token,
                'domain': domain,
                "v": version,
            },
        ).json()

        items = response.get("response", {}).get("items", [])
        if not items:
            break  # Если постов больше нет, выходим из цикла

        # Фильтрация по диапазону времени
        for post in items:
            post_date = post["date"]
            if date_start <= post_date <= date_end:
                posts.append(post)
            elif post_date < date_start:
                break  # Прекращаем обработку, если достигли более старых постов

        # Увеличиваем offset
        offset += COUNT

        # Если достигнуты более старые посты, выходим из цикла
        if items and items[-1]["date"] < date_start:
            break
    return posts


def get_comments(posts, token=TOKEN_USER, version=5.199, COUNT=100):
    comments = []

    for post in posts:
        post_id = post["id"]
        owner_id = post["owner_id"]

        offset = 0

        while True:
            # Запрос к API для получения комментариев
            response = requests.get(
                "https://api.vk.com/method/wall.getComments",
                params={
                    "owner_id": owner_id,
                    "post_id": post_id,
                    "count": COUNT,
                    "offset": offset,
                    "access_token": token,
                    "v": version,
                },
            ).json()

            items = response.get("response", {}).get("items", [])
            if not items:
                break  # Если комментариев больше нет, выходим из цикла

            # Сохраняем комментарии
            for comment in items:
                comments.append({
                    "post_id": post_id,
                    "owner_id": owner_id,
                    "comment_id": comment["id"],
                    "text": comment.get("text", ""),
                    "from_id": comment.get("from_id", ""),
                    "date": comment.get("date", 0),
                })

            # Увеличиваем offset
            offset += COUNT
    return comments

#Передается список доменов групп в ВК
def get_all_comments(domains, date_start=int(datetime(2024, 1, 1, 0, 0).timestamp())):
    all_comments = {}
    for domain in domains:
        posts = get_posts(domain, date_start=date_start)
        comments = get_comments(posts)
        all_comments[domain] = comments
        with open(f"comments_{domain}.json", "w", encoding="utf-8") as f:
            json.dump(all_comments, f, ensure_ascii=False, indent=4)
    return all_comments
