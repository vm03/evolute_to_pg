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


def save_stats_to_db(odometer, battery_percentage):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT battery_percentage, battery_percentage_charged, battery_percentage_consumed FROM stats ORDER BY time DESC LIMIT 1")
        result1 = cursor.fetchone()
        battery_percentage0, battery_percentage_charged, battery_percentage_consumed = result1
        if battery_percentage > battery_percentage0:
            battery_percentage_charged = battery_percentage_charged + (battery_percentage - battery_percentage0)
        if battery_percentage0 > battery_percentage:
            battery_percentage_consumed = battery_percentage_consumed + (battery_percentage0 - battery_percentage)
        cursor.execute("SELECT odometer, battery_percentage_consumed FROM stats WHERE odometer <= %s - 10  ORDER BY time DESC  LIMIT 1", [odometer])
        result2 = cursor.fetchone()
        if result2:
            odometer2, battery_percentage_consumed2 = result2
            if battery_percentage_consumed-battery_percentage_consumed2 != 0 and odometer-odometer2 != 0:
                avg10km = (battery_percentage_consumed-battery_percentage_consumed2)/(odometer-odometer2)
                rem10 = battery_percentage/avg10km
                avg10km = avg10km*53
            else:
                avg10km = 0;
                rem10 = 0;
        else:
            avg10km = 0;
            rem10 = 0;
        cursor.execute("SELECT odometer, battery_percentage_consumed FROM stats  WHERE odometer <= %s - 100  ORDER BY time DESC  LIMIT 1", [odometer])
        result3 = cursor.fetchone()
        if result3:
            odometer3, battery_percentage_consumed3 = result3
            if battery_percentage_consumed-battery_percentage_consumed3 != 0 and odometer-odometer3 != 0:
                avg100km = (battery_percentage_consumed-battery_percentage_consumed3)/(odometer-odometer3)
                rem100 = battery_percentage/avg100km
                avg100km = avg100km*53
            else:
                avg100km = 0;
                rem100 = 0;
        else:
           avg100km = 0;
           rem100 = 0;
        cursor.execute("SELECT odometer, battery_percentage_consumed FROM stats  WHERE odometer <= %s - 30  ORDER BY time DESC  LIMIT 1", [odometer])
        result4 = cursor.fetchone()
        if result4:
            odometer4, battery_percentage_consumed4 = result4
            if battery_percentage_consumed-battery_percentage_consumed4 != 0 and odometer-odometer4 != 0:
                avg30km = (battery_percentage_consumed-battery_percentage_consumed4)/(odometer-odometer4)
                rem30 = battery_percentage/avg30km
                avg30km = avg30km*53
            else:
                avg30km = 0;
                rem30 = 0;
        else:
           avg30km = 0;
           rem30 = 0;
        cursor.execute("SELECT odometer, battery_percentage_consumed FROM stats  WHERE odometer <= %s - 50  ORDER BY time DESC  LIMIT 1", [odometer])
        result5 = cursor.fetchone()
        if result5:
            odometer5, battery_percentage_consumed5 = result5
            if battery_percentage_consumed-battery_percentage_consumed5 != 0 and odometer-odometer5 != 0:
                avg50km = (battery_percentage_consumed-battery_percentage_consumed5)/(odometer-odometer5)
                rem50 = battery_percentage/avg50km
                avg50km = avg50km*53
            else:
                avg50km = 0;
                rem50 = 0;
        else:
           avg50km = 0;
           rem50 = 0;
        cursor.execute("INSERT INTO stats (time, odometer, battery_percentage, battery_percentage_charged, battery_percentage_consumed, avg10km, avg100km, avg30km, avg50km, rem10, rem100, rem30, rem50 ) VALUES (NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (odometer, battery_percentage, battery_percentage_charged, battery_percentage_consumed, avg10km, avg100km, avg30km, avg50km, rem10, rem100, rem30, rem50))
        conn.commit()
    except Exception as e:
        print(f"Ошибка сохранения статистики: {e}")
        return None
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
            charging_status, climate_ac_status, climate_status, climate_f_window_status, immobiliser,soh
        ) VALUES (
            NOW(), %(ptc)s, %(12VBatteryVoltage)s, %(odometer)s, %(batteryPercentage)s, %(remainsMileage)s,
            %(ignitionStatus)s, %(outsideTemp)s, %(centralLockingStatus)s, %(doorFLStatus)s, %(doorFRStatus)s, %(trunkStatus)s,
            %(doorRRStatus)s, %(doorRLStatus)s, %(headLightsStatus)s, %(ready)s, %(batteryTemp)s,
            %(climateAirCirculation)s, %(coolantTemp)s, %(inBoardTemp)s, %(climateFanDirection)s,
            %(climateTargetTemp)s, %(climateFanSpeed)s, %(climateAutoStatus)s, %(climateRWindowStatus)s,
            %(chargingStatus)s, %(climateACStatus)s, %(climateStatus)s, %(climateFWindowStatus)s, %(immobiliser)s , %(soh)s
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
            save_stats_to_db(sensorsData.get("odometer"), sensorsData.get("batteryPercentage"))
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
