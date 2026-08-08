#!/usr/bin/env python3
"""Validate business-viability assessment artifacts deterministically."""

from __future__ import annotations

import argparse
import csv
import json
import math
import tempfile
from pathlib import Path
from typing import Any


QUICK_FILES = (
    "executive-summary.md",
    "assumptions.md",
    "sources.md",
    "coverage-manifest.md",
)

STANDARD_FILES = (
    "executive-summary.md",
    "project-understanding.md",
    "market-demand.md",
    "competitors.md",
    "mvp-scope.md",
    "development-estimate.md",
    "infrastructure-costs.md",
    "marketing-plan.md",
    "unit-economics.md",
    "risks-and-validation.md",
    "assumptions.md",
    "sources.md",
    "coverage-manifest.md",
    "financial-model.csv",
    "assessment.json",
)

CSV_COLUMNS = (
    "scenario",
    "month",
    "new_customers",
    "active_customers",
    "churned_customers",
    "arpu",
    "revenue",
    "payment_fees",
    "variable_infrastructure",
    "fixed_infrastructure",
    "marketing_cost",
    "sales_cost",
    "development_cost",
    "support_cost",
    "other_cost",
    "total_cost",
    "gross_profit",
    "operating_profit",
    "cumulative_cash_flow",
)

REQUIRED_SCENARIOS = {"pessimistic", "base", "optimistic"}
VERDICTS = {"GO", "VALIDATE_FIRST", "PIVOT", "NO_GO"}
CONFIDENCE = {"HIGH", "MEDIUM", "LOW"}
ABSOLUTE_TOLERANCE = 0.02
RELATIVE_TOLERANCE = 1e-9
COST_COLUMNS = (
    "payment_fees",
    "variable_infrastructure",
    "fixed_infrastructure",
    "marketing_cost",
    "sales_cost",
    "development_cost",
    "support_cost",
    "other_cost",
)


def _finite_number(value: str) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _check_derived_value(
    *,
    line_number: int,
    scenario: str,
    month: int,
    name: str,
    actual: float,
    expected: float,
    errors: list[str],
) -> None:
    if math.isclose(
        actual,
        expected,
        rel_tol=RELATIVE_TOLERANCE,
        abs_tol=ABSOLUTE_TOLERANCE,
    ):
        return
    errors.append(
        "financial-model.csv line "
        f"{line_number}: derived {name} for {scenario} month {month} is {actual}, "
        f"expected {expected} (absolute tolerance {ABSOLUTE_TOLERANCE}, "
        f"relative tolerance {RELATIVE_TOLERANCE})"
    )


def _validate_formulas(
    rows_by_scenario: dict[str, dict[int, tuple[int, dict[str, float]]]],
    horizon: int,
    errors: list[str],
) -> None:
    for scenario, rows in sorted(rows_by_scenario.items()):
        for month in range(1, horizon + 1):
            parsed = rows.get(month)
            if parsed is None:
                continue
            line_number, values = parsed

            previous = rows.get(month - 1)
            previous_active = 0.0 if month == 1 else (
                previous[1]["active_customers"] if previous is not None else None
            )
            previous_cash = 0.0 if month == 1 else (
                previous[1]["cumulative_cash_flow"] if previous is not None else None
            )

            if previous_active is not None:
                expected_active = (
                    previous_active
                    + values["new_customers"]
                    - values["churned_customers"]
                )
                _check_derived_value(
                    line_number=line_number,
                    scenario=scenario,
                    month=month,
                    name="active_customers",
                    actual=values["active_customers"],
                    expected=expected_active,
                    errors=errors,
                )

            expected_revenue = values["active_customers"] * values["arpu"]
            _check_derived_value(
                line_number=line_number,
                scenario=scenario,
                month=month,
                name="revenue",
                actual=values["revenue"],
                expected=expected_revenue,
                errors=errors,
            )

            expected_total_cost = sum(values[column] for column in COST_COLUMNS)
            _check_derived_value(
                line_number=line_number,
                scenario=scenario,
                month=month,
                name="total_cost",
                actual=values["total_cost"],
                expected=expected_total_cost,
                errors=errors,
            )

            expected_gross_profit = (
                values["revenue"]
                - values["payment_fees"]
                - values["variable_infrastructure"]
            )
            _check_derived_value(
                line_number=line_number,
                scenario=scenario,
                month=month,
                name="gross_profit",
                actual=values["gross_profit"],
                expected=expected_gross_profit,
                errors=errors,
            )

            expected_operating_profit = values["revenue"] - values["total_cost"]
            _check_derived_value(
                line_number=line_number,
                scenario=scenario,
                month=month,
                name="operating_profit",
                actual=values["operating_profit"],
                expected=expected_operating_profit,
                errors=errors,
            )

            if previous_cash is not None:
                expected_cumulative_cash = previous_cash + values["operating_profit"]
                _check_derived_value(
                    line_number=line_number,
                    scenario=scenario,
                    month=month,
                    name="cumulative_cash_flow",
                    actual=values["cumulative_cash_flow"],
                    expected=expected_cumulative_cash,
                    errors=errors,
                )


