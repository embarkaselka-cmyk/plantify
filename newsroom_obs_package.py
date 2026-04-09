import obspython as obs
from datetime import datetime

# -------- Global settings --------
CHANNEL_NAME = "Plantify News"
LOGO_PATH = ""
CAMERA_SOURCES = ["Cam1", "Cam2", "Cam3"]
LOWER_THIRD_TEXT = "المراسل: البث المباشر"
TICKER_ITEMS = [
    "عاجل: بدء التغطية الصحفية للحدث",
    "مراسلنا: تحديثات مستمرة من موقع الحدث",
    "تابعونا للمزيد من التفاصيل أولاً بأول",
]
TICKER_SPEED_MS = 2500
ACTIVE_TICKER_INDEX = 0

SCENES = [
    "01_Studio_Wide",
    "02_Anchor_Close",
    "03_Field_Report",
    "04_Breaking_News",
    "05_Multi_Cam",
]

LOWER_THIRD_SOURCE = "PKG_LowerThird"
TICKER_SOURCE = "PKG_Ticker"
CLOCK_SOURCE = "PKG_Clock"
LOGO_SOURCE = "PKG_Logo"


def script_description():
    return (
        "Newsroom package for OBS (مشاهد متعددة + كاميرات + شريط أخبار + شعار).\n"
        "1) أضف أسماء الكاميرات الموجودة لديك في الإعدادات.\n"
        "2) اختر مسار الشعار.\n"
        "3) اضغط زر Build / Update News Package."
    )


def script_defaults(settings):
    obs.obs_data_set_default_string(settings, "channel_name", CHANNEL_NAME)
    obs.obs_data_set_default_string(settings, "logo_path", LOGO_PATH)
    obs.obs_data_set_default_string(settings, "camera_1", CAMERA_SOURCES[0])
    obs.obs_data_set_default_string(settings, "camera_2", CAMERA_SOURCES[1])
    obs.obs_data_set_default_string(settings, "camera_3", CAMERA_SOURCES[2])
    obs.obs_data_set_default_string(settings, "lower_third", LOWER_THIRD_TEXT)
    obs.obs_data_set_default_string(settings, "ticker_items", "\n".join(TICKER_ITEMS))
    obs.obs_data_set_default_int(settings, "ticker_speed_ms", TICKER_SPEED_MS)


