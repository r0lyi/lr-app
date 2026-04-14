(function () {
  const MONTHS = [
    "Enero",
    "Febrero",
    "Marzo",
    "Abril",
    "Mayo",
    "Junio",
    "Julio",
    "Agosto",
    "Septiembre",
    "Octubre",
    "Noviembre",
    "Diciembre",
  ];

  function parseIsoDate(value) {
    if (!value) {
      return null;
    }

    const parts = value.split("-");
    if (parts.length !== 3) {
      return null;
    }

    const year = Number(parts[0]);
    const month = Number(parts[1]) - 1;
    const day = Number(parts[2]);
    const date = new Date(year, month, day);

    if (
      Number.isNaN(date.getTime()) ||
      date.getFullYear() !== year ||
      date.getMonth() !== month ||
      date.getDate() !== day
    ) {
      return null;
    }

    return date;
  }

  function formatIsoDate(date) {
    const year = String(date.getFullYear());
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
  }

  function formatDisplayDate(date) {
    const day = String(date.getDate()).padStart(2, "0");
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const year = date.getFullYear();
    return `${day}/${month}/${year}`;
  }

  function getUtcDayTimestamp(date) {
    return Date.UTC(date.getFullYear(), date.getMonth(), date.getDate());
  }

  function getMondayFirstIndex(date) {
    return (date.getDay() + 6) % 7;
  }

  function getTotalDaysInMonth(year, monthIndex) {
    return new Date(year, monthIndex + 1, 0).getDate();
  }

  function buildYearOptions(selectEl, centerYear) {
    if (!selectEl) {
      return;
    }

    const currentValue = Number(selectEl.value);
    const shouldRebuild =
      !selectEl.options.length ||
      centerYear <= Number(selectEl.options[0].value) + 1 ||
      centerYear >= Number(selectEl.options[selectEl.options.length - 1].value) - 1 ||
      !Array.from(selectEl.options).some((option) => Number(option.value) === centerYear);

    if (!shouldRebuild) {
      if (!Number.isNaN(currentValue)) {
        selectEl.value = String(currentValue);
      }
      return;
    }

    selectEl.innerHTML = "";
    for (let year = centerYear - 8; year <= centerYear + 8; year += 1) {
      const option = document.createElement("option");
      option.value = String(year);
      option.textContent = String(year);
      selectEl.appendChild(option);
    }
  }

  function initializeCalendar(root) {
    const inputId = root.dataset.inputId;
    const inputEl = document.getElementById(inputId);
    const monthSelect = root.querySelector("[data-calendar-month]");
    const yearSelect = root.querySelector("[data-calendar-year]");
    const prevButton = root.querySelector("[data-calendar-prev]");
    const nextButton = root.querySelector("[data-calendar-next]");
    const daysContainer = root.querySelector("[data-calendar-days]");
    const selectionText = root.querySelector("[data-calendar-selection]");

    if (!inputEl || !monthSelect || !yearSelect || !prevButton || !nextButton || !daysContainer) {
      return null;
    }

    monthSelect.innerHTML = "";
    MONTHS.forEach(function (monthName, index) {
      const option = document.createElement("option");
      option.value = String(index);
      option.textContent = monthName;
      monthSelect.appendChild(option);
    });

    const selectedDate = parseIsoDate(inputEl.value);
    const baseDate = selectedDate || new Date();
    const state = {
      inputEl: inputEl,
      monthSelect: monthSelect,
      yearSelect: yearSelect,
      prevButton: prevButton,
      nextButton: nextButton,
      daysContainer: daysContainer,
      selectionText: selectionText,
      selectedDate: selectedDate,
      viewDate: new Date(baseDate.getFullYear(), baseDate.getMonth(), 1),
    };

    function renderDays() {
      const year = state.viewDate.getFullYear();
      const monthIndex = state.viewDate.getMonth();
      const firstDay = new Date(year, monthIndex, 1);
      const leadingEmpty = getMondayFirstIndex(firstDay);
      const totalDays = getTotalDaysInMonth(year, monthIndex);
      const totalCells = Math.ceil((leadingEmpty + totalDays) / 7) * 7;

      state.daysContainer.innerHTML = "";

      for (let index = 0; index < totalCells; index += 1) {
        if (index < leadingEmpty || index >= leadingEmpty + totalDays) {
          const emptyCell = document.createElement("span");
          emptyCell.className = "vac-calendar__day--empty";
          state.daysContainer.appendChild(emptyCell);
          continue;
        }

        const dayNumber = index - leadingEmpty + 1;
        const cellDate = new Date(year, monthIndex, dayNumber);
        const button = document.createElement("button");
        const isToday =
          formatIsoDate(cellDate) === formatIsoDate(new Date());
        const isSelected =
          state.selectedDate && formatIsoDate(state.selectedDate) === formatIsoDate(cellDate);

        button.type = "button";
        button.className = "vac-calendar__day";
        if (isToday) {
          button.classList.add("vac-calendar__day--today");
        }
        if (isSelected) {
          button.classList.add("vac-calendar__day--selected");
          button.setAttribute("aria-pressed", "true");
        } else {
          button.setAttribute("aria-pressed", "false");
        }

        button.textContent = String(dayNumber);
        button.addEventListener("click", function () {
          state.selectedDate = cellDate;
          state.inputEl.value = formatIsoDate(cellDate);
          render();
          document.dispatchEvent(new CustomEvent("vacation-request:dates-changed"));
        });

        state.daysContainer.appendChild(button);
      }
    }

    function render() {
      buildYearOptions(state.yearSelect, state.viewDate.getFullYear());
      state.monthSelect.value = String(state.viewDate.getMonth());
      state.yearSelect.value = String(state.viewDate.getFullYear());

      if (state.selectionText) {
        state.selectionText.textContent = state.selectedDate
          ? formatDisplayDate(state.selectedDate)
          : "Sin seleccionar";
      }

      renderDays();
    }

    state.prevButton.addEventListener("click", function () {
      state.viewDate = new Date(state.viewDate.getFullYear(), state.viewDate.getMonth() - 1, 1);
      render();
    });

    state.nextButton.addEventListener("click", function () {
      state.viewDate = new Date(state.viewDate.getFullYear(), state.viewDate.getMonth() + 1, 1);
      render();
    });

    state.monthSelect.addEventListener("change", function () {
      state.viewDate = new Date(state.viewDate.getFullYear(), Number(state.monthSelect.value), 1);
      render();
    });

    state.yearSelect.addEventListener("change", function () {
      state.viewDate = new Date(Number(state.yearSelect.value), state.viewDate.getMonth(), 1);
      render();
    });

    render();
    return state;
  }

  const calendarRoots = Array.from(document.querySelectorAll("[data-calendar]"));
  const calendars = calendarRoots.map(initializeCalendar).filter(Boolean);
  if (!calendars.length) {
    return;
  }

  const annualCounterRoot = document.querySelector("[data-vacation-annual-counter]");
  const annualCounterValue = document.getElementById("annual-vacation-remaining-days");
  const annualDaysTotalRaw = annualCounterRoot
    ? annualCounterRoot.dataset.annualDaysTotal || ""
    : "";
  const annualDaysTotal = annualDaysTotalRaw
    ? Number(annualDaysTotalRaw.replace(",", "."))
    : Number.NaN;
  const startInput = document.getElementById("id_start_date");
  const endInput = document.getElementById("id_end_date");
  const selectedDaysCounter = document.getElementById("selected-days-counter");
  const selectedRangeSummary = document.getElementById("selected-range-summary");
  const submitButton = document.getElementById("submit-request-button");

  function formatDayCount(value) {
    if (!Number.isFinite(value)) {
      return "0.00";
    }

    return value.toFixed(2);
  }

  function updateAnnualDaysCounter(selectedDays) {
    if (!annualCounterValue || !Number.isFinite(annualDaysTotal)) {
      return;
    }

    const remainingDays = annualDaysTotal - selectedDays;
    annualCounterValue.textContent = formatDayCount(Math.max(0, remainingDays));
    annualCounterValue.classList.toggle(
      "vac-request-summary-value--warning",
      remainingDays < 0
    );
  }

  function updateSummary() {
    const startDate = parseIsoDate(startInput ? startInput.value : "");
    const endDate = parseIsoDate(endInput ? endInput.value : "");

    if (!selectedDaysCounter || !selectedRangeSummary || !submitButton) {
      return;
    }

    selectedRangeSummary.classList.remove("is-invalid");

    if (!startDate && !endDate) {
      selectedDaysCounter.textContent = "0";
      selectedRangeSummary.textContent = "Aun no has seleccionado ambas fechas";
      submitButton.disabled = true;
      updateAnnualDaysCounter(0);
      return;
    }

    if (startDate && !endDate) {
      selectedDaysCounter.textContent = "0";
      selectedRangeSummary.textContent = `Inicio: ${formatDisplayDate(startDate)}. Falta la fecha final`;
      submitButton.disabled = true;
      updateAnnualDaysCounter(0);
      return;
    }

    if (!startDate && endDate) {
      selectedDaysCounter.textContent = "0";
      selectedRangeSummary.textContent = `Final: ${formatDisplayDate(endDate)}. Falta la fecha inicial`;
      submitButton.disabled = true;
      updateAnnualDaysCounter(0);
      return;
    }

    if (endDate < startDate) {
      selectedDaysCounter.textContent = "0";
      selectedRangeSummary.textContent = "La fecha final debe ser igual o posterior a la inicial";
      selectedRangeSummary.classList.add("is-invalid");
      submitButton.disabled = true;
      updateAnnualDaysCounter(0);
      return;
    }

    const millisecondsPerDay = 1000 * 60 * 60 * 24;
    const totalSelectedDays =
      Math.round(
        (getUtcDayTimestamp(endDate) - getUtcDayTimestamp(startDate)) /
          millisecondsPerDay
      ) + 1;

    selectedDaysCounter.textContent = String(totalSelectedDays);
    updateAnnualDaysCounter(totalSelectedDays);

    const remainingDays = annualDaysTotal - totalSelectedDays;
    if (Number.isFinite(annualDaysTotal) && remainingDays < 0) {
      selectedRangeSummary.textContent = `La seleccion supera tu derecho anual disponible en ${formatDayCount(Math.abs(remainingDays))} dias.`;
      selectedRangeSummary.classList.add("is-invalid");
      submitButton.disabled = true;
      return;
    }

    selectedRangeSummary.textContent = `${formatDisplayDate(startDate)} - ${formatDisplayDate(endDate)}`;
    submitButton.disabled = false;
  }

  document.addEventListener("vacation-request:dates-changed", updateSummary);
  updateSummary();
})();
