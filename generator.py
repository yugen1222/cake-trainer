import random
import time
from datetime import datetime

try:
    from zoneinfo import ZoneInfo
except Exception:
    ZoneInfo = None


FIFO_COLORS = {
    1: "fifo-green",   # Пн
    2: "fifo-yellow",  # Вт
    3: "fifo-red",     # Ср
    4: "fifo-blue",    # Чт
    5: "fifo-orange",  # Пт
    6: "fifo-purple",  # Сб
    7: "fifo-white",   # Вс
}

FIFO_LABELS = {
    1: "Пн",
    2: "Вт",
    3: "Ср",
    4: "Чт",
    5: "Пт",
    6: "Сб",
    7: "Вс",
}

SHELF_TIER = {
    1: "high",
    2: "high",
    3: "mid",
    4: "mid",
    5: "low",
    6: "low",
}

TIER_LABELS = {
    "high": "Дорогая категория",
    "mid": "Средняя категория",
    "low": "Низкая категория",
}


def today_fifo_day() -> int:
    if ZoneInfo:
        now = datetime.now(ZoneInfo("Asia/Tashkent"))
    else:
        now = datetime.now()
    return now.weekday() + 1


def fifo_order_for_today(today_day: int):
    days = [1, 2, 3, 4, 5, 6, 7]
    start = today_day % 7
    return days[start:] + days[:start]


def fifo_rank_for_day(fifo_day: int, today_day: int) -> int:
    order = fifo_order_for_today(today_day)
    return order.index(fifo_day) + 1


def price_tier(price: int) -> str:
    if price >= 320000:
        return "high"
    if price >= 240000:
        return "mid"
    return "low"


LEFT_FRUIT = [
    ("Сафия Торт Оформление", 375000),
    ("Киевский оформленный", 369000),
    ("Киевский бантик", 349000),
    ("Киевский розовый", 335000),
    ("Радуга торт круглый", 329000),
    ("Корзинка торт", 329000),
    ("Сафия торт Бежевый", 319000),
    ("Сафия торт Розовый", 319000),
    ("Мороженко торт", 315000),
    ("Шок малиновый торт круглый", 315000),
    ("Барби торт", 315000),
    ("Динозаврик торт", 315000),
    ("Киевский рожок", 299000),
    ("Фруктовый торт круглый", 285000),
    ("Торт Стич", 279000),
    ("Микс торт круглый", 275000),
    ("Джульетта оформленная", 269000),
    ("Джульета торт", 259000),
    ("Ягодно-творожный торт", 259000),
    ("Радуга шоколадная", 259000),
    ("Торт Мишка", 249000),
    ("Фисташковый Меренговый рул", 239000),
    ("Верона стандартный торт", 235000),
    ("Меренговый рулет", 219000),
    ("Берри кейк мини", 219000),
    ("Смородина торт", 199000),
    ("Сказка Рулет NEW", 175000),
]

RIGHT_CHOCO = [
    ("Рафаэлло торт", 429000),
    ("Орео торт", 395000),
    ("Роше торт", 389000),
    ("Шок банан круг", 359000),
    ("Ириска торт", 345000),
    ("Адмирал торт круглый", 319000),
    ("Сникерс торт круглый", 315000),
    ("Черный принц торт круглый", 299000),
    ("Виктория торт", 279000),
    ("Баунти торт", 269000),
    ("Карамельно-медовый торт", 265000),
    ("Торт Молочная девочка", 259000),
    ("Торт Блэк форест", 249000),
    ("Рафаэлло мини торт", 249000),
    ("Шок банан мини торт", 239000),
    ("Браво торт", 239000),
    ("Париж торт", 239000),
    ("Прага торт", 229000),
    ("Лесной орех мини торт", 209000),
    ("Тирамису мини торт", 209000),
    ("Кофе тоффи мини торт", 199000),
    ("Песочно - Малиновый", 195000),
    ("Милк слайс мини торт", 195000),
    ("Птичка торт", 165000),
    ("Вишенка мини торт", 122000),
]

