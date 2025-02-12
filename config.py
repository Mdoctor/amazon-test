class ScraperConfig:
    # 爬虫配置
    WAIT_TIME = 10
    MIN_SLEEP = 2
    MAX_SLEEP = 5
    SCROLL_STEPS = 3

    # 浏览器配置
    WINDOW_SIZE = (1920, 1080)
    
    # 选择器配置
    TITLE_SELECTORS = [
        ('ID', 'productTitle'),
        ('CSS_SELECTOR', 'h1.a-text-normal'),
        ('CSS_SELECTOR', 'span#productTitle')
    ]
    
    PRICE_SELECTORS = [
        ('CSS_SELECTOR', 'span.a-price-whole'),
        ('ID', 'priceblock_ourprice'),
        ('ID', 'priceblock_dealprice'),
        ('CSS_SELECTOR', 'span.a-offscreen')
    ]
    
    RATING_SELECTORS = [
        ('CSS_SELECTOR', 'span.a-icon-alt'),
        ('CSS_SELECTOR', 'i.a-icon-star span.a-icon-alt'),
        ('CSS_SELECTOR', '#acrPopover span.a-icon-alt')
    ]
    
    REVIEW_COUNT_SELECTORS = [
        ('ID', 'acrCustomerReviewText'),
        ('CSS_SELECTOR', 'span#acrCustomerReviewText'),
        ('CSS_SELECTOR', "[data-csa-c-func-deps='acrCustomerReviewText']")
    ]
    
    DESCRIPTION_SELECTORS = [
        ('ID', 'productDescription'),
        ('CSS_SELECTOR', '#feature-bullets .a-list-item'),
        ('CSS_SELECTOR', '#feature-bullets')
    ]
    
    CATEGORY_NAME_SELECTORS = [
        "//span[@class='category-title']",
        "//h1[contains(@class, 'category-title')]",
        "//div[contains(@class, 'category-title')]",
        "//h1[contains(@class, 'a-size-large')]"
    ]
    
    PRODUCT_LINK_SELECTORS = [
        "a[href*='/dp/']",
        ".zg-item-immersion a[href*='/dp/']",
        ".zg-grid-general-faceout a[href*='/dp/']",
        "div[data-component-type='s-search-result'] a[href*='/dp/']",
        ".a-link-normal[href*='/dp/']"
    ]