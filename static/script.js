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

    resultText.textContent = msg;
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

  // ---------- drag ----------
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
    if (!slot) return;

    e.preventDefault();

    if (e.dataTransfer) {
      e.dataTransfer.dropEffect = "move";
    }
  });

  document.addEventListener("drop", (e) => {
    const targetSlot = closestSlot(e.target);
    if (!targetSlot) return;

    e.preventDefault();

    if (!draggedCake) return;

    if (MODE === 4 && fromFreezer) {
      if (slotHasCake(targetSlot)) return;

      removeEmpty(targetSlot);
      targetSlot.appendChild(draggedCake);
      return;
    }

    if (MODE !== 4 && fromFreezer) return;

    if (fromSlot && fromSlot === targetSlot) return;

    const targetCake = qs(".cake", targetSlot);

    if (!targetCake) {
      removeEmpty(targetSlot);
      targetSlot.appendChild(draggedCake);

      if (fromSlot) ensureEmpty(fromSlot);
      return;
    }

    if (fromSlot) {
      targetSlot.appendChild(draggedCake);
      fromSlot.appendChild(targetCake);
    }
  });

  // ---------- check helpers ----------
  function parseRank(cakeEl) {
    const r = Number(cakeEl?.dataset?.rank);
    return Number.isFinite(r) ? r : 999999;
  }

  function getTier(cakeEl) {
    return (cakeEl?.dataset?.tier ?? "").toString();
  }

  function getExpectedTier(slotEl) {
    return (slotEl?.dataset?.expectedTier ?? "").toString();
  }

  function checkFIFOinShelf(shelfEl) {
    const slots = qsa(".slot", shelfEl);
    const perSlot = new Map();

    let last = -Infinity;
    let okAll = true;

    for (const slot of slots) {
      const cake = qs(".cake", slot);
      if (!cake) continue;

      const r = parseRank(cake);
      const ok = r >= last;

      perSlot.set(slot, ok);

      if (!ok) okAll = false;

      last = Math.max(last, r);
    }

    return {
      ok: okAll,
      perSlot: perSlot
    };
  }

  function checkTierInShelf(shelfEl) {
    const slots = qsa(".slot", shelfEl);
    const perSlot = new Map();

    let okAll = true;

    for (const slot of slots) {
      const cake = qs(".cake", slot);
      if (!cake) continue;

      const expected = getExpectedTier(slot);

      if (!expected) {
        perSlot.set(slot, true);
        continue;
      }

      const ok = getTier(cake) === expected;

      perSlot.set(slot, ok);

      if (!ok) okAll = false;
    }

    return {
      ok: okAll,
      perSlot: perSlot
    };
  }

  function isSlotCorrectByMode(slot, fifo, tier) {
    const hasCake = !!qs(".cake", slot);

    if (!hasCake) {
      return MODE !== 4;
    }

    if (MODE === 1) {
      return fifo.perSlot.get(slot) ?? true;
    }

    if (MODE === 2) {
      return (fifo.perSlot.get(slot) ?? true) && (tier.perSlot.get(slot) ?? true);
    }

    if (MODE === 3) {
      return (fifo.perSlot.get(slot) ?? true) && (tier.perSlot.get(slot) ?? true);
    }

    if (MODE === 4) {
      return (fifo.perSlot.get(slot) ?? true) && (tier.perSlot.get(slot) ?? true);
    }

    return true;
  }

  function isShelfCorrectByMode(shelf, fifo, tier) {
    const hasEmpty = qsa(".slot", shelf).some(slot => !qs(".cake", slot));

    if (MODE === 1) {
      return fifo.ok;
    }

    if (MODE === 2) {
      return fifo.ok && tier.ok;
    }

    if (MODE === 3) {
      return fifo.ok && tier.ok;
    }

    if (MODE === 4) {
      return !hasEmpty && fifo.ok && tier.ok;
    }

    return true;
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

    const shelves = qsa(".showcase .shelf");

    let totalSlots = 0;
    let goodSlots = 0;
    let errorsCount = 0;
    let emptyErrors = 0;

    for (const shelf of shelves) {
      const fifo = checkFIFOinShelf(shelf);
      const tier = checkTierInShelf(shelf);
      const slots = qsa(".slot", shelf);

      for (const slot of slots) {
        const cake = qs(".cake", slot);

        if (!cake && MODE === 4) {
          totalSlots++;
          errorsCount++;
          emptyErrors++;
          markSlot(slot, false);
          continue;
        }

        if (!cake) continue;

        totalSlots++;

        const ok = isSlotCorrectByMode(slot, fifo, tier);

        if (ok) goodSlots++;
        else errorsCount++;

        markSlot(slot, ok);
      }

      const anyCake = !!qs(".cake", shelf);
      if (anyCake || MODE === 4) {
        const shelfOk = isShelfCorrectByMode(shelf, fifo, tier);
        markShelf(shelf, shelfOk);
      }
    }

    const percent = totalSlots ? Math.round((goodSlots / totalSlots) * 100) : 0;

    await saveResultToDB(percent, errorsCount);

    if (MODE === 4 && emptyErrors > 0) {
      showResult(
        "❌ Есть пустые места: " +
        emptyErrors +
        ". Заполни витрину и проверь FIFO + ценовую категорию. Результат: " +
        percent +
        "%"
      );
      return;
    }

    if (percent >= 90) {
      showResult("✅ Отлично! Правильно: " + percent + "%");
    } else if (percent >= 70) {
      showResult("🟡 Неплохо! Правильно: " + percent + "% (есть ошибки)");
    } else {
      showResult("❌ Пока плохо: " + percent + "%. Исправь подсвеченные места.");
    }
  }

  // ---------- timer ----------
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

  if (btnTimer) {
    btnTimer.addEventListener("click", startTimer);
  }

  if (btnCheck) {
    btnCheck.addEventListener("click", doCheck);
  }

  if (btnClear) {
    btnClear.addEventListener("click", clearMarks);
  }

  qsa(".showcase .slot").forEach(ensureEmpty);
})();
