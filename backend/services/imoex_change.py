import requests
import xml.etree.ElementTree as ET

url = "https://iss.moex.com/iss/engines/stock/markets/index/boards/SNDX/securities/IMOEX.xml"


def get_current_value(xml_content):
    root = ET.fromstring(xml_content)
    # ищем элемент data с id="marketdata" и внутри row с SECID="IMOEX"
    for row in root.findall(".//data[@id='marketdata']/rows/row"):
        if row.attrib.get("SECID") == "IMOEX":
            return float(row.attrib.get("CURRENTVALUE"))
    return None


def get_imoex_quote() -> dict:
    """
    Получает текущую котировку IMOEX.

    Возвращает:
      {
         "price": текущее значение,
         "abs_change": изменение от предыдущего запроса,
         "percent_change": процентное изменение
      }
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        new_value = get_current_value(response.content)
        if new_value is None:
            raise Exception("CURRENTVALUE не найден")
    except Exception as e:
        raise Exception(f"Ошибка получения данных: {e}")

    abs_change = 0.0
    percent_change = 0.0
    if hasattr(get_imoex_quote, "prev_value") and get_imoex_quote.prev_value is not None:
        abs_change = new_value - get_imoex_quote.prev_value
        percent_change = (abs_change / get_imoex_quote.prev_value) * 100 if get_imoex_quote.prev_value != 0 else 0
    get_imoex_quote.prev_value = new_value

    return {"price": round(new_value, 2), "abs_change": round(abs_change, 2), "percent_change": round(percent_change, 2)}