def _read_json(path: Path, errors: list[str]) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        errors.append(f"assessment.json is not valid UTF-8 JSON: {exc}")
        return None
    if not isinstance(value, dict):
        errors.append("assessment.json must contain a JSON object")
        return None
    return value


def _validate_json(
    path: Path, mode: str, horizon: int, currency: str, errors: list[str]
) -> None:
    data = _read_json(path, errors)
    if data is None:
        return

    meta = data.get("meta")
    if not isinstance(meta, dict):
        errors.append("assessment.json meta must be an object")
    else:
        if meta.get("mode") != mode:
            errors.append(
                f"assessment.json meta.mode must be {mode!r}, got {meta.get('mode')!r}"
            )
        if str(meta.get("currency", "")).casefold() != currency.casefold():
            errors.append(
                "assessment.json meta.currency does not match the configured currency"
            )
        if meta.get("forecast_horizon_months") != horizon:
            errors.append(
                "assessment.json meta.forecast_horizon_months does not match the configured horizon"
            )

    recommendation = data.get("recommendation")
    if not isinstance(recommendation, dict):
        errors.append("assessment.json recommendation must be an object")
    else:
        decision = recommendation.get("decision")
        if decision not in VERDICTS:
            errors.append(
                "assessment.json recommendation.decision must be one of "
                + ", ".join(sorted(VERDICTS))
            )
        confidence = recommendation.get("confidence")
        if confidence not in CONFIDENCE:
            errors.append(
                "assessment.json recommendation.confidence must be HIGH, MEDIUM, or LOW"
            )

    scores = data.get("scores")
    if not isinstance(scores, dict) or not scores:
        errors.append("assessment.json scores must be a non-empty object")
    else:
        for name, value in scores.items():
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                errors.append(f"assessment.json score {name!r} must be numeric")
            elif not 0 <= value <= 10:
                errors.append(f"assessment.json score {name!r} must be between 0 and 10")

    estimates = data.get("estimates")
    if isinstance(estimates, dict):
        mvp_cost = estimates.get("mvp_cash_cost")
        if isinstance(mvp_cost, dict) and str(mvp_cost.get("currency", "")).casefold() != currency.casefold():
            errors.append(
                "assessment.json estimates.mvp_cash_cost.currency does not match the configured currency"
            )


