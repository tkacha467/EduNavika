# EduNavika — Milestone 2.5: OCR Coverage Audit Report

## Executive Summary

| Metric | Count |
| :--- | :--- |
| **Total Documents Audited** | 86 |
| **Total Pages Across Dataset** | 14252 |
| **Text-Dominant Documents** | 25 |
| **OCR-Required Documents (Image/Outline Scans)** | 61 |
| **Hybrid Documents** | 0 |
| **Total Text-Extracted Pages** | 4587 |
| **Total OCR-Required Pages** | 9665 |
| **Dataset OCR Ratio** | 67.82% |

## Manifest Inconsistencies & Notes

- ⚠️ Std-11_Bilology_EnglishMedium.pdf: Manifest marked REQUIRED but sample indicates text is selectable
- ⚠️ Std-11_Economics_SelfLearningBook _EnglishMedium.pdf: Manifest marked NONE but sample indicates scanned pages requiring OCR
- ⚠️ Std-11_Hornbill_EnglishMedium.pdf: Manifest marked REQUIRED but sample indicates text is selectable
- ⚠️ Std-12_Biology Lab Manual_EnglishM.pdf: Manifest marked NONE but sample indicates scanned pages requiring OCR
- ⚠️ Std-12 Chemistry Part-2_EnglishMedium.pdf: Manifest marked REQUIRED but sample indicates text is selectable
- ⚠️ Std-12_Chemistry Part-1_EnglishMedium.pdf: Manifest marked REQUIRED but sample indicates text is selectable
- ⚠️ Std-12_Economics_SelfLearningBook _EnglishMedium.pdf: Manifest marked NONE but sample indicates scanned pages requiring OCR
- ⚠️ Std-12_Kaleidoscope_EnglishMedium.pdf: Manifest marked REQUIRED but sample indicates text is selectable
- ⚠️ Std-12_Vistas-English Suppl Reader Core.pdf: Manifest marked REQUIRED but sample indicates text is selectable
- ⚠️ Std-9 Beehive Textbook In English.pdf: Manifest marked REQUIRED but sample indicates text is selectable
- ⚠️ Std-9_Moments English Suppl Reader Course-B.pdf: Manifest marked REQUIRED but sample indicates text is selectable

## Document OCR Coverage Breakdown

