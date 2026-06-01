import os
import csv
import time
import psutil
import argparse
from datetime import datetime
from colorama import Fore, Style, init
from plyer import notification

init(autoreset=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def parse_args():
    parser = argparse.ArgumentParser(description="System Health Monitor")
    parser.add_argument("--cpu",      type=float, default=80.0, help="CPU alert threshold (default: 80)")
    parser.add_argument("--memory",   type=float, default=80.0, help="Memory alert threshold (default: 80)")
    parser.add_argument("--disk",     type=float, default=90.0, help="Disk alert threshold (default: 90)")
    parser.add_argument("--interval", type=int,   default=5,    help="Refresh interval in seconds (default: 5)")
    return parser.parse_args()


def get_log_file():
    date_str = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(BASE_DIR, f"health_log_{date_str}.csv")


def get_metrics(prev_net=None, elapsed=None):
    net = psutil.net_io_counters()
    battery = psutil.sensors_battery()

    if prev_net and elapsed and elapsed > 0:
        sent_speed = (net.bytes_sent - prev_net.bytes_sent) / elapsed / 1024
        recv_speed = (net.bytes_recv - prev_net.bytes_recv) / elapsed / 1024
    else:
        sent_speed = 0.0
        recv_speed = 0.0

    return {
        "timestamp":    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cpu":          psutil.cpu_percent(interval=1),
        "memory":       psutil.virtual_memory().percent,
        "disk":         psutil.disk_usage('/').percent,
        "network_sent": net.bytes_sent,
        "network_recv": net.bytes_recv,
        "sent_speed":   sent_speed,
        "recv_speed":   recv_speed,
        "battery":      battery.percent if battery else None,
        "plugged_in":   battery.power_plugged if battery else None,
    }, net


def check_alerts(metrics, cpu_threshold, memory_threshold, disk_threshold):
    alerts = []
    if metrics["cpu"] > cpu_threshold:
        alerts.append(f"HIGH CPU: {metrics['cpu']}%")
    if metrics["memory"] > memory_threshold:
        alerts.append(f"HIGH MEMORY: {metrics['memory']}%")
    if metrics["disk"] > disk_threshold:
        alerts.append(f"HIGH DISK: {metrics['disk']}%")
    return alerts


def send_desktop_notification(alerts):
    try:
        notification.notify(
            title="Health Monitor Alert",
            message="\n".join(alerts),
            timeout=5
        )
    except Exception:
        pass


def display_metrics(metrics, alerts, cpu_threshold, memory_threshold, disk_threshold):
    print(f"\n{Fore.CYAN}--- System Health Monitor ---{Style.RESET_ALL}")
    print(f"Time:    {metrics['timestamp']}")

    cpu_color  = Fore.RED if metrics['cpu']    > cpu_threshold    else Fore.GREEN
    mem_color  = Fore.RED if metrics['memory'] > memory_threshold else Fore.GREEN
    disk_color = Fore.RED if metrics['disk']   > disk_threshold   else Fore.GREEN

    print(f"CPU:      {cpu_color}{metrics['cpu']}%{Style.RESET_ALL}")
    print(f"Memory:   {mem_color}{metrics['memory']}%{Style.RESET_ALL}")
    print(f"Disk:     {disk_color}{metrics['disk']}%{Style.RESET_ALL}")
    print(f"Net Sent: {metrics['sent_speed']:.1f} KB/s  (Total: {metrics['network_sent'] / 1024 / 1024:.2f} MB)")
    print(f"Net Recv: {metrics['recv_speed']:.1f} KB/s  (Total: {metrics['network_recv'] / 1024 / 1024:.2f} MB)")

    if metrics['battery'] is not None:
        plug_status = "Plugged in" if metrics['plugged_in'] else "On battery"
        bat_color = Fore.RED if metrics['battery'] < 20 else Fore.GREEN
        print(f"Battery:  {bat_color}{metrics['battery']:.0f}%{Style.RESET_ALL} ({plug_status})")

    if alerts:
        print(f"\n{Fore.RED}⚠️  ALERTS:{Style.RESET_ALL}")
        for alert in alerts:
            print(f"   {Fore.RED}{alert}{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.GREEN}✅ All systems normal.{Style.RESET_ALL}")

    top = get_top_processes()
    if top:
        print(f"\n{Fore.CYAN}Top Processes:{Style.RESET_ALL}")
        for p in top:
            print(f"  {p['name']:<25} {p['cpu_percent']:>5.1f}% CPU   {p['memory_percent']:>5.1f}% MEM")


def print_session_summary(session_data, alert_count):
    if not session_data:
        return

    cpu_vals  = [r['cpu']    for r in session_data]
    mem_vals  = [r['memory'] for r in session_data]
    disk_vals = [r['disk']   for r in session_data]

    print(f"\n{Fore.CYAN}{'=' * 40}")
    print(f"Session Summary ({len(session_data)} readings)")
    print(f"{'=' * 40}{Style.RESET_ALL}")
    print(f"  CPU     avg: {sum(cpu_vals)  / len(cpu_vals):.1f}%   max: {max(cpu_vals):.1f}%")
    print(f"  Memory  avg: {sum(mem_vals)  / len(mem_vals):.1f}%   max: {max(mem_vals):.1f}%")
    print(f"  Disk    avg: {sum(disk_vals) / len(disk_vals):.1f}%   max: {max(disk_vals):.1f}%")
    print(f"  Alerts triggered: {alert_count}")


def save_log(metrics, alerts, log_file):
    file_exists = os.path.exists(log_file)

    with open(log_file, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow([
                "Timestamp", "CPU %", "Memory %", "Disk %",
                "Net Sent (KB/s)", "Net Recv (KB/s)", "Battery %", "Alerts"
            ])

        writer.writerow([
            metrics["timestamp"],
            metrics["cpu"],
            metrics["memory"],
            metrics["disk"],
            f"{metrics['sent_speed']:.1f}",
            f"{metrics['recv_speed']:.1f}",
            f"{metrics['battery']:.0f}" if metrics["battery"] is not None else "N/A",
            ", ".join(alerts) if alerts else "None"
        ])


def get_top_processes():
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            info = proc.info
            if info['name'] and info['cpu_percent'] is not None and info['memory_percent'] is not None:
                processes.append(info)
        except Exception:
            continue

    return sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:5]


def main():
    args = parse_args()
    log_file = get_log_file()

    print("Starting Health Monitor...")
    print(f"Logging to: {log_file}")
    print(f"Thresholds — CPU: {args.cpu}%  Memory: {args.memory}%  Disk: {args.disk}%")
    print(f"Refresh interval: {args.interval}s")
    print("Press Ctrl+C to stop.\n")

    session_data = []
    alert_count  = 0
    prev_net     = None
    prev_time    = None

    try:
        while True:
            now     = time.time()
            elapsed = now - prev_time if prev_time else None

            metrics, net = get_metrics(prev_net, elapsed)
            prev_net  = net
            prev_time = now

            alerts = check_alerts(metrics, args.cpu, args.memory, args.disk)
            display_metrics(metrics, alerts, args.cpu, args.memory, args.disk)
            save_log(metrics, alerts, log_file)

            session_data.append(metrics)
            alert_count += len(alerts)

            if alerts:
                send_desktop_notification(alerts)

            time.sleep(args.interval)

    except KeyboardInterrupt:
        print(f"\nMonitor stopped. Log saved to:")
        print(log_file)
        print_session_summary(session_data, alert_count)


if __name__ == "__main__":
    main()
