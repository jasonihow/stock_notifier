# 等待交易時段下拉選單可見
    # market_code_select_element = WebDriverWait(driver, 60).until(
    #     EC.visibility_of_element_located((By.ID, "MarketCode"))
    # )

    # # 使用 JavaScript 選擇一般交易時段
    # driver.execute_script(
    #     """
    #     var select = arguments[0];
    #     for(var i = 0; i < select.options.length; i++) {
    #         if(select.options[i].value === '0') {  // 一般交易時段
    #             select.selectedIndex = i;
    #             var event = new Event('change');
    #             select.dispatchEvent(event);
    #             break;
    #         }
    #     }
    #     """,
    #     market_code_select_element,
    # )

    # # 等待一些時間以確保選擇事件完成
    # time.sleep(1)

    # # 確保契約選擇下拉選單可見
    # commodity_idt_select_element = WebDriverWait(driver, 60).until(
    #     EC.visibility_of_element_located((By.ID, "commodity_idt"))
    # )

    # # 使用 JavaScript 選擇MTX
    # driver.execute_script(
    #     """
    #     var select = arguments[0];
    #     for(var i = 0; i < select.options.length; i++) {
    #         if(select.options[i].value === 'MTX') {  // 選擇小型臺指
    #             select.selectedIndex = i;
    #             var event = new Event('change');
    #             select.dispatchEvent(event);
    #             break;
    #         }
    #     }
    #     """,
    #     commodity_idt_select_element,
    # )
