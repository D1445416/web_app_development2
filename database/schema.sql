PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS registrations;
DROP TABLE IF EXISTS users;

-- 建立報名紀錄表
CREATE TABLE registrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('是', '否')),
    needs_lunchbox TEXT CHECK(needs_lunchbox IN ('是', '否')),
    dietary_preference TEXT CHECK(dietary_preference IN ('葷', '素')),
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

-- 建立管理者帳號表
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);
