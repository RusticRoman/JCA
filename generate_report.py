import pandas as pd
import random

# Student names (Last, First)
students = [
    "Taylor, James", "Miller, William", "White, Richard", "Brown, Thomas",
    "Taylor, Brian", "Thompson, David", "Martin, George", "Davis, Joseph",
    "Brown, John", "Brown, Donald", "Wilson, Joseph", "Moore, Kenneth",
    "Davis, Paul", "Davis, Steven", "Jones, Charles", "Thomas, Edward",
    "Smith, Richard", "Martinez, Mark", "Smith, James", "White, Donald"
]

# Detailed subjects from all semesters (8 semesters × 5 subjects)
subjects = [
    # Semester 1
    "Jewish Beliefs/Values", "Jewish History Overview", "Hebrew Alphabet Basics",
    "Jewish Identity Concepts", "Daily Jewish Living Intro",
    
    # Semester 2
    "Shabbat Meaning", "Candle Lighting/Kiddush", "Shabbat Prohibitions",
    "Shabbat Meal Hosting", "Havdalah Ritual",
    
    # Semester 3
    "Kashrut Sources", "Meat/Dairy Separation", "Kosher Kitchen Setup",
    "Eating Out Kosher", "Kosher Market Visit",
    
    # Semester 4
    "Brachot Philosophy", "Prayer Structure", "Food Blessings",
    "Siddur Navigation", "Leading Prayers",
    
    # Semester 5
    "Holiday Calendar", "High Holidays Deep Dive", "Pilgrim Festivals",
    "Minor Holidays", "Holiday Celebration Practice",
    
    # Semester 6
    "Family Purity Laws", "Mikveh Practice", "Lifecycle Events",
    "Jewish Family Structure", "Lifecycle Attendance",
    
    # Semester 7
    "Tzedakah Practice", "Mitzvot Daily Living", "Mezuzah Installation",
    "Jewish/Non-Jewish Balance", "Home Rituals",
    
    # Semester 8
    "Denominational Differences", "Israel History", "Antisemitism Education",
    "Beit Din Preparation", "Hebrew Name Selection"
]

data = []
for student in students:
    enrollment = random.randint(1, 8)
    progress = {"Student": student, "Enrollment Semester": f"Semester {enrollment}"}
    
    # Track watched videos
    watched_count = 0
    required_subjects = 0
    
    for idx, subject in enumerate(subjects):
        subject_semester = (idx // 5) + 1
        if subject_semester >= enrollment:
            required_subjects += 1
            if random.random() < 0.7:  # 70% completion probability
                progress[subject] = "x"
                watched_count += 1
            else:
                progress[subject] = ""
        else:
            progress[subject] = ""
    
    # Calculate accurate percentage of required subjects watched
    completion_rate = (watched_count / required_subjects * 100) if required_subjects > 0 else 0
    progress["% Completed"] = f"{completion_rate:.1f}%"
    
    data.append(progress)

# Create DataFrame and save
df = pd.DataFrame(data)
df.to_csv("conversion_progress_detailed.csv", index=False)

