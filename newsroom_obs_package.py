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
TEXT_SOURCE_KIND = "text_gdiplus"


def log_info(message):
    obs.script_log(obs.LOG_INFO, message)


def log_warning(message):
    obs.script_log(obs.LOG_WARNING, message)


def detect_text_source_kind():
    global TEXT_SOURCE_KIND

    for kind in ("text_gdiplus", "text_ft2_source"):
        try:
            display_name = obs.obs_source_get_display_name(kind)
        except Exception:
            display_name = ""

        if display_name:
            TEXT_SOURCE_KIND = kind
            return

    TEXT_SOURCE_KIND = "text_gdiplus"


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
    detect_text_source_kind()
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


def _data_from_dict(settings_dict):
    data = obs.obs_data_create()
    for key, value in settings_dict.items():
        if isinstance(value, bool):
            obs.obs_data_set_bool(data, key, value)
        elif isinstance(value, int):
            obs.obs_data_set_int(data, key, value)
        elif isinstance(value, float):
            obs.obs_data_set_double(data, key, value)
        else:
            obs.obs_data_set_string(data, key, str(value))
    return data


def ensure_scene_source(scene_name, source_name, source_kind, settings_dict):
    scene_src = obs.obs_get_source_by_name(scene_name)
    if scene_src is None:
        log_warning(f"Scene not found while ensuring source: '{scene_name}'")
        return

    scene = obs.obs_scene_from_source(scene_src)
    if scene is None:
        obs.obs_source_release(scene_src)
        return

    scene_item = obs.obs_scene_find_source(scene, source_name)
    if scene_item is None:
        data = _data_from_dict(settings_dict)
        src = obs.obs_source_create(source_kind, source_name, data, None)
        obs.obs_data_release(data)

        if src is None:
            log_warning(f"Could not create source '{source_name}' of kind '{source_kind}'")
            obs.obs_source_release(scene_src)
            return

        obs.obs_scene_add(scene, src)
        obs.obs_source_release(src)
    else:
        src = obs.obs_sceneitem_get_source(scene_item)
        if src is not None:
            data = obs.obs_source_get_settings(src)
            for key, value in settings_dict.items():
                if isinstance(value, bool):
                    obs.obs_data_set_bool(data, key, value)
                elif isinstance(value, int):
                    obs.obs_data_set_int(data, key, value)
                elif isinstance(value, float):
                    obs.obs_data_set_double(data, key, value)
                else:
                    obs.obs_data_set_string(data, key, str(value))
            obs.obs_source_update(src, data)
            obs.obs_data_release(data)

    obs.obs_source_release(scene_src)


def add_existing_source_to_scene(scene_name, source_name):
    scene_src = obs.obs_get_source_by_name(scene_name)
    src = obs.obs_get_source_by_name(source_name)
    if scene_src is None or src is None:
        if src is None:
            log_warning(f"Source not found, skipping scene attach: '{source_name}' -> '{scene_name}'")
        if scene_src is not None:
            obs.obs_source_release(scene_src)
        if src is not None:
            obs.obs_source_release(src)
        return

    scene = obs.obs_scene_from_source(scene_src)
    if scene is not None:
        existing = obs.obs_scene_find_source(scene, source_name)
        if existing is None:
            obs.obs_scene_add(scene, src)

    obs.obs_source_release(src)
    obs.obs_source_release(scene_src)


def lower_third_name(scene_name):
    return f"{LOWER_THIRD_SOURCE}_{scene_name}"


def ticker_name(scene_name):
    return f"{TICKER_SOURCE}_{scene_name}"


def clock_name(scene_name):
    return f"{CLOCK_SOURCE}_{scene_name}"


def logo_name(scene_name):
    return f"{LOGO_SOURCE}_{scene_name}"


def build_news_package():
    detect_text_source_kind()

    for scene_name in SCENES:
        ensure_scene(scene_name)

    first_ticker = TICKER_ITEMS[0] if TICKER_ITEMS else ""

    for scene_name in SCENES:
        ensure_scene_source(
            scene_name,
            lower_third_name(scene_name),
            TEXT_SOURCE_KIND,
            {
                "text": LOWER_THIRD_TEXT,
                "font": "Arial",
                "size": 42,
                "color": 0x00FFFFFF,
                "outline": True,
                "outline_color": 0x00000000,
            },
        )
        ensure_scene_source(
            scene_name,
            ticker_name(scene_name),
            TEXT_SOURCE_KIND,
            {
                "text": f"{CHANNEL_NAME} | {first_ticker}",
                "font": "Arial",
                "size": 34,
                "color": 0x00FFFFFF,
                "outline": True,
                "outline_color": 0x00000000,
            },
        )
        ensure_scene_source(
            scene_name,
            clock_name(scene_name),
            TEXT_SOURCE_KIND,
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
            ensure_scene_source(scene_name, logo_name(scene_name), "image_source", {"file": LOGO_PATH, "unload": False})

    # Main scenes: 01..04
    for scene_name in SCENES[:4]:
        for index, cam in enumerate(CAMERA_SOURCES, start=1):
            if not cam:
                continue

            cam_source = obs.obs_get_source_by_name(cam)
            if cam_source is not None:
                obs.obs_source_release(cam_source)
                add_existing_source_to_scene(scene_name, cam)
            else:
                missing_name = f"PKG_Missing_Camera_{index}_{scene_name}"
                ensure_scene_source(
                    scene_name,
                    missing_name,
                    TEXT_SOURCE_KIND,
                    {
                        "text": f"Missing camera source: {cam}",
                        "font": "Arial",
                        "size": 28,
                        "color": 0x0000FFFF,
                        "outline": True,
                        "outline_color": 0x00000000,
                    },
                )
                log_warning(f"Configured camera source was not found: '{cam}'")

    # Multi cam: attach only existing cameras
    for cam in CAMERA_SOURCES:
        if cam:
            cam_source = obs.obs_get_source_by_name(cam)
            if cam_source is not None:
                obs.obs_source_release(cam_source)
                add_existing_source_to_scene("05_Multi_Cam", cam)
            else:
                log_warning(f"Configured camera source was not found for 05_Multi_Cam: '{cam}'")

    rotate_ticker()
    update_clock()
    log_info("News package build completed")


def update_scene_overlay_sources(source_name_factory, settings_dict):
    for scene_name in SCENES:
        ensure_scene_source(scene_name, source_name_factory(scene_name), TEXT_SOURCE_KIND, settings_dict)


def rotate_ticker():
    global ACTIVE_TICKER_INDEX

    if not TICKER_ITEMS:
        return

    ACTIVE_TICKER_INDEX = (ACTIVE_TICKER_INDEX + 1) % len(TICKER_ITEMS)
    headline = TICKER_ITEMS[ACTIVE_TICKER_INDEX]
    update_scene_overlay_sources(ticker_name, {"text": f"{CHANNEL_NAME} | {headline}"})


def update_clock():
    update_scene_overlay_sources(clock_name, {"text": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")})