CAKE_IMAGE = {
    "Рафаэлло торт": "Рафаэлло.png",
    "Орео торт": "Орео.png",
    "Роше торт": "Роше.png",
    "Шок банан круг": "Шоколадно банановый.png",
    "Ириска торт": "Ириска.png",
    "Адмирал торт круглый": "Адмирал.png",
    "Сникерс торт круглый": "Сникерс.png",
    "Черный принц торт круглый": "Чёрный принц.png",
    "Виктория торт": "Виктория.png",
    "Баунти торт": "баунти.png",
    "Торт Молочная девочка": "Молочная девочка.png",
    "Торт Блэк форест": "Торт Блэк Форест.png",
    "Рафаэлло мини торт": "Мини торт Рафаэлло.png",
    "Шок банан мини торт": "Мини торт Шоколадно-банановый.png",
    "Браво торт": "Торт Браво.png",
    "Париж торт": "Торт Париж.png",
    "Прага торт": "Прага.png",
    "Лесной орех мини торт": "Мини торт Лесной орех.png",
    "Кофе тоффи мини торт": "Мини торт Кофе-тоффи.png",
    "Песочно - Малиновый": "Песочно-малиновый.png",
    "Милк слайс мини торт": "Мини торт Милк слайс.png",
    "Птичка торт": "Птичье молоко.png",
    "Вишенка мини торт": "вишенка.png",

    "Сафия Торт Оформление": "Сафия оформление.png",
    "Радуга торт круглый": "Радуга.png",
    "Корзинка торт": "Корзинка.png",
    "Сафия торт Бежевый": "Сафия бежевый.png",
    "Сафия торт Розовый": "Сафия розовый.png",
    "Мороженко торт": "Мороженко.png",
    "Шок малиновый торт круглый": "Шоколадно малиновый.png",
    "Барби торт": "барби.png",
    "Фруктовый торт круглый": "Фруктовый.png",
    "Торт Стич": "Торт Стич.png",
    "Микс торт круглый": "Микс.png",
    "Джульетта оформленная": "Джульетта оформленный.png",
    "Джульета торт": "Джульетта.png",
    "Ягодно-творожный торт": "Ягодно творожный.png",
    "Торт Мишка": "Торт Мишка.png",
    "Верона стандартный торт": "Верона.png",
    "Берри кейк мини": "Мини торт Берри кейк.png",
    "Смородина торт": "Смородина.png",
    "Сказка Рулет NEW": "Сказка.png",
}


def _set_fifo(item, today_day: int):
    fifo_day = random.randint(1, 7)
    item["fifo_day"] = fifo_day
    item["fifo_label"] = FIFO_LABELS[fifo_day]
    item["fifo_color"] = FIFO_COLORS[fifo_day]
    item["rank"] = fifo_rank_for_day(fifo_day, today_day)
    return item


def _catalog_to_items(side: str, pairs, today_day: int):
    out = []
    for name, price in pairs:
        tier = price_tier(price)
        item = {
            "name": name,
            "price": price,
            "tier": tier,
            "tier_label": TIER_LABELS[tier],
            "side": side,
            "rank": 0,
            "fifo_day": 1,
            "fifo_label": "Пн",
            "fifo_color": "fifo-green",
            "img": CAKE_IMAGE.get(name),
        }
        _set_fifo(item, today_day)
        out.append(item)
    return out


