from __future__ import annotations

import argparse
import os
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

REQUIRED_LIVE_ENV_VARS = (
    "COSMOS_ENDPOINT",
    "COSMOS_KEY",
    "SEARCH_ENDPOINT",
    "SEARCH_KEY",
)


@dataclass(slots=True)
class DemoConfig:
    stack: dict[str, list[str]]
    run: dict[str, Any]


def load_demo_config(path: Path) -> DemoConfig:
    raw_payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw_payload, dict):
        raise ValueError("Demo config must be a YAML mapping.")

    stack = raw_payload.get("stack")
    if not isinstance(stack, dict):
        raise ValueError("demo/config.yaml must define a stack mapping.")

    products = _string_list(stack.get("products"))
    if not products:
        raise ValueError("stack.products must include at least one product.")

    normalized_stack = {
        "products": products,
        "platforms": _string_list(stack.get("platforms")),
        "keywords": _string_list(stack.get("keywords")),
        "exclude": _string_list(stack.get("exclude")),
    }

    run = raw_payload.get("run")
    if not isinstance(run, dict):
        raise ValueError("demo/config.yaml must define a run mapping.")

    normalized_run = {
        "collection_window_days": _positive_int(run, "collection_window_days", 7),
        "max_items_per_source": _positive_int(run, "max_items_per_source", 25),
        "cve_results_per_page": _optional_positive_int(run, "cve_results_per_page"),
        "intel_limit": _optional_positive_int(run, "intel_limit"),
        "correlation_limit": _positive_int(run, "correlation_limit", 120),
        "correlation_top_k": _positive_int(run, "correlation_top_k", 8),
        "correlation_min_confidence": _bounded_float(
            run,
            "correlation_min_confidence",
            default=0.35,
            minimum=0.0,
            maximum=1.0,
        ),
        "prioritization_limit": _positive_int(run, "prioritization_limit", 120),
        "report_top_risks": _positive_int(run, "report_top_risks", 5),
        "report_notable_mentions": _non_negative_int(
            run,
            "report_notable_mentions",
            3,
        ),
        "report_output_path": _string_value(
            run, "report_output_path", "docs/demo_brief.md"
        ),
    }

    return DemoConfig(stack=normalized_stack, run=normalized_run)


def _string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        items = [value]
    elif isinstance(value, list):
        items = value
    else:
        raise ValueError("Expected a string or list of strings.")

    normalized: list[str] = []
    for item in items:
        text = str(item).strip()
        if text:
            normalized.append(text)
    return normalized


def _positive_int(payload: dict[str, Any], key: str, default: int) -> int:
    raw = payload.get(key, default)
    try:
        value = int(raw)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{key} must be an integer.") from exc
    if value <= 0:
        raise ValueError(f"{key} must be greater than zero.")
    return value


def _optional_positive_int(payload: dict[str, Any], key: str) -> int | None:
    if key not in payload or payload.get(key) is None:
        return None
    return _positive_int(payload, key, 1)


def _non_negative_int(payload: dict[str, Any], key: str, default: int) -> int:
    raw = payload.get(key, default)
    try:
        value = int(raw)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{key} must be an integer.") from exc
    if value < 0:
        raise ValueError(f"{key} must be zero or greater.")
    return value


def _bounded_float(
    payload: dict[str, Any],
    key: str,
    *,
    default: float,
    minimum: float,
    maximum: float,
) -> float:
    raw = payload.get(key, default)
    try:
        value = float(raw)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{key} must be numeric.") from exc
    if value < minimum or value > maximum:
        raise ValueError(f"{key} must be between {minimum} and {maximum}.")
    return value


def _string_value(payload: dict[str, Any], key: str, default: str) -> str:
    text = str(payload.get(key, default)).strip()
    if not text:
        raise ValueError(f"{key} cannot be empty.")
    return text


def _missing_live_env_vars() -> list[str]:
    return [name for name in REQUIRED_LIVE_ENV_VARS if not os.getenv(name)]


def _resolved_cve_results_per_page(config: DemoConfig) -> int:
    configured = config.run.get("cve_results_per_page")
    if configured is not None:
        return int(configured)
    return int(config.run["max_items_per_source"])


def _resolved_intel_limit(config: DemoConfig) -> int:
    configured = config.run.get("intel_limit")
    if configured is not None:
        return int(configured)
    return int(config.run["max_items_per_source"])


def _print_dry_run(config: DemoConfig, config_path: Path) -> None:
    print("DRY RUN: no external APIs will be called and no Azure writes will occur.")
    print(f"Config: {config_path}")
    print(f"Stack: {', '.join(config.stack['products'])}")
    print("Planned flow:")
    print(
        "1) collect -> CVE(results_per_page="
        f"{_resolved_cve_results_per_page(config)}), "
        f"Intel(limit={_resolved_intel_limit(config)}), "
        "News(default feeds)"
    )
    print(
        "2) correlate -> top_k="
        f"{config.run['correlation_top_k']}, "
        f"limit={config.run['correlation_limit']}, "
        f"min_confidence={config.run['correlation_min_confidence']}"
    )
    print(
        "3) prioritize -> limit="
        f"{config.run['prioritization_limit']} for stack profile from config"
    )
    print(
        "4) report -> top_risks="
        f"{config.run['report_top_risks']}, "
        f"notable_mentions={config.run['report_notable_mentions']}, "
        f"output={config.run['report_output_path']}"
    )


