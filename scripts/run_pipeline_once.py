import subprocess
import sys

def run(cmd):
    print("running", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(result.stderr.strip())
    if result.returncode != 0:
        raise SystemExit(result.returncode)

def main():
    run([sys.executable, "src/ingest/gbfs_ingest.py"])
    run([sys.executable, "src/ingest/weather_ingest.py"])
    run([sys.executable, "scripts/run_sql_file.py", "scripts/analytics_views.sql"])
    run([sys.executable, "scripts/run_quality_checks.py"])
    print("ok, pipeline run complete")

if __name__ == "__main__":
    main()