def script_properties():
    props = obs.obs_properties_create()
    obs.obs_properties_add_text(props, "channel_name", "Channel Name", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_path(
        props,
        "logo_path",
        "Logo Path",
        obs.OBS_PATH_FILE,
        "Image (*.png *.jpg *.jpeg *.webp)",
        None,
    )
    obs.obs_properties_add_text(props, "camera_1", "Camera 1 Source Name", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(props, "camera_2", "Camera 2 Source Name", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(props, "camera_3", "Camera 3 Source Name", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(props, "lower_third", "Lower Third Text", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(props, "ticker_items", "Ticker Items (one per line)", obs.OBS_TEXT_MULTILINE)
    obs.obs_properties_add_int(props, "ticker_speed_ms", "Ticker Update Speed (ms)", 1000, 10000, 250)

    obs.obs_properties_add_button(props, "build_package", "Build / Update News Package", on_build_button)
    obs.obs_properties_add_button(props, "next_headline", "Next Headline Now", on_next_headline_button)
    return props


def script_update(settings):
    global CHANNEL_NAME, LOGO_PATH, CAMERA_SOURCES, LOWER_THIRD_TEXT, TICKER_ITEMS, TICKER_SPEED_MS

    CHANNEL_NAME = obs.obs_data_get_string(settings, "channel_name")
    LOGO_PATH = obs.obs_data_get_string(settings, "logo_path")
    CAMERA_SOURCES = [
        obs.obs_data_get_string(settings, "camera_1"),
        obs.obs_data_get_string(settings, "camera_2"),
        obs.obs_data_get_string(settings, "camera_3"),
    ]
    LOWER_THIRD_TEXT = obs.obs_data_get_string(settings, "lower_third")
    ticker_raw = obs.obs_data_get_string(settings, "ticker_items")
    TICKER_ITEMS = [line.strip() for line in ticker_raw.splitlines() if line.strip()]
    TICKER_SPEED_MS = obs.obs_data_get_int(settings, "ticker_speed_ms")

    obs.timer_remove(update_clock)
    obs.timer_remove(rotate_ticker)
    obs.timer_add(update_clock, 1000)
    obs.timer_add(rotate_ticker, max(1000, TICKER_SPEED_MS))


def script_load(settings):
    script_update(settings)


def script_unload():
    obs.timer_remove(update_clock)
    obs.timer_remove(rotate_ticker)


def on_build_button(props, prop):
    build_news_package()
    return True


def on_next_headline_button(props, prop):
    rotate_ticker()
    return True


def ensure_scene(scene_name):
    source = obs.obs_get_source_by_name(scene_name)
    if source is None:
        scene = obs.obs_scene_create(scene_name)
        if scene is not None:
            obs.obs_scene_release(scene)
    else:
        obs.obs_source_release(source)


def ensure_source(source_name, source_kind, settings_dict):
    source = obs.obs_get_source_by_name(source_name)
    if source is None:
        settings = obs.obs_data_create()
        for key, value in settings_dict.items():
            if isinstance(value, bool):
                obs.obs_data_set_bool(settings, key, value)
            elif isinstance(value, int):
                obs.obs_data_set_int(settings, key, value)
            elif isinstance(value, float):
                obs.obs_data_set_double(settings, key, value)
            else:
                obs.obs_data_set_string(settings, key, str(value))

        source = obs.obs_source_create(source_kind, source_name, settings, None)
        obs.obs_data_release(settings)
        if source is not None:
            obs.obs_source_release(source)
    else:
        obs.obs_source_release(source)
        update_source_settings(source_name, settings_dict)


def update_source_settings(source_name, settings_dict):
    source = obs.obs_get_source_by_name(source_name)
    if source is None:
        return

    settings = obs.obs_source_get_settings(source)
    for key, value in settings_dict.items():
        if isinstance(value, bool):
            obs.obs_data_set_bool(settings, key, value)
        elif isinstance(value, int):
            obs.obs_data_set_int(settings, key, value)
        elif isinstance(value, float):
            obs.obs_data_set_double(settings, key, value)
        else:
            obs.obs_data_set_string(settings, key, str(value))

    obs.obs_source_update(source, settings)
    obs.obs_data_release(settings)
    obs.obs_source_release(source)


def add_source_to_scene(scene_name, source_name):
    scene_source = obs.obs_get_source_by_name(scene_name)
    src = obs.obs_get_source_by_name(source_name)
    if scene_source is None or src is None:
        if scene_source is not None:
            obs.obs_source_release(scene_source)
        if src is not None:
            obs.obs_source_release(src)
        return

    scene = obs.obs_scene_from_source(scene_source)
    if scene is not None:
        existing = obs.obs_scene_find_source(scene, source_name)
        if existing is None:
            obs.obs_scene_add(scene, src)

    obs.obs_source_release(src)
    obs.obs_source_release(scene_source)


def build_news_package():
    for scene_name in SCENES:
        ensure_scene(scene_name)

    ensure_source(
        LOWER_THIRD_SOURCE,
        "text_gdiplus",
        {
            "text": LOWER_THIRD_TEXT,
            "font": "Arial",
            "size": 42,
            "color": 0x00FFFFFF,
            "outline": True,
            "outline_color": 0x00000000,
        },
    )

    first_ticker = TICKER_ITEMS[0] if TICKER_ITEMS else ""
    ensure_source(
        TICKER_SOURCE,
        "text_gdiplus",
        {
            "text": f"{CHANNEL_NAME} | {first_ticker}",
            "font": "Arial",
            "size": 34,
            "color": 0x00FFFFFF,
            "outline": True,
            "outline_color": 0x00000000,
        },
    )

    ensure_source(
        CLOCK_SOURCE,
        "text_gdiplus",
        {
            "text": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "font": "Consolas",
            "size": 28,
            "color": 0x00FFFFFF,
            "outline": True,
            "outline_color": 0x00000000,
        },
    )

    if LOGO_PATH:
        ensure_source(LOGO_SOURCE, "image_source", {"file": LOGO_PATH, "unload": False})

    # Scene composition
    main_scenes = SCENES[:4]
    for scene_name in main_scenes:
        for cam in CAMERA_SOURCES:
            if cam:
                add_source_to_scene(scene_name, cam)
        add_source_to_scene(scene_name, LOWER_THIRD_SOURCE)
        add_source_to_scene(scene_name, TICKER_SOURCE)
        add_source_to_scene(scene_name, CLOCK_SOURCE)
        if LOGO_PATH:
            add_source_to_scene(scene_name, LOGO_SOURCE)

    # Multi-cam scene: include all cameras only
    for cam in CAMERA_SOURCES:
        if cam:
            add_source_to_scene("05_Multi_Cam", cam)
    add_source_to_scene("05_Multi_Cam", TICKER_SOURCE)
    add_source_to_scene("05_Multi_Cam", CLOCK_SOURCE)
    if LOGO_PATH:
        add_source_to_scene("05_Multi_Cam", LOGO_SOURCE)

    rotate_ticker()
    update_clock()


def rotate_ticker():
    global ACTIVE_TICKER_INDEX

    if not TICKER_ITEMS:
        return

    ACTIVE_TICKER_INDEX = (ACTIVE_TICKER_INDEX + 1) % len(TICKER_ITEMS)
    headline = TICKER_ITEMS[ACTIVE_TICKER_INDEX]
    update_source_settings(TICKER_SOURCE, {"text": f"{CHANNEL_NAME} | {headline}"})


def update_clock():
    update_source_settings(CLOCK_SOURCE, {"text": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")})