| Standard | Subject | Filename | Pages | Extracted | OCR Req | OCR % | Status |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| 10 | 10 Black-Buck Supplementry Reader | `Std-10_Black-Buck_Supplementry_Reader.pdf` | 112 | 0 | 112 | 100.0% | **OCR_REQUIRED** |
| 10 | Computer Studies | `Std-10_ComputerStudies_EnglishMedium.pdf` | 320 | 0 | 320 | 100.0% | **OCR_REQUIRED** |
| 10 | Commerce & Economics | `Std-10_English Second Language.pdf` | 154 | 0 | 154 | 100.0% | **OCR_REQUIRED** |
| 10 | English Literature & Language | `Std-10_First Flight_EnglishMedium.pdf` | 154 | 154 | 0 | 0.0% | **TEXT_DOMINANT** |
| 10 | English Literature & Language | `Std-10_Footprints Without Feet_EM.pdf` | 86 | 86 | 0 | 0.0% | **TEXT_DOMINANT** |
| 10 | Mathematics | `Std-10_Maths_EnglishMedium.pdf` | 278 | 278 | 0 | 0.0% | **TEXT_DOMINANT** |
| 10 | English Literature & Language | `Std-10_Sanskrut_EnglishMedium.pdf` | 130 | 0 | 130 | 100.0% | **OCR_REQUIRED** |
| 10 | Science & Technology | `Std-10_Science_English Medium.pdf` | 234 | 234 | 0 | 0.0% | **TEXT_DOMINANT** |
| 10 | English Literature & Language | `Std-10_ShrimadBhagwatGita_EnglishM.pdf` | 16 | 0 | 16 | 100.0% | **OCR_REQUIRED** |
| 10 | Science & Technology | `Std-10_Social_Science_EnglishMedium.pdf` | 206 | 0 | 206 | 100.0% | **OCR_REQUIRED** |
| 10 | 10 Word and Expressions-2 Eng | `Std-10_Word and Expressions-2_Eng.pdf` | 156 | 125 | 31 | 20.0% | **TEXT_DOMINANT** |
| 10 | 10 Yoga, Health and Physical Education Eng M | `Std_10_Yoga, Health and Physical Education_Eng_M.pdf` | 114 | 0 | 114 | 100.0% | **OCR_REQUIRED** |
| 11 | Science & Technology | `BIOLOGY PRACITAL REORD BOOK (JOURNAL).pdf` | 78 | 0 | 78 | 100.0% | **OCR_REQUIRED** |
| 11 | Science & Technology | `CHEMISTRY PRACTICAL RECORED BOOK (JOURNAL).pdf` | 110 | 0 | 110 | 100.0% | **OCR_REQUIRED** |
| 11 | Science & Technology | `PHYSICS PRACTICAL RECORD BOOK (JOURNAL).pdf` | 94 | 0 | 94 | 100.0% | **OCR_REQUIRED** |
| 11 | Science & Technology | `Std-11_Chemistry Lab Manual_EngM.pdf` | 174 | 0 | 174 | 100.0% | **OCR_REQUIRED** |
| 11 | Science & Technology | `Std-11_Laboratory Manual Biology_EnglishM.pdf` | 102 | 0 | 102 | 100.0% | **OCR_REQUIRED** |
| 11 | Science & Technology | `Std-11_Physics Laboratory Manual_EnglishM.pdf` | 286 | 0 | 286 | 100.0% | **OCR_REQUIRED** |
| 11 | English Literature & Language | `Std-11_Bilology_EnglishMedium.pdf` | 266 | 266 | 0 | 0.0% | **TEXT_DOMINANT** |
| 11 | Science & Technology | `Std-11_Chemistry Part-1_English Medium.pdf` | 254 | 254 | 0 | 0.0% | **TEXT_DOMINANT** |
| 11 | Science & Technology | `Std-11_Chemistry Part-2_English Medium.pdf` | 110 | 110 | 0 | 0.0% | **TEXT_DOMINANT** |
| 11 | Mathematics | `Std-11_Maths_EnglishMedium.pdf` | 376 | 376 | 0 | 0.0% | **TEXT_DOMINANT** |
| 11 | Science & Technology | `Std-11_Physics Part 1_English Medium.pdf` | 186 | 186 | 0 | 0.0% | **TEXT_DOMINANT** |
| 11 | Science & Technology | `Std-11_Physics Part 2_English Medium.pdf` | 164 | 132 | 32 | 20.0% | **TEXT_DOMINANT** |
| 11 | Commerce & Economics | `Std-11_Economics_SelfLearningBook _EnglishMedium.pdf` | 188 | 0 | 188 | 100.0% | **OCR_REQUIRED** |
| 11 | English Literature & Language | `Std-11 Flamingo_Supplementry_Reader.pdf` | 110 | 0 | 110 | 100.0% | **OCR_REQUIRED** |
| 11 | Commerce & Economics | `Std-11 Statistics_English Medium.pdf` | 320 | 0 | 320 | 100.0% | **OCR_REQUIRED** |
| 11 | Social Science & Humanities | `Std-11-Geography_Eng_M.pdf` | 146 | 0 | 146 | 100.0% | **OCR_REQUIRED** |
| 11 | English Literature & Language | `Std-11-Psaychology EnglishMedium.pdf` | 130 | 0 | 130 | 100.0% | **OCR_REQUIRED** |
| 11 | Commerce & Economics | `Std-11_Commercial Organization and Management_Eng_M.pdf` | 138 | 28 | 110 | 80.0% | **OCR_REQUIRED** |
| 11 | Computer Studies | `STD-11_COMPUTER_STUDIES_EnglishMedium.pdf` | 188 | 0 | 188 | 100.0% | **OCR_REQUIRED** |
| 11 | Commerce & Economics | `Std-11_Elements of Book Keeping and Accountancy Part-1_Eng_M.pdf` | 314 | 0 | 314 | 100.0% | **OCR_REQUIRED** |
| 11 | Commerce & Economics | `Std-11_Elements of Book Keeping and Accountancy Part-2_Eng_M.pdf` | 330 | 0 | 330 | 100.0% | **OCR_REQUIRED** |
| 11 | Social Science & Humanities | `STD-11_HISTORY_English Medium.pdf` | 154 | 0 | 154 | 100.0% | **OCR_REQUIRED** |
| 11 | English Literature & Language | `Std-11_Hornbill_EnglishMedium.pdf` | 118 | 118 | 0 | 0.0% | **TEXT_DOMINANT** |
| 11 | Mathematics | `Std-11_Maths_EnglishMedium.pdf` | 376 | 376 | 0 | 0.0% | **TEXT_DOMINANT** |
| 11 | English Literature & Language | `Std-11_ShrimadBhagwatGita_EnglishM.pdf` | 16 | 0 | 16 | 100.0% | **OCR_REQUIRED** |
| 11 | English Literature & Language | `Std-11_Sociology English Medium.pdf` | 82 | 0 | 82 | 100.0% | **OCR_REQUIRED** |
| 11 | English Literature & Language | `Std-11_Yog Health EnglishMedium.pdf` | 138 | 0 | 138 | 100.0% | **OCR_REQUIRED** |
| 11 | Commerce & Economics | `Std_11_Commercial Correspondance and Secretarial Practice_Eng_M.pdf` | 144 | 0 | 144 | 100.0% | **OCR_REQUIRED** |
| 11 | Commerce & Economics | `Std_11_Economics_English_Medium.pdf` | 150 | 0 | 150 | 100.0% | **OCR_REQUIRED** |
| 11 | Science & Technology | `Std_11_Political Science_English Medium.pdf` | 96 | 0 | 96 | 100.0% | **OCR_REQUIRED** |
| 11 | Sanskrit Literature | `Std_11_Sanskrit_Eng_M.pdf` | 115 | 0 | 115 | 100.0% | **OCR_REQUIRED** |
| 12 | Science & Technology | `12_CHEMISTRY-JOURNAL.pdf` | 124 | 0 | 124 | 100.0% | **OCR_REQUIRED** |
| 12 | Science & Technology | `12_PHYSICS-JOURNAL.pdf` | 100 | 20 | 80 | 80.0% | **OCR_REQUIRED** |
| 12 | Science & Technology | `Std-12_Biology Lab Manual_EnglishM.pdf` | 100 | 0 | 100 | 100.0% | **OCR_REQUIRED** |
| 12 | Science & Technology | `Std-12 Chemistry Part-2_EnglishMedium.pdf` | 164 | 132 | 32 | 20.0% | **TEXT_DOMINANT** |
| 12 | Science & Technology | `Std-12_Biology_EnglishMedium.pdf` | 240 | 192 | 48 | 20.0% | **TEXT_DOMINANT** |
| 12 | Science & Technology | `Std-12_Chemistry Part-1_EnglishMedium.pdf` | 172 | 138 | 34 | 20.0% | **TEXT_DOMINANT** |
| 12 | Mathematics | `Std-12_Maths-Part1_EnglishMedium.pdf` | 236 | 189 | 47 | 20.0% | **TEXT_DOMINANT** |
| 12 | Mathematics | `Std-12_Maths-Part2_EnglishMedium.pdf` | 248 | 199 | 49 | 20.0% | **TEXT_DOMINANT** |
| 12 | Science & Technology | `Std-12_Physics Part-1_English Medium.pdf` | 235 | 188 | 47 | 20.0% | **TEXT_DOMINANT** |
| 12 | Science & Technology | `Std-12_Physics Part-2_English Medium.pdf` | 152 | 122 | 30 | 20.0% | **TEXT_DOMINANT** |
| 12 | Commerce & Economics | `Std-12_Economics_SelfLearningBook _EnglishMedium.pdf` | 216 | 0 | 216 | 100.0% | **OCR_REQUIRED** |
| 12 | Commerce & Economics | `Std-12 Commercial Cooresponda...Secretarial Practice E.M..pdf` | 168 | 0 | 168 | 100.0% | **OCR_REQUIRED** |
| 12 | Commerce & Economics | `Std-12 Commercial Organization and Management E.M..pdf` | 160 | 0 | 160 | 100.0% | **OCR_REQUIRED** |
| 12 | Commerce & Economics | `Std-12 Elements of Accounts Part-1 E.M..pdf` | 336 | 0 | 336 | 100.0% | **OCR_REQUIRED** |
| 12 | Commerce & Economics | `Std-12 Elements of Accounts Part-2 E.M..pdf` | 304 | 0 | 304 | 100.0% | **OCR_REQUIRED** |
| 12 | Social Science & Humanities | `Std-12 Geography E.M.pdf` | 121 | 0 | 121 | 100.0% | **OCR_REQUIRED** |
| 12 | 12 Lapwing  Supplementry Reader | `Std-12 Lapwing__Supplementry_Reader.pdf` | 101 | 0 | 101 | 100.0% | **OCR_REQUIRED** |
| 12 | 12 Psychology E.M | `Std-12 Psychology E.M.pdf` | 144 | 0 | 144 | 100.0% | **OCR_REQUIRED** |
| 12 | Sanskrit Literature | `Std-12 Sanskrit E.M.pdf` | 120 | 0 | 120 | 100.0% | **OCR_REQUIRED** |
| 12 | 12 Sociology E.M | `Std-12 Sociology E.M.pdf` | 118 | 0 | 118 | 100.0% | **OCR_REQUIRED** |
| 12 | English Literature & Language | `Std-12 Sociology English Medium.pdf` | 116 | 0 | 116 | 100.0% | **OCR_REQUIRED** |
| 12 | Commerce & Economics | `Std-12 Statistics Part-1 E.M.pdf` | 200 | 0 | 200 | 100.0% | **OCR_REQUIRED** |
| 12 | Commerce & Economics | `Std-12 Statistics Part-2 E.M.pdf` | 216 | 0 | 216 | 100.0% | **OCR_REQUIRED** |
| 12 | 12 Yoga Health and Physical Education E.M | `Std-12 Yoga Health and Physical Education E.M.pdf` | 112 | 0 | 112 | 100.0% | **OCR_REQUIRED** |
| 12 | Computer Studies | `STD-12_COMPUTER_STUDIES_ENG.pdf` | 288 | 0 | 288 | 100.0% | **OCR_REQUIRED** |
| 12 | Commerce & Economics | `Std-12_Economics_English Medium.pdf` | 162 | 0 | 162 | 100.0% | **OCR_REQUIRED** |
| 12 | Social Science & Humanities | `STD-12_HISTORY_English Medium.pdf` | 154 | 0 | 154 | 100.0% | **OCR_REQUIRED** |
| 12 | English Literature & Language | `Std-12_Kaleidoscope_EnglishMedium.pdf` | 248 | 248 | 0 | 0.0% | **TEXT_DOMINANT** |
| 12 | English Literature & Language | `Std-12_Lapwimg English Medium.pdf` | 100 | 0 | 100 | 100.0% | **OCR_REQUIRED** |
| 12 | English Literature & Language | `Std-12_psaychology English Medium.pdf` | 144 | 0 | 144 | 100.0% | **OCR_REQUIRED** |
| 12 | English Literature & Language | `Std-12_ShrimadBhagwatGita_EnglishM.pdf` | 16 | 0 | 16 | 100.0% | **OCR_REQUIRED** |
| 12 | English Literature & Language | `Std-12_Vistas-English Suppl Reader Core.pdf` | 74 | 74 | 0 | 0.0% | **TEXT_DOMINANT** |
| 9 | English Literature & Language | `Std-09_ShrimadBhagwatGita_EnglishM.pdf` | 16 | 0 | 16 | 100.0% | **OCR_REQUIRED** |
| 9 | English Literature & Language | `Std-9 Beehive Textbook In English.pdf` | 122 | 122 | 0 | 0.0% | **TEXT_DOMINANT** |
| 9 | Computer Studies | `Std-9 Computer Studies EnglishMedium.pdf` | 194 | 0 | 194 | 100.0% | **OCR_REQUIRED** |
| 9 | Sanskrit Literature | `Std-9 Sanskrit E.M.pdf` | 122 | 0 | 122 | 100.0% | **OCR_REQUIRED** |
| 9 | Science & Technology | `Std-9 Social_Science_EnglishMedium.pdf` | 174 | 0 | 174 | 100.0% | **OCR_REQUIRED** |
| 9 | 9 Yoga Health and Physical Education EM | `Std-9 Yoga Health and Physical Education EM.pdf` | 130 | 0 | 130 | 100.0% | **OCR_REQUIRED** |
| 9 | 9 Dolhin Supplementry Reader | `Std-9_Dolhin_Supplementry_Reader.pdf` | 118 | 0 | 118 | 100.0% | **OCR_REQUIRED** |
| 9 | English Literature & Language | `Std-9_Farsi Parshian_EnglishMedium.pdf` | 100 | 0 | 100 | 100.0% | **OCR_REQUIRED** |
| 9 | Mathematics | `Std-9_Maths_English Medium.pdf` | 234 | 0 | 234 | 100.0% | **OCR_REQUIRED** |
| 9 | English Literature & Language | `Std-9_Moments English Suppl Reader Course-B.pdf` | 73 | 73 | 0 | 0.0% | **TEXT_DOMINANT** |
| 9 | Science & Technology | `Std-9_Science_English Medium.pdf` | 167 | 167 | 0 | 0.0% | **TEXT_DOMINANT** |