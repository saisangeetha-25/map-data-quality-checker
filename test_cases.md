# Map Data Quality Checker
## Test Case Documentation

### 1. Project Overview

The Map Data Quality Checker is a Python-based tool designed to validate geographical location datasets and identify data quality issues.

The project performs six validation checks on location records, generates structured defect reports, summarizes test execution results, and visualizes flagged geographical locations using an interactive map.

**Technologies Used:**
- Python
- Pandas
- Folium
- CSV
- Git and GitHub

### 2. Testing Objectives

The main objectives of testing are:

- Verify that mandatory location information is available.
- Validate latitude and longitude values.
- Identify locations outside the configured Hyderabad geographical boundaries.
- Detect duplicate places within a specified distance.
- Identify inconsistent category labels.
- Detect improper place name formatting.
- Generate accurate defect reports and test summaries.

### 3. Test Environment

| Component | Details |
|---|---|
| Programming Language | Python |
| Data Processing | Pandas |
| Map Visualization | Folium |
| Input Format | CSV |
| Operating System | Windows |
| Development Environment | Visual Studio Code |
| Geographical Region | Hyderabad, Telangana, India |
| Duplicate Detection Threshold | 50 metres |

### 4. Test Cases

#### TC01 – Required Fields Validation

**Test Case ID:** QC01

**Objective:** Verify that all mandatory fields contain valid information.

**Fields Checked:**
- Name
- Latitude
- Longitude
- Category

**Test Procedure:**
1. Load the location dataset.
2. Check each record for missing or empty mandatory fields.
3. Identify records containing missing information.
4. Log the identified defects.

**Expected Result:**

Records containing missing or empty mandatory fields should be flagged.

**Severity:** High

---

#### TC02 – Coordinate Validation

**Test Case ID:** QC02

**Objective:** Verify that latitude and longitude values are geographically valid.

**Test Procedure:**
1. Read latitude and longitude values.
2. Convert coordinate values into numeric format.
3. Check whether latitude falls between -90 and 90.
4. Check whether longitude falls between -180 and 180.
5. Identify coordinates containing invalid values.
6. Identify coordinates with both latitude and longitude equal to 0.

**Expected Result:**

Records containing invalid coordinates, non-numeric values, missing coordinates, or (0,0) should be flagged.

**Severity:** High

---

#### TC03 – Hyderabad Geographical Boundary Validation

**Test Case ID:** QC03

**Objective:** Identify locations outside the configured Hyderabad geographical bounding box.

**Configured Boundaries:**
- Minimum Latitude: 17.20
- Maximum Latitude: 17.65
- Minimum Longitude: 78.20
- Maximum Longitude: 78.70

**Test Procedure:**
1. Read the latitude and longitude of each record.
2. Verify that the coordinates are valid.
3. Compare the coordinates against the configured geographical boundaries.
4. Identify records outside the specified boundaries.
5. Log the identified defects.

**Expected Result:**

Locations outside the configured Hyderabad bounding box should be flagged.

**Severity:** Medium

---

#### TC04 – Duplicate Place Detection

**Test Case ID:** QC04

**Objective:** Identify potentially duplicated places within a distance of 50 metres.

**Test Procedure:**
1. Read place names and geographical coordinates.
2. Normalize place names by removing leading and trailing spaces and converting them to lowercase.
3. Group records with matching normalized place names.
4. Calculate the geographical distance between matching records using the Haversine formula.
5. Identify matching places located within 50 metres of each other.
6. Record the duplicate information in the defect report.

**Expected Result:**

Places with matching normalized names and geographical coordinates within 50 metres should be flagged as potential duplicates.

**Severity:** Medium

---

#### TC05 – Category Label Consistency Validation

**Test Case ID:** QC05

**Objective:** Identify inconsistent formatting of category labels.

**Test Procedure:**
1. Read category values from the dataset.
2. Normalize category labels by removing leading and trailing spaces and converting them to lowercase.
3. Group equivalent category labels.
4. Identify the most frequently occurring original label format within each normalized category group.
5. Compare individual category values against the selected standard format.
6. Log inconsistent category labels.

**Example:**

| Category Values | Expected Standard |
|---|---|
| Restaurant | Restaurant |
| restaurant | Restaurant |
| RESTAURANT | Restaurant |
| Restaurant (with trailing space) | Restaurant |

**Expected Result:**

Category labels that differ from the selected standard representation should be flagged.

**Severity:** Low

---

#### TC06 – Place Name Formatting Validation

**Test Case ID:** QC06

**Objective:** Identify improperly formatted place names.

**Test Procedure:**
1. Read place names from the dataset.
2. Check whether names contain unnecessary leading or trailing spaces.
3. Check whether names are entirely in uppercase.
4. Identify uppercase names containing more than three characters.
5. Log records containing formatting issues.

**Expected Result:**

Place names containing leading or trailing spaces or entirely uppercase names longer than three characters should be flagged.

**Severity:** Low

---

### 5. Test Execution Summary

The project generates an automated test execution summary in `test_summary.csv`.

The summary includes:

| Test Case ID | Validation Area | Result |
|---|---|---|
| QC01 | Required Fields Validation | PASS / FAIL |
| QC02 | Coordinate Validation | PASS / FAIL |
| QC03 | Hyderabad Boundary Validation | PASS / FAIL |
| QC04 | Duplicate Place Detection | PASS / FAIL |
| QC05 | Category Consistency Validation | PASS / FAIL |
| QC06 | Name Formatting Validation | PASS / FAIL |

**Result Interpretation:**

- PASS: No defects were identified by the corresponding validation check.
- FAIL: One or more defects were identified by the corresponding validation check.

### 6. Defect Documentation

All identified defects are automatically recorded in `defect_report.csv`.

The defect report contains:

| Field | Description |
|---|---|
| Defect ID | Unique identifier assigned to each logged defect |
| Check ID | Associated validation test case |
| Check Name | Name of the validation check |
| Severity | High, Medium or Low |
| Record ID | Identifier of the affected location |
| Name | Name of the affected place |
| Latitude | Latitude of the affected location |
| Longitude | Longitude of the affected location |
| Expected | Expected data quality condition |
| Actual | Actual condition identified during validation |

### 7. Geographical Visualization

The project generates an interactive geographical map named `flagged_map.html` using Folium.

The map provides:

- Visual representation of location records.
- Green markers for records not flagged.
- Red markers for records identified as defective.
- Interactive location markers with place information.
- Zoom and geographical navigation functionality.

### 8. Expected Project Outputs

After successful execution, the project generates the following files:

| Output File | Description |
|---|---|
| defect_report.csv | Contains identified data quality defects |
| test_summary.csv | Contains test execution results |
| flagged_map.html | Interactive map displaying location records |

### 9. Testing Conclusion

The Map Data Quality Checker provides an automated approach to validating geographical location datasets.

It performs six data quality checks, identifies potential defects, generates structured defect documentation, summarizes validation results, and visualizes flagged locations on an interactive map.

The project demonstrates practical understanding of Python-based data validation, geospatial data analysis, test case design, defect documentation, and map data quality verification.

### 10. Project Limitations

- Geographical validation uses a predefined Hyderabad bounding box rather than an official administrative boundary polygon.
- Duplicate detection identifies matching normalized place names within 50 metres; it does not identify every possible duplicate.
- Category consistency uses the most frequent original label representation within each normalized category group.
- Name formatting validation checks leading/trailing spaces and entirely uppercase names longer than three characters.
- Map visualization displays records with usable numeric coordinates, including records that may have other validation defects.

These limitations can be addressed through future enhancements.