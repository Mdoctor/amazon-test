class ScraperConfig:
    HEADLESS = True
    MAX_PRODUCTS_PER_CATEGORY = 10  # 每个类别爬取的商品数量
    MAX_WORKERS = 4  # 最大并行进程数
    CHUNK_SIZE = 10  # 每个进程处理的产品数量
    WAIT_TIME = 10
    MIN_SLEEP = 1
    MAX_SLEEP = 2
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
        ('CSS_SELECTOR', '.a-price .a-offscreen'),
        ('CSS_SELECTOR', '.a-color-price'),
        ('CSS_SELECTOR', '#priceblock_ourprice'),
        ('CSS_SELECTOR', '#priceblock_dealprice'),
        ('CSS_SELECTOR', '.apexPriceToPay .a-offscreen'),
        ('CSS_SELECTOR', '.a-price .a-price-whole'),
        ('CSS_SELECTOR', '.a-price .a-price-fraction'),
        ('CSS_SELECTOR', '.a-price'),
        ('CSS_SELECTOR', '.a-price-whole'),
        ('XPATH', "//span[contains(@class,'a-price')]"),
        ('XPATH', "//span[contains(@class,'a-price-whole')]"),
        ('XPATH', "//span[contains(@class,'a-price-fraction')]"),
        ('CSS_SELECTOR', '#corePrice_feature_div .a-price'),
        ('ID', 'priceblock_ourprice'),
        ('ID', 'priceblock_dealprice'),
    ]

    RATING_SELECTORS = [
        ('CSS_SELECTOR', 'i.a-icon-star .a-icon-alt'),
        ('CSS_SELECTOR', '#averageCustomerReviews .a-icon-star'),
        ('CSS_SELECTOR', '#acrPopover .a-size-base.a-color-base'),
        ('CSS_SELECTOR', '#acrPopover .a-size-base.a-color-base'),
        ('CSS_SELECTOR', '#acrPopover .a-size-base.a-color-base'),
        ('CSS_SELECTOR', '#acrPopover .a-size-base.a-color-base'),
        ('CSS_SELECTOR', '#averageCustomerReviews .a-icon-star .a-icon-alt'),
        ('XPATH', "//span[@class='a-icon-alt'][contains(text(),'out of 5 stars')]"),
        ('CSS_SELECTOR', 'span[data-hook="rating-out-of-text"]'),
        ('CSS_SELECTOR', '#acrPopover .a-declarative'),
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
        ('ID', 'acrCustomerReviewText')
    ]

    DESCRIPTION_SELECTORS = [
        # 产品描述区域
        ('ID', 'productDescription'),
        ('CSS_SELECTOR', '#productDescription'),
        ('CSS_SELECTOR', '#productDescription_feature_div'),

        # 重要特性列表
        ('ID', 'feature-bullets'),
        ('CSS_SELECTOR', '#feature-bullets'),
        ('CSS_SELECTOR', '#feature-bullets .a-list-item'),

        # 产品详情区域
        ('ID', 'detailBullets_feature_div'),
        ('CSS_SELECTOR', '#detailBullets_feature_div'),
        ('CSS_SELECTOR', '#detailBulletsWrapper_feature_div'),

        # 技术详情
        ('ID', 'technicalSpecifications_feature_div'),
        ('CSS_SELECTOR', '#technicalSpecifications_feature_div'),
        ('CSS_SELECTOR', '#productDetails_techSpec_section_1'),
        ('CSS_SELECTOR', '#productDetails_techSpec_section_2'),

        # 附加产品信息
        ('ID', 'productDetails_feature_div'),
        ('CSS_SELECTOR', '#productDetails_feature_div'),
        ('CSS_SELECTOR', '#prodDetails'),

        # 产品信息表格
        ('CSS_SELECTOR', '#productDetails_db_sections'),
        ('CSS_SELECTOR', '.content-grid-block'),
        ('CSS_SELECTOR', '#aplus'),
        ('CSS_SELECTOR', '#aplus_feature_div'),

        # 商品概述
        ('CSS_SELECTOR', '#featurebullets_feature_div'),
        ('CSS_SELECTOR', '#feature-bullets .a-unordered-list'),

        # 关于这个商品区域
        ('CSS_SELECTOR', '#aboutTheProduct'),
        ('CSS_SELECTOR', '#aboutTheProduct_feature_div'),

        # 产品规格
        ('CSS_SELECTOR', '#productSpecification'),
        ('CSS_SELECTOR', '#productSpecification_feature_div'),

        # 商品详情表格
        ('CSS_SELECTOR', '.detail-bullets'),
        ('CSS_SELECTOR', '.detail-bullets-wrapper'),

        # 其他可能包含描述的区域
        ('CSS_SELECTOR', '.product-facts'),
        ('CSS_SELECTOR', '.product-description'),
        ('CSS_SELECTOR', '.item-model-number'),
        ('CSS_SELECTOR', '#importantInformation'),
        ('CSS_SELECTOR', '#productOverview_feature_div'),

        # 使用 XPath 查找可能包含描述的区域
        ('XPATH', "//div[contains(@id, 'description')]"),
        ('XPATH', "//div[contains(@id, 'Description')]"),
        ('XPATH', "//div[contains(@class, 'description')]"),
        ('XPATH', "//div[contains(@id, 'product-description')]"),
        ('XPATH', "//div[contains(@id, 'product_description')]"),
        ('XPATH', "//div[@id='feature-bullets']//li"),
        ('XPATH', "//div[contains(@class, 'product-description')]"),
        ('XPATH', "//div[contains(@id, 'productDescription')]//p"),
        ('XPATH', "//div[@id='detailBulletsWrapper_feature_div']//span[@class='a-list-item']"),
        ('XPATH', "//div[contains(@id, 'detail')]//table//tr"),
        ('XPATH', "//div[contains(@id, 'product')]//table//tr")
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

    SEARCH_RESULT_RANK_SELECTORS = [
        '.zg-badge-text',
        '[class*="zg-badge"]',
        '.zg-rank',
        '.a-row.a-size-base span:first-child'
    ]

    SPONSORED_MARKERS = [
        '[data-component-type="sp-sponsored-result"]',
        '.s-sponsored-label-info-icon',
        '.puis-sponsored-label-text'
    ]
