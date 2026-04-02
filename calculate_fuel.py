import requests
from bs4 import BeautifulSoup
import json

# 城市字典库
city_names = {
    # 直辖市
    "北京": "beijing",
    "上海": "shanghai",
    "天津": "tianjin",
    "重庆": "chongqing",
    
    # 省份
    "河北": "hebei",
    "山西": "shanxi",
    "辽宁": "liaoning",
    "吉林": "jilin",
    "黑龙江": "heilongjiang",
    "江苏": "jiangsu",
    "浙江": "zhejiang",
    "安徽": "anhui",
    "福建": "fujian",
    "江西": "jiangxi",
    "山东": "shandong",
    "河南": "henan",
    "湖北": "hubei",
    "湖南": "hunan",
    "广东": "guangdong",
    "海南": "hainan",
    "四川": "sichuan",
    "贵州": "guizhou",
    "云南": "yunnan",
    "陕西": "shaanxi",
    "甘肃": "gansu",
    "青海": "qinghai",
    
    # 自治区
    "内蒙古": "neimenggu",
    "广西": "guangxi",
    "西藏": "xizang",
    "宁夏": "ningxia",
    "新疆": "xinjiang",
}

# 燃油品类
fuel_type = {
    "92": "92#汽油",
    "95": "95#汽油",
    "98": "98#汽油",
    "0": "0#柴油"
}

def get_fuel_price_from_qukuaiyouhua(city,fuel_code):
    """
    从 http://www.qiyoujiage.com/guangdong.shtml 获取广东省最新油价
    :return: 指定类型油价（元/升）
    """
    try:
        city_name = city_names.get(city, city)
        url = f"http://www.qiyoujiage.com/{city_name}.shtml"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)   # 设置超时时间，避免长时间等待
        response.encoding = 'utf-8'  # 确保正确解析中文页面
        soup = BeautifulSoup(response.text, 'html.parser')  # 解析页面内容
        # 直接查找指定类型汽油/柴油价格
        fuel_label = fuel_type.get(fuel_code)

        dls = soup.find_all('dl')   # 指定类型油价通常在dl标签中，dt标签包含油品名称，dd标签包含价格
        for dl in dls:
            dt = dl.find('dt')
            dd = dl.find('dd')
            if dt and dd and fuel_label in dt.get_text():
                price_text = dd.get_text().strip()
                try:
                    price = float(price_text)
                    return price
                except Exception:
                    continue
        print(f"未能在页面中找到{fuel_label}价格")
    except Exception as e:
        print(f"获取油价失败: {e}")
    return None


def calculate_fuel_cost(distance, fuel_efficiency, fuel_price):
    """
    计算油费
    distance: 行驶距离（公里）
    fuel_efficiency: 油耗（L/100km）
    fuel_price: 燃油价格（元/升）
    :return: 油费总成本（元）
    """

    # 计算所需燃油量
    fuel_needed = (distance * fuel_efficiency) / 100
    # 计算总油费
    total_cost = fuel_needed * fuel_price
    return total_cost

# 示例使用
if __name__ == "__main__":
    # 单次行程距离
    distance = 120  
    # 单次行程油耗
    fuel_efficiency = 6.2
    # 修改为你所在的城市
    city_name = "广东"
    # 修改为你需要的油品类型
    fuel_code = "95"

    # 方案1: 爬取指定城市指定类型油价
    fuel_price = get_fuel_price_from_qukuaiyouhua(city_name, fuel_code)
    if fuel_price:
        print(f"获取到的{city_name}{fuel_type.get(fuel_code, '92#汽油')}油价: {fuel_price} 元/升")
    else:
        print(f"未能获取到{city_name}{fuel_type.get(fuel_code, '92#汽油')}油价，使用本地默认油价。")
        fuel_price = 7.59

    cost = calculate_fuel_cost(distance, fuel_efficiency, fuel_price)
    print(f"行驶 {distance} 公里需要的油费总成本为: {cost:.2f} 元")
