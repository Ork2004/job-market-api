import pytest

from app.analytics.salary import InvalidGroupByField, salary_stats_by

ROWS = [
    {
        "id": 1,
        "location": "Moscow",
        "employment_type": "Full time",
        "company": "Acme",
        "currency": "RUR",
        "salary_min": 100_000,
        "salary_max": 150_000,
    },
    {
        "id": 2,
        "location": "Moscow",
        "employment_type": "Full time",
        "company": "Beta",
        "currency": "RUR",
        "salary_min": 150_000,
        "salary_max": 200_000,
    },
    {
        "id": 3,
        "location": "Remote",
        "employment_type": "Full time",
        "company": "Acme",
        "currency": "USD",
        "salary_min": 2_000,
        "salary_max": None,
    },
    {
        # No salary info at all -- must be excluded, not counted as zero.
        "id": 4,
        "location": "Moscow",
        "employment_type": "Full time",
        "company": "Gamma",
        "currency": "RUR",
        "salary_min": None,
        "salary_max": None,
    },
]


def test_groups_by_field_and_currency_separately() -> None:
    result = salary_stats_by(ROWS, "location")

    by_group = {(row["group"], row["currency"]): row for row in result}
    assert set(by_group) == {("Moscow", "RUR"), ("Remote", "USD")}


def test_excludes_vacancies_with_no_salary_data() -> None:
    result = salary_stats_by(ROWS, "location")

    moscow = next(row for row in result if row["group"] == "Moscow")
    assert moscow["vacancy_count"] == 2  # not 3 -- the null-salary row is excluded


def test_computes_avg_min_max_from_midpoints() -> None:
    result = salary_stats_by(ROWS, "location")

    moscow = next(row for row in result if row["group"] == "Moscow")
    # midpoints: (100k+150k)/2=125k, (150k+200k)/2=175k -> avg 150k
    assert moscow["avg_salary"] == 150_000.0
    assert moscow["min_salary"] == 100_000.0
    assert moscow["max_salary"] == 200_000.0


def test_handles_one_sided_salary_range() -> None:
    result = salary_stats_by(ROWS, "location")

    remote = next(row for row in result if row["group"] == "Remote")
    assert remote["vacancy_count"] == 1
    assert remote["avg_salary"] == 2_000.0
    assert remote["max_salary"] is None


def test_empty_input_returns_empty_list() -> None:
    assert salary_stats_by([], "location") == []


def test_rejects_unknown_group_by_field() -> None:
    with pytest.raises(InvalidGroupByField):
        salary_stats_by(ROWS, "id")
