import mysql.connector
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
import requests

# 设置 Chrome 驱动路径
driver_path = "./chromedriver-win64/chromedriver.exe"  # 修改为相对路径
service = Service(driver_path)
driver = webdriver.Chrome(service=service)

# 数据库连接配置
db_config = {
    'host': 'xxx.xxx.xxx.xxx',
    'user': "xxx",
    'password': "xxx",
    'database': "xxx",
    'port': 3306  # 添加端口号配置
}

# 连接数据库
def connect_to_database():
    try:
        connection = mysql.connector.connect(**db_config)
        print("数据库连接成功！")
        return connection
    except mysql.connector.Error as err:
        print(f"数据库连接失败: {err}")
        return None

connection = connect_to_database()

# 下载图片并获取本地路径
def download_image(image_url):
    # 获取文件名（从 URL 中提取）
    image_name = image_url.split("/")[-1]
    local_image_path = f"./images/{image_name}"

    if not os.path.exists("./images"):
        os.makedirs("./images")

    # 下载图片
    try:
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            with open(local_image_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"成功下载图片: {local_image_path}")
            return local_image_path
        else:
            print(f"图片下载失败，状态码: {response.status_code}")
            return None
    except Exception as e:
        print(f"下载图片出错: {e}")
        return None

# 插入食物信息
def insert_food_info(name, calories, category, category_type, alias_name, image_path):
    if connection:
        try:
            cursor = connection.cursor()
            sql = """
            INSERT INTO foods_info (name, calories_per_100g, category, category_type, alias_name, image_path)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (name, calories, category, category_type, alias_name, image_path))
            connection.commit()
            print(f"成功插入食物信息: {name}, {calories}, {category}, {alias_name}, {image_path}")
            return cursor.lastrowid
        except mysql.connector.Error as err:
            print(f"插入数据失败: {err}")
            return None

# 插入营养信息       
def insert_food_nutrition(food_id, nutrition):
    if connection:
        try:
            cursor = connection.cursor()
            sql = """
            INSERT INTO food_nutrition (food_id, nutrient_name, amount_per_100g, nutrient_type)
            VALUES (%s, %s, %s, %s)
            """
            for nutrient_name, amount, nutrient_type in nutrition:
                cursor.execute(sql, (food_id, nutrient_name, amount, nutrient_type))
            connection.commit()
            print(f"成功插入营养信息: {nutrition}")
        except mysql.connector.Error as err:
            print(f"插入营养信息失败: {err}")

# 打开页面
def open_page(page):
    url = f"https://www.xuanshiwu.com/foods/2/{page}"
    driver.get(url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".mt-16px.w-100vw ul li.mx-16px.pt-16px a"))
    )

NUTRIENT_TYPE_MAP = {
    "热量（大卡）": 1,
    "脂肪（克）": 4,
    "纤维素（克）": 5,
    "碳水化合物（克）": 2,
    "蛋白质（克）": 3
}

# 提取字段
def extract_fields():
    try:
        # 获取 image_path
        image_url = driver.find_element(By.CSS_SELECTOR, ".flex.py-16px.items-center .box img.lazyloaded").get_attribute("src")

        # 下载图片并获取本地路径
        local_image_path = download_image(image_url)

        # 拼接存储在数据库中的图片路径
        if local_image_path:
            image_path_in_db = f"static/images/{os.path.basename(local_image_path)}"

        # 获取 name
        name = driver.find_element(By.CSS_SELECTOR, ".flex.py-16px.items-center .text-desc .line-clamp-2 span").text.strip()

        # 获取 alias_name 直接存入 foods_info 表的 alias_name 字段
        alias_name = driver.find_element(By.CSS_SELECTOR, ".flex.py-16px.items-center .text-desc .line-clamp-2:nth-child(2) span").text.strip()

        # 获取 calories_per_100g
        calories_per_100g = driver.find_element(By.CSS_SELECTOR, ".flex.py-16px.items-center .text-desc .text-content a").text.strip()

        # 获取 nutrient_name 和 amount_per_100g
        nutrients = []
        rows = driver.find_elements(By.CSS_SELECTOR, ".info-table table tbody tr")
        for row in rows:
            try:
                nutrient_name = row.find_element(By.CSS_SELECTOR, "td:nth-child(1)").text.strip()
                amount_per_100g = row.find_element(By.CSS_SELECTOR, "td:nth-child(2)").text.strip()

                # 根据 nutrient_name 获取 nutrient_type
                nutrient_type = NUTRIENT_TYPE_MAP.get(nutrient_name, 2)  # 默认值为 2

                # 处理 amount_per_100g 为 "一" 时转为 0.00
                if amount_per_100g == "一":
                    amount_per_100g = "0.00"

                nutrients.append((nutrient_name, amount_per_100g, nutrient_type))
            except Exception as e:
                print(f"提取营养数据时发生错误: {e}")

        # 插入食物信息
        food_id = insert_food_info(name, calories_per_100g, "蛋类、肉类及制品", 2, alias_name, image_path_in_db)

        # 插入营养信息
        if food_id and nutrients:
            insert_food_nutrition(food_id, nutrients)

        # 打印结果
        print(f"image_path: {image_path_in_db}")
        print(f"name: {name}")
        print(f"alias_name: {alias_name}")
        print(f"calories_per_100g: {calories_per_100g}")
        print(f"nutrients: {nutrients}")

    except Exception as e:
        print(f"提取字段时发生错误: {e}")

# 处理每一页
def process_pages(start_page, end_page):
    for page in range(start_page, end_page + 1):
        try:
            open_page(page)
            # 使用显式等待替代隐式等待
            wait = WebDriverWait(driver, 10)
            items = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".mt-16px.w-100vw ul li.mx-16px.pt-16px a"))
            )
            
            for item in items:
                try:
                    link = item.get_attribute("href")
                    driver.execute_script("window.open(arguments[0]);", link)
                    driver.switch_to.window(driver.window_handles[-1])
                    
                    # 使用显式等待替代 time.sleep
                    wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".flex.py-16px.items-center"))
                    )

                    extract_fields()

                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                except Exception as e:
                    print(f"处理链接时发生错误: {e}")
            print(f"已完成第 {page} 页的处理")
        except Exception as e:
            print(f"处理第 {page} 页时发生错误: {e}")

# 主函数
def main():
    start_page = 1
    end_page = 1426  # 总共1426页
    
    try:
        process_pages(start_page, end_page)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
    if connection:
        connection.close()
