from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import *
import time
import os
import signal
from contextlib import contextmanager
from bs4 import BeautifulSoup
import signal
import time
import threading
from contextlib import contextmanager

FIELD_ID_MAP = {
    "mqtt_server_ip": "mqtt_server_ip",
    "device_name": "device_name",
    "device_secret": "device_secret",
    "product_key": "product_key"
}

@contextmanager
def timeout(seconds):
    """设置操作超时的上下文管理器"""
    if hasattr(signal, 'SIGALRM'):
        # Unix系统
        def signal_handler(signum, frame):
            raise TimeoutError(f"操作超时 ({seconds}秒)")

        signal.signal(signal.SIGALRM, signal_handler)
        signal.alarm(seconds)

        try:
            yield
        finally:
            signal.alarm(0)  # 取消闹钟
    else:
        # Windows系统
        class TimeoutThread(threading.Thread):
            def __init__(self):
                threading.Thread.__init__(self)
                self.timed_out = False

            def run(self):
                time.sleep(seconds)
                self.timed_out = True

        timeout_thread = TimeoutThread()
        timeout_thread.start()

        try:
            yield
        finally:
            if timeout_thread.timed_out:
                raise TimeoutError(f"操作超时 ({seconds}秒)")

def get_chrome_driver(options=None, executable_path=None):
    """安全获取Chrome驱动实例，带版本检查"""
    try:
        if not options:
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')  # 必需的Linux参数
            options.add_argument('--disable-dev-shm-usage')  # 避免/dev/shm问题
        
        # 尝试创建驱动实例
        if executable_path:
            driver = webdriver.Chrome(options=options, executable_path=executable_path)
        else:
            driver = webdriver.Chrome(options=options)
        
        # 验证驱动是否正常工作
        driver.get("about:blank")
        return driver
    except Exception as e:
        print(f"创建Chrome驱动失败: {str(e)}")
        print("提示: 请确保ChromeDriver版本与Chrome浏览器版本兼容")
        raise

def safe_quit_driver(driver):
    """安全关闭驱动，确保资源释放"""
    try:
        if driver:
            driver.quit()
            print("浏览器已安全关闭")
    except Exception as e:
        print(f"关闭浏览器时出错: {str(e)}")

def set_web_config(form_data, url, index, max_wait_time=30):
    """安全配置网页表单，带全面错误处理"""
    print(f"[{index}] 开始配置: {url}")
    driver = None
    
    try:
        # 获取Chrome驱动
        driver = get_chrome_driver()
        
        # 设置页面加载超时
        driver.set_page_load_timeout(max_wait_time)
        
        # 打开网页
        print(f"[{index}] 正在打开网页...")
        with timeout(max_wait_time):
            driver.get(url)
        
        # 等待页面稳定
        print(f"[{index}] 等待页面加载完成...")
        WebDriverWait(driver, max_wait_time).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )
        time.sleep(1)  # 额外等待页面渲染
        
        # 填写表单字段
        print(f"[{index}] 开始填写表单...")
        for key, value in form_data.items():
            if key in FIELD_ID_MAP:
                print(f"[{index}] 处理字段: {key}")
                try:
                    elem = WebDriverWait(driver, max_wait_time).until(
                        EC.element_to_be_clickable((By.ID, FIELD_ID_MAP[key]))
                    )
                    elem.clear()
                    elem.send_keys(value)
                    print(f"[{index}] 成功填写: {value}")
                except TimeoutException:
                    print(f"[{index}] 超时: 无法找到或操作字段 {key}")
                    continue
        
        # 查找并点击提交按钮
        print(f"[{index}] 查找提交按钮...")
        submit_btn = WebDriverWait(driver, max_wait_time).until(
            EC.element_to_be_clickable((By.NAME, "config_submit"))
        )
        
        # 滚动到按钮位置并点击
        driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
        time.sleep(0.5)
        submit_btn.click()
        print(f"[{index}] 已点击提交按钮")
        
        # 等待提交后可能的页面变化
        time.sleep(2)
        
        # 保存表单内容
        print(f"[{index}] 保存表单内容...")
        soup = BeautifulSoup(driver.page_source, "html.parser")
        form = soup.find("form", {"id": "config-form"})
        
        # 创建输出目录
        out_dir = "htmls"
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, f"A{index}.html")
        
        # 写入文件
        with open(out_path, "w", encoding="utf-8") as f:
            if form:
                f.write(str(form))
                print(f"[{index}] 表单已保存至: {out_path}")
            else:
                f.write("未找到表单内容")
                print(f"[{index}] 警告: 未找到表单元素")
        
        print(f"[{index}] 配置完成")
        
    except TimeoutError:
        print(f"[{index}] 操作超时，程序终止")
    except WebDriverException as e:
        print(f"[{index}] WebDriver错误: {str(e)}")
    except Exception as e:
        print(f"[{index}] 未知错误: {str(e)}")
    finally:
        # 确保驱动程序始终关闭
        safe_quit_driver(driver)
        print(f"[{index}] 任务结束")