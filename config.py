import json


def read_json_file(file_path):
    with open(file_path, "r") as f:
        return json.load(f)


json_config = read_json_file("configure.json")
print(json_config)


class ScraperConfig:
    HEADLESS = json_config["headless"]
    MAX_PRODUCTS_PER_CATEGORY = json_config[
        "max_products_per_category"
    ]  # 每个类别爬取的商品数量
    MAX_WORKERS = json_config["max_workers"]  # 最大并行进程数
    CHUNK_SIZE = json_config["chunk_size"]  # 每个进程处理的产品数量
    WAIT_TIME = json_config["wait_time"]  # 等待时间
    MIN_SLEEP = json_config["min_sleep"]  # 最小等待时间
    MAX_SLEEP = json_config["max_sleep"]  # 最大等待时间
    SCROLL_STEPS = json_config["scroll_steps"]  # 滚动次数
    VPN_ENABLE = json_config["vpn_enable"]  # 是否启用VPN
    VPN_NAME = json_config["vpn_name"]  # VPN名称
    VPN_USERNAME = json_config["vpn_username"]  # VPN用户名
    VPN_PASSWORD = json_config["vpn_password"]  # VPN密码
    WINDOW_SIZE = (1920, 1080)

    TITLE_SELECTORS = [
        ("ID", "productTitle"),
        ("CSS_SELECTOR", "h1.a-text-normal"),
        ("CSS_SELECTOR", "span#productTitle"),
        ("CSS_SELECTOR", ".nav-search-label"),
        ("XPATH", "//span[@id='productTitle']"),
    ]

    PRICE_SELECTORS = [
        # 当前价格
        ("CSS_SELECTOR", ".apexPriceToPay .a-offscreen"),
        ("CSS_SELECTOR", ".a-price .a-offscreen"),
        ("CSS_SELECTOR", "#priceblock_ourprice"),
        ("CSS_SELECTOR", "#priceblock_dealprice"),
        # 划线价格/原价
        ("CSS_SELECTOR", ".a-text-price .a-offscreen"),
        ("CSS_SELECTOR", "#priceblock_listprice"),
        ("CSS_SELECTOR", '.a-price.a-text-price[data-a-strike="true"] .a-offscreen'),
        ("CSS_SELECTOR", ".a-text-strike"),
        # 促销价格
        ("CSS_SELECTOR", "#priceblock_saleprice"),
        ("CSS_SELECTOR", ".savingsPercentage"),
        ("CSS_SELECTOR", "#dealprice_savings"),
        ("CSS_SELECTOR", ".priceBlockSavingsString"),
        # 价格范围
        ("CSS_SELECTOR", "#priceblock_ourprice_lbl"),
        ("CSS_SELECTOR", ".a-price-range"),
        ("CSS_SELECTOR", ".a-price-range .a-price:first-child .a-offscreen"),  # 最低价
        ("CSS_SELECTOR", ".a-price-range .a-price:last-child .a-offscreen"),  # 最高价
        # 优惠信息
        ("CSS_SELECTOR", "#regularprice_savings"),
        ("CSS_SELECTOR", "#dealprice_savings"),
        ("CSS_SELECTOR", ".priceBlockSavingsString"),
        ("CSS_SELECTOR", "#couponBadgeRegularVpc"),
        # 分期付款信息
        ("CSS_SELECTOR", "#installmentCalculator"),
        ("CSS_SELECTOR", ".best-offer-name"),
        # Prime会员价格
        ("CSS_SELECTOR", "#prime_price_block"),
        ("CSS_SELECTOR", ".primePriceLabel"),
        # 其他可能的价格选择器
        ("XPATH", "//span[contains(@class,'a-price')]//span[@class='a-offscreen']"),
        ("XPATH", "//div[@id='corePrice_desktop']//span[contains(@class,'a-price')]"),
        (
            "XPATH",
            "//div[contains(@class,'price')]//span[contains(@class,'a-offscreen')]",
        ),
        (
            "XPATH",
            "//tr[contains(.,'List Price')]//span[@class='a-price']//span[@class='a-offscreen']",
        ),
        (
            "XPATH",
            "//tr[contains(.,'Deal Price')]//span[@class='a-price']//span[@class='a-offscreen']",
        ),
        (
            "XPATH",
            "//div[@id='corePriceDisplay_desktop_feature_div']//span[contains(@class,'a-price')]",
        ),
    ]

    RATING_SELECTORS = [
        ("CSS_SELECTOR", "i.a-icon-star .a-icon-alt"),
        ("CSS_SELECTOR", "#averageCustomerReviews .a-icon-star"),
        ("CSS_SELECTOR", "#acrPopover .a-size-base.a-color-base"),
        ("CSS_SELECTOR", "#acrPopover .a-size-base.a-color-base"),
        ("CSS_SELECTOR", "#acrPopover .a-size-base.a-color-base"),
        ("CSS_SELECTOR", "#acrPopover .a-size-base.a-color-base"),
        ("CSS_SELECTOR", "#averageCustomerReviews .a-icon-star .a-icon-alt"),
        ("XPATH", "//span[@class='a-icon-alt'][contains(text(),'out of 5 stars')]"),
        ("CSS_SELECTOR", 'span[data-hook="rating-out-of-text"]'),
        ("CSS_SELECTOR", "#acrPopover .a-declarative"),
        ("CSS_SELECTOR", "span.a-size-base.a-color-base"),
        (
            "CSS_SELECTOR",
            '[data-action="acrStarsLink-click-metrics"] .a-size-base.a-color-base',
        ),
        ("CSS_SELECTOR", "#acrPopover"),
        ("CSS_SELECTOR", 'span[data-hook="rating-out-of-text"]'),
        ("CSS_SELECTOR", ".a-icon-star .a-icon-alt"),
        ("XPATH", '//span[@class="a-icon-alt"]'),
        (
            "CSS_SELECTOR",
            "#averageCustomerReviews_feature_div .a-size-base.a-color-base",
        ),
        (
            "XPATH",
            "//div[@id='averageCustomerReviews']//span[contains(@class,'a-size-base')][contains(@class,'a-color-base')]",
        ),
    ]

    REVIEW_COUNT_SELECTORS = [("ID", "acrCustomerReviewText")]

    DESCRIPTION_SELECTORS = [
        # 产品描述区域
        ("ID", "productDescription"),
        ("CSS_SELECTOR", "#productDescription"),
        ("CSS_SELECTOR", "#productDescription_feature_div"),
        # 重要特性列表
        ("ID", "feature-bullets"),
        ("CSS_SELECTOR", "#feature-bullets"),
        ("CSS_SELECTOR", "#feature-bullets .a-list-item"),
        # 产品详情区域
        ("ID", "detailBullets_feature_div"),
        ("CSS_SELECTOR", "#detailBullets_feature_div"),
        ("CSS_SELECTOR", "#detailBulletsWrapper_feature_div"),
        # 技术详情
        ("ID", "technicalSpecifications_feature_div"),
        ("CSS_SELECTOR", "#technicalSpecifications_feature_div"),
        ("CSS_SELECTOR", "#productDetails_techSpec_section_1"),
        ("CSS_SELECTOR", "#productDetails_techSpec_section_2"),
        # 附加产品信息
        ("ID", "productDetails_feature_div"),
        ("CSS_SELECTOR", "#productDetails_feature_div"),
        ("CSS_SELECTOR", "#prodDetails"),
        # 产品信息表格
        ("CSS_SELECTOR", "#productDetails_db_sections"),
        ("CSS_SELECTOR", ".content-grid-block"),
        ("CSS_SELECTOR", "#aplus"),
        ("CSS_SELECTOR", "#aplus_feature_div"),
        # 商品概述
        ("CSS_SELECTOR", "#featurebullets_feature_div"),
        ("CSS_SELECTOR", "#feature-bullets .a-unordered-list"),
        # 关于这个商品区域
        ("CSS_SELECTOR", "#aboutTheProduct"),
        ("CSS_SELECTOR", "#aboutTheProduct_feature_div"),
        # 产品规格
        ("CSS_SELECTOR", "#productSpecification"),
        ("CSS_SELECTOR", "#productSpecification_feature_div"),
        # 商品详情表格
        ("CSS_SELECTOR", ".detail-bullets"),
        ("CSS_SELECTOR", ".detail-bullets-wrapper"),
        # 其他可能包含描述的区域
        ("CSS_SELECTOR", ".product-facts"),
        ("CSS_SELECTOR", ".product-description"),
        ("CSS_SELECTOR", ".item-model-number"),
        ("CSS_SELECTOR", "#importantInformation"),
        ("CSS_SELECTOR", "#productOverview_feature_div"),
        # 使用 XPath 查找可能包含描述的区域
        ("XPATH", "//div[contains(@id, 'description')]"),
        ("XPATH", "//div[contains(@id, 'Description')]"),
        ("XPATH", "//div[contains(@class, 'description')]"),
        ("XPATH", "//div[contains(@id, 'product-description')]"),
        ("XPATH", "//div[contains(@id, 'product_description')]"),
        ("XPATH", "//div[@id='feature-bullets']//li"),
        ("XPATH", "//div[contains(@class, 'product-description')]"),
        ("XPATH", "//div[contains(@id, 'productDescription')]//p"),
        (
            "XPATH",
            "//div[@id='detailBulletsWrapper_feature_div']//span[@class='a-list-item']",
        ),
        ("XPATH", "//div[contains(@id, 'detail')]//table//tr"),
        ("XPATH", "//div[contains(@id, 'product')]//table//tr"),
    ]

    PRODUCT_LINK_SELECTORS = [
        "a[href*='/dp/']",
        ".zg-item-immersion a[href*='/dp/']",
        ".zg-grid-general-faceout a[href*='/dp/']",
        "div[data-component-type='s-search-result'] a[href*='/dp/']",
        ".a-link-normal[href*='/dp/']",
        "#gridItemRoot a[href*='/dp/']",
        ".s-result-item a[href*='/dp/']",
        ".s-include-content-margin a[href*='/dp/']",
    ]

    IMAGE_SELECTORS = [
        ("ID", "landingImage"),
        ("CSS_SELECTOR", "#imgBlkFront"),
        ("CSS_SELECTOR", "#main-image"),
        ("CSS_SELECTOR", ".a-dynamic-image"),
        ("XPATH", "//img[@id='landingImage']"),
    ]

    BRAND_SELECTORS = [
        ("ID", "bylineInfo"),
        ("CSS_SELECTOR", "#bylineInfo"),
        ("CSS_SELECTOR", "#brand"),
        ("XPATH", "//a[@id='bylineInfo']"),
        ("CSS_SELECTOR", "#bylineInfo_feature_div"),
        ("CSS_SELECTOR", ".po-brand .a-span9"),
        ("CSS_SELECTOR", ".po-brand .a-size-base"),
        ("XPATH", "//a[contains(@class, 'contributorNameID')]"),
        ("XPATH", "//div[@id='bylineInfo_feature_div']//a"),
        ("XPATH", "//div[@id='brandByline_feature_div']//a"),
        ("XPATH", "//tr[contains(.,'Brand')]/td[2]"),
        ("XPATH", "//div[contains(@class, 'po-brand')]//span[@class='a-size-base']"),
    ]

    AVAILABILITY_SELECTORS = [
        ("ID", "availability"),
        ("CSS_SELECTOR", "#availability span"),
        ("CSS_SELECTOR", "#outOfStock"),
        ("XPATH", "//div[@id='availability']/span"),
        ("CSS_SELECTOR", "#availability span"),
        ("CSS_SELECTOR", "#merchantInfoFeature"),
        ("CSS_SELECTOR", "#buybox-see-all-buying-choices"),
        (
            "XPATH",
            '//div[@id="availability"]//span[@class="a-size-medium a-color-success"]',
        ),
        ("CSS_SELECTOR", "#outOfStock .a-color-price"),
    ]

    CATEGORY_NAME_SELECTORS = [
        "//h1[contains(@class, 'a-size-large')]",
        "//span[contains(@class, 'zg-banner-text')]",
        "//span[@class='category']",
        "//title",
        "//div[contains(@class, 'category-title')]",
    ]

    SEARCH_RESULT_RANK_SELECTORS = [
        ".zg-badge-text",
        '[class*="zg-badge"]',
        ".zg-rank",
        ".a-row.a-size-base span:first-child",
    ]

    SPONSORED_MARKERS = [
        '[data-component-type="sp-sponsored-result"]',
        ".s-sponsored-label-info-icon",
        ".puis-sponsored-label-text",
    ]