def _validate_csv(path: Path, horizon: int, errors: list[str]) -> None:
    try:
        handle = path.open("r", encoding="utf-8-sig", newline="")
    except OSError as exc:
        errors.append(f"financial-model.csv could not be opened: {exc}")
        return

    months_by_scenario: dict[str, set[int]] = {}
    rows_by_scenario: dict[str, dict[int, tuple[int, dict[str, float]]]] = {}
    row_keys: set[tuple[str, int]] = set()

    with handle:
        reader = csv.DictReader(handle)
        fields = tuple(reader.fieldnames or ())
        missing = [column for column in CSV_COLUMNS if column not in fields]
        if missing:
            errors.append("financial-model.csv missing columns: " + ", ".join(missing))
            return

        for line_number, row in enumerate(reader, start=2):
            scenario = (row.get("scenario") or "").strip().casefold()
            if not scenario:
                errors.append(f"financial-model.csv line {line_number}: empty scenario")
                continue

            month_text = (row.get("month") or "").strip()
            try:
                month = int(month_text)
            except ValueError:
                errors.append(
                    f"financial-model.csv line {line_number}: month must be an integer"
                )
                continue
            if not 1 <= month <= horizon:
                errors.append(
                    f"financial-model.csv line {line_number}: month {month} is outside 1..{horizon}"
                )

            key = (scenario, month)
            if key in row_keys:
                errors.append(
                    f"financial-model.csv line {line_number}: duplicate {scenario} month {month}"
                )
            row_keys.add(key)
            months_by_scenario.setdefault(scenario, set()).add(month)

            numeric_values: dict[str, float] = {}
            numeric_valid = True
            for column in CSV_COLUMNS[2:]:
                text = (row.get(column) or "").strip()
                if not _finite_number(text):
                    errors.append(
                        f"financial-model.csv line {line_number}: {column} must be a finite number"
                    )
                    numeric_valid = False
                else:
                    numeric_values[column] = float(text)

            if (
                numeric_valid
                and month not in rows_by_scenario.setdefault(scenario, {})
                and 1 <= month <= horizon
            ):
                rows_by_scenario[scenario][month] = (line_number, numeric_values)

    missing_scenarios = sorted(REQUIRED_SCENARIOS - months_by_scenario.keys())
    if missing_scenarios:
        errors.append(
            "financial-model.csv missing scenarios: " + ", ".join(missing_scenarios)
        )

    expected_months = set(range(1, horizon + 1))
    for scenario, months in sorted(months_by_scenario.items()):
        missing_months = sorted(expected_months - months)
        if missing_months:
            preview = ", ".join(str(month) for month in missing_months[:10])
            suffix = "..." if len(missing_months) > 10 else ""
            errors.append(
                f"financial-model.csv scenario {scenario!r} missing months: {preview}{suffix}"
            )

    _validate_formulas(rows_by_scenario, horizon, errors)


def validate_report(report: Path, mode: str, horizon: int, currency: str) -> list[str]:
    errors: list[str] = []
    if horizon < 1:
        return ["horizon must be a positive integer"]
    if not currency.strip():
        return ["currency must be non-empty"]
    if not report.is_dir():
        return [f"report directory does not exist: {report}"]

    required = QUICK_FILES if mode == "quick" else STANDARD_FILES
    missing = [name for name in required if not (report / name).is_file()]
    if missing:
        errors.append("missing required artifacts: " + ", ".join(missing))

    for name in required:
        path = report / name
        if path.is_file() and path.stat().st_size == 0:
            errors.append(f"artifact is empty: {name}")

    if mode in {"standard", "deep"}:
        csv_path = report / "financial-model.csv"
        if csv_path.is_file():
            _validate_csv(csv_path, horizon, errors)
        json_path = report / "assessment.json"
        if json_path.is_file():
            _validate_json(json_path, mode, horizon, currency, errors)

    return errors


