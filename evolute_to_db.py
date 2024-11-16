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

API_URL = 'https://app.evassist.ru/car-service/tbox/<carid>/info' # Заменить carid на свой

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

def get_data():
    access_token, refresh_token = get_tokens_from_db()
    if not access_token or not refresh_token:
        print("Не удалось получить токены из базы данных.")
        return None

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
    # Запрос данных
    response = requests.get(API_URL, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Ошибка заброса: {response.status_code}")
        return None

def save_data_to_db():
    data = get_data()
    if data:
        sensors = data.get("sensors")
        positionData = sensors.get("positionData")
        sensorsData = sensors.get("sensorsData")
        #print (positionData)
        #print (sensorsData)
        query_s = """
        INSERT INTO sensors_data (
            time, ptc, v12_battery_voltage, odometer, battery_percentage, remains_mileage,
            ignition_status, outside_temp, central_locking_status, door_fl_status, door_fr_status, trunk_status,
            door_rr_status, door_rl_status, head_lights_status, ready_status, battery_temp,
            climate_air_circulation, coolant_temp, in_board_temp, climate_fan_direction,
            climate_target_temp, climate_fan_speed, climate_auto_status, climate_r_window_status,
            charging_status, climate_ac_status, climate_status, climate_f_window_status, immobiliser
        ) VALUES (
            NOW(), %(ptc)s, %(12VBatteryVoltage)s, %(odometer)s, %(batteryPercentage)s, %(remainsMileage)s,
            %(ignitionStatus)s, %(outsideTemp)s, %(centralLockingStatus)s, %(doorFLStatus)s, %(doorFRStatus)s, %(trunkStatus)s,
            %(doorRRStatus)s, %(doorRLStatus)s, %(headLightsStatus)s, %(ready)s, %(batteryTemp)s,
            %(climateAirCirculation)s, %(coolantTemp)s, %(inBoardTemp)s, %(climateFanDirection)s,
            %(climateTargetTemp)s, %(climateFanSpeed)s, %(climateAutoStatus)s, %(climateRWindowStatus)s,
            %(chargingStatus)s, %(climateACStatus)s, %(climateStatus)s, %(climateFWindowStatus)s, %(immobiliser)s
        );
        """
        query_p = """
        INSERT INTO position_data (
            time, location, speed, course, height, sats, hdop
        ) VALUES (
            NOW(), ST_SetSRID(ST_MakePoint(%(lon)s, %(lat)s), 4326), %(speed)s, %(course)s, %(height)s, %(sats)s, %(hdop)s
        );
        """
        #print (query)
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor()
            cur.execute(query_s, sensorsData)
            cur.execute(query_p, positionData)
            conn.commit()
            cur.close()
            conn.close()
            return True
        except Exception as e:
            print("Ошибка при вставке данных:", e)
            return False
    else:
        print("Некорректные данные от API")

def main():
    if not save_data_to_db():
        print("Не удалось получить данные Evolute.")

if __name__ == "__main__":
    main()
