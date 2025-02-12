class ScraperConfig:
    MAX_PRODUCTS_PER_CATEGORY = 2
    MAX_WORKERS = 4  # 默认并行进程数
    CHUNK_SIZE = 10  # 每个进程处理的产品数量
    WAIT_TIME = 15
    MIN_SLEEP = 3
    MAX_SLEEP = 7
    SCROLL_STEPS = 3
    WINDOW_SIZE = (1920, 1080)

    TITLE_SELECTORS = [
        ('ID', 'productTitle'),
        ('CSS_SELECTOR', 'h1.a-text-normal'),
        ('CSS_SELECTOR', 'span#productTitle'),
        ('CSS_SELECTOR', '.nav-search-label'),
        ('XPATH', "//span[@id='productTitle']")
    ]

    PRICE_SELECTORS = [
        ('CSS_SELECTOR', '.a-price'),
        ('CSS_SELECTOR', '.a-price .a-price-whole'),
        ('CSS_SELECTOR', '.a-price .a-price-fraction'),
        ('CSS_SELECTOR', '.a-price .a-offscreen'),
        ('XPATH', "//span[contains(@class,'a-price')]"),
        ('XPATH', "//span[contains(@class,'a-price-whole')]"),
        ('XPATH', "//span[contains(@class,'a-price-fraction')]"),
        ('CSS_SELECTOR', '#corePrice_feature_div .a-price'),
        ('ID', 'priceblock_ourprice'),
        ('ID', 'priceblock_dealprice'),
    ]

    RATING_SELECTORS = [
        ('CSS_SELECTOR', '#acrPopover .a-size-base.a-color-base'),
        ('CSS_SELECTOR', '#averageCustomerReviews .a-icon-star .a-icon-alt'),
        ('XPATH', "//span[@class='a-icon-alt'][contains(text(),'out of 5 stars')]"),
        ('CSS_SELECTOR', 'span[data-hook="rating-out-of-text"]'),
        ('CSS_SELECTOR', '#acrPopover .a-declarative'),
        ('CSS_SELECTOR', 'i.a-icon-star .a-icon-alt'),
        ('CSS_SELECTOR', 'span.a-size-base.a-color-base'),
        ('CSS_SELECTOR', '[data-action="acrStarsLink-click-metrics"] .a-size-base.a-color-base'),
        ('CSS_SELECTOR', '#acrPopover'),
        ('CSS_SELECTOR', 'span[data-hook="rating-out-of-text"]'),
        ('CSS_SELECTOR', '.a-icon-star .a-icon-alt'),
        ('XPATH', '//span[@class="a-icon-alt"]'),
        ('CSS_SELECTOR', '#averageCustomerReviews_feature_div .a-size-base.a-color-base'),
        ('XPATH',
         "//div[@id='averageCustomerReviews']//span[contains(@class,'a-size-base')][contains(@class,'a-color-base')]")
    ]

    REVIEW_COUNT_SELECTORS = [
        ('ID', 'acrCustomerReviewText'),
        ('CSS_SELECTOR', 'span#acrCustomerReviewText'),
        ('CSS_SELECTOR', '#acrCustomerReviewLink'),
        ('XPATH', "//span[@id='acrCustomerReviewText']"),
        ('CSS_SELECTOR', '[data-hook="total-review-count"]'),
        ('CSS_SELECTOR', '#acrCustomerReviewText'),
        ('XPATH', "//span[@id='acrCustomerReviewText']/text()"),
        ('CSS_SELECTOR', '#reviews-medley-footer .totalReviewCount'),
        ('XPATH', "//span[contains(@class, 'totalReviewCount')]"),
        ('XPATH', "//a[contains(@href, '#customerReviews')]//span[contains(text(), 'ratings')]"),
        ('CSS_SELECTOR', '#acrCustomerReviewText'),
        ('CSS_SELECTOR', '#reviews-medley-footer .a-size-base'),
        ('XPATH', '//span[@id="acrCustomerReviewText"]'),
        ('CSS_SELECTOR', 'a[data-hook="see-all-reviews-link-foot"]')
    ]

    DESCRIPTION_SELECTORS = [
        ('ID', 'productDescription'),
        ('CSS_SELECTOR', '#feature-bullets .a-list-item'),
        ('CSS_SELECTOR', '#feature-bullets'),
        ('CSS_SELECTOR', '.a-unordered-list .a-list-item'),
        ('CSS_SELECTOR', '#productDescription p'),
        ('XPATH', "//div[@id='feature-bullets']//li")
    ]

    PRODUCT_LINK_SELECTORS = [
        "a[href*='/dp/']",
        ".zg-item-immersion a[href*='/dp/']",
        ".zg-grid-general-faceout a[href*='/dp/']",
        "div[data-component-type='s-search-result'] a[href*='/dp/']",
        ".a-link-normal[href*='/dp/']",
        "#gridItemRoot a[href*='/dp/']",
        ".s-result-item a[href*='/dp/']",
        ".s-include-content-margin a[href*='/dp/']"
    ]

    IMAGE_SELECTORS = [
        ('ID', 'landingImage'),
        ('CSS_SELECTOR', '#imgBlkFront'),
        ('CSS_SELECTOR', '#main-image'),
        ('CSS_SELECTOR', '.a-dynamic-image'),
        ('XPATH', "//img[@id='landingImage']")
    ]

    BRAND_SELECTORS = [
        ('ID', 'bylineInfo'),
        ('CSS_SELECTOR', '#bylineInfo'),
        ('CSS_SELECTOR', '#brand'),
        ('XPATH', "//a[@id='bylineInfo']"),
        ('CSS_SELECTOR', '#bylineInfo_feature_div'),
        ('CSS_SELECTOR', '.po-brand .a-span9'),
        ('CSS_SELECTOR', '.po-brand .a-size-base'),
        ('XPATH', "//a[contains(@class, 'contributorNameID')]"),
        ('XPATH', "//div[@id='bylineInfo_feature_div']//a"),
        ('XPATH', "//div[@id='brandByline_feature_div']//a"),
        ('XPATH', "//tr[contains(.,'Brand')]/td[2]"),
        ('XPATH', "//div[contains(@class, 'po-brand')]//span[@class='a-size-base']")
    ]

    AVAILABILITY_SELECTORS = [
        ('ID', 'availability'),
        ('CSS_SELECTOR', '#availability span'),
        ('CSS_SELECTOR', '#outOfStock'),
        ('XPATH', "//div[@id='availability']/span"),
        ('CSS_SELECTOR', '#availability span'),
        ('CSS_SELECTOR', '#merchantInfoFeature'),
        ('CSS_SELECTOR', '#buybox-see-all-buying-choices'),
        ('XPATH', '//div[@id="availability"]//span[@class="a-size-medium a-color-success"]'),
        ('CSS_SELECTOR', '#outOfStock .a-color-price')
    ]

    CATEGORY_NAME_SELECTORS = [
        "//h1[contains(@class, 'a-size-large')]",
        "//span[contains(@class, 'zg-banner-text')]",
        "//span[@class='category']",
        "//title",
        "//div[contains(@class, 'category-title')]"
    ]
