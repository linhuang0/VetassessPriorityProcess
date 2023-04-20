from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

import ddddocr
import time

# 设置最大重试次数
max_retry = 5
retry_count = 0

# 创建浏览器实例
driver = webdriver.Chrome()
driver.maximize_window()

# 打开登录页面
driver.get('https://skillassess.vetassess.com.au/Account/Login')

while retry_count < max_retry:

    try:
        # 等待页面加载完成
        driver.implicitly_wait(5)

        # 输入用户名和密码
        username = driver.find_element(By.ID, "UserName")
        password = driver.find_element(By.ID, "Password")
        captcha = driver.find_element(By.ID, "CaptchaCode")
        login_btn = driver.find_element(By.ID, "Login")

        username.send_keys(" ")  # 替换用户名
        password.send_keys(" ")  # 替换密码

        # 获取验证码图片
        imgCaptcha = driver.find_element(By.ID, "Captcha_CaptchaImage")
        imgCaptcha.screenshot("captcha.png")

        # 识别验证码
        ocr = ddddocr.DdddOcr()
        with open("captcha.png", "rb") as fp:
            image = fp.read()
        captchaCode = ocr.classification(image)

        captcha.clear()  # 清空验证码输入框
        captcha.send_keys(captchaCode)  # 输入验证码

        login_btn.click()  # 点击登录按钮

    
        # 判断是否登录成功
        if "Welcome" in driver.page_source:
            print("Login successful!")
            time.sleep(1)
            driver.execute_script("window.open('https://skillassess.vetassess.com.au/Payment?AppId=')")
            driver.switch_to.window(driver.window_handles[-1])  # 切换到新打开的标签页
            while True:
                try:
                    # 尝试勾选优先处理选项
                    isSelectedPriorityProcess = driver.find_element(By.ID, "IsSelectedPriorityProcess")
                    print(isSelectedPriorityProcess.is_enabled())
                    # 检查是否为disable状态，如果是则刷新页面
                    #1.if  not isSelectedPriorityProcess.is_enabled():
                    #2.    print("Priority process options are disabled. Refreshing the page in 1 seconds...")
                    #3.    time.sleep(1)
                    #4.    driver.refresh()
                    #5.    continue

                    #6.isSelectedPriorityProcess.click()
                    #7.isAgreePriorityProcess =driver.find_element(By.CSS_SELECTOR, "label > strong")
                    #8.isAgreePriorityProcess.click()
                    
                    

                    # 输入验证码    
                    captcha = driver.find_element(By.ID, "CaptchaCode")  # 验证码输入框位置
                    imgCaptcha = driver.find_element(By.ID, "Captcha_CaptchaImage")  # 验证码图片位置
                    #imgCaptcha= WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "Captcha_CaptchaImage")))
                    imgCaptcha.screenshot("captcha.png")  # 将验证码截图，保存为captcha.png
                    time.sleep(1)
                    # 以下为识别验证码的代码
                    ocr = ddddocr.DdddOcr()
                    with open("captcha.png", "rb") as fp:
                        image = fp.read()
                    captchaCode = ocr.classification(image)  # 验证码返回给captchaCode
                    captcha.send_keys(captchaCode)  # 将识别到的验证码输入到

                    # 点击确认支付按钮
                    confirm_payment_btn = driver.find_element(By.NAME, "Continue")
                    time.sleep(10)
                    confirm_payment_btn.click()

                    # 等待页面加载
                    #WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.XPATH, "//div[@class='payment-header']//h1[contains(text(), 'Payment')]")))
                    
                    # 确认支付页面
                    driver.execute_script("window.open('https://skillassess.vetassess.com.au/Payment/PaymentConfirmation?AppId=')")
                    driver.switch_to.window(driver.window_handles[-1])  # 切换到新打开的标签页
                    SelectedPaymentMethod =driver.find_element(By.CSS_SELECTOR, ".radio-inline > span:nth-child(2)")
                    SelectedPaymentMethod.click()
                    confirm_payment_finally = driver.find_element(By.NAME, "Continue")
                    time.sleep(50)
                    #confirm_payment_finally.click()

                    # 检查是否提交成功
                    if "Time Remaining" in driver.page_source:
                        print("Payment submitted successfully!")
                        
                        time.sleep(20000)
                        break
                    else:
                        print("Payment submission failed. Refreshing the page in 2 seconds...")
                        time.sleep(1)
                        driver.refresh()
                except Exception as e:
                    print("Error occurred: ", str(e))
                    print("Exception Refreshing the page in 1 seconds...")
                    time.sleep(1)
                    driver.refresh()
        else:
            # 等待错误信息元素出现，判断是否登录成功
            #errtext = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='validation-summary-errors']")))
            #if errtext =="":
                print("Login failed. Retry {}/{}".format(retry_count + 1, max_retry))
                retry_count += 1  # 增加重试次数
                driver.refresh()  # 刷新页面
                # time.sleep(1)  # 可根据需要调整重试间隔
    except NoSuchElementException:
        print("Login failed. Retry {}/{}".format(retry_count + 1, max_retry))
        retry_count += 1  # 增加重试次数
        driver.refresh()  # 刷新页面
        #time.sleep(1)  # 可根据需要调整重试间隔


if retry_count >= max_retry:
    print("Max retry reached. Login failed.")
    time.sleep(10000)
