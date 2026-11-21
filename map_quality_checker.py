"""
Map Data Quality Checker
Validates a location/POI dataset (id, name, lat, lon, category, address),
logs defects in a test-case style report, and plots flagged points on a map.

Usage:
    python map_quality_checker.py --demo              # run on generated sample data
    python map_quality_checker.py --input places.csv  # run on your own CSV
"""
import argparse
import math
import random

import pandas as pd

# Hyderabad bounding box: lat_min, lat_max, lon_min, lon_max
BBOX = (17.20, 17.65, 78.20, 78.70)
REQUIRED = ["name", "lat", "lon", "category"]
DUP_RADIUS_M = 50


def haversine_m(lat1, lon1, lat2, lon2):
    r = 6371000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def make_demo(path="sample_places.csv", n=200):
    random.seed(7)
    cats = ["Restaurant", "Hospital", "ATM", "School", "Fuel Station"]
    rows = []
    for i in range(n):
        rows.append([i, f"Place {i}", round(random.uniform(17.30, 17.55), 6),
                     round(random.uniform(78.30, 78.60), 6), random.choice(cats), f"Street {i}, Hyderabad"])
    df = pd.DataFrame(rows, columns=["id", "name", "lat", "lon", "category", "address"])
    df.loc[3, "name"] = None                                  # missing name
    df.loc[10, "lat"] = 95.0                                  # invalid latitude
    df.loc[15, ["lat", "lon"]] = [28.61, 77.20]               # outside Hyderabad
    df.loc[20, ["lat", "lon"]] = [0.0, 0.0]                   # null island
    df.loc[30, "category"] = "restaurant "                    # inconsistent label
    df.loc[31, "category"] = "HOSPITAL"                       # inconsistent label
    df.loc[40, "name"] = "  " + df.loc[40, "name"].upper()    # bad formatting
    df.loc[50, ["name", "lat", "lon"]] = [df.loc[49, "name"], df.loc[49, "lat"] + 0.0001, df.loc[49, "lon"]]  # duplicate
    df.to_csv(path, index=False)
    return path


def run_checks(df):
    defects = []

    def log(check, name, sev, row, expected, actual):
        defects.append({"Check_ID": check, "Check_Name": name, "Severity": sev,
                        "Record_ID": row.get("id"), "Name": row.get("name"),
                        "Lat": row.get("lat"), "Lon": row.get("lon"),
                        "Expected": expected, "Actual": actual})

    df = df.copy()
    df["lat_n"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lon_n"] = pd.to_numeric(df["lon"], errors="coerce")

    for _, r in df.iterrows():
        row = r.to_dict()
        # QC01 required fields
        missing = [c for c in REQUIRED if pd.isna(r[c]) or str(r[c]).strip() == ""]
        if missing:
            log("QC01", "Required fields present", "High", row, "No missing fields", f"Missing: {', '.join(missing)}")
        # QC02 coordinate validity
        if pd.isna(r.lat_n) or pd.isna(r.lon_n) or not (-90 <= r.lat_n <= 90 and -180 <= r.lon_n <= 180) \
                or (r.lat_n == 0 and r.lon_n == 0):
            log("QC02", "Valid coordinates", "High", row, "Lat -90..90, Lon -180..180, not 0,0", f"{r['lat']}, {r['lon']}")
        # QC03 within region
        elif not (BBOX[0] <= r.lat_n <= BBOX[1] and BBOX[2] <= r.lon_n <= BBOX[3]):
            log("QC03", "Inside Hyderabad bounds", "Medium", row, "Point inside Hyderabad bbox", f"{r['lat']}, {r['lon']}")
        # QC06 name formatting
        nm = r["name"]
        if isinstance(nm, str) and (nm != nm.strip() or (nm.isupper() and len(nm) > 3)):
            log("QC06", "Name formatting", "Low", row, "Trimmed, not ALL CAPS", repr(nm))

    # QC04 duplicates: same normalized name within DUP_RADIUS_M
    valid = df.dropna(subset=["name", "lat_n", "lon_n"]).copy()
    valid["key"] = valid["name"].astype(str).str.strip().str.lower()
    for _, grp in valid.groupby("key"):
        pts = grp.to_dict("records")
        for i in range(len(pts)):
            for j in range(i + 1, len(pts)):
                d = haversine_m(pts[i]["lat_n"], pts[i]["lon_n"], pts[j]["lat_n"], pts[j]["lon_n"])
                if d <= DUP_RADIUS_M:
                    log("QC04", "No duplicate places", "Medium", pts[j], "Unique place",
                        f"Duplicate of id {pts[i].get('id')} ({d:.0f} m apart)")

    # QC05 category label consistency
    cats = df["category"].dropna().astype(str)
    norm = cats.str.strip().str.lower()
    canonical = cats.groupby(norm).agg(lambda s: s.value_counts().index[0])
    for idx, val in cats.items():
        std = canonical[val.strip().lower()]
        if val != std:
            log("QC05", "Consistent category labels", "Low", df.loc[idx].to_dict(), f"'{std}'", repr(val))

    return pd.DataFrame(defects)


def summarize(df, defects):
    names = {"QC01": "Required fields present", "QC02": "Valid coordinates", "QC03": "Inside Hyderabad bounds",
             "QC04": "No duplicate places", "QC05": "Consistent category labels", "QC06": "Name formatting"}
    rows = []
    for k, v in names.items():
        fails = int((defects["Check_ID"] == k).sum()) if not defects.empty else 0
        rows.append({"Check_ID": k, "Check_Name": v, "Records_Checked": len(df),
                     "Failures": fails, "Result": "FAIL" if fails else "PASS"})
    return pd.DataFrame(rows)


def make_map(df, defects, out="flagged_map.html"):
    try:
        import folium
    except ImportError:
        print("folium not installed (pip install folium); skipping map.")
        return
    d = df.copy()
    d["lat_n"] = pd.to_numeric(d["lat"], errors="coerce")
    d["lon_n"] = pd.to_numeric(d["lon"], errors="coerce")
    d = d.dropna(subset=["lat_n", "lon_n"])
    m = folium.Map(location=[17.385, 78.4867], zoom_start=11)
    flagged = set(defects["Record_ID"]) if not defects.empty else set()
    for _, r in d.iterrows():
        bad = r["id"] in flagged
        folium.CircleMarker([r.lat_n, r.lon_n], radius=5 if bad else 3,
                            color="red" if bad else "green", fill=True,
                            tooltip=f"{r['name']} ({'FLAGGED' if bad else 'OK'})").add_to(m)
    m.save(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", help="CSV with columns: id,name,lat,lon,category,address")
    ap.add_argument("--demo", action="store_true", help="generate and use sample data")
    a = ap.parse_args()
    path = make_demo() if a.demo or not a.input else a.input
    
    try:
        df = pd.read_csv(path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        df = pd.read_csv(path, encoding="cp1252", encoding_errors="replace")
    if "id" not in df.columns:
        df.insert(0, "id", range(len(df)))
    defects = run_checks(df)
    if not defects.empty:
        defects.insert(0, "Defect_ID", [f"DEF-{i+1:03d}" for i in range(len(defects))])
    summary = summarize(df, defects)
    defects.to_csv("defect_report.csv", index=False)
    summary.to_csv("test_summary.csv", index=False)
    make_map(df, defects)
    print(summary.to_string(index=False))
    print(f"\n{len(defects)} defects logged -> defect_report.csv | map -> flagged_map.html")


if __name__ == "__main__":
    main()
