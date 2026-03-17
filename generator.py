import random
import time

# ----------------------------
# FIFO (1..7) => цвет (как ты сказала)
# 1 Пн = green
# 2 Вт = yellow
# 3 Ср = red
# 4 Чт = blue
# 5 Пт = orange
# 6 Сб = purple
# 7 Вс = white
# ----------------------------
FIFO_COLORS = {
    1: "fifo-green",
    2: "fifo-yellow",
    3: "fifo-red",
    4: "fifo-blue",
    5: "fifo-orange",
    6: "fifo-purple",
    7: "fifo-white",
}

# 1-2 high, 3-4 mid, 5-6 low
SHELF_TIER = {1: "high", 2: "high", 3: "mid", 4: "mid", 5: "low", 6: "low"}

def price_tier(price: int) -> str:
    if price >= 320000:
        return "high"
    if price >= 240000:
        return "mid"
    return "low"


# ----------------------------
# Каталоги
# ----------------------------
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

# ----------------------------
# Карта "имя торта" -> файл PNG
# (твоя версия, можно расширять)
# ----------------------------
CAKE_IMAGE = {
    # RIGHT (шоколадные)
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

    # LEFT (фруктовые/оформленные)
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


def _catalog_to_items(side: str, pairs):
    out = []
    for name, price in pairs:
        out.append({
            "name": name,
            "price": price,
            "tier": price_tier(price),
            "side": side,
            "rank": random.randint(1, 7),
            "fifo_color": FIFO_COLORS[1],  # временно, ниже перезапишем
            "img": CAKE_IMAGE.get(name),
        })
    return out


def _set_fifo_color(item):
    item["fifo_color"] = FIFO_COLORS.get(item["rank"], "fifo-white")
    return item


def _pick_for_shelf(catalog, tier, count=4):
    pool = [c for c in catalog if c["tier"] == tier]
    if len(pool) < count:
        pool = catalog[:]

    chosen = []
    counts = {}
    tries = 0
    while len(chosen) < count and tries < 5000:
        c = random.choice(pool)
        nm = c["name"]
        # нельзя 3 одинаковых на полке
        if counts.get(nm, 0) >= 2:
            tries += 1
            continue
        chosen.append(c.copy())
        counts[nm] = counts.get(nm, 0) + 1
        tries += 1

    # если вдруг не набрали — добьём любыми
    while len(chosen) < count:
        chosen.append(random.choice(pool).copy())

    # каждому торту рандомный FIFO (1..7)
    for it in chosen:
        it["rank"] = random.randint(1, 7)
        _set_fifo_color(it)

    return chosen


def _build_perfect_showcase(left_catalog, right_catalog):
    # showcase: sides -> shelves -> slots(4)
    showcase = {"left": [], "right": []}
    for shelf_no in range(1, 7):
        tier = SHELF_TIER[shelf_no]
        showcase["left"].append(_pick_for_shelf(left_catalog, tier, 4))
        showcase["right"].append(_pick_for_shelf(right_catalog, tier, 4))
    return showcase


def _make_fifo_errors(showcase, error_rate: float):
    """Сделаем часть полок/позиций неверными по FIFO (старые сзади)"""
    # правило FIFO: "старый" (бОльший rank?) должен быть СПЕРЕДИ.
    # тут rank = день 1..7; считаем что "старее" = больше (7 старее 1)
    # Ошибка FIFO: сделаем так, чтобы один старый оказался сзади
    for side in ["left", "right"]:
        for shelf in showcase[side]:
            if random.random() < error_rate:
                # обменяем местами один back и один front
                b = random.choice([0, 1])
                f = random.choice([2, 3])
                shelf[b], shelf[f] = shelf[f], shelf[b]


def _make_price_errors(showcase, error_rate: float):
    """Нарушим ценовую категорию полки: подложим торт не того tier"""
    for side in ["left", "right"]:
        for idx, shelf in enumerate(showcase[side], start=1):
            correct_tier = SHELF_TIER[idx]
            if random.random() < error_rate:
                # поменяем tier у одного торта (симуляция ошибки)
                # реально: перетащим "не того tier" (для проверки)
                victim = random.choice([0, 1, 2, 3])
                # просто пометим "fake_tier" как неправильный
                shelf[victim]["tier"] = random.choice([t for t in ["high", "mid", "low"] if t != correct_tier])


def _apply_difficulty(showcase, mode: int):
    # режимы:
    # 1: только FIFO, витрина правильна 80% (то есть 20% ошибок FIFO)
    # 2: FIFO + цена, оба 80% (то есть 20% ошибок FIFO и 20% ошибок price)
    # 3: витрина правильна 70% (30% ошибок в перемешку FIFO+цена)
    if mode == 1:
        _make_fifo_errors(showcase, error_rate=0.20)
    elif mode == 2:
        _make_fifo_errors(showcase, error_rate=0.20)
        _make_price_errors(showcase, error_rate=0.20)
    elif mode == 3:
        _make_fifo_errors(showcase, error_rate=0.30)
        _make_price_errors(showcase, error_rate=0.30)


def _make_fill_mode(showcase, left_catalog, right_catalog, empty_slots=6):
    """mode 4: сделаем 6 пустых мест в витрине, остальное — норм"""
    empties = []
    # соберём все позиции
    positions = []
    for side in ["left", "right"]:
        for sidx in range(6):
            for pos in range(4):
                positions.append((side, sidx, pos))
    random.shuffle(positions)
    for i in range(empty_slots):
        side, sidx, pos = positions[i]
        empties.append((side, sidx, pos))
        showcase[side][sidx][pos] = None  # пусто
    return empties


def _build_freezer(showcase, left_catalog, right_catalog):
    """Склад: все торты, которых НЕТ в витрине (по имени)"""
    in_showcase = set()
    for side in ["left", "right"]:
        for shelf in showcase[side]:
            for it in shelf:
                if it is None:
                    continue
                in_showcase.add(it["name"])

    freezer = {"left": [], "right": []}
    for it in left_catalog:
        if it["name"] not in in_showcase:
            freezer["left"].append(it.copy())
    for it in right_catalog:
        if it["name"] not in in_showcase:
            freezer["right"].append(it.copy())

    # FIFO на складе тоже пусть будет рандом
    for side in ["left", "right"]:
        for it in freezer[side]:
            it["rank"] = random.randint(1, 7)
            _set_fifo_color(it)

    return freezer


def generate_game_state(mode: int, recent_seeds):
    # seed так, чтобы не повторялось
    # берём текущий time + попытки, пока не найдём новый
    base = int(time.time() * 1000)
    seed = base
    tries = 0
    while seed in recent_seeds and tries < 200:
        seed = base + random.randint(1, 999999)
        tries += 1

    random.seed(seed)

    left_catalog = _catalog_to_items("left", LEFT_FRUIT)
    right_catalog = _catalog_to_items("right", RIGHT_CHOCO)

    # идеальная витрина
    showcase = _build_perfect_showcase(left_catalog, right_catalog)

    empties = []
    if mode in [1, 2, 3]:
        _apply_difficulty(showcase, mode)
    elif mode == 4:
        # сначала идеально, потом сделаем пустые места
        empties = _make_fill_mode(showcase, left_catalog, right_catalog, empty_slots=6)

    freezer = _build_freezer(showcase, left_catalog, right_catalog)

    return {
        "seed": seed,
        "mode": mode,
        "showcase": showcase,
        "freezer": freezer,
        "empties": empties,
        "tiers": SHELF_TIER,
    }
