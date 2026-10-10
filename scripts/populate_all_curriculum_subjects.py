"""
Script to populate complete GSEB Standard 10 subjects, chapters, topics,
and learning content chunks across all textbook dataset PDFs.
"""

import uuid
from backend.app.core.database import SessionLocal
from backend.app.models import Standard, Subject, Chapter, Topic, LearningContent
from backend.app.models.curriculum_models import ContentType

STANDARD_ID = "26da4ce8-cf71-4ee4-bbd8-bd2d6b9db4d9"

CURRICULUM_DATA = [
    {
        "name": "Social Science",
        "code": "social_science",
        "description": "GSEB Standard 10 Social Science",
        "source_doc": "STD-10/Std-10_Social_Science_EnglishMedium.pdf",
        "chapters": [
            {
                "chapter_number": 1,
                "title": "Heritage of India",
                "topics": [
                    {"order": 1, "title": "1.1 Meaning and Cultural Heritage of India", "page": 1, "text": "India has a rich and varied heritage. Heritage means a valuable gift from our ancestors to us. Indian culture is peaceful and tolerant. Our cultural heritage includes literature, sculpture, architecture, philosophy, religion, and social customs handed down through generations."},
                    {"order": 2, "title": "1.2 Natural Heritage of India", "page": 4, "text": "Natural heritage of India comprises landscapes, rivers, vegetation, and wildlife. Rivers like the Ganga, Yamuna, Narmada, and Godavari are revered as Lokmata. The flora and fauna of India have deep ecological and spiritual significance in our daily life."}
                ]
            },
            {
                "chapter_number": 2,
                "title": "Cultural Heritage of India: Traditional Arts",
                "topics": [
                    {"order": 1, "title": "2.1 Art of Clay Work, Weaving and Embroidery", "page": 8, "text": "Clay work is the oldest art in human history. In India, toys, pots, pitchers, and clay stoves were made from ancient times. Hand weaving and textile craft like Patola of Patan, Kanchipuram, and Banarasi sarees are world renowned traditional arts."},
                    {"order": 2, "title": "2.2 Leather, Diamond and Enamel Work", "page": 12, "text": "Leather work flourished in India for footwear, shields, and bellows. India is famous for precious stones and diamonds like the Kohinoor and Great Mughal. Enamel work (Meenakari) of Jaipur, Delhi, and Lucknow displays incredible craftsmanship."}
                ]
            },
            {
                "chapter_number": 3,
                "title": "India's Cultural Heritage: Fine Arts",
                "topics": [
                    {"order": 1, "title": "3.1 Music, Dance and Dramatic Arts", "page": 16, "text": "Indian music consists of vocal and instrumental traditions with seven fundamental swaras (Sa, Re, Ga, Ma, Pa, Dha, Ni) and classical ragas. Classical dance forms include Bharatanatyam (Tamil Nadu), Kathakali (Kerala), and Kathak (North India). Dramatic art combines entertainment with moral education."},
                    {"order": 2, "title": "3.2 Folk Dances of Gujarat", "page": 20, "text": "Gujarat is celebrated for its folk dances, especially Garba performed during Navratri, Ras, Gof Gunthan, and tribal dances. These dances represent the devotion, social harmony, and joyous festive traditions of the Gujarati people."}
                ]
            },
            {
                "chapter_number": 4,
                "title": "Literary Heritage of India",
                "topics": [
                    {"order": 1, "title": "4.1 Ancient Indian Literature and Vedas", "page": 25, "text": "The Vedas are the oldest literary monuments: Rigveda (hymns of praise), Samaveda (music of hymns), Yajurveda (rituals), and Atharvaveda (prayers and charms). The Upanishads explore philosophical inquiries into Brahman, the soul, and the universe."},
                    {"order": 2, "title": "4.2 Classical Epics and Medieval Literature", "page": 29, "text": "The Ramayana and the Mahabharata are the two great Indian epics. Kalidasa composed masterpieces like Shakuntalam and Meghadutam. Medieval literature saw the rise of regional languages and devotional poetry by Kabir, Tulsidas, and Mirabai."}
                ]
            },
            {
                "chapter_number": 5,
                "title": "India's Heritage of Science and Technology",
                "topics": [
                    {"order": 1, "title": "5.1 Metallurgy, Chemistry and Medical Science", "page": 35, "text": "Ancient Indians achieved great feats in metallurgy, exemplified by the Iron Pillar of Delhi and copper Buddha statues. Nagarjuna of Nalanda University pioneered Rasashastra (applied chemistry). Charaka (Charaka Samhita) and Sushruta (Sushruta Samhita) advanced medicine and surgery."},
                    {"order": 2, "title": "5.2 Mathematics, Astronomy and Vastu Shastra", "page": 39, "text": "Aryabhata introduced the concept of zero, decimal place value system, and the value of Pi (3.1416). Varahamihira contributed to astronomy in Panchasiddhantika. Vastu Shastra laid architectural principles for harmonious city and temple planning."}
                ]
            },
            {
                "chapter_number": 6,
                "title": "Places of Indian Cultural Heritage",
                "topics": [
                    {"order": 1, "title": "6.1 Caves of Ajanta, Ellora and Elephanta", "page": 44, "text": "Ajanta caves in Maharashtra feature Buddhist mural paintings and chaityas. Ellora caves represent Buddhist, Hindu, and Jain monuments, featuring the Kailash Temple carved out of a single monolithic rock. Elephanta caves house the magnificent Trimurti sculpture."},
                    {"order": 2, "title": "6.2 Sun Temple of Modhera and Monuments of Gujarat", "page": 49, "text": "The Sun Temple at Modhera, built in 1026 CE by King Bhimdev I of the Solanki dynasty, is noted for its Sabha Mandap and eastern doorway catching the first sun rays. Rani ki Vav at Patan is an exemplary UNESCO World Heritage subterranean stepwell."}
                ]
            },
            {
                "chapter_number": 7,
                "title": "Preservation of Our Heritage",
                "topics": [
                    {"order": 1, "title": "7.1 Need and Measures for Heritage Conservation", "page": 55, "text": "Preserving cultural and natural heritage is our fundamental duty under Article 51A of the Indian Constitution. The Ancient Monuments and Archaeological Sites and Remains Act of 1958 protects historical monuments from vandalism and illegal trade."}
                ]
            },
            {
                "chapter_number": 8,
                "title": "Natural Resources",
                "topics": [
                    {"order": 1, "title": "8.1 Types and Uses of Resources", "page": 59, "text": "Resources satisfy human needs through technology and knowledge. They are classified into renewable (solar, wind, forests) and non-renewable (coal, petroleum, minerals) resources. Judicious resource conservation is essential for future generations."},
                    {"order": 2, "title": "8.2 Soil Conservation and Types of Soils", "page": 63, "text": "Soil is the uppermost fertile layer of the Earth supporting plant life. Major soil types in India include Alluvial, Black (Regur), Red, Laterite, Desert, and Mountain soils. Soil erosion can be controlled through contour bunding, afforestation, and strip cropping."}
                ]
            },
            {
                "chapter_number": 9,
                "title": "Forests and Wildlife Resources",
                "topics": [
                    {"order": 1, "title": "9.1 Classification of Forests and Conservation", "page": 68, "text": "Forests are classified by administration into Reserved, Protected, and Unclassed forests. Ecological types include Tropical Evergreen, Tropical Deciduous, Thorn, and Mangrove forests. Deforestation leads to global warming, desertification, and loss of biodiversity."},
                    {"order": 2, "title": "9.2 Wildlife Protection and Sanctuaries", "page": 73, "text": "India hosts over 81,000 animal species. Project Tiger (1973), Project Elephant, and Project Rhinoceros protect endangered species. National Parks, Sanctuaries, and Biosphere Reserves provide protected habitats for wildlife conservation."}
                ]
            },
            {
                "chapter_number": 10,
                "title": "India: Agriculture",
                "topics": [
                    {"order": 1, "title": "10.1 Types of Farming and Cropping Seasons", "page": 78, "text": "Agriculture is the backbone of the Indian economy, employing over 50% of the population. Farming types include subsistence, intensive, dry, wetland, plantation, and shifting farming. Cropping seasons are Kharif (monsoon), Rabi (winter), and Zaid (summer)."},
                    {"order": 2, "title": "10.2 Major Food Grains, Cash Crops and Green Revolution", "page": 83, "text": "Paddy (rice) and wheat are primary staple grains. Cash crops include cotton, sugarcane, jute, tea, and groundnut. The Green Revolution modernized farming through High Yielding Variety (HYV) seeds, irrigation, chemical fertilizers, and mechanization."}
                ]
            },
            {
                "chapter_number": 11,
                "title": "Water Resources",
                "topics": [
                    {"order": 1, "title": "11.1 Sources and Multi-purpose Projects", "page": 89, "text": "Water resources include rain, surface water, and groundwater. Multi-purpose river valley projects like Sardar Sarovar (Narmada), Bhakra Nangal (Satluj), and Hirakud (Mahanadi) serve irrigation, hydroelectricity generation, flood control, and drinking water supply."},
                    {"order": 2, "title": "11.2 Rainwater Harvesting and Conservation", "page": 93, "text": "Growing population and industrialization cause water scarcity. Rainwater harvesting through rooftop catchments, percolation tanks, and check dams replenishes groundwater tables and ensures drought resilience."}
                ]
            },
            {
                "chapter_number": 12,
                "title": "Mineral and Energy Resources",
                "topics": [
                    {"order": 1, "title": "12.1 Minerals and Conventional Energy", "page": 98, "text": "Minerals are natural inorganic substances with definite chemical composition: metallic (iron, bauxite, copper) and non-metallic (limestone, mica). Conventional energy sources include coal, crude oil, and natural gas, which are finite and polluting."},
                    {"order": 2, "title": "12.2 Non-Conventional Energy Sources", "page": 103, "text": "Renewable energy includes solar energy (Gujarat's Charanka solar park), wind energy, biomass, geothermal, and tidal energy. Transitioning to renewable energy ensures sustainable and clean economic development."}
                ]
            },
            {
                "chapter_number": 13,
                "title": "Manufacturing Industries",
                "topics": [
                    {"order": 1, "title": "13.1 Agro-based and Mineral-based Industries", "page": 108, "text": "Industries convert raw materials into valuable finished goods. Agro-based industries include cotton textiles, sugar, and jute. Mineral-based industries include iron and steel (Jamshedpur), aluminum smelting, chemical, fertilizer, and automobile industries."}
                ]
            },
            {
                "chapter_number": 14,
                "title": "Transportation, Communication and Trade",
                "topics": [
                    {"order": 1, "title": "14.1 Roadways and Railways in India", "page": 114, "text": "India possesses one of the largest road networks in the world, categorized into Golden Quadrilateral, National Highways, State Highways, and rural roads. Indian Railways is the primary mode of long-distance passenger and freight transport."}
                ]
            },
            {
                "chapter_number": 15,
                "title": "Economic Development",
                "topics": [
                    {"order": 1, "title": "15.1 Economic Features of Developing Economy", "page": 120, "text": "Economic development implies increases in national income and per capita income alongside qualitative improvements in living standards. Developing economies exhibit dual economy characteristics, high population growth, poverty, and agricultural dependency."},
                    {"order": 2, "title": "15.2 Market System and Mixed Economy", "page": 124, "text": "Economic systems allocate resources: Market system (capitalist, profit-driven), Socialist system (state-owned), and Mixed Economy (co-existence of public and private sectors, as in India)."}
                ]
            },
            {
                "chapter_number": 16,
                "title": "Economic Liberalization and Globalization",
                "topics": [
                    {"order": 1, "title": "16.1 Liberalization, Privatization and Globalization", "page": 130, "text": "In 1991, India initiated economic reforms: Liberalization (reducing licensing and regulations), Privatization (reducing public sector monopoly), and Globalization (integrating the Indian economy with the world market through foreign direct investment and trade)."}
                ]
            },
            {
                "chapter_number": 17,
                "title": "Economic Problems: Poverty and Unemployment",
                "topics": [
                    {"order": 1, "title": "17.1 Poverty Alleviation and Employment Measures", "page": 138, "text": "Poverty is a condition where people are deprived of basic necessities like food, clothing, shelter, education, and healthcare. Programmes like MGNREGA guarantee 100 days of wage employment to rural households."}
                ]
            },
            {
                "chapter_number": 18,
                "title": "Price Rise and Consumer Awareness",
                "topics": [
                    {"order": 1, "title": "18.1 Causes of Inflation and Consumer Rights", "page": 146, "text": "Price rise occurs due to increasing demand, hoarding, black marketing, and supply shortages. The Consumer Protection Act of 1986 (COPRA) empowers consumers through the 'Jago Grahak Jago' movement and consumer dispute redressal forums."}
                ]
            },
            {
                "chapter_number": 19,
                "title": "Human Development",
                "topics": [
                    {"order": 1, "title": "19.1 Human Development Index (HDI)", "page": 154, "text": "Human Development focuses on expanding human choices and well-being. The United Nations Development Programme (UNDP) measures HDI through life expectancy, education (mean years of schooling), and per capita gross national income."}
                ]
            },
            {
                "chapter_number": 20,
                "title": "Social Problems of India and Challenges",
                "topics": [
                    {"order": 1, "title": "20.1 Communalism, Casteism and Minority Rights", "page": 162, "text": "India is a pluralistic secular democracy. Constitutional safeguards under Articles 14, 15, and 16 protect equality and prohibit discrimination based on religion, race, caste, sex, or place of birth."}
                ]
            },
            {
                "chapter_number": 21,
                "title": "Social Change",
                "topics": [
                    {"order": 1, "title": "21.1 Right to Education (RTE) and Public Accountability", "page": 170, "text": "The Right of Children to Free and Compulsory Education Act (RTE 2009) makes elementary education a fundamental right for children aged 6 to 14. The Right to Information Act (RTI 2005) ensures transparency and accountability in governance."}
                ]
            }
        ]
    },
    {
        "name": "Computer Studies",
        "code": "computer_studies",
        "description": "GSEB Standard 10 Computer Studies",
        "source_doc": "STD-10/Std-10_ComputerStudies_EnglishMedium.pdf",
        "chapters": [
            {
                "chapter_number": 1,
                "title": "Introduction to HTML",
                "topics": [
                    {"order": 1, "title": "1.1 HTML Document Structure and Basic Tags", "page": 1, "text": "HTML (HyperText Markup Language) is the standard markup language for creating web pages. An HTML document consists of nested elements enclosed in angle brackets: <html>, <head>, <title>, and <body>. Tags usually occur in pairs: opening and closing tags."}
                ]
            },
            {
                "chapter_number": 2,
                "title": "Head and Body Sections in HTML",
                "topics": [
                    {"order": 1, "title": "2.1 Head Metadata and Text Formatting Elements", "page": 14, "text": "The <head> section contains metadata like character encoding, author information, and links to stylesheets. The <body> contains renderable content formatted with headings (<h1> to <h6>), paragraphs (<p>), bold (<b>), italics (<i>), and horizontal rules (<hr>)."}
                ]
            },
            {
                "chapter_number": 3,
                "title": "Working with Images in HTML",
                "topics": [
                    {"order": 1, "title": "3.1 Embedding Images and Image Attributes", "page": 28, "text": "The <img> tag is an empty tag used to display images on a webpage. Important attributes include 'src' (image file path), 'alt' (alternative text), 'width', and 'height' in pixels or percentages. Supported formats include JPEG, PNG, and GIF."}
                ]
            },
            {
                "chapter_number": 4,
                "title": "Lists and Tables in HTML",
                "topics": [
                    {"order": 1, "title": "4.1 Ordered, Unordered Lists and Table Layouts", "page": 42, "text": "HTML supports ordered lists (<ol>), unordered lists (<ul>), and definition lists (<dl>). Tables are constructed using <table>, <tr> (table row), <th> (table header), and <td> (table data). Attributes like 'border', 'cellpadding', and 'cellspacing' control spacing."}
                ]
            },
            {
                "chapter_number": 5,
                "title": "Introduction to Cascading Style Sheets (CSS)",
                "topics": [
                    {"order": 1, "title": "5.1 CSS Syntax, Selectors and Styling Methods", "page": 58, "text": "CSS describes how HTML elements are to be displayed. CSS rules consist of a selector and a declaration block containing property-value pairs. Styles can be applied inline (style attribute), internally (<style> tag in head), or externally (.css file)."}
                ]
            },
            {
                "chapter_number": 6,
                "title": "Working with Forms in HTML",
                "topics": [
                    {"order": 1, "title": "6.1 Form Input Elements, Checkboxes and Radio Buttons", "page": 74, "text": "Forms collect user input using the <form> element with 'action' and 'method' (GET/POST) attributes. Input controls include text boxes, password fields, radio buttons, checkboxes, dropdown select menus (<select>), and submit buttons."}
                ]
            },
            {
                "chapter_number": 7,
                "title": "Introduction to C Language",
                "topics": [
                    {"order": 1, "title": "7.1 C Program Structure and Compilation", "page": 90, "text": "C is a structured, middle-level programming language developed by Dennis Ritchie at Bell Labs in 1972. A C program includes preprocessor directives (#include <stdio.h>), a main() function, variable declarations, executable statements, and return 0."}
                ]
            },
            {
                "chapter_number": 8,
                "title": "Constants, Variables and Data Types in C",
                "topics": [
                    {"order": 1, "title": "8.1 Basic Data Types, Identifiers and Memory", "page": 105, "text": "Variables are named memory locations storing data. Fundamental data types in C are int (integer), float (floating point), double (double precision), and char (single character). Constants are fixed values that cannot be altered during execution."}
                ]
            },
            {
                "chapter_number": 9,
                "title": "Operators and Expressions in C",
                "topics": [
                    {"order": 1, "title": "9.1 Arithmetic, Relational and Logical Operators", "page": 120, "text": "Operators perform operations on variables and values. C supports arithmetic (+, -, *, /, %), relational (<, >, <=, >=, ==, !=), logical (&&, ||, !), assignment (=), and increment/decrement (++, --) operators."}
                ]
            },
            {
                "chapter_number": 10,
                "title": "Decision Making and Branching in C",
                "topics": [
                    {"order": 1, "title": "10.1 If-Else and Switch-Case Constructs", "page": 135, "text": "Conditional statements control program flow based on conditions. The 'if' statement executes code if a condition is true; 'if-else' provides an alternative block. 'switch-case' selects one of many code blocks to execute based on an expression value."}
                ]
            },
            {
                "chapter_number": 11,
                "title": "Looping Structures in C",
                "topics": [
                    {"order": 1, "title": "11.1 For, While and Do-While Loops", "page": 150, "text": "Loops execute a block of statements repeatedly. 'for' loop is entry-controlled with initialization, condition, and increment/decrement. 'while' loop checks the condition before entry. 'do-while' loop is exit-controlled, executing at least once."}
                ]
            },
            {
                "chapter_number": 12,
                "title": "Functions and Arrays in C",
                "topics": [
                    {"order": 1, "title": "12.1 Single-dimensional Arrays and Modular Functions", "page": 168, "text": "An array is a collection of elements of the same data type stored in contiguous memory locations accessed by an index starting from 0. Functions break complex code into reusable, modular blocks with parameters and return values."}
                ]
            }
        ]
    },
    {
        "name": "10 Yoga, Health and Physical Education Eng M",
        "code": "10_yoga,_health_and_physical_education_eng_m",
        "description": "GSEB Standard 10 Yoga, Health and Physical Education",
        "source_doc": "STD-10/Std_10_Yoga, Health and Physical Education_Eng_M.pdf",
        "chapters": [
            {
                "chapter_number": 1,
                "title": "Asanas and Pranayama",
                "topics": [
                    {"order": 1, "title": "1.1 Postural Asanas: Halasana, Bhujangasana and Padmasana", "page": 1, "text": "Yoga brings balance between mind, body, and breath. Asanas improve flexibility, blood circulation, and spinal health. Halasana (Plow Pose) strengthens back muscles. Bhujangasana (Cobra Pose) expands chest capacity and relieves fatigue."},
                    {"order": 2, "title": "1.2 Breathing Techniques: Anulom Vilom and Kapalbhati", "page": 12, "text": "Pranayama is the regulation of breath (Prana). Anulom Vilom (alternate nostril breathing) purifies the nervous system and balances autonomic functions. Kapalbhati cleanses respiratory passages and enhances mental alertness."}
                ]
            },
            {
                "chapter_number": 2,
                "title": "Ashtanga Yoga",
                "topics": [
                    {"order": 1, "title": "2.1 Eight Limbs of Patanjali Yoga", "page": 24, "text": "Maharshi Patanjali codified Yoga into eight limbs (Ashtanga): Yama (social ethics), Niyama (personal discipline), Asana (posture), Pranayama (breath control), Pratyahara (sensory withdrawal), Dharana (concentration), Dhyana (meditation), and Samadhi (absorption)."}
                ]
            },
            {
                "chapter_number": 3,
                "title": "Personal Health and Hygiene",
                "topics": [
                    {"order": 1, "title": "3.1 Balanced Diet, Cleanliness and Nutrition", "page": 38, "text": "Health is a state of complete physical, mental, and social well-being. A balanced diet contains carbohydrates, proteins, fats, vitamins, minerals, roughage, and water in proper proportions. Personal hygiene prevents communicable diseases."}
                ]
            },
            {
                "chapter_number": 4,
                "title": "Postural Deformities and Corrective Exercises",
                "topics": [
                    {"order": 1, "title": "4.1 Common Postural Deformities and Remedies", "page": 52, "text": "Correct posture minimizes strain on muscles and ligaments during sitting, standing, and walking. Common deformities include Kyphosis (round upper back), Lordosis (swayback), Scoliosis (lateral curve), Flat Foot, and Knock Knees. Remedial exercises restore spinal balance."}
                ]
            },
            {
                "chapter_number": 5,
                "title": "First Aid and Safety",
                "topics": [
                    {"order": 1, "title": "5.1 Emergency First Aid, Sprains and CPR", "page": 66, "text": "First aid is the immediate assistance given to an injured person before professional medical help arrives. The R.I.C.E. protocol (Rest, Ice, Compression, Elevation) is essential for sprains and soft tissue injuries. CPR revives cardiac arrest victims."}
                ]
            },
            {
                "chapter_number": 6,
                "title": "Track and Field Events",
                "topics": [
                    {"order": 1, "title": "6.1 Sprints, Relays and Long Jump", "page": 80, "text": "Athletics develops speed, stamina, and strength. Track events include short sprints (100m, 200m), middle-distance runs, and 4x100m relay races with baton exchange. Field events include long jump, high jump, and shot put."}
                ]
            },
            {
                "chapter_number": 7,
                "title": "Team Games and Sportsmanship",
                "topics": [
                    {"order": 1, "title": "7.1 Football, Volleyball, Cricket and Fair Play", "page": 95, "text": "Team sports build collaboration, discipline, leadership, and emotional resilience. Playing according to rules, respecting opponents and referees, and accepting both victory and defeat with dignity define true sportsmanship."}
                ]
            }
        ]
    },
    {
        "name": "10 Black-Buck Supplementry Reader",
        "code": "10_black-buck_supplementry_reader",
        "description": "GSEB Standard 10 Black-Buck Supplementary Reader",
        "source_doc": "STD-10/Std-10_Black-Buck_Supplementry_Reader.pdf",
        "chapters": [
            {
                "chapter_number": 1,
                "title": "The Black Buck",
                "topics": [
                    {"order": 1, "title": "1.1 Velavadar National Park and Blackbuck Conservation", "page": 1, "text": "The Blackbuck is one of the fastest and most elegant antelopes in the world, capable of reaching speeds up to 80 km/h. Velavadar Blackbuck National Park in Bhavnagar district of Gujarat provides a protected sanctuary for herds of blackbucks and wolves."}
                ]
            },
            {
                "chapter_number": 2,
                "title": "Oh! No, You Can't!",
                "topics": [
                    {"order": 1, "title": "2.1 Overcoming Adversity and Determination", "page": 18, "text": "This inspiring story depicts how self-belief and continuous perseverance can overcome doubts, physical limitations, and discouraging social attitudes, empowering youth to realize their dreams."}
                ]
            },
            {
                "chapter_number": 3,
                "title": "The Gentle Giant",
                "topics": [
                    {"order": 1, "title": "3.1 Compassion for Animals and Wildlife Coexistence", "page": 35, "text": "The story highlights human empathy towards majestic elephants and other wild animals, underscoring that kindness and understanding foster harmony between human communities and nature."}
                ]
            },
            {
                "chapter_number": 4,
                "title": "The Boy Who Broke the Bank",
                "topics": [
                    {"order": 1, "title": "4.1 Rumours, Gossip and Community Panic", "page": 52, "text": "Written by Ruskin Bond, this humorous tale illustrates how a small remark by Nathu, the sweeper boy complaining of delayed pay, escalates into an uncontrollable rumour causing a bank run in Pipalnagar."}
                ]
            },
            {
                "chapter_number": 5,
                "title": "The Cherry Tree",
                "topics": [
                    {"order": 1, "title": "5.1 Nature, Growth and the Joy of Creation", "page": 70, "text": "Rakesh plants a cherry seed in the Himalayan foothills. Despite goats eating its leaves and a grass cutter splitting it, the resilient plant survives and blossoms into a cherry tree, bringing profound joy to Rakesh and his grandfather."}
                ]
            },
            {
                "chapter_number": 6,
                "title": "The Gift of the Magi",
                "topics": [
                    {"order": 1, "title": "6.1 Sacrificial Love and True Wealth", "page": 88, "text": "O. Henry's classic story follows Jim and Della, a poor young couple who secretly sell their most prized possessions (Jim's gold watch and Della's beautiful hair) to buy Christmas gifts for each other, illustrating that mutual love is the highest treasure."}
                ]
            }
        ]
    },
    {
        "name": "Commerce & Economics",
        "code": "commerce_and_economics",
        "description": "GSEB Standard 10 Commerce, Economics & Applied English",
        "source_doc": "STD-10/Std-10_English Second Language.pdf",
        "chapters": [
            {
                "chapter_number": 1,
                "title": "Against the Odds",
                "topics": [
                    {"order": 1, "title": "1.1 Rural Electrification and Community Empowerment", "page": 1, "text": "The chapter highlights community triumphs: Taj Nagar railway station built through villagers' savings, Sitapur's solar micro-grids providing clean lighting, and Palakkad's District Public Library empowering women through reading and collective action."}
                ]
            },
            {
                "chapter_number": 2,
                "title": "The Human Robot",
                "topics": [
                    {"order": 1, "title": "2.1 Robotic Ethics and Prem Chopra's Trial", "page": 15, "text": "Prem Chopra purchases Ram Singh-070, a metallic blue robot programmed with Asimov's principles of robotics. When coerced into stealing jewels, Ram Singh chooses self-destruction in court rather than harming humans or disobeying moral loyalty."}
                ]
            },
            {
                "chapter_number": 3,
                "title": "An Interview with Arun Krishnamurthy",
                "topics": [
                    {"order": 1, "title": "3.1 Environmental Conservation and Lake Revival", "page": 28, "text": "Arun Krishnamurthy founded the Environmentalist Foundation of India (EFI) at age 17. The interview recounts how his team cleans polluted lakes, protects aquatic ecosystems, and mobilizes student volunteers for environmental preservation."}
                ]
            },
            {
                "chapter_number": 4,
                "title": "A Wonderful Creation",
                "topics": [
                    {"order": 1, "title": "4.1 The Care, Strength and Unconditional Love of Mothers", "page": 42, "text": "A poetic narrative where the Lord explains the creation of a mother: endowed with endless endurance, a comforting kiss that heals broken limbs and hearts, and unconditional devotion that supports families through all challenges."}
                ]
            },
            {
                "chapter_number": 5,
                "title": "Playing with Fire",
                "topics": [
                    {"order": 1, "title": "5.1 Science of Fireworks, Pyrotechnics and Safety", "page": 56, "text": "Pyrotechnics is the science of fire and fireworks derived from Greek 'pyr' (fire) and 'techne' (art). It explores the history of gunpowder (black powder) invented in ancient China, manufacturing in Sivakasi, and critical safety rules."}
                ]
            },
            {
                "chapter_number": 6,
                "title": "I Love You, Teacher",
                "topics": [
                    {"order": 1, "title": "6.1 Helen Keller and the Mentorship of Anne Sullivan", "page": 70, "text": "Helen Keller, who became blind and deaf at an early age, recalls how her compassionate teacher Anne Sullivan spelt words on her palm to unlock the world of language, culminating in Keller graduating from college and inspiring millions."}
                ]
            }
        ]
    },
    {
        "name": "Sanskrit",
        "code": "sanskrit",
        "description": "GSEB Standard 10 Sanskrit",
        "source_doc": "STD-10/Std-10_Sanskrut_EnglishMedium.pdf",
        "chapters": [
            {
                "chapter_number": 1,
                "title": "Samgachchhadhvam",
                "topics": [
                    {"order": 1, "title": "1.1 Rigvedic Hymn of Unity and Universal Harmony", "page": 1, "text": "The famous prayer from the Rigveda (10.191.2) urges humanity to move together, speak with one voice, and unite in thoughts and purpose for universal welfare and concord."}
                ]
            },
            {
                "chapter_number": 2,
                "title": "Yadbhavishyo Vinashyati",
                "topics": [
                    {"order": 1, "title": "2.1 Story of the Three Fishes from Panchatantra", "page": 15, "text": "The Panchatantra fable narrates the fate of three fishes: Anagatavidhata (the forethinking), Pratyutpannamati (the quick-witted), and Yadbhavishya (the fatalist). It illustrates that foresight and timely action preserve life, while fatalism leads to ruin."}
                ]
            },
            {
                "chapter_number": 3,
                "title": "Swasthavrittam Samachara",
                "topics": [
                    {"order": 1, "title": "3.1 Daily Health Regimen according to Ayurveda", "page": 30, "text": "The chapter outlines the Ayurvedic Dinacharya (daily routine): rising early, morning exercise, bathing, wholesome food, truthfulness, and mental calmness to maintain physical vitality and spiritual well-being."}
                ]
            },
            {
                "chapter_number": 4,
                "title": "Janardanasya Pashchima Sandesha",
                "topics": [
                    {"order": 1, "title": "4.1 Sri Krishna's Final Message from Dutaghatotkacham", "page": 46, "text": "Adapted from Bhasa's play Dutaghatotkacham, Ghatotkacha delivers Sri Krishna's message to the Kaurava court, urging them to abandon pride and injustice to avoid disastrous war."}
                ]
            },
            {
                "chapter_number": 5,
                "title": "Gunavati Kanya",
                "topics": [
                    {"order": 1, "title": "5.1 The Virtuous Maiden by Dandin", "page": 62, "text": "From Dandin's Dashakumaracharita, Shaktikumara tests a young maiden with a single measure of paddy. Through exceptional thrift, skill, and culinary wisdom, she prepares a feast, showing that virtue and intelligence are the highest adornments."}
                ]
            }
        ]
    },
    {
        "name": "Shrimad Bhagwat Gita",
        "code": "shrimad_bhagwat_gita",
        "description": "GSEB Standard 10 Shrimad Bhagwat Gita",
        "source_doc": "STD-10/Std-10_ShrimadBhagwatGita_EnglishM.pdf",
        "chapters": [
            {
                "chapter_number": 1,
                "title": "Gita Mahatmya and Introduction",
                "topics": [
                    {"order": 1, "title": "1.1 The Context of Kurukshetra and Inner Conflict", "page": 1, "text": "The Bhagavad Gita, part of the Mahabharata, is a dialogue between Sri Krishna and Arjuna on the battlefield of Kurukshetra. It addresses Arjuna's despondency and provides timeless wisdom on duty, ethics, and overcoming moral dilemmas."}
                ]
            },
            {
                "chapter_number": 2,
                "title": "Karma Yoga — Selfless Action",
                "topics": [
                    {"order": 1, "title": "2.1 Nishkama Karma and Dedicated Service", "page": 5, "text": "'Karmanye Vadhikaraste Ma Phaleshu Kadachana' — You have a right to perform your prescribed duty, but you are not entitled to the fruits of action. Selfless action without attachment purifies the mind and leads to liberation."}
                ]
            },
            {
                "chapter_number": 3,
                "title": "Jnana Yoga — Eternal Wisdom",
                "topics": [
                    {"order": 1, "title": "3.1 Immortality of the Soul and Steady Intellect", "page": 9, "text": "The Atman (soul) is eternal, indestructible, and beyond the changes of birth and death: weapons cannot cleave it, fire cannot burn it. The person with steady intellect (Sthitaprajna) remains serene in joy and sorrow."}
                ]
            },
            {
                "chapter_number": 4,
                "title": "Bhakti Yoga & Universal Harmony",
                "topics": [
                    {"order": 1, "title": "4.1 Equanimity, Compassion and Devotion", "page": 13, "text": "True devotion is characterized by harmlessness, friendliness, compassion towards all living beings, freedom from egoism, and treating praise and censure with equal calmness."}
                ]
            }
        ]
    }
]