def _write_self_test_fixture(report: Path, mode: str, horizon: int, currency: str) -> None:
    for name in STANDARD_FILES:
        if name not in {"financial-model.csv", "assessment.json"}:
            (report / name).write_text(f"# {name}\n", encoding="utf-8")

    with (report / "financial-model.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        scenario_factor = {"pessimistic": 0.7, "base": 1.0, "optimistic": 1.3}
        for scenario in sorted(REQUIRED_SCENARIOS):
            active_customers = 0.0
            cumulative_cash_flow = 0.0
            for month in range(1, horizon + 1):
                factor = scenario_factor[scenario]
                new_customers = (12.0 - month) * factor
                churned_customers = 0.0 if month == 1 else 1.0 * factor
                active_customers = (
                    active_customers + new_customers - churned_customers
                )
                arpu = 25.0
                revenue = active_customers * arpu
                payment_fees = revenue * 0.03
                variable_infrastructure = active_customers * 1.25
                fixed_infrastructure = 40.0
                marketing_cost = 75.0
                sales_cost = 25.0
                development_cost = 150.0 if month == 1 else 30.0
                support_cost = active_customers * 2.0
                other_cost = 10.0
                total_cost = sum(
                    (
                        payment_fees,
                        variable_infrastructure,
                        fixed_infrastructure,
                        marketing_cost,
                        sales_cost,
                        development_cost,
                        support_cost,
                        other_cost,
                    )
                )
                gross_profit = revenue - payment_fees - variable_infrastructure
                operating_profit = revenue - total_cost
                cumulative_cash_flow += operating_profit
                row = {
                    "scenario": scenario,
                    "month": month,
                    "new_customers": new_customers,
                    "active_customers": active_customers,
                    "churned_customers": churned_customers,
                    "arpu": arpu,
                    "revenue": revenue,
                    "payment_fees": payment_fees,
                    "variable_infrastructure": variable_infrastructure,
                    "fixed_infrastructure": fixed_infrastructure,
                    "marketing_cost": marketing_cost,
                    "sales_cost": sales_cost,
                    "development_cost": development_cost,
                    "support_cost": support_cost,
                    "other_cost": other_cost,
                    "total_cost": total_cost,
                    "gross_profit": gross_profit,
                    "operating_profit": operating_profit,
                    "cumulative_cash_flow": cumulative_cash_flow,
                }
                writer.writerow(row)

    data = {
        "meta": {
            "mode": mode,
            "currency": currency,
            "forecast_horizon_months": horizon,
            "generated_at_utc": "2026-01-01T00:00:00Z",
        },
        "project": {
            "name": "Fixture",
            "summary": "Self-test fixture",
            "target_customer": "Test",
            "business_model": "Test",
        },
        "scores": {"overall_viability": 5, "evidence_of_demand": 5},
        "estimates": {"mvp_cash_cost": {"currency": currency}},
        "recommendation": {
            "decision": "VALIDATE_FIRST",
            "confidence": "LOW",
            "main_reasons": [],
            "critical_assumptions": [],
            "next_actions": [],
            "kill_criteria": [],
        },
    }
    (report / "assessment.json").write_text(
        json.dumps(data, indent=2) + "\n", encoding="utf-8"
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="assessment-validator-") as temporary:
        root = Path(temporary)
        for mode in ("standard", "deep"):
            report = root / mode
            report.mkdir()
            _write_self_test_fixture(report, mode, 3, "USD")
            valid_errors = validate_report(report, mode, 3, "USD")
            if valid_errors:
                print(f"SELF-TEST FAILED: valid {mode} fixture was rejected")
                for error in valid_errors:
                    print(f"  {error}")
                return 1

        report = root / "standard"
        data = json.loads((report / "assessment.json").read_text(encoding="utf-8"))
        data["recommendation"]["decision"] = "MAYBE"
        (report / "assessment.json").write_text(
            json.dumps(data, indent=2) + "\n", encoding="utf-8"
        )
        invalid_errors = validate_report(report, "standard", 3, "USD")
        if not any("recommendation.decision" in error for error in invalid_errors):
            print("SELF-TEST FAILED: invalid verdict was accepted")
            return 1

        _write_self_test_fixture(report, "standard", 3, "USD")
        csv_path = report / "financial-model.csv"
        with csv_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            rows = list(reader)
        rows[0]["revenue"] = str(float(rows[0]["revenue"]) + 1.0)
        with csv_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
            writer.writeheader()
            writer.writerows(rows)
        invalid_errors = validate_report(report, "standard", 3, "USD")
        if not any("derived revenue" in error for error in invalid_errors):
            print("SELF-TEST FAILED: incorrect derived revenue was accepted")
            return 1

    print(
        "SELF-TEST PASSED: valid standard/deep fixtures accepted; invalid verdict "
        "and derived revenue rejected"
    )
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate business-viability assessment artifacts."
    )
    parser.add_argument("report_directory", nargs="?", type=Path)
    parser.add_argument("--mode", choices=("quick", "standard", "deep"), default="standard")
    parser.add_argument("--horizon", type=int, default=36)
    parser.add_argument("--currency", default="EUR")
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    if args.report_directory is None:
        print("ERROR: report_directory is required unless --self-test is used")
        return 2

    errors = validate_report(
        args.report_directory, args.mode, args.horizon, args.currency
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print(f"Assessment artifacts valid: {args.report_directory.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
