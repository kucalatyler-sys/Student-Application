PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    first_name TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    is_admin INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS student (
    StudentID INTEGER PRIMARY KEY AUTOINCREMENT,
    LastName TEXT NOT NULL DEFAULT '',
    FirstName TEXT NOT NULL DEFAULT '',
    MiddleInitial TEXT NOT NULL DEFAULT '',
    DateOfBirth TEXT,
    Contact TEXT,
    PhoneNumber TEXT,
    Citizenship TEXT,
    StreetAddress TEXT,
    State TEXT,
    City TEXT,
    ZipCode TEXT
);

CREATE TABLE IF NOT EXISTS finance (
    FinanceID INTEGER PRIMARY KEY AUTOINCREMENT,
    HouseholdIncome TEXT,
    FinancialAid TEXT,
    AidAmount TEXT,
    Employment TEXT,
    VolunteerWork TEXT,
    Assets TEXT,
    Expenses TEXT,
    FinancialNotes TEXT,
    StudentID INTEGER NOT NULL UNIQUE,
    FOREIGN KEY (StudentID) REFERENCES student(StudentID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS academics (
    GradeID INTEGER PRIMARY KEY AUTOINCREMENT,
    GPA TEXT,
    SchoolName TEXT,
    Notes TEXT,
    TranscriptPath TEXT,
    StudentID INTEGER NOT NULL UNIQUE,
    FOREIGN KEY (StudentID) REFERENCES student(StudentID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS income (
    IncomeID INTEGER PRIMARY KEY AUTOINCREMENT,
    GuardianFirstName TEXT,
    GuardianMiddleInitial TEXT,
    GuardianLastName TEXT,
    GuardianRelationship TEXT,
    GuardianIncome TEXT,
    GuardianEmployment TEXT,
    IncomeSupport TEXT,
    PeopleSupported TEXT,
    GuardianNotes TEXT,
    IncomeDocumentsPath TEXT,
    StudentID INTEGER NOT NULL UNIQUE,
    FOREIGN KEY (StudentID) REFERENCES student(StudentID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS major (
    MajorID INTEGER PRIMARY KEY AUTOINCREMENT,
    MajorChoice TEXT NOT NULL DEFAULT '',
    MinorChoice TEXT,
    Notes TEXT,
    StudentID INTEGER NOT NULL UNIQUE,
    FOREIGN KEY (StudentID) REFERENCES student(StudentID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS applications (
    ApplicationID INTEGER PRIMARY KEY AUTOINCREMENT,
    StudentID INTEGER NOT NULL,
    UserID INTEGER,
    SubmittedAt TEXT NOT NULL,
    Status TEXT NOT NULL DEFAULT 'Draft',
    ReviewedBy INTEGER,
    ReviewedAt TEXT,
    AdminNotes TEXT,
    AdditionalInfo TEXT,
    FOREIGN KEY (StudentID) REFERENCES student(StudentID) ON DELETE CASCADE,
    FOREIGN KEY (UserID) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_applications_student_id ON applications(StudentID);
CREATE INDEX IF NOT EXISTS idx_applications_user_id ON applications(UserID);
CREATE INDEX IF NOT EXISTS idx_finance_student_id ON finance(StudentID);
CREATE INDEX IF NOT EXISTS idx_academics_student_id ON academics(StudentID);
CREATE INDEX IF NOT EXISTS idx_income_student_id ON income(StudentID);
CREATE INDEX IF NOT EXISTS idx_major_student_id ON major(StudentID);
