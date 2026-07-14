"""Fix headings in generate_report.py to match original document format."""
import re

with open('generate_report.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Phase 1: Restructure chapter I into 1, 2, 3
content = content.replace(
    "add_heading('I. Introduction', level=1)",
    "add_heading('1. Introduction', level=2)",
    1
)

content = content.replace(
    "add_heading('1.2 Problem Statement', level=2)",
    "add_page_break()\nadd_heading('2. Problem Statement', level=2)",
    1
)

content = content.replace(
    "add_heading('1.3 Objectives', level=2)",
    "add_page_break()\nadd_heading('3. Objectives', level=2)",
    1
)

content = content.replace(
    "add_heading('1.3.1 Primary Objectives', level=3)",
    "add_heading('3.1 Primary Objectives', level=3)",
    1
)

content = content.replace(
    "add_heading('1.3.2 Secondary Objectives', level=3)",
    "add_heading('3.2 Secondary Objectives', level=3)",
    1
)

# Phase 2: Rename Roman numeral chapters to Arabic
replacements = {
    "add_heading('II. Tools and Technologies', level=1)": "add_heading('4. Tools and Technologies Used', level=2)",
    "add_heading('III. System Architecture', level=1)": "add_heading('5. System Architecture', level=2)",
    "add_heading('IV. Database Design', level=1)": "add_heading('6. Database Design', level=2)",
    "add_heading('V. Features Implemented', level=1)": "add_heading('7. Features Implemented', level=2)",
    "add_heading('VI. Implementation Details', level=1)": "add_heading('8. Implementation Details', level=2)",
    "add_heading('VII. Challenges and Solutions', level=1)": "add_heading('9. Challenges and Solutions', level=2)",
    "add_heading('VIII. Testing and Results', level=1)": "add_heading('10. Testing and Results', level=2)",
    "add_heading('IX. Conclusion and Future Work', level=1)": "add_heading('11. Conclusion and Future Work', level=2)",
    "add_heading('References', level=1)": "add_heading('12. References', level=2)",
}
for old, new in replacements.items():
    content = content.replace(old, new, 1)

# Phase 3: Sub-section headings level 2 -> 3
sub_replacements = {
    "add_heading('1.1 Background', level=2)": "add_heading('1.1 Background', level=3)",
    "add_heading('2.1 Backend Technologies', level=2)": "add_heading('4.1 Backend Technologies', level=3)",
    "add_heading('2.2 Frontend Technologies', level=2)": "add_heading('4.2 Frontend Technologies', level=3)",
    "add_heading('2.3 Development Tools', level=2)": "add_heading('4.3 Development Tools', level=3)",
    "add_heading('3.1 High-Level Architecture', level=2)": "add_heading('5.1 High-Level Architecture', level=3)",
    "add_heading('3.2 Request Flow', level=2)": "add_heading('5.2 Request Flow', level=3)",
    "add_heading('4.1 Schema Overview', level=2)": "add_heading('6.1 Schema Overview', level=3)",
    "add_heading('4.2 Entity Relationship Diagram', level=2)": "add_heading('6.2 Entity Relationship Diagram', level=3)",
    "add_heading('4.3 Migration from JSON to SQLite', level=2)": "add_heading('6.3 Migration from JSON to SQLite', level=3)",
    "add_heading('5.1 Multi-Country Support', level=2)": "add_heading('7.1 Multi-Country Support', level=3)",
    "add_heading('5.2 Internationalisation (11 Languages)', level=2)": "add_heading('7.2 Internationalisation (11 Languages)', level=3)",
    "add_heading('5.3 Passenger Booking Flow', level=2)": "add_heading('7.3 Passenger Booking Flow', level=3)",
    "add_heading('5.4 Real-Time Seat Map', level=2)": "add_heading('7.4 Real-Time Seat Map', level=3)",
    "add_heading('5.5 Agency Portal', level=2)": "add_heading('7.5 Agency Portal', level=3)",
    "add_heading('5.6 Ministry of Transport Portal', level=2)": "add_heading('7.6 Ministry of Transport Portal', level=3)",
    "add_heading('5.7 Subscription Monetisation', level=2)": "add_heading('7.7 Subscription Monetisation', level=3)",
    "add_heading('5.8 Departure Notification Scheduler', level=2)": "add_heading('7.8 Departure Notification Scheduler', level=3)",
    "add_heading('5.9 E-Ticket Generation', level=2)": "add_heading('7.9 E-Ticket Generation', level=3)",
    "add_heading('5.10 Commission System', level=2)": "add_heading('7.10 Commission System', level=3)",
    "add_heading('5.11 Flash Alert Categories', level=2)": "add_heading('7.11 Flash Alert Categories', level=3)",
    "add_heading('5.12 Flag-Coloured Hero Title', level=2)": "add_heading('7.12 Flag-Coloured Hero Title', level=3)",
    "add_heading('5.13 Responsive Design', level=2)": "add_heading('7.13 Responsive Design', level=3)",
    "add_heading('5.14 Security and Concurrency Hardening', level=2)": "add_heading('7.14 Security and Concurrency Hardening', level=3)",
    "add_heading('6.1 Project Structure', level=2)": "add_heading('8.1 Project Structure', level=3)",
    "add_heading('6.2 Key Code Patterns', level=2)": "add_heading('8.2 Key Code Patterns', level=3)",
    "add_heading('8.1 Testing Approach', level=2)": "add_heading('10.1 Testing Approach', level=3)",
    "add_heading('8.2 Route Verification', level=2)": "add_heading('10.2 Route Verification', level=3)",
    "add_heading('8.3 Migration Results', level=2)": "add_heading('10.3 Migration Results', level=3)",
    "add_heading('8.4 Additional Feature Tests', level=2)": "add_heading('10.4 Additional Feature Tests', level=3)",
    "add_heading('9.1 Summary of Achievements', level=2)": "add_heading('11.1 Summary of Achievements', level=3)",
    "add_heading('9.2 Future Improvements', level=2)": "add_heading('11.2 Future Improvements', level=3)",
}
for old, new in sub_replacements.items():
    content = content.replace(old, new, 1)

# Phase 4: Fix challenge sub-section numbering in the data list
challenge_fixes = {
    "'7.1 Data Redundancy in JSON Storage'": "'9.1 Data Redundancy in JSON Storage'",
    "'7.2 TOCTOU Race Conditions'": "'9.2 TOCTOU Race Conditions'",
    "'7.3 Booking Reference Counter Race'": "'9.3 Booking Reference Counter Race'",
    "'7.4 Concurrent Seat Booking'": "'9.4 Concurrent Seat Booking'",
    "'7.5 Free Departure Notification Delivery'": "'9.5 Free Departure Notification Delivery'",
    "'7.6 Multi-Language Translation Management'": "'9.6 Multi-Language Translation Management'",
    "'7.7 Agency Privacy'": "'9.7 Agency Privacy'",
    "'7.8 Other Challenges'": "'9.8 Other Challenges'",
}
for old, new in challenge_fixes.items():
    content = content.replace(old, new)

# Phase 5: Fix challenge heading level (loop variable) from level=2 to level=3
content = content.replace("add_heading(title, level=2)", "add_heading(title, level=3)")

# Phase 6: Fix TOC items
toc_fixes = {
    "'I. Introduction'": "'1. Introduction'",
    "'II. Tools and Technologies'": "'4. Tools and Technologies Used'",
    "'III. System Architecture'": "'5. System Architecture'",
    "'IV. Database Design'": "'6. Database Design'",
    "'V. Features Implemented'": "'7. Features Implemented'",
    "'VI. Implementation Details'": "'8. Implementation Details'",
    "'VII. Challenges and Solutions'": "'9. Challenges and Solutions'",
    "'VIII. Testing and Results'": "'10. Testing and Results'",
    "'IX. Conclusion and Future Work'": "'11. Conclusion and Future Work'",
}
for old, new in toc_fixes.items():
    content = content.replace(old, new)

with open('generate_report.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("All heading fixes applied successfully.")