def _arrange_cross_if_duplicate(shelf):
    """
    Позиции:
    0 = задний левый
    1 = задний правый
    2 = передний левый
    3 = передний правый

    Если 2 одинаковых торта на одной полке:
    должны стоять диагонально:
    0 и 3 или 1 и 2.

    Более старый из двух ставим впереди.
    """
    names = {}
    for idx, item in enumerate(shelf):
        if item is None:
            continue
        names.setdefault(item["name"], []).append((idx, item))

    duplicate_groups = [v for v in names.values() if len(v) == 2]

    if not duplicate_groups:
        return shelf

    # если на полке есть одна пара одинаковых — красиво ставим крестом
    group = duplicate_groups[0]
    duplicates = [group[0][1], group[1][1]]
    others = [item for item in shelf if item["name"] != duplicates[0]["name"]]

    duplicates.sort(key=lambda x: x["rank"])
    older = duplicates[0]
    newer = duplicates[1]

    new_shelf = [None, None, None, None]

    if random.choice([True, False]):
        # новый сзади слева, старый спереди справа
        new_shelf[0] = newer
        new_shelf[3] = older
        free_positions = [1, 2]
    else:
        # новый сзади справа, старый спереди слева
        new_shelf[1] = newer
        new_shelf[2] = older
        free_positions = [0, 3]

    random.shuffle(others)
    for pos, item in zip(free_positions, others):
        new_shelf[pos] = item

    # страховка
    for i in range(4):
        if new_shelf[i] is None and others:
            new_shelf[i] = others.pop()

    return new_shelf


def _pick_for_shelf(catalog, tier, global_counts, count=4, today_day=1):
    pool = [c for c in catalog if c["tier"] == tier]
    if len(pool) < count:
        pool = catalog[:]

    chosen = []
    local_counts = {}
    tries = 0

    while len(chosen) < count and tries < 10000:
        base = random.choice(pool)
        name = base["name"]

        # во всей витрине один вид торта максимум 2 раза
        if global_counts.get(name, 0) >= 2:
            tries += 1
            continue

        # на одной полке тоже максимум 2 одинаковых
        if local_counts.get(name, 0) >= 2:
            tries += 1
            continue

        item = base.copy()
        _set_fifo(item, today_day)

        chosen.append(item)
        global_counts[name] = global_counts.get(name, 0) + 1
        local_counts[name] = local_counts.get(name, 0) + 1
        tries += 1

    # если вдруг не хватило из-за ограничений — добираем уникальными без превышения 2
    while len(chosen) < count:
        available = [
            c for c in pool
            if global_counts.get(c["name"], 0) < 2
            and local_counts.get(c["name"], 0) < 2
        ]

        if not available:
            available = [
                c for c in catalog
                if global_counts.get(c["name"], 0) < 2
                and local_counts.get(c["name"], 0) < 2
            ]

        if not available:
            break

        base = random.choice(available)
        name = base["name"]

        item = base.copy()
        _set_fifo(item, today_day)

        chosen.append(item)
        global_counts[name] = global_counts.get(name, 0) + 1
        local_counts[name] = local_counts.get(name, 0) + 1

    chosen.sort(key=lambda x: x["rank"])

    # если на одной полке 2 одинаковых — ставим крест-на-крест
    chosen = _arrange_cross_if_duplicate(chosen)

    return chosen


def _build_perfect_showcase(left_catalog, right_catalog, today_day: int):
    showcase = {"left": [], "right": []}

    left_counts = {}
    right_counts = {}

    for shelf_no in range(1, 7):
        tier = SHELF_TIER[shelf_no]

        left_shelf = _pick_for_shelf(
            left_catalog,
            tier,
            left_counts,
            count=4,
            today_day=today_day
        )

        right_shelf = _pick_for_shelf(
            right_catalog,
            tier,
            right_counts,
            count=4,
            today_day=today_day
        )

        showcase["left"].append(left_shelf)
        showcase["right"].append(right_shelf)

    return showcase


def _make_fifo_errors(showcase, error_rate: float):
    for side in ["left", "right"]:
        for shelf in showcase[side]:
            if random.random() < error_rate:
                filled = [i for i, item in enumerate(shelf) if item is not None]
                if len(filled) >= 2:
                    a, b = random.sample(filled, 2)
                    shelf[a], shelf[b] = shelf[b], shelf[a]


