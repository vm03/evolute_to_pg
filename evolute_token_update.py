import requests
import psycopg2
from datetime import datetime
import asyncio

# Настройки для подключения к PostgreSQL
DB_CONFIG = {
    "dbname": "evolute",
    "user": "evolute",
    "password": "secret",
    "host": "localhost",
    "port": "5432"
}

REFRESH_TOKEN_URL = 'https://app.evassist.ru/id-service/auth/refresh-token'

def get_tokens_from_db():
    """Извлекает токены из базы данных PostgreSQL."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT access_token, refresh_token FROM token_storage ORDER BY updated_at DESC LIMIT 1")
        result = cursor.fetchone()
        if result:
            access_token, refresh_token = result
            return access_token, refresh_token
        else:
            print("Токены не найдены в базе данных.")
            return None, None
    except Exception as e:
        print(f"Ошибка при извлечении токенов из базы данных: {e}")
        return None, None
    finally:
        cursor.close()
        conn.close()

def refresh_token():
    """Обновляет токены через запрос и возвращает их."""
    access_token, refresh_token = get_tokens_from_db()
    if not access_token or not refresh_token:
        print("Не удалось получить токены из базы данных.")
        return None, None

    # Заголовки с полученными токенами
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Origin': 'https://app.evassist.ru',
        'Connection': 'keep-alive',
        'Referer': 'https://app.evassist.ru/fleet/car',
        'Cookie': f'evy-platform-access={access_token}; evy-platform-refresh={refresh_token}',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'TE': 'trailers'
    }
    # Запрос на обновление токенов
    response = requests.post(REFRESH_TOKEN_URL, headers=headers)
    if response.status_code == 200:
        tokens = response.json()
        new_access_token = tokens.get("accessToken")
        new_refresh_token = tokens.get("refreshToken")
        return new_access_token, new_refresh_token
    else:
        print(f"Ошибка обновления токена: {response.status_code}")
        return None, None

def save_tokens_to_db(access_token, refresh_token):
    """Сохраняет токены в PostgreSQL."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO token_storage (access_token, refresh_token, updated_at)
            VALUES (%s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                access_token = EXCLUDED.access_token,
                refresh_token = EXCLUDED.refresh_token,
                updated_at = EXCLUDED.updated_at
        """, (access_token, refresh_token, datetime.now()))
        conn.commit()
        #print("Токены успешно сохранены в базе данных.")
    except Exception as e:
        print(f"Ошибка сохранения токенов в БД: {e}")
    finally:
        cursor.close()
        conn.close()

def main():
    new_access_token, new_refresh_token = refresh_token()
    if new_access_token and new_refresh_token:
        save_tokens_to_db(new_access_token, new_refresh_token)
    else:
        print("Не удалось обновить токены Evolute.")

if __name__ == "__main__":
    main()
