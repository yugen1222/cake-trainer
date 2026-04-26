(() => {
  "use strict";

  const MODE = Number(window.GAME_MODE || 1);
  const GAME_SEED = Number(window.GAME_SEED || 0);

  const btnCheck = document.getElementById("btnCheck");
  const btnClear = document.getElementById("btnClear");
  const btnTimer = document.getElementById("btnTimer");
  const timerBox = document.getElementById("timerBox");

  const modal = document.getElementById("resultModal");
  const resultText = document.getElementById("resultText");
  const btnCloseModal = document.getElementById("btnCloseModal");

  const CLS_OK = "mark-ok";
  const CLS_BAD = "mark-bad";
  const CLS_SHELF_OK = "shelf-ok";
  const CLS_SHELF_BAD = "shelf-bad";

  let draggedCake = null;
  let fromSlot = null;
  let fromFreezer = false;

  let timerInterval = null;
  let timerSeconds = 0;

  function qs(sel, root = document) {
    return root.querySelector(sel);
  }

  function qsa(sel, root = document) {
    return Array.from(root.querySelectorAll(sel));
  }

  function closestSlot(el) {
    return el ? el.closest(".slot") : null;
  }

  function closestCake(el) {
    return el ? el.closest(".cake") : null;
  }

  function isCakeInFreezer(cakeEl) {
    return !!cakeEl.closest(".freezer");
  }

  function getFreezerGrid() {
    return qs(".freezer-grid");
  }

  function slotHasCake(slotEl) {
    return !!qs(".cake", slotEl);
  }

  function removeEmpty(slotEl) {
    const empty = qs(".empty", slotEl);
    if (empty) empty.remove();
  }

  function ensureEmpty(slotEl) {
    if (!qs(".cake", slotEl) && !qs(".empty", slotEl)) {
      const d = document.createElement("div");
      d.className = "empty";
      d.textContent = "Пусто";
      slotEl.appendChild(d);
    }
  }

  function clearMarks() {
    qsa("." + CLS_OK).forEach(el => el.classList.remove(CLS_OK));
    qsa("." + CLS_BAD).forEach(el => el.classList.remove(CLS_BAD));
    qsa("." + CLS_SHELF_OK).forEach(el => el.classList.remove(CLS_SHELF_OK));
    qsa("." + CLS_SHELF_BAD).forEach(el => el.classList.remove(CLS_SHELF_BAD));
  }

  function markSlot(slotEl, ok) {
    slotEl.classList.remove(CLS_OK, CLS_BAD);
    slotEl.classList.add(ok ? CLS_OK : CLS_BAD);
  }

  function markShelf(shelfEl, ok) {
    shelfEl.classList.remove(CLS_SHELF_OK, CLS_SHELF_BAD);
    shelfEl.classList.add(ok ? CLS_SHELF_OK : CLS_SHELF_BAD);
  }

  function showResult(msg) {
    if (!modal || !resultText) {
      alert(msg);
      return;
    }

    resultText.innerHTML = msg.replace(/\n/g, "<br>");
    modal.hidden = false;
  }

  if (btnCloseModal) {
    btnCloseModal.addEventListener("click", () => {
      modal.hidden = true;
    });
  }

  if (modal) {
    modal.addEventListener("click", (e) => {
      if (e.target === modal) modal.hidden = true;
    });
  }

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && modal && !modal.hidden) {
      modal.hidden = true;
    }
  });

  // ---------- DRAG ----------
  document.addEventListener("dragstart", (e) => {
    const cake = closestCake(e.target);
    if (!cake) return;

    const inFreezer = isCakeInFreezer(cake);

    if (inFreezer && MODE !== 4) {
      e.preventDefault();
      return;
    }

    draggedCake = cake;
    fromSlot = closestSlot(cake);
    fromFreezer = inFreezer;

    if (e.dataTransfer) {
      e.dataTransfer.setData("text/plain", cake.dataset.name || "cake");
      e.dataTransfer.effectAllowed = "move";
    }
  });

  document.addEventListener("dragend", () => {
    draggedCake = null;
    fromSlot = null;
    fromFreezer = false;
  });

  document.addEventListener("dragover", (e) => {
    const slot = closestSlot(e.target);
    const freezerGrid = e.target.closest(".freezer-grid");

    if (slot || freezerGrid) {
      e.preventDefault();
      if (e.dataTransfer) e.dataTransfer.dropEffect = "move";
    }
  });

  document.addEventListener("drop", (e) => {
    if (!draggedCake) return;

    const targetSlot = closestSlot(e.target);
    const targetFreezerGrid = e.target.closest(".freezer-grid");

    e.preventDefault();

    // Режим 4: из витрины можно убрать обратно в морозилку
    if (MODE === 4 && targetFreezerGrid && !fromFreezer) {
      targetFreezerGrid.appendChild(draggedCake);
      if (fromSlot) ensureEmpty(fromSlot);
      return;
    }

    // В режимах 1-3 морозилку трогать нельзя
    if (MODE !== 4 && fromFreezer) return;

    // Если бросаем не в слот — ничего
    if (!targetSlot) return;

    // Режим 4: из морозилки можно класть только в пустой слот
    if (MODE === 4 && fromFreezer) {
      if (slotHasCake(targetSlot)) return;

      removeEmpty(targetSlot);
      targetSlot.appendChild(draggedCake);
      return;
    }

    if (fromSlot && fromSlot === targetSlot) return;

    const targetCake = qs(".cake", targetSlot);

    // Перемещение в пустой слот
    if (!targetCake) {
      removeEmpty(targetSlot);
      targetSlot.appendChild(draggedCake);

      if (fromSlot) ensureEmpty(fromSlot);
      return;
    }

    // Обмен местами
    if (fromSlot) {
      targetSlot.appendChild(draggedCake);
      fromSlot.appendChild(targetCake);
    }
  });

  // ---------- CHECK HELPERS ----------
  function parseRank(cakeEl) {
    const r = Number(cakeEl?.dataset?.rank);
    return Number.isFinite(r) ? r : 999999;
  }

  function cakeName(cakeEl) {
    return (cakeEl?.dataset?.name || "").trim();
  }

  function cakeLabel(cakeEl) {
    return (cakeEl?.dataset?.fifoLabel || "").trim();
  }

  function getTier(cakeEl) {
    return (cakeEl?.dataset?.tier || "").toString();
  }

  function getExpectedTier(slotEl) {
    return (slotEl?.dataset?.expectedTier || "").toString();
  }

  function slotPositionName(slotEl) {
    const p = Number(slotEl.dataset.slot);
    const shelf = slotEl.dataset.shelf;
    const side = slotEl.dataset.side === "left" ? "фруктовая сторона" : "шоколадная сторона";

    let row = "";
    if (p === 0) row = "задний левый";
    else if (p === 1) row = "задний правый";
    else if (p === 2) row = "передний левый";
    else if (p === 3) row = "передний правый";
    else row = "позиция " + p;

    return side + ", полка " + shelf + ", " + row;
  }

  function accessibilityScore(slotEl) {
    const p = Number(slotEl.dataset.slot);
    const shelf = Number(slotEl.dataset.shelf || 0);

    const isFront = p === 2 || p === 3;
    const rowScore = isFront ? 0 : 1;

    return rowScore * 100 + shelf;
  }

  function getShowcaseCakes() {
    return qsa(".showcase .slot").map(slot => {
      const cake = qs(".cake", slot);
      if (!cake) return null;

      return {
        slot,
        cake,
        name: cakeName(cake),
        rank: parseRank(cake),
        label: cakeLabel(cake),
        access: accessibilityScore(slot)
      };
    }).filter(Boolean);
  }

  function checkTierSlot(slot) {
    const cake = qs(".cake", slot);
    if (!cake) return false;

    const expected = getExpectedTier(slot);
    if (!expected) return true;

    return getTier(cake) === expected;
  }

  function checkShelfCrossRule(shelf, errors) {
    const slots = qsa(".slot", shelf);
    const byName = new Map();
    let shelfOk = true;

    for (const slot of slots) {
      const cake = qs(".cake", slot);
      if (!cake) continue;

      const name = cakeName(cake);
      if (!byName.has(name)) byName.set(name, []);
      byName.get(name).push(slot);
    }

    for (const [name, cakeSlots] of byName.entries()) {
      if (cakeSlots.length > 2) {
        shelfOk = false;
        cakeSlots.forEach(slot => markSlot(slot, false));
        errors.push(
          "❌ Ошибка количества: «" + name + "».\n" +
          "На одной полке больше 2 одинаковых тортов. Оставь максимум 2."
        );
        continue;
      }

      if (cakeSlots.length === 2) {
        const positions = cakeSlots.map(slot => Number(slot.dataset.slot)).sort((a, b) => a - b);
        const key = positions.join("-");

        const isDiagonal = key === "0-3" || key === "1-2";

        if (!isDiagonal) {
          shelfOk = false;
          cakeSlots.forEach(slot => markSlot(slot, false));

          errors.push(
            "❌ Ошибка выкладки: «" + name + "».\n" +
            "Одинаковые торты должны стоять крест-на-крест: задний левый + передний правый или задний правый + передний левый."
          );
        }
      }
    }

    return shelfOk;
  }

  function checkGlobalDuplicateLimit(errors) {
    const items = getShowcaseCakes();
    const byName = new Map();
    let okAll = true;

    for (const item of items) {
      if (!byName.has(item.name)) byName.set(item.name, []);
      byName.get(item.name).push(item);
    }

    for (const [name, arr] of byName.entries()) {
      if (arr.length > 2) {
        okAll = false;
        arr.forEach(x => markSlot(x.slot, false));

        errors.push(
          "❌ Ошибка количества: «" + name + "».\n" +
          "В витрине больше 2 одинаковых тортов. По правилу должно быть максимум 2."
        );
      }
    }

    return okAll;
  }

  function checkSameCakeFIFO(errors) {
    const items = getShowcaseCakes();
    const byName = new Map();
    let okAll = true;

    for (const item of items) {
      if (!byName.has(item.name)) byName.set(item.name, []);
      byName.get(item.name).push(item);
    }

    for (const [name, arr] of byName.entries()) {
      if (arr.length <= 1) continue;

      for (let i = 0; i < arr.length; i++) {
        for (let j = 0; j < arr.length; j++) {
          if (i === j) continue;

          const a = arr[i];
          const b = arr[j];

          // Если A доступнее, чем B, то A должен быть старее или равен по FIFO.
          // rank меньше = старее.
          if (a.access < b.access && a.rank > b.rank) {
            okAll = false;
            markSlot(a.slot, false);
            markSlot(b.slot, false);

            errors.push(
              "❌ Ошибка FIFO: «" + name + "».\n" +
              "В более доступном месте стоит более свежий торт: " +
              cakeLabel(a.cake) + " (" + slotPositionName(a.slot) + ").\n" +
              "Но есть более старый торт: " +
              cakeLabel(b.cake) + " (" + slotPositionName(b.slot) + ").\n" +
              "Старый торт должен продаваться первым."
            );
          }
        }
      }
    }

    return okAll;
  }

  function checkModeTier(errors) {
    let okAll = true;

    if (![2, 3, 4].includes(MODE)) return true;

    qsa(".showcase .slot").forEach(slot => {
      const cake = qs(".cake", slot);
      if (!cake) return;

      const ok = checkTierSlot(slot);

      if (!ok) {
        okAll = false;
        markSlot(slot, false);

        errors.push(
          "❌ Ошибка категории: «" + cakeName(cake) + "».\n" +
          "Стоит не на своей ценовой полке: " + slotPositionName(slot) + "."
        );
      }
    });

    return okAll;
  }

  function checkMode4Filled(errors) {
    if (MODE !== 4) return true;

    let okAll = true;

    qsa(".showcase .slot").forEach(slot => {
      const cake = qs(".cake", slot);

      if (!cake) {
        okAll = false;
        markSlot(slot, false);
        errors.push(
          "❌ Пустое место.\n" +
          "Нужно заполнить слот: " + slotPositionName(slot) + "."
        );
      }
    });

    return okAll;
  }

  function checkBasicShelfFIFO(errors) {
    let okAll = true;

    qsa(".showcase .shelf").forEach(shelf => {
      const slots = qsa(".slot", shelf);
      let shelfOk = true;

      // Проверяем только глубину:
      // если одинаковый торт есть спереди и сзади — спереди должен быть старее.
      const byName = new Map();

      for (const slot of slots) {
        const cake = qs(".cake", slot);
        if (!cake) continue;

        const name = cakeName(cake);
        if (!byName.has(name)) byName.set(name, []);
        byName.get(name).push({ slot, cake, rank: parseRank(cake) });
      }

      for (const [name, arr] of byName.entries()) {
        for (const front of arr.filter(x => [2, 3].includes(Number(x.slot.dataset.slot)))) {
          for (const back of arr.filter(x => [0, 1].includes(Number(x.slot.dataset.slot)))) {
            if (front.rank > back.rank) {
              shelfOk = false;
              okAll = false;

              markSlot(front.slot, false);
              markSlot(back.slot, false);

              errors.push(
                "❌ Ошибка FIFO по глубине: «" + name + "».\n" +
                "Сзади стоит более старый торт (" + cakeLabel(back.cake) + "), чем спереди (" + cakeLabel(front.cake) + ").\n" +
                "Старый торт должен стоять впереди."
              );
            }
          }
        }
      }

      const crossOk = checkShelfCrossRule(shelf, errors);

      if (!shelfOk || !crossOk) {
        markShelf(shelf, false);
      }
    });

    return okAll;
  }

  async function saveResultToDB(scorePercent, errorsCount) {
    try {
      await fetch("/save_result", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          mode: MODE,
          score_percent: scorePercent,
          errors_count: errorsCount,
          seed: GAME_SEED || null
        })
      });
    } catch (err) {
      console.error("save_result error:", err);
    }
  }

  async function doCheck() {
    clearMarks();

    const errors = [];

    const fillOk = checkMode4Filled(errors);
    const countOk = checkGlobalDuplicateLimit(errors);
    const fifoDepthOk = checkBasicShelfFIFO(errors);
    const fifoGlobalOk = checkSameCakeFIFO(errors);
    const tierOk = checkModeTier(errors);

    qsa(".showcase .shelf").forEach(shelf => {
      const bad = !!qs("." + CLS_BAD, shelf);
      markShelf(shelf, !bad);
    });

    qsa(".showcase .slot").forEach(slot => {
      const cake = qs(".cake", slot);

      if (!cake && MODE !== 4) return;

      if (!slot.classList.contains(CLS_BAD)) {
        markSlot(slot, true);
      }
    });

    const totalSlots = qsa(".showcase .slot").length;
    const badSlots = qsa(".showcase .slot." + CLS_BAD).length;
    const goodSlots = Math.max(0, totalSlots - badSlots);
    const percent = totalSlots ? Math.round((goodSlots / totalSlots) * 100) : 0;

    await saveResultToDB(percent, errors.length);

    if (errors.length === 0 && fillOk && countOk && fifoDepthOk && fifoGlobalOk && tierOk) {
      showResult("✅ Отлично! Всё правильно.\nРезультат: " + percent + "%");
      return;
    }

    const limitedErrors = errors.slice(0, 8);
    const more = errors.length > 8 ? "\n\nИ ещё ошибок: " + (errors.length - 8) : "";

    showResult(
      "Результат: " + percent + "%\n" +
      "Ошибок: " + errors.length + "\n\n" +
      limitedErrors.join("\n\n") +
      more
    );
  }

  // ---------- TIMER ----------
  function timerSecondsByMode() {
    if (MODE === 1) return 180;
    if (MODE === 2) return 300;
    if (MODE === 3) return 360;
    if (MODE === 4) return 420;
    return 300;
  }

  function formatTime(sec) {
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return String(m).padStart(2, "0") + ":" + String(s).padStart(2, "0");
  }

  function startTimer() {
    if (!timerBox) return;

    if (timerInterval) {
      clearInterval(timerInterval);
      timerInterval = null;
    }

    timerSeconds = timerSecondsByMode();
    timerBox.textContent = "⏱ " + formatTime(timerSeconds);
    timerBox.classList.add("timer-active");

    timerInterval = setInterval(() => {
      timerSeconds--;
      timerBox.textContent = "⏱ " + formatTime(timerSeconds);

      if (timerSeconds <= 0) {
        clearInterval(timerInterval);
        timerInterval = null;
        timerBox.classList.remove("timer-active");
        showResult("⏰ Время вышло! Нажми «Проверить», чтобы увидеть результат.");
      }
    }, 1000);
  }

  if (btnTimer) btnTimer.addEventListener("click", startTimer);
  if (btnCheck) btnCheck.addEventListener("click", doCheck);
  if (btnClear) btnClear.addEventListener("click", clearMarks);

  qsa(".showcase .slot").forEach(ensureEmpty);
})();
