
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

STAGING_SCRIPTS = [
    "build_staging_orders.py",
    "build_staging_order_items.py",
    "build_staging_order_payments.py",
    "build_staging_customers.py",
    "build_staging_products.py",
    "build_staging_sellers.py",
    "build_staging_order_reviews.py",
    "build_staging_category_translation.py",
    "build_staging_geolocation.py",
]

PIPELINE_STEPS = [
    ("Raw ingestion", "ingest_raw.py"),
    *[
        (f"Staging: {script}", script)
        for script in STAGING_SCRIPTS
    ],
    ("Verify staging", "verify_staging.py"),
    ("Data quality gate", "run_quality_checks.py"),
    ("Build analytics mart", "build_mart.py"),
    ("Generate charts", "generate_charts.py"),
    ("Build PDF report", "build_report.py"),
]


def run_step(name, script):
    script_path = SRC / script

    if not script_path.exists():
        raise FileNotFoundError(
            f"Pipeline script not found: {script_path}"
        )

    print(f"\n{'=' * 65}", flush=True)
    print(f"STEP: {name}", flush=True)
    print(f"RUNNING: {script}", flush=True)
    print("=" * 65, flush=True)

    subprocess.run(
        [sys.executable, str(script_path)],
        cwd=ROOT,
        check=True,
    )

    print(f"COMPLETED: {name}", flush=True)


def main():
    print("OLIST BUSINESS REVIEW PIPELINE", flush=True)
    print(f"Project root: {ROOT}", flush=True)

    try:
        for name, script in PIPELINE_STEPS:
            run_step(name, script)

    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        print("\nPIPELINE FAILED.", flush=True)

        if isinstance(exc, subprocess.CalledProcessError):
            print(
                f"Script exited with code {exc.returncode}.",
                flush=True,
            )
        else:
            print(str(exc), flush=True)

        print(
            "Fix the error before rerunning the pipeline.",
            flush=True,
        )
        sys.exit(1)

    print("\n" + "=" * 65, flush=True)
    print("PIPELINE COMPLETED SUCCESSFULLY.", flush=True)
    print(
        "Review PDF: reports/olist_weekly_business_review.pdf",
        flush=True,
    )
    print("=" * 65, flush=True)


if __name__ == "__main__":
    main()