def _make_price_errors(showcase, left_catalog, right_catalog, error_rate: float, today_day: int):
    for side in ["left", "right"]:
        catalog = left_catalog if side == "left" else right_catalog

        for shelf_idx, shelf in enumerate(showcase[side], start=1):
            correct_tier = SHELF_TIER[shelf_idx]

            if random.random() < error_rate:
                wrong_pool = [c for c in catalog if c["tier"] != correct_tier]
                if not wrong_pool:
                    continue

                filled = [i for i, item in enumerate(shelf) if item is not None]
                if not filled:
                    continue

                victim_pos = random.choice(filled)
                wrong_item = random.choice(wrong_pool).copy()
                _set_fifo(wrong_item, today_day)

                shelf[victim_pos] = wrong_item


def _apply_difficulty(showcase, mode: int, left_catalog, right_catalog, today_day: int):
    if mode == 1:
        _make_fifo_errors(showcase, error_rate=0.20)

    elif mode == 2:
        _make_fifo_errors(showcase, error_rate=0.20)
        _make_price_errors(showcase, left_catalog, right_catalog, 0.20, today_day)

    elif mode == 3:
        _make_fifo_errors(showcase, error_rate=0.30)
        _make_price_errors(showcase, left_catalog, right_catalog, 0.30, today_day)


def _make_fill_mode(showcase, empty_slots=6):
    empties = []

    positions = []
    for side in ["left", "right"]:
        for sidx in range(6):
            for pos in range(4):
                positions.append((side, sidx, pos))

    random.shuffle(positions)

    for i in range(empty_slots):
        side, sidx, pos = positions[i]
        empties.append((side, sidx, pos))
        showcase[side][sidx][pos] = None

    return empties


def _build_freezer(showcase, left_catalog, right_catalog, today_day: int):
    in_showcase = set()

    for side in ["left", "right"]:
        for shelf in showcase[side]:
            for item in shelf:
                if item is None:
                    continue
                in_showcase.add(item["name"])

    freezer = {"left": [], "right": []}

    for base in left_catalog:
        if base["name"] not in in_showcase:
            item = base.copy()
            _set_fifo(item, today_day)
            freezer["left"].append(item)

    for base in right_catalog:
        if base["name"] not in in_showcase:
            item = base.copy()
            _set_fifo(item, today_day)
            freezer["right"].append(item)

    random.shuffle(freezer["left"])
    random.shuffle(freezer["right"])

    return freezer


def _build_price_table(left_catalog, right_catalog):
    all_items = []

    for item in left_catalog + right_catalog:
        all_items.append({
            "name": item["name"],
            "price": item["price"],
            "tier": item["tier"],
            "tier_label": item["tier_label"],
            "side": item["side"],
            "img": item["img"],
        })

    all_items.sort(key=lambda x: x["name"])
    return all_items


def generate_game_state(mode: int, recent_seeds=None):
    if recent_seeds is None:
        recent_seeds = []

    base = int(time.time() * 1000)
    seed = base
    tries = 0

    while seed in recent_seeds and tries < 200:
        seed = base + random.randint(1, 999999)
        tries += 1

    random.seed(seed)

    today_day = today_fifo_day()
    fifo_order = fifo_order_for_today(today_day)

    left_catalog = _catalog_to_items("left", LEFT_FRUIT, today_day)
    right_catalog = _catalog_to_items("right", RIGHT_CHOCO, today_day)

    showcase = _build_perfect_showcase(left_catalog, right_catalog, today_day)

    empties = []

    if mode in [1, 2, 3]:
        _apply_difficulty(showcase, mode, left_catalog, right_catalog, today_day)

    elif mode == 4:
        empties = _make_fill_mode(showcase, empty_slots=6)

    freezer = _build_freezer(showcase, left_catalog, right_catalog, today_day)
    price_table = _build_price_table(left_catalog, right_catalog)

    return {
        "seed": seed,
        "mode": mode,

        "showcase": showcase,
        "freezer": freezer,
        "empties": empties,
        "tiers": SHELF_TIER,

        "today_fifo_day": today_day,
        "today_fifo_label": FIFO_LABELS[today_day],
        "fifo_order": fifo_order,
        "fifo_order_labels": [FIFO_LABELS[d] for d in fifo_order],

        "price_table": price_table,
    }