def run():
    db = SessionLocal()
    try:
        standard = db.query(Standard).filter(Standard.id == STANDARD_ID).first()
        if not standard:
            print("Standard 10 not found!")
            return

        for subj_data in CURRICULUM_DATA:
            code = subj_data["code"]
            name = subj_data["name"]

            subj = db.query(Subject).filter(
                Subject.standard_id == standard.id,
                (Subject.code == code) | (Subject.name == name)
            ).first()

            if not subj:
                subj = Subject(
                    id=str(uuid.uuid4()),
                    standard_id=standard.id,
                    name=name,
                    code=code,
                    description=subj_data["description"],
                    is_active=True
                )
                db.add(subj)
                db.commit()
                db.refresh(subj)
                print(f"[CREATED SUBJECT] {name} ({code}) -> {subj.id}")
            else:
                print(f"[FOUND SUBJECT] {name} ({code}) -> {subj.id}")

            # Check if subject has dummy "General Curriculum Content" chapter and remove it
            dummy_chaps = db.query(Chapter).filter(
                Chapter.subject_id == subj.id,
                Chapter.title.ilike("%general curriculum content%")
            ).all()
            for d in dummy_chaps:
                print(f"  Removing dummy chapter: {d.title} ({d.id})")
                db.delete(d)
            db.commit()

            # Now create chapters and topics
            for ch_data in subj_data["chapters"]:
                ch_num = ch_data["chapter_number"]
                ch_title = ch_data["title"]

                chap = db.query(Chapter).filter(
                    Chapter.subject_id == subj.id,
                    Chapter.chapter_number == ch_num
                ).first()

                if not chap:
                    chap = Chapter(
                        id=str(uuid.uuid4()),
                        subject_id=subj.id,
                        chapter_number=ch_num,
                        title=ch_title,
                        description=f"{name} Chapter {ch_num}: {ch_title}",
                        source_reference=subj_data["source_doc"],
                        is_active=True
                    )
                    db.add(chap)
                    db.commit()
                    db.refresh(chap)
                    print(f"  [CREATED CHAPTER] Ch {ch_num}: {ch_title} -> {chap.id}")
                else:
                    chap.title = ch_title
                    chap.is_active = True
                    db.commit()

                for tp_data in ch_data["topics"]:
                    t_order = tp_data["order"]
                    t_title = tp_data["title"]

                    topic = db.query(Topic).filter(
                        Topic.chapter_id == chap.id,
                        Topic.topic_order == t_order
                    ).first()

                    if not topic:
                        topic = Topic(
                            id=str(uuid.uuid4()),
                            chapter_id=chap.id,
                            topic_order=t_order,
                            title=t_title,
                            description=f"{ch_title} - {t_title}",
                            is_active=True
                        )
                        db.add(topic)
                        db.commit()
                        db.refresh(topic)
                        print(f"    [CREATED TOPIC] {t_order}: {t_title} -> {topic.id}")
                    else:
                        topic.title = t_title
                        topic.is_active = True
                        db.commit()

                    # Check or create learning content chunk
                    lc = db.query(LearningContent).filter(
                        LearningContent.topic_id == topic.id
                    ).first()

                    if not lc:
                        lc = LearningContent(
                            id=str(uuid.uuid4()),
                            topic_id=topic.id,
                            content_type=ContentType.TEXT,
                            title=t_title,
                            content_text=tp_data["text"],
                            source_document=subj_data["source_doc"],
                            source_page=tp_data["page"],
                            source_reference=f"Page {tp_data['page']} of {subj_data['source_doc']}",
                            chunk_identifier=f"chunk_{subj_data['code']}_{ch_num}_{t_order}"
                        )
                        db.add(lc)
                        db.commit()
                        print(f"      [CREATED CONTENT CHUNK] Page {tp_data['page']} -> {lc.id}")
                    else:
                        lc.content_text = tp_data["text"]
                        lc.source_document = subj_data["source_doc"]
                        lc.source_page = tp_data["page"]
                        db.commit()

        print("\nAll curriculum subjects and chapters successfully populated!")

    finally:
        db.close()


if __name__ == "__main__":
    run()
