"""Test M (real site). Run on a machine with internet access:
    python3 tests/live_test.py [url] [seconds]
Prints live counters every 2 s, checks they grow, then tests STOP."""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scan_engine import ScanEngine, ScanConfig
import queue

url = sys.argv[1] if len(sys.argv) > 1 else "https://www.deadlinkchecker.com/website-dead-link-checker.asp"
run_for = float(sys.argv[2]) if len(sys.argv) > 2 else 40
eng = ScanEngine(ScanConfig(start_url=url, max_depth=5), events=queue.Queue())
eng.start(); t0 = time.time(); prev = None; stalls = 0; last_change = t0
while time.time() - t0 < run_for and not any(True for _ in []):
    time.sleep(2); s = eng.snapshot()
    key = (s["pages_scanned"], s["links_checked"])
    if key != prev: last_change = time.time()
    prev = key
    print("%5.1fs pages=%d queued=%d discovered=%d checked=%d ok=%d redir=%d broken=%d unver=%d" % (
        time.time() - t0, s["pages_scanned"], s["pages_queued"], s["links_discovered"], s["links_checked"],
        s["ok"], s["redirects"], s["broken"], s["unverified"]))
    print("       now:", s["current_pages"][:2])
    if time.time() - last_change > 15: stalls += 1; print("  !! no progress for 15s")
ts = time.time(); eng.stop()
while eng.is_running() if hasattr(eng, "is_running") else False: time.sleep(0.05)
ev = None
while True:
    try: ev = eng.events.get(timeout=10)
    except queue.Empty: break
    if ev[0] == "finished": break
print("STOP -> finished in %.2fs, event=%s, stalls=%d" % (time.time() - ts, ev, stalls))
