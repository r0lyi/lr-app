"""Capa de revision previa para solicitudes visibles antes de exportar."""

from collections import defaultdict
from datetime import date
from decimal import Decimal

from apps.vacations.models import VacationRequest
from apps.vacations.services.policies import (
    ACTIVE_REQUEST_STATUS_NAMES,
    HIGH_LOAD_PERIODS,
    LONG_DURATION_VACATION_DAYS,
)


def build_rrhh_export_review(vacation_requests):
    """Enriquece el listado de RRHH con orden y avisos previos a exportar."""

    reviewed_requests = sorted(
        list(vacation_requests),
        key=_get_seniority_sort_key,
    )
    overlap_counts = _get_department_overlap_counts(reviewed_requests)

    summary = {
        "department_overlap_requests_count": 0,
        "high_load_requests_count": 0,
        "long_duration_requests_count": 0,
    }

    for vacation_request in reviewed_requests:
        overlap_count = overlap_counts.get(vacation_request.pk, 0)
        high_load_labels = _get_high_load_period_labels(
            vacation_request.start_date,
            vacation_request.end_date,
        )
        is_long_duration = _normalize_requested_days(
            vacation_request.requested_days
        ) == LONG_DURATION_VACATION_DAYS

        vacation_request.department_overlap_employees_count = overlap_count
        vacation_request.high_load_period_labels = high_load_labels
        vacation_request.is_high_load_period = bool(high_load_labels)
        vacation_request.is_long_duration = is_long_duration
        vacation_request.export_review_observations = _build_request_observations(
            overlap_count,
            high_load_labels,
            is_long_duration,
        )

        if overlap_count:
            summary["department_overlap_requests_count"] += 1
        if high_load_labels:
            summary["high_load_requests_count"] += 1
        if is_long_duration:
            summary["long_duration_requests_count"] += 1

    return {
        "vacation_requests": reviewed_requests,
        "summary": summary,
    }


def _get_seniority_sort_key(vacation_request):
    return (
        vacation_request.employee.hire_date,
        vacation_request.start_date,
        vacation_request.request_date,
        vacation_request.pk,
    )


def _get_department_overlap_counts(vacation_requests):
    department_ids = {
        vacation_request.employee.department_id
        for vacation_request in vacation_requests
        if vacation_request.employee.department_id is not None
    }
    if not department_ids:
        return {}

    active_requests = (
        VacationRequest.objects.select_related("employee", "employee__department")
        .filter(
            employee__department_id__in=department_ids,
            status__name__in=ACTIVE_REQUEST_STATUS_NAMES,
        )
        .order_by("employee__department_id", "start_date", "id")
    )

    requests_by_department = defaultdict(list)
    for active_request in active_requests:
        requests_by_department[active_request.employee.department_id].append(
            active_request
        )

    overlap_counts = {}
    for vacation_request in vacation_requests:
        department_id = vacation_request.employee.department_id
        if department_id is None:
            overlap_counts[vacation_request.pk] = 0
            continue

        overlapping_employee_ids = {
            other_request.employee_id
            for other_request in requests_by_department.get(department_id, [])
            if other_request.employee_id != vacation_request.employee_id
            and _date_ranges_overlap(
                vacation_request.start_date,
                vacation_request.end_date,
                other_request.start_date,
                other_request.end_date,
            )
        }
        overlap_counts[vacation_request.pk] = len(overlapping_employee_ids)

    return overlap_counts


def _build_request_observations(overlap_count, high_load_labels, is_long_duration):
    observations = []

    if overlap_count:
        suffix = "" if overlap_count == 1 else "s"
        observations.append(f"Coincide con {overlap_count} empleado{suffix}")

    for period_label in high_load_labels:
        observations.append(f"Alta carga: {period_label}")

    if is_long_duration:
        observations.append("Larga duracion")

    return observations


def _normalize_requested_days(requested_days):
    return Decimal(str(requested_days)).quantize(Decimal("0.00"))


def _get_high_load_period_labels(start_date, end_date):
    matched_labels = []

    for period_label, period_start, period_end in HIGH_LOAD_PERIODS:
        if _request_overlaps_high_load_period(
            start_date,
            end_date,
            period_start=period_start,
            period_end=period_end,
        ):
            matched_labels.append(period_label)

    return matched_labels


def _request_overlaps_high_load_period(
    start_date,
    end_date,
    *,
    period_start,
    period_end,
):
    for year in range(start_date.year - 1, end_date.year + 1):
        period_start_date, period_end_date = _build_period_window(
            year,
            period_start=period_start,
            period_end=period_end,
        )
        if _date_ranges_overlap(
            start_date,
            end_date,
            period_start_date,
            period_end_date,
        ):
            return True

    return False


def _build_period_window(year, *, period_start, period_end):
    start_month, start_day = period_start
    end_month, end_day = period_end

    period_start_date = date(year, start_month, start_day)
    if end_month < start_month:
        period_end_date = date(year + 1, end_month, end_day)
    else:
        period_end_date = date(year, end_month, end_day)

    return period_start_date, period_end_date


def _date_ranges_overlap(first_start, first_end, second_start, second_end):
    return first_start <= second_end and second_start <= first_end
