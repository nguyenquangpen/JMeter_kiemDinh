"""Ve bieu do minh hoa tu cac file ket qua JMeter (.jtl) -> thu muc images/."""
import csv
import json
import statistics as st
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
RES, IMG = ROOT / "results", ROOT / "images"
IMG.mkdir(exist_ok=True)
plt.rcParams.update({"figure.dpi": 110, "axes.grid": True, "grid.alpha": 0.3})


def load(name):
    with open(RES / f"{name}.jtl", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def over_time(name, title):
    rows = load(name)
    t0 = min(int(r["timeStamp"]) for r in rows)
    buckets = defaultdict(lambda: defaultdict(list))
    threads = defaultdict(int)
    for r in rows:
        sec = (int(r["timeStamp"]) - t0) // 1000
        buckets[r["label"]][sec].append(int(r["elapsed"]))
        threads[sec] = max(threads[sec], int(r["allThreads"]))
    fig, ax = plt.subplots(figsize=(11, 5))
    for label, b in sorted(buckets.items()):
        xs = sorted(b)
        ax.plot(xs, [st.mean(b[x]) for x in xs], marker=".", label=label)
    ax.set(title=title, xlabel="Thoi gian (giay)", ylabel="Response time trung binh (ms)")
    ax2 = ax.twinx()
    xs = sorted(threads)
    ax2.fill_between(xs, [threads[x] for x in xs], step="post", alpha=0.12, color="gray")
    ax2.set_ylabel("Active threads (vung xam)")
    ax2.grid(False)
    ax.legend(fontsize=8, loc="upper right")
    fig.tight_layout()
    fig.savefig(IMG / f"{name}_response_over_time.png")
    plt.close(fig)


def by_request(name, title):
    with open(RES / f"{name}-report" / "statistics.json", encoding="utf-8") as f:
        stats = json.load(f)
    labels = sorted(k for k in stats if k != "Total")
    avg = [stats[l]["meanResTime"] for l in labels]
    p90 = [round(stats[l]["pct1ResTime"]) for l in labels]
    fig, ax = plt.subplots(figsize=(11, 5))
    x = range(len(labels))
    ax.bar([i - 0.2 for i in x], avg, width=0.4, label="Average")
    ax.bar([i + 0.2 for i in x], p90, width=0.4, label="90th percentile")
    for i, (a, p) in enumerate(zip(avg, p90)):
        ax.text(i - 0.2, a, f"{a:.0f}", ha="center", va="bottom", fontsize=8)
        ax.text(i + 0.2, p, f"{p}", ha="center", va="bottom", fontsize=8)
    ax.set_xticks(list(x))
    ax.set_xticklabels([l.split(" (")[0] for l in labels], rotation=15, fontsize=8)
    ax.set(title=title, ylabel="Response time (ms)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(IMG / f"{name}_by_request.png")
    plt.close(fig)


def load_comparison():
    users, avg, p90, p95, thr = [], [], [], [], []
    for u in (10, 50, 100):
        # So lieu tong lay tu statistics.json do JMeter sinh ra cung HTML report
        with open(RES / f"load-{u}-report" / "statistics.json", encoding="utf-8") as f:
            total = json.load(f)["Total"]
        users.append(u)
        avg.append(total["meanResTime"])
        p90.append(total["pct1ResTime"])
        p95.append(total["pct2ResTime"])
        thr.append(total["throughput"])
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.5))
    a1.plot(users, avg, marker="o", label="Average")
    a1.plot(users, p90, marker="o", label="90th pct")
    a1.plot(users, p95, marker="o", label="95th pct")
    a1.set(title="Response time theo so luong user", xlabel="So user dong thoi", ylabel="ms", xticks=users)
    a1.legend()
    bars = a2.bar([str(u) for u in users], thr, color="tab:green")
    a2.bar_label(bars, fmt="%.1f")
    a2.set(title="Throughput theo so luong user", xlabel="So user dong thoi", ylabel="requests/giay")
    fig.tight_layout()
    fig.savefig(IMG / "load_comparison.png")
    plt.close(fig)


if __name__ == "__main__":
    over_time("web", "BlazeDemo Web - Response time theo thoi gian (20 users)")
    by_request("web", "BlazeDemo Web - Response time tung buoc")
    over_time("api", "JSONPlaceholder API - Response time theo thoi gian (30 users)")
    by_request("api", "JSONPlaceholder API - Response time tung endpoint")
    load_comparison()
    print("Charts saved to", IMG)