def _temporary_stack_file(stack: dict[str, list[str]]) -> Path:
    temp_dir = tempfile.mkdtemp(prefix="delvn-demo-")
    stack_path = Path(temp_dir) / "stack.yaml"
    stack_path.write_text(yaml.safe_dump(stack, sort_keys=False), encoding="utf-8")
    return stack_path


def _run_live_pipeline(config: DemoConfig) -> int:
    from agents.correlator_agent import run_correlation
    from agents.cve_agent import run_cve_collection
    from agents.intel_agent import run_intel_collection
    from agents.news_agent import run_news_collection
    from agents.prioritizer_agent import run_prioritization
    from agents.reporter_agent import run_reporting

    pub_start = datetime.now(timezone.utc) - timedelta(
        days=int(config.run["collection_window_days"])
    )

    cve_stats = run_cve_collection(
        pub_start=pub_start,
        results_per_page=_resolved_cve_results_per_page(config),
    )
    intel_stats = run_intel_collection(limit=_resolved_intel_limit(config))
    news_stats = run_news_collection()

    correlation_stats = run_correlation(
        limit=int(config.run["correlation_limit"]),
        top_k=int(config.run["correlation_top_k"]),
        min_confidence=float(config.run["correlation_min_confidence"]),
    )

    stack_path = _temporary_stack_file(config.stack)
    try:
        prioritization_result = run_prioritization(
            stack_path=str(stack_path),
            limit=int(config.run["prioritization_limit"]),
        )
        report_output_path = Path(str(config.run["report_output_path"]))
        if not report_output_path.is_absolute():
            report_output_path = ROOT / report_output_path

        report_result = run_reporting(
            stack_path=str(stack_path),
            limit=int(config.run["prioritization_limit"]),
            top_risk_count=int(config.run["report_top_risks"]),
            notable_count=int(config.run["report_notable_mentions"]),
            output_path=str(report_output_path),
            prioritization_output=prioritization_result,
        )
    finally:
        stack_path.unlink(missing_ok=True)
        stack_path.parent.rmdir()

    print("Demo pipeline complete.")
    print(
        "Collection: "
        f"CVE stored={cve_stats.get('stored', 0)}, "
        f"Intel stored={intel_stats.get('stored', 0)}, "
        f"News stored={news_stats.get('stored', 0)}"
    )
    print(
        "Correlation: "
        f"links_created={correlation_stats.get('links_created', 0)}, "
        f"errors={correlation_stats.get('errors', 0)}"
    )

    prio_stats = prioritization_result.get("stats", {})
    print(
        "Prioritization: "
        f"total={prio_stats.get('total', 0)}, "
        f"HIGH={prio_stats.get('high', 0)}, "
        f"MEDIUM={prio_stats.get('medium', 0)}, "
        f"LOW={prio_stats.get('low', 0)}, "
        f"NONE={prio_stats.get('none', 0)}"
    )

    top_headlines = [
        str(entry.get("headline", "")).strip()
        for entry in report_result.get("brief", {}).get("top_risks", [])
        if isinstance(entry, dict) and str(entry.get("headline", "")).strip()
    ][:3]
    if top_headlines:
        print("Top headlines:")
        for headline in top_headlines:
            print(f"- {headline}")
    else:
        print("Top headlines: none generated")

    print(f"Brief written to: {report_output_path}")
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Delvn demo pipeline.")
    parser.add_argument(
        "--config",
        default=str(ROOT / "demo" / "config.yaml"),
        help="Path to the demo config YAML file.",
    )

    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate config and print planned steps without external calls or Azure writes.",
    )
    mode.add_argument(
        "--live",
        action="store_true",
        help="Run the live end-to-end pipeline (requires Azure environment variables).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    config_path = Path(args.config)

    try:
        config = load_demo_config(config_path)
    except Exception as exc:
        print(f"Config validation failed: {exc}", file=sys.stderr)
        return 1

    if args.live:
        missing_env = _missing_live_env_vars()
        if missing_env:
            print(
                "Live run blocked. Missing required environment variables: "
                + ", ".join(missing_env),
                file=sys.stderr,
            )
            print("Use --dry-run to validate without external calls.", file=sys.stderr)
            return 2

        try:
            return _run_live_pipeline(config)
        except Exception as exc:
            print(f"Live run failed: {exc}", file=sys.stderr)
            return 1

    _print_dry_run(config, config_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
