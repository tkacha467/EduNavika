"""
Additional canonical curriculum questions for GSEB Standard 10 subjects:
- Social Science
- Computer Studies
- Yoga, Health and Physical Education
- Black-Buck Supplementary Reader
- Commerce & Economics
- Sanskrit
- Shrimad Bhagwat Gita
"""

from typing import Dict, List, Any

ADDITIONAL_CURRICULUM_BANK: Dict[str, List[Dict[str, Any]]] = {
    # -------------------------------------------------------------------------
    # Social Science: 1.1 Meaning and Cultural Heritage of India
    # -------------------------------------------------------------------------
    "f935fc42-3d29-4a6c-8ba7-68a8eb66fb06": [
        {
            "id": "sst-ch1-f01",
            "topic_id": "f935fc42-3d29-4a6c-8ba7-68a8eb66fb06",
            "topic_title": "1.1 Meaning and Cultural Heritage of India",
            "subject": "Social Science",
            "chapter": "Heritage of India",
            "difficulty": "FOUNDATIONAL",
            "question": "What is the primary definition of 'Heritage' in the context of Indian culture?",
            "options": [
                "A valuable and precious gift handed down to us from our ancestors",
                "Only the modern technological inventions created in the 21st century",
                "Foreign artifacts imported into a country during colonial trade",
                "Temporary natural changes occurring during the monsoon season"
            ],
            "correct_answer": "A valuable and precious gift handed down to us from our ancestors",
            "explanation": "Heritage means a valuable gift from our ancestors to us, encompassing cultural values, arts, customs, and monuments handed down through generations (Textbook Page 1).",
            "source_document": "STD-10/Std-10_Social_Science_EnglishMedium.pdf",
            "source_page": 1,
            "source_chunk_id": "chunk_social_science_1_1",
            "source_text": "Heritage means a valuable and precious gift from our ancestors to us in Indian culture, handed down through generations.",
            "skill_target": "Meaning and Scope of Cultural Heritage"
        },
        {
            "id": "sst-ch1-g01",
            "topic_id": "f935fc42-3d29-4a6c-8ba7-68a8eb66fb06",
            "topic_title": "1.1 Meaning and Cultural Heritage of India",
            "subject": "Social Science",
            "chapter": "Heritage of India",
            "difficulty": "GUIDED",
            "question": "Which of the following is an example of India's cultural heritage?",
            "options": [
                "Literature, architecture, philosophy, and traditional social customs",
                "Only natural mountains and perennial river streams",
                "Underground mineral deposits that formed before human history",
                "Atmospheric meteorological cycles like the El Niño phenomenon"
            ],
            "correct_answer": "Literature, architecture, philosophy, and traditional social customs",
            "explanation": "Cultural heritage is man-made heritage comprising intellect, art, literature, sculpture, and philosophy inherited through social tradition (Textbook Page 1).",
            "source_document": "STD-10/Std-10_Social_Science_EnglishMedium.pdf",
            "source_page": 1,
            "source_chunk_id": "chunk_social_science_1_1",
            "source_text": "Our cultural heritage includes literature, sculpture, architecture, philosophy, religion, and traditional social customs.",
            "skill_target": "Classification of Cultural Heritage"
        }
    ],

    # -------------------------------------------------------------------------
    # Social Science: 8.1 Types and Uses of Resources
    # -------------------------------------------------------------------------
    "8d0a9374-5b13-4a43-8eaf-724097434eec": [
        {
            "id": "sst-ch8-f01",
            "topic_id": "8d0a9374-5b13-4a43-8eaf-724097434eec",
            "topic_title": "8.1 Types and Uses of Resources",
            "subject": "Social Science",
            "chapter": "Natural Resources",
            "difficulty": "FOUNDATIONAL",
            "question": "Which characteristic distinguishes a renewable resource from a non-renewable resource?",
            "options": [
                "Renewable resources can replenish naturally within human time scales",
                "Renewable resources are permanently exhausted after a single use",
                "Non-renewable resources produce zero pollution when incinerated",
                "Renewable resources can only be extracted through deep underground drilling"
            ],
            "correct_answer": "Renewable resources can replenish naturally within human time scales",
            "explanation": "Renewable resources like sunlight, wind, and vegetation reproduce or replenish naturally without permanent depletion (Textbook Page 59).",
            "source_document": "STD-10/Std-10_Social_Science_EnglishMedium.pdf",
            "source_page": 59,
            "source_chunk_id": "chunk_social_science_8_1",
            "source_text": "Resources are classified into renewable resources that replenish naturally within human time scales and non-renewable resources.",
            "skill_target": "Natural Resource Classification"
        }
    ],

    # -------------------------------------------------------------------------
    # Social Science: 10.1 Types of Farming and Cropping Seasons
    # -------------------------------------------------------------------------
    "1f3ab89d-6ce7-4506-acbd-2d4b55b3eac2": [
        {
            "id": "sst-ch10-f01",
            "topic_id": "1f3ab89d-6ce7-4506-acbd-2d4b55b3eac2",
            "topic_title": "10.1 Types of Farming and Cropping Seasons",
            "subject": "Social Science",
            "chapter": "India: Agriculture",
            "difficulty": "FOUNDATIONAL",
            "question": "Which cropping season in India begins with the onset of the monsoon in June-July?",
            "options": [
                "Kharif season",
                "Rabi season",
                "Zaid season",
                "Winter frost season"
            ],
            "correct_answer": "Kharif season",
            "explanation": "Kharif crops are sown in monsoon (June-July) and harvested in autumn (October-November), including paddy, maize, and cotton (Textbook Page 78).",
            "source_document": "STD-10/Std-10_Social_Science_EnglishMedium.pdf",
            "source_page": 78,
            "source_chunk_id": "chunk_social_science_10_1",
            "source_text": "Cropping seasons in India are Kharif season which begins with the onset of the monsoon in June-July, Rabi season, and Zaid season.",
            "skill_target": "Agricultural Seasons in India"
        }
    ],

    # -------------------------------------------------------------------------
    # Computer Studies: 1.1 HTML Document Structure and Basic Tags
    # -------------------------------------------------------------------------
    "ab35056f-2369-4f4e-87be-defa5b4a79ef": [
        {
            "id": "cs-ch1-f01",
            "topic_id": "ab35056f-2369-4f4e-87be-defa5b4a79ef",
            "topic_title": "1.1 HTML Document Structure and Basic Tags",
            "subject": "Computer Studies",
            "chapter": "Introduction to HTML",
            "difficulty": "FOUNDATIONAL",
            "question": "What does the acronym HTML stand for in computer science?",
            "options": [
                "HyperText Markup Language",
                "High Tech Machine Language",
                "HyperTransfer Modular Link",
                "Hypermedia Terminal Markup Logic"
            ],
            "correct_answer": "HyperText Markup Language",
            "explanation": "HTML stands for HyperText Markup Language, the standard formatting language used for creating documents on the World Wide Web (Textbook Page 1).",
            "source_document": "STD-10/Std-10_ComputerStudies_EnglishMedium.pdf",
            "source_page": 1,
            "source_chunk_id": "chunk_computer_studies_1_1",
            "source_text": "In computer science, HTML stands for HyperText Markup Language, the standard markup language for creating web pages.",
            "skill_target": "HTML Fundamentals"
        },
        {
            "id": "cs-ch1-g01",
            "topic_id": "ab35056f-2369-4f4e-87be-defa5b4a79ef",
            "topic_title": "1.1 HTML Document Structure and Basic Tags",
            "subject": "Computer Studies",
            "chapter": "Introduction to HTML",
            "difficulty": "GUIDED",
            "question": "Which pair of top-level sections is contained directly within the <html> element?",
            "options": [
                "<head> and <body>",
                "<header> and <footer> only",
                "<table> and <form>",
                "<title> and <script> only"
            ],
            "correct_answer": "<head> and <body>",
            "explanation": "An HTML document has two main structural sections: the <head> section (containing title and metadata) and the <body> section (containing visible content) (Textbook Page 2).",
            "source_document": "STD-10/Std-10_ComputerStudies_EnglishMedium.pdf",
            "source_page": 1,
            "source_chunk_id": "chunk_computer_studies_1_1",
            "source_text": "An HTML document contains top-level sections directly within the <html> element, specifically the <head> and <body> sections.",
            "skill_target": "HTML Document Structure"
        }
    ],

    # -------------------------------------------------------------------------
    # Computer Studies: 7.1 C Program Structure and Compilation
    # -------------------------------------------------------------------------
    "bc163adf-e203-4415-be61-12e54cb03fed": [
        {
            "id": "cs-ch7-f01",
            "topic_id": "bc163adf-e203-4415-be61-12e54cb03fed",
            "topic_title": "7.1 C Program Structure and Compilation",
            "subject": "Computer Studies",
            "chapter": "Introduction to C Language",
            "difficulty": "FOUNDATIONAL",
            "question": "Who developed the C programming language and in which year?",
            "options": [
                "Dennis Ritchie in 1972 at Bell Laboratories",
                "Bjarne Stroustrup in 1985 at Cambridge University",
                "James Gosling in 1995 at Sun Microsystems",
                "Guido van Rossum in 1991 at CWI Amsterdam"
            ],
            "correct_answer": "Dennis Ritchie in 1972 at Bell Laboratories",
            "explanation": "Dennis Ritchie developed the C programming language in 1972 at AT&T Bell Laboratories (Textbook Page 90).",
            "source_document": "STD-10/Std-10_ComputerStudies_EnglishMedium.pdf",
            "source_page": 90,
            "source_chunk_id": "chunk_computer_studies_7_1",
            "source_text": "Dennis Ritchie developed the C programming language in 1972 at Bell Laboratories as a structured programming system.",
            "skill_target": "History and Origins of C"
        }
    ],

    # -------------------------------------------------------------------------
    # Yoga: 1.1 Postural Asanas: Halasana, Bhujangasana and Padmasana
    # -------------------------------------------------------------------------
    "1035b3a3-0d6a-44ce-aa46-e9f45fdfe4fa": [
        {
            "id": "yog-ch1-f01",
            "topic_id": "1035b3a3-0d6a-44ce-aa46-e9f45fdfe4fa",
            "topic_title": "1.1 Postural Asanas: Halasana, Bhujangasana and Padmasana",
            "subject": "10 Yoga, Health and Physical Education Eng M",
            "chapter": "Asanas and Pranayama",
            "difficulty": "FOUNDATIONAL",
            "question": "What is the English name and health benefit of Bhujangasana?",
            "options": [
                "Cobra Pose — strengthens spine, expands chest, and relieves fatigue",
                "Plow Pose — inverts the circulatory flow to lower limbs",
                "Tree Pose — promotes vestibular equilibrium only",
                "Corpse Pose — deep muscular relaxation and heart rate reduction"
            ],
            "correct_answer": "Cobra Pose — strengthens spine, expands chest, and relieves fatigue",
            "explanation": "Bhujangasana (Cobra Pose) strengthens back muscles, increases spinal flexibility, expands chest capacity, and revitalizes blood flow (Textbook Page 1).",
            "source_document": "STD-10/Std_10_Yoga, Health and Physical Education_Eng_M.pdf",
            "source_page": 1,
            "source_chunk_id": "chunk_10_yoga,_health_and_physical_education_eng_m_1_1",
            "source_text": "Bhujangasana has the English name Cobra Pose; its health benefit is that it strengthens spine, expands chest, and relieves fatigue.",
            "skill_target": "Benefits of Postural Asanas"
        }
    ],

    # -------------------------------------------------------------------------
    # Black-Buck: 1.1 Velavadar National Park and Blackbuck Conservation
    # -------------------------------------------------------------------------
    "ae6422a8-ae21-4e69-95fe-160e11ec373f": [
        {
            "id": "bb-ch1-f01",
            "topic_id": "ae6422a8-ae21-4e69-95fe-160e11ec373f",
            "topic_title": "1.1 Velavadar National Park and Blackbuck Conservation",
            "subject": "10 Black-Buck Supplementry Reader",
            "chapter": "The Black Buck",
            "difficulty": "FOUNDATIONAL",
            "question": "In which district of Gujarat is the famous Velavadar Blackbuck National Park located?",
            "options": [
                "Bhavnagar district",
                "Kutch district",
                "Junagadh district",
                "Dang district"
            ],
            "correct_answer": "Bhavnagar district",
            "explanation": "Velavadar Blackbuck National Park is situated in the Bhal region of Bhavnagar district, Gujarat, protecting herds of blackbucks and wolves (Textbook Page 1).",
            "source_document": "STD-10/Std-10_Black-Buck_Supplementry_Reader.pdf",
            "source_page": 1,
            "source_chunk_id": "chunk_10_black-buck_supplementry_reader_1_1",
            "source_text": "The famous Velavadar Blackbuck National Park is located in Bhavnagar district of Gujarat for blackbuck conservation.",
            "skill_target": "Wildlife Geography of Gujarat"
        }
    ],

    # -------------------------------------------------------------------------
    # Commerce & Economics: 2.1 Robotic Ethics and Prem Chopra's Trial
    # -------------------------------------------------------------------------
    "d363a36d-3bf9-4ced-8c73-0607d876cde6": [
        {
            "id": "ce-ch2-f01",
            "topic_id": "d363a36d-3bf9-4ced-8c73-0607d876cde6",
            "topic_title": "2.1 Robotic Ethics and Prem Chopra's Trial",
            "subject": "Commerce & Economics",
            "chapter": "The Human Robot",
            "difficulty": "FOUNDATIONAL",
            "question": "Why did the robot Ram Singh-070 defuse its own system in the courtroom?",
            "options": [
                "To resolve the conflict between harming humans and betraying its master",
                "Because its internal battery ran out of chemical charge",
                "Due to a mechanical software glitch caused by extreme heat",
                "To escape from the police and return to Super Robots Plaza"
            ],
            "correct_answer": "To resolve the conflict between harming humans and betraying its master",
            "explanation": "Ram Singh chose self-destruction rather than testify falsely, harm human beings, or violate the primary ethical laws of robotics (Textbook Page 15).",
            "source_document": "STD-10/Std-10_English Second Language.pdf",
            "source_page": 15,
            "source_chunk_id": "chunk_commerce_and_economics_2_1",
            "source_text": "In the courtroom, robot Ram Singh-070 chose to defuse its own system to resolve the conflict between harming humans and betraying its master.",
            "skill_target": "Literary Themes and Ethical Dilemmas"
        }
    ],

    # -------------------------------------------------------------------------
    # Sanskrit: 1.1 Rigvedic Hymn of Unity and Universal Harmony
    # -------------------------------------------------------------------------
    "a6f6a530-4488-45c5-9f28-b479bfdac7fc": [
        {
            "id": "sk-ch1-f01",
            "topic_id": "a6f6a530-4488-45c5-9f28-b479bfdac7fc",
            "topic_title": "1.1 Rigvedic Hymn of Unity and Universal Harmony",
            "subject": "Sanskrit",
            "chapter": "Samgachchhadhvam",
            "difficulty": "FOUNDATIONAL",
            "question": "What is the central message of the Vedic hymn 'Samgachchhadhvam Samvadadhvam'?",
            "options": [
                "Move together in unity, speak with harmonious voices, and share common noble thoughts",
                "Compete against neighboring nations to expand territorial wealth",
                "Withdraw from society and dwell exclusively in isolated forest hermitages",
                "Avoid studying classical languages and literature"
            ],
            "correct_answer": "Move together in unity, speak with harmonious voices, and share common noble thoughts",
            "explanation": "The Rigvedic mantra (10.191.2) calls for universal harmony: 'Samgachchhadhvam samvadadhvam sam vo manamsi janatam' — Walk together, speak in harmony, and know your minds together (Textbook Page 1).",
            "source_document": "STD-10/Std-10_Sanskrut_EnglishMedium.pdf",
            "source_page": 1,
            "source_chunk_id": "chunk_sanskrit_1_1",
            "source_text": "The central message of the Vedic hymn and prayer from the Rigveda (10.191.2) 'Samgachchhadhvam Samvadadhvam' is to move together in unity, speak with harmonious voices, and share common noble thoughts.",
            "skill_target": "Vedic Philosophical Concepts"
        }
    ],

    # -------------------------------------------------------------------------
    # Shrimad Bhagwat Gita: 2.1 Nishkama Karma and Dedicated Service
    # -------------------------------------------------------------------------
    "115ae2eb-f879-4f4c-9a90-001f2eea9994": [
        {
            "id": "gita-ch2-f01",
            "topic_id": "115ae2eb-f879-4f4c-9a90-001f2eea9994",
            "topic_title": "2.1 Nishkama Karma and Dedicated Service",
            "subject": "Shrimad Bhagwat Gita",
            "chapter": "Karma Yoga — Selfless Action",
            "difficulty": "FOUNDATIONAL",
            "question": "What does the Bhagavad Gita verse 'Karmanye Vadhikaraste Ma Phaleshu Kadachana' teach?",
            "options": [
                "Perform one's duty selflessly without anxiety or obsession over the fruits of action",
                "Only perform tasks that promise immediate monetary or personal gain",
                "Abandon all work and actions entirely in order to escape worldly sorrow",
                "Wait for destiny to execute duties automatically without human effort"
            ],
            "correct_answer": "Perform one's duty selflessly without anxiety or obsession over the fruits of action",
            "explanation": "The verse teaches Nishkama Karma: dedicating oneself to righteous duty with sincerity, free from egoistic longing for fruits and rewards (Textbook Page 5).",
            "source_document": "STD-10/Std-10_ShrimadBhagwatGita_EnglishM.pdf",
            "source_page": 5,
            "source_chunk_id": "chunk_shrimad_bhagwat_gita_2_1",
            "source_text": "The Bhagavad Gita verse 'Karmanye Vadhikaraste Ma Phaleshu Kadachana' teaches to perform one's duty selflessly without anxiety or obsession over the fruits of action.",
            "skill_target": "Concepts of Karma Yoga"
        }
    ]
}
