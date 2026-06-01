# System Health Monitor

A command-line tool that monitors your system's CPU, memory, disk, battery, and network usage in real time, with color-coded output, desktop alerts, and daily log rotation.

## Features

- Live system metrics refreshed on a configurable interval
- Color-coded output — green for normal, red for above threshold
- Automatic alerts when CPU, memory, or disk exceed thresholds
- Desktop pop-up notifications when an alert triggers
- Real-time network upload/download speed (KB/s)
- Battery percentage and plug status (laptops)
- Top 5 CPU-consuming processes displayed each cycle
- Daily log rotation — a new CSV file is created each day automatically
- Session summary printed on exit (avg/max stats + total alerts)
- Configurable thresholds and refresh interval via command-line arguments

## Requirements

- Python 3.8+
- [psutil](https://pypi.org/project/psutil/)
- [colorama](https://pypi.org/project/colorama/)
- [plyer](https://pypi.org/project/plyer/)

Install all dependencies with:

```bash
pip install psutil colorama plyer
```

## Usage

Default settings:

```bash
python health_monitor.py
```

Custom thresholds and interval:

```bash
python health_monitor.py --cpu 70 --memory 75 --disk 85 --interval 10
```

Press `Ctrl+C` to stop. A session summary is printed on exit.

## Command-Line Arguments

| Argument     | Default | Description                        |
|--------------|---------|------------------------------------|
| `--cpu`      | 80      | CPU alert threshold (%)            |
| `--memory`   | 80      | Memory alert threshold (%)         |
| `--disk`     | 90      | Disk alert threshold (%)           |
| `--interval` | 5       | Refresh interval in seconds        |

## Output Example

```
--- System Health Monitor ---
Time:    2026-06-01 07:27:26
CPU:      82.1%               <- red when above threshold
Memory:   62.9%               <- green when normal
Disk:     67.5%
Net Sent: 45.2 KB/s  (Total: 110.44 MB)
Net Recv: 312.8 KB/s  (Total: 341.88 MB)
Battery:  87% (Plugged in)

⚠️  ALERTS:
   HIGH CPU: 82.1%

Top Processes:
  chrome.exe                12.4% CPU     1.2% MEM
  python.exe                 8.1% CPU     0.8% MEM
  explorer.exe               2.3% CPU     0.5% MEM
```

## Session Summary (on Ctrl+C)

```
========================================
Session Summary (24 readings)
========================================
  CPU     avg: 18.3%   max: 82.1%
  Memory  avg: 60.1%   max: 63.5%
  Disk    avg: 67.5%   max: 67.5%
  Alerts triggered: 1
```

## Alert Thresholds

| Metric  | Default Threshold |
|---------|-------------------|
| CPU     | > 80%             |
| Memory  | > 80%             |
| Disk    | > 90%             |
| Battery | < 20% (red only)  |

## Log File

A new CSV log file is created each day automatically, named by date (e.g. `health_log_2026-06-01.csv`).

| Column           | Description                        |
|------------------|------------------------------------|
| Timestamp        | Date and time of the reading       |
| CPU %            | CPU usage percentage               |
| Memory %         | RAM usage percentage               |
| Disk %           | Disk usage percentage              |
| Net Sent (KB/s)  | Upload speed for that interval     |
| Net Recv (KB/s)  | Download speed for that interval   |
| Battery %        | Battery level, or N/A if desktop   |
| Alerts           | Any threshold alerts, or "None"    |

## Project Structure

```
health-monitor/
├── health_monitor.py            # Main script
├── health_log_YYYY-MM-DD.csv    # Auto-generated daily log files
└── HEALTH_MONITOR_README.md     # This file
```
