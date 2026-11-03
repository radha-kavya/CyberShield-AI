
import pandas as pd


def analyze_login_logs(file_path):

    # 1. Read CSV file
    df = pd.read_csv(file_path)

    # 2. Convert timestamp into datetime
    df["timestamp"] = pd.to_datetime(
        df["timestamp"], errors="coerce"
    )

    # 3. Count total events
    total_events = len(df)

    # 4. Separate successful and failed logins
    failed = df[df["status"].str.lower() == "failed"].copy()
    successful = df[df["status"].str.lower() == "success"]

    # 5. Count failed attempts by IP
    failed_by_ip = failed.groupby("source_ip").size()

    # 6. Identify potentially suspicious IPs
    suspicious_ips = failed_by_ip[failed_by_ip >= 3]

    # 7. Count failed attempts by username
    failed_by_user = failed.groupby("username").size()

    # 8. Detect rapid repeated login attempts
    rapid_attempts = []

    for ip, group in failed.groupby("source_ip"):

        timestamps = group["timestamp"].dropna().sort_values()

        for i in range(len(timestamps)):

            start_time = timestamps.iloc[i]
            end_time = start_time + pd.Timedelta(minutes=5)

            count = (
                (timestamps >= start_time) &
                (timestamps <= end_time)
            ).sum()

            if count >= 3:
                rapid_attempts.append({
                    "source_ip": ip,
                    "failed_attempts": count,
                    "start_time": start_time,
                    "end_time": end_time
                })
                break

    # 9. Analyze event severity
    severity_counts = df["severity"].str.lower().value_counts()

    # 10. Calculate security summary
    high_severity_failed = failed[
        failed["severity"].str.lower() == "high"
    ]

    unique_failed_ips = failed["source_ip"].nunique()

    targeted_users = failed["username"].nunique()

    # 11. Display results
    print("\n========== CYBERSHIELD AI ==========")
    print("       SECURITY LOG ANALYSIS")
    print("====================================")

    print(f"\nTotal Events       : {total_events}")
    print(f"Successful Logins  : {len(successful)}")
    print(f"Failed Logins      : {len(failed)}")

    print("\nFailed Attempts by IP:")

    for ip, count in failed_by_ip.items():
        print(f"{ip:<20} {count}")

    print("\nPotentially Suspicious IPs:")

    if suspicious_ips.empty:
        print("No IPs crossed the demo threshold.")
    else:
        for ip, count in suspicious_ips.items():
            print(f"{ip:<20} {count}")

    print("\nFailed Attempts by Username:")

    for username, count in failed_by_user.items():
        print(f"{username:<20} {count}")

    print("\nRapid Repeated Login Attempts (5-minute window):")

    if not rapid_attempts:
        print("No rapid repeated attempts detected.")
    else:
        for item in rapid_attempts:
            print(f"IP Address       : {item['source_ip']}")
            print(f"Failed Attempts  : {item['failed_attempts']}")
            print(f"Start Time       : {item['start_time']}")
            print(f"End Time         : {item['end_time']}")
            print("------------------------------------")

    print("\nSecurity Event Severity Analysis:")

    for severity in ["low", "medium", "high"]:
        count = severity_counts.get(severity, 0)
        print(f"{severity.capitalize():<20} {count}")

    # 12. Display security event summary
    print("\n========== SECURITY EVENT SUMMARY ==========")

    print(f"Total Security Events          : {total_events}")
    print(f"High-Severity Failed Logins    : {len(high_severity_failed)}")
    print(f"Unique IPs with Failed Logins  : {unique_failed_ips}")
    print(f"Targeted User Accounts         : {targeted_users}")
    print(f"Potentially Suspicious IPs     : {len(suspicious_ips)}")
    print(f"Rapid Login Patterns           : {len(rapid_attempts)}")

    # 13. Generate preliminary observation
    print("\nSecurity Observation:")

    if len(suspicious_ips) > 0:
        print("Repeated failed login activity requires investigation.")
    elif len(failed) > 0:
        print("Failed login activity detected. Review the events.")
    else:
        print("No failed login activity detected.")

    print("\n============================================")
    print("Analysis completed successfully!")


if __name__ == "__main__":

    file_path = "data/logs/login_logs.csv"

    analyze_login_logs(file_path)
