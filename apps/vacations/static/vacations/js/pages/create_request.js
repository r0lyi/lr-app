(function () {
  const gettext =
    typeof window.gettext === "function" ? window.gettext : (message) => message;
  const interpolate =
    typeof window.interpolate === "function"
      ? window.interpolate
      : function (format, values, named) {
          if (named) {
            return format.replace(/%\((\w+)\)s/g, function (match, key) {
              return Object.prototype.hasOwnProperty.call(values, key)
                ? values[key]
                : match;
            });
          }

          var index = 0;
          return format.replace(/%s/g, function (match) {
            if (!Array.isArray(values) || index >= values.length) {
              return match;
            }
            var value = values[index];
            index += 1;
            return value;
          });
        };

  const UNSELECTED_LABEL = gettext("Sin seleccionar");
  const PENDING_LABEL = gettext("Pendiente");
  const SELECT_BOTH_DATES_LABEL = gettext("Selecciona ambas fechas en el calendario.");
  const SELECT_END_DATE_LABEL = gettext("Elige la fecha de fin para completar el periodo.");
  const SELECT_START_DATE_LABEL = gettext("Elige la fecha de inicio para completar el periodo.");
  const END_DATE_AFTER_START_LABEL = gettext("La fecha final debe ser igual o posterior a la inicial.");
  const START_SELECTED_LABEL = gettext("Inicio: %(date)s");
  const COMPLETE_RANGE_LABEL = gettext("%(start)s - %(end)s");
  const SELECT_DATE_LABEL = gettext("Seleccionar %(date)s");
  const MONTHS = [
    gettext("Enero"),
    gettext("Febrero"),
    gettext("Marzo"),
    gettext("Abril"),
    gettext("Mayo"),
    gettext("Junio"),
    gettext("Julio"),
    gettext("Agosto"),
    gettext("Septiembre"),
    gettext("Octubre"),
    gettext("Noviembre"),
    gettext("Diciembre"),
  ];

  const SHORT_MONTHS = [
    gettext("ene"),
    gettext("feb"),
    gettext("mar"),
    gettext("abr"),
    gettext("may"),
    gettext("jun"),
    gettext("jul"),
    gettext("ago"),
    gettext("sep"),
    gettext("oct"),
    gettext("nov"),
    gettext("dic"),
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

  function formatBadgeDate(date) {
    const day = String(date.getDate()).padStart(2, "0");
    const month = SHORT_MONTHS[date.getMonth()];
    const year = date.getFullYear();
    return `${day} ${month} ${year}`;
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

  function isSameDate(firstDate, secondDate) {
    return (
      firstDate &&
      secondDate &&
      firstDate.getFullYear() === secondDate.getFullYear() &&
      firstDate.getMonth() === secondDate.getMonth() &&
      firstDate.getDate() === secondDate.getDate()
    );
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

  const startInput = document.getElementById("id_start_date");
  const endInput = document.getElementById("id_end_date");
  const rangeCalendarRoot = document.querySelector("[data-range-calendar]");
  const annualCounterRoot = document.querySelector("[data-vacation-annual-counter]");
  const annualCounterValue = document.getElementById("annual-vacation-remaining-days");
  const annualDaysTotalRaw = annualCounterRoot
    ? annualCounterRoot.dataset.annualDaysTotal || ""
    : "";
  const annualDaysTotal = annualDaysTotalRaw
    ? Number(annualDaysTotalRaw.replace(",", "."))
    : Number.NaN;
  const selectedStartSummary = document.getElementById("selected-start-summary");
  const selectedEndSummary = document.getElementById("selected-end-summary");
  const selectedDaysCounter = document.getElementById("selected-days-counter");
  const selectedRangeSummary = document.getElementById("selected-range-summary");
  const submitButton = document.getElementById("submit-request-button");

  if (!startInput || !endInput || !rangeCalendarRoot) {
    return;
  }

  function formatDayCount(value) {
    if (!Number.isFinite(value)) {
      return "0";
    }

    if (Number.isInteger(value)) {
      return String(value);
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
    const startDate = parseIsoDate(startInput.value);
    const endDate = parseIsoDate(endInput.value);

    if (
      !selectedDaysCounter ||
      !selectedRangeSummary ||
      !submitButton ||
      !selectedStartSummary ||
      !selectedEndSummary
    ) {
      return;
    }

    selectedRangeSummary.classList.remove("is-invalid");
    selectedStartSummary.textContent = UNSELECTED_LABEL;
    selectedEndSummary.textContent = UNSELECTED_LABEL;

    if (!startDate && !endDate) {
      selectedDaysCounter.textContent = "0";
      selectedRangeSummary.textContent = SELECT_BOTH_DATES_LABEL;
      submitButton.disabled = true;
      updateAnnualDaysCounter(0);
      return;
    }

    if (startDate && !endDate) {
      selectedDaysCounter.textContent = "0";
      selectedStartSummary.textContent = formatDisplayDate(startDate);
      selectedEndSummary.textContent = PENDING_LABEL;
      selectedRangeSummary.textContent = SELECT_END_DATE_LABEL;
      submitButton.disabled = true;
      updateAnnualDaysCounter(0);
      return;
    }

    if (!startDate && endDate) {
      selectedDaysCounter.textContent = "0";
      selectedStartSummary.textContent = PENDING_LABEL;
      selectedEndSummary.textContent = formatDisplayDate(endDate);
      selectedRangeSummary.textContent = SELECT_START_DATE_LABEL;
      submitButton.disabled = true;
      updateAnnualDaysCounter(0);
      return;
    }

    selectedStartSummary.textContent = formatDisplayDate(startDate);
    selectedEndSummary.textContent = formatDisplayDate(endDate);

    if (endDate < startDate) {
      selectedDaysCounter.textContent = "0";
      selectedRangeSummary.textContent = END_DATE_AFTER_START_LABEL;
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
      selectedRangeSummary.textContent = interpolate(
        gettext("La selección supera tu saldo disponible en %(days)s días."),
        { days: formatDayCount(Math.abs(remainingDays)) },
        true
      );
      selectedRangeSummary.classList.add("is-invalid");
      submitButton.disabled = true;
      return;
    }

    selectedRangeSummary.textContent = interpolate(
      COMPLETE_RANGE_LABEL,
      {
        start: formatDisplayDate(startDate),
        end: formatDisplayDate(endDate),
      },
      true
    );
    submitButton.disabled = false;
  }

  function initializeRangeCalendar(root) {
    const monthSelect = root.querySelector("[data-calendar-month]");
    const yearSelect = root.querySelector("[data-calendar-year]");
    const prevButton = root.querySelector("[data-calendar-prev]");
    const nextButton = root.querySelector("[data-calendar-next]");
    const daysContainer = root.querySelector("[data-calendar-days]");
    const selectionText = root.querySelector("[data-calendar-selection]");
    const rangeStartDisplay = root.querySelector("[data-range-start-display]");
    const rangeEndDisplay = root.querySelector("[data-range-end-display]");

    if (!monthSelect || !yearSelect || !prevButton || !nextButton || !daysContainer) {
      return null;
    }

    monthSelect.innerHTML = "";
    MONTHS.forEach(function (monthName, index) {
      const option = document.createElement("option");
      option.value = String(index);
      option.textContent = monthName;
      monthSelect.appendChild(option);
    });

    const minDate = parseIsoDate(root.dataset.minDate || "");
    const initialStartDate = parseIsoDate(startInput.value);
    const initialEndDate = parseIsoDate(endInput.value);
    const baseDate = initialStartDate || initialEndDate || minDate || new Date();
    const state = {
      minDate: minDate,
      hoverDate: null,
      viewDate: new Date(baseDate.getFullYear(), baseDate.getMonth(), 1),
      render: null,
    };

    function getCurrentRange() {
      const startDate = parseIsoDate(startInput.value);
      const endDate = parseIsoDate(endInput.value);

      if (startDate && endDate && endDate >= startDate) {
        return {
          startDate: startDate,
          endDate: endDate,
          isPreview: false,
        };
      }

      if (startDate && !endDate && state.hoverDate && state.hoverDate >= startDate) {
        return {
          startDate: startDate,
          endDate: state.hoverDate,
          isPreview: true,
        };
      }

      return {
        startDate: startDate,
        endDate: null,
        isPreview: false,
      };
    }

    function shouldSelectEndNext() {
      return Boolean(parseIsoDate(startInput.value) && !parseIsoDate(endInput.value));
    }

    function updateSelectionLabels() {
      const startDate = parseIsoDate(startInput.value);
      const endDate = parseIsoDate(endInput.value);

      if (rangeStartDisplay) {
        rangeStartDisplay.textContent = startDate
          ? formatBadgeDate(startDate)
          : UNSELECTED_LABEL;
      }

      if (rangeEndDisplay) {
        rangeEndDisplay.textContent = endDate
          ? formatBadgeDate(endDate)
          : UNSELECTED_LABEL;
      }

      if (!selectionText) {
        return;
      }

      if (startDate && endDate && endDate >= startDate) {
        selectionText.textContent = interpolate(
          COMPLETE_RANGE_LABEL,
          {
            start: formatBadgeDate(startDate),
            end: formatBadgeDate(endDate),
          },
          true
        );
        return;
      }

      if (startDate) {
        selectionText.textContent = interpolate(
          START_SELECTED_LABEL,
          { date: formatBadgeDate(startDate) },
          true
        );
        return;
      }

      selectionText.textContent = UNSELECTED_LABEL;
    }

    function selectDate(cellDate) {
      const startDate = parseIsoDate(startInput.value);
      const endDate = parseIsoDate(endInput.value);

      if (!startDate || endDate) {
        startInput.value = formatIsoDate(cellDate);
        endInput.value = "";
      } else if (cellDate < startDate) {
        startInput.value = formatIsoDate(cellDate);
        endInput.value = "";
      } else {
        endInput.value = formatIsoDate(cellDate);
      }

      state.hoverDate = null;
      render();
      updateSummary();
    }

    function renderDays() {
      const year = state.viewDate.getFullYear();
      const monthIndex = state.viewDate.getMonth();
      const firstDay = new Date(year, monthIndex, 1);
      const leadingEmpty = getMondayFirstIndex(firstDay);
      const totalDays = getTotalDaysInMonth(year, monthIndex);
      const totalCells = Math.ceil((leadingEmpty + totalDays) / 7) * 7;
      const range = getCurrentRange();
      const startTimestamp = range.startDate ? getUtcDayTimestamp(range.startDate) : null;
      const endTimestamp = range.endDate ? getUtcDayTimestamp(range.endDate) : null;

      daysContainer.innerHTML = "";

      for (let index = 0; index < totalCells; index += 1) {
        if (index < leadingEmpty || index >= leadingEmpty + totalDays) {
          const emptyCell = document.createElement("span");
          emptyCell.className = "vac-calendar__day--empty";
          daysContainer.appendChild(emptyCell);
          continue;
        }

        const dayNumber = index - leadingEmpty + 1;
        const cellDate = new Date(year, monthIndex, dayNumber);
        const cellTimestamp = getUtcDayTimestamp(cellDate);
        const button = document.createElement("button");
        const isToday = isSameDate(cellDate, new Date());
        const isStart = isSameDate(cellDate, range.startDate);
        const isEnd = isSameDate(cellDate, range.endDate);
        const isInRange =
          startTimestamp !== null &&
          endTimestamp !== null &&
          cellTimestamp > startTimestamp &&
          cellTimestamp < endTimestamp;
        const isDisabled = state.minDate && cellDate < state.minDate;

        button.type = "button";
        button.className = "vac-calendar__day";
        if (isToday) {
          button.classList.add("vac-calendar__day--today");
        }
        if (isInRange) {
          button.classList.add("vac-calendar__day--in-range");
        }
        if (range.isPreview && (isInRange || isEnd)) {
          button.classList.add("vac-calendar__day--preview");
        }
        if (isStart) {
          button.classList.add(
            "vac-calendar__day--selected",
            "vac-calendar__day--range-start"
          );
        }
        if (isEnd) {
          button.classList.add(
            "vac-calendar__day--selected",
            "vac-calendar__day--range-end"
          );
        }
        if (isDisabled) {
          button.classList.add("vac-calendar__day--disabled");
          button.disabled = true;
          button.setAttribute("aria-disabled", "true");
        } else {
          button.setAttribute("aria-disabled", "false");
          button.addEventListener("mouseenter", function () {
            if (
              shouldSelectEndNext() &&
              cellDate >= parseIsoDate(startInput.value) &&
              !isSameDate(state.hoverDate, cellDate)
            ) {
              state.hoverDate = cellDate;
              render();
            }
          });
          button.addEventListener("click", function () {
            selectDate(cellDate);
          });
        }

        button.setAttribute("aria-pressed", isStart || isEnd ? "true" : "false");
        button.setAttribute(
          "aria-label",
          interpolate(SELECT_DATE_LABEL, { date: formatDisplayDate(cellDate) }, true)
        );
        button.title = formatDisplayDate(cellDate);
        button.textContent = String(dayNumber);
        daysContainer.appendChild(button);
      }
    }

    function render() {
      buildYearOptions(yearSelect, state.viewDate.getFullYear());
      monthSelect.value = String(state.viewDate.getMonth());
      yearSelect.value = String(state.viewDate.getFullYear());
      root.classList.toggle("is-selecting-end", shouldSelectEndNext());
      updateSelectionLabels();
      renderDays();
    }

    state.render = render;

    prevButton.addEventListener("click", function () {
      state.viewDate = new Date(state.viewDate.getFullYear(), state.viewDate.getMonth() - 1, 1);
      state.hoverDate = null;
      render();
    });

    nextButton.addEventListener("click", function () {
      state.viewDate = new Date(state.viewDate.getFullYear(), state.viewDate.getMonth() + 1, 1);
      state.hoverDate = null;
      render();
    });

    monthSelect.addEventListener("change", function () {
      state.viewDate = new Date(state.viewDate.getFullYear(), Number(monthSelect.value), 1);
      state.hoverDate = null;
      render();
    });

    yearSelect.addEventListener("change", function () {
      state.viewDate = new Date(Number(yearSelect.value), state.viewDate.getMonth(), 1);
      state.hoverDate = null;
      render();
    });

    daysContainer.addEventListener("mouseleave", function () {
      if (state.hoverDate) {
        state.hoverDate = null;
        render();
      }
    });

    render();
    return state;
  }

  const rangeCalendar = initializeRangeCalendar(rangeCalendarRoot);
  if (!rangeCalendar) {
    return;
  }

  updateSummary();
})();
