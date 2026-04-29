"""
Run this script once to create a test SQLite database.
Usage: python create_test_db.py
"""
import sqlite3
import os
from pathlib import Path

DB_PATH = "./data/test_business.db"
Path("./data").mkdir(exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ── Create tables ──────────────────────────────────────────────────────────────

cursor.executescript("""
DROP TABLE IF EXISTS sales;
DROP TABLE IF EXISTS finance;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS products;

CREATE TABLE sales (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    date        TEXT,
    revenue     REAL,
    cogs        REAL,
    category    TEXT,
    sales_rep   TEXT,
    region      TEXT,
    deals_won   INTEGER,
    deals_total INTEGER
);

CREATE TABLE finance (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    date            TEXT,
    revenue         REAL,
    expenses        REAL,
    net_profit      REAL,
    depreciation    REAL,
    cash_balance    REAL,
    accounts_receivable REAL,
    accounts_payable    REAL
);

CREATE TABLE customers (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    date            TEXT,
    total_customers INTEGER,
    new_customers   INTEGER,
    churned         INTEGER,
    monthly_amount  REAL
);

CREATE TABLE products (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    date        TEXT,
    product     TEXT,
    units_sold  INTEGER,
    unit_price  REAL,
    revenue     REAL,
    category    TEXT
);
""")

# ── Insert sales data ──────────────────────────────────────────────────────────

sales_data = [
    ("2024-01-01", 187500, 102900, "SaaS Subscriptions", "Alice", "North", 18, 25),
    ("2024-01-02", 62400,  27200,  "Professional Services", "Bob", "South", 7, 11),
    ("2024-01-03", 34700,  17000,  "Hardware", "Charlie", "East", 5, 8),
    ("2024-01-04", 28900,  12600,  "Consulting", "Diana", "West", 4, 7),
    ("2024-02-01", 198300, 108800, "SaaS Subscriptions", "Alice", "North", 20, 27),
    ("2024-02-02", 58700,  25600,  "Professional Services", "Bob", "South", 6, 10),
    ("2024-02-03", 37200,  18200,  "Hardware", "Charlie", "East", 6, 9),
    ("2024-02-04", 31400,  13700,  "Consulting", "Diana", "West", 5, 8),
    ("2024-03-01", 214600, 117700, "SaaS Subscriptions", "Alice", "North", 22, 29),
    ("2024-03-02", 71300,  31100,  "Professional Services", "Bob", "South", 9, 13),
    ("2024-03-03", 39800,  19500,  "Hardware", "Charlie", "East", 6, 9),
    ("2024-03-04", 34200,  14900,  "Consulting", "Diana", "West", 5, 8),
    ("2024-04-01", 229800, 126100, "SaaS Subscriptions", "Alice", "North", 24, 31),
    ("2024-04-02", 74800,  32600,  "Professional Services", "Bob", "South", 9, 13),
    ("2024-04-03", 42300,  20700,  "Hardware", "Charlie", "East", 7, 10),
    ("2024-04-04", 36700,  16000,  "Consulting", "Diana", "West", 6, 9),
    ("2024-05-01", 248700, 136400, "SaaS Subscriptions", "Alice", "North", 26, 33),
    ("2024-05-02", 79600,  34700,  "Professional Services", "Bob", "South", 10, 14),
    ("2024-05-03", 44900,  22000,  "Hardware", "Charlie", "East", 7, 10),
    ("2024-05-04", 39100,  17000,  "Consulting", "Diana", "West", 6, 9),
    ("2024-06-01", 264300, 145000, "SaaS Subscriptions", "Alice", "North", 27, 34),
    ("2024-06-02", 83400,  36300,  "Professional Services", "Bob", "South", 10, 14),
    ("2024-06-03", 47600,  23300,  "Hardware", "Charlie", "East", 8, 11),
    ("2024-06-04", 41800,  18200,  "Consulting", "Diana", "West", 7, 10),
    ("2024-07-01", 281200, 154200, "SaaS Subscriptions", "Alice", "North", 29, 36),
    ("2024-07-02", 87300,  38000,  "Professional Services", "Bob", "South", 11, 15),
    ("2024-07-03", 50400,  24700,  "Hardware", "Charlie", "East", 8, 11),
    ("2024-07-04", 44500,  19400,  "Consulting", "Diana", "West", 7, 10),
    ("2024-08-01", 296400, 162600, "SaaS Subscriptions", "Alice", "North", 30, 37),
    ("2024-08-02", 91800,  40000,  "Professional Services", "Bob", "South", 12, 16),
    ("2024-08-03", 53200,  26000,  "Hardware", "Charlie", "East", 9, 12),
    ("2024-08-04", 47300,  20600,  "Consulting", "Diana", "West", 8, 11),
    ("2024-09-01", 314700, 172700, "SaaS Subscriptions", "Alice", "North", 32, 39),
    ("2024-09-02", 96400,  42000,  "Professional Services", "Bob", "South", 12, 16),
    ("2024-09-03", 56100,  27500,  "Hardware", "Charlie", "East", 9, 12),
    ("2024-09-04", 50200,  21900,  "Consulting", "Diana", "West", 8, 11),
    ("2024-10-01", 334200, 183400, "SaaS Subscriptions", "Alice", "North", 34, 41),
    ("2024-10-02", 101700, 44300,  "Professional Services", "Bob", "South", 13, 17),
    ("2024-10-03", 59200,  29000,  "Hardware", "Charlie", "East", 10, 13),
    ("2024-10-04", 53400,  23300,  "Consulting", "Diana", "West", 9, 12),
    ("2024-11-01", 352600, 193500, "SaaS Subscriptions", "Alice", "North", 35, 42),
    ("2024-11-02", 107300, 46800,  "Professional Services", "Bob", "South", 14, 18),
    ("2024-11-03", 62400,  30600,  "Hardware", "Charlie", "East", 10, 13),
    ("2024-11-04", 56900,  24800,  "Consulting", "Diana", "West", 9, 12),
    ("2024-12-01", 378400, 207600, "SaaS Subscriptions", "Alice", "North", 38, 45),
    ("2024-12-02", 114800, 50100,  "Professional Services", "Bob", "South", 15, 19),
    ("2024-12-03", 66700,  32700,  "Hardware", "Charlie", "East", 11, 14),
    ("2024-12-04", 61200,  26700,  "Consulting", "Diana", "West", 10, 13),
]
cursor.executemany(
    "INSERT INTO sales (date,revenue,cogs,category,sales_rep,region,deals_won,deals_total) VALUES (?,?,?,?,?,?,?,?)",
    sales_data
)

# ── Insert finance data ────────────────────────────────────────────────────────

finance_data = [
    ("2024-01-01", 313500, 89200, 45800, 3200, 820000, 124000, 67000),
    ("2024-02-01", 325600, 92400, 47900, 3200, 775000, 118000, 71000),
    ("2024-03-01", 359900, 98100, 52300, 3200, 726900, 131000, 63000),
    ("2024-04-01", 383600, 104200, 55800, 3200, 671100, 127000, 69000),
    ("2024-05-01", 412300, 111200, 59400, 3200, 612700, 138000, 74000),
    ("2024-06-01", 436100, 117600, 62900, 3200, 551800, 143000, 68000),
    ("2024-07-01", 463400, 124900, 66700, 3200, 487100, 151000, 72000),
    ("2024-08-01", 488700, 131800, 70200, 3200, 418900, 146000, 76000),
    ("2024-09-01", 517400, 139600, 74100, 3200, 347300, 158000, 71000),
    ("2024-10-01", 548500, 148100, 78400, 3200, 272200, 163000, 79000),
    ("2024-11-01", 579200, 156400, 82900, 3200, 192800, 171000, 83000),
    ("2024-12-01", 621100, 167200, 88700, 3200, 107600, 178000, 77000),
]
cursor.executemany(
    "INSERT INTO finance (date,revenue,expenses,net_profit,depreciation,cash_balance,accounts_receivable,accounts_payable) VALUES (?,?,?,?,?,?,?,?)",
    finance_data
)

# ── Insert customers data ──────────────────────────────────────────────────────

customers_data = [
    ("2024-01-01", 420, 28, 6,  33625),
    ("2024-02-01", 441, 26, 5,  35275),
    ("2024-03-01", 463, 29, 7,  37075),
    ("2024-04-01", 482, 26, 7,  38600),
    ("2024-05-01", 504, 31, 9,  40350),
    ("2024-06-01", 521, 26, 9,  41700),
    ("2024-07-01", 540, 28, 9,  43200),
    ("2024-08-01", 557, 26, 9,  44575),
    ("2024-09-01", 578, 30, 9,  46250),
    ("2024-10-01", 599, 30, 9,  47950),
    ("2024-11-01", 618, 28, 9,  49450),
    ("2024-12-01", 641, 32, 9,  51300),
]
cursor.executemany(
    "INSERT INTO customers (date,total_customers,new_customers,churned,monthly_amount) VALUES (?,?,?,?,?)",
    customers_data
)

# ── Insert products data ───────────────────────────────────────────────────────

products_data = [
    ("2024-01-01", "Pro Plan",      850,  220, 187000, "SaaS"),
    ("2024-01-01", "Starter Plan",  1200, 62,  74400,  "SaaS"),
    ("2024-01-01", "Consulting",    45,   642, 28890,  "Services"),
    ("2024-01-01", "Server Bundle", 28,   1239,34692,  "Hardware"),
    ("2024-04-01", "Pro Plan",      920,  220, 202400, "SaaS"),
    ("2024-04-01", "Starter Plan",  1350, 62,  83700,  "SaaS"),
    ("2024-04-01", "Consulting",    52,   642, 33384,  "Services"),
    ("2024-04-01", "Server Bundle", 34,   1239,42126,  "Hardware"),
    ("2024-07-01", "Pro Plan",      1010, 220, 222200, "SaaS"),
    ("2024-07-01", "Starter Plan",  1480, 62,  91760,  "SaaS"),
    ("2024-07-01", "Consulting",    61,   642, 39162,  "Services"),
    ("2024-07-01", "Server Bundle", 41,   1239,50799,  "Hardware"),
    ("2024-10-01", "Pro Plan",      1120, 220, 246400, "SaaS"),
    ("2024-10-01", "Starter Plan",  1620, 62,  100440, "SaaS"),
    ("2024-10-01", "Consulting",    71,   642, 45582,  "Services"),
    ("2024-10-01", "Server Bundle", 48,   1239,59472,  "Hardware"),
]
cursor.executemany(
    "INSERT INTO products (date,product,units_sold,unit_price,revenue,category) VALUES (?,?,?,?,?,?)",
    products_data
)

conn.commit()
conn.close()

print("✅ Test database created at:", DB_PATH)
print("\nTables created:")
print("  • sales      — 48 rows  (revenue, COGS, category, rep, region)")
print("  • finance    — 12 rows  (P&L, cash, AR/AP)")
print("  • customers  — 12 rows  (growth, churn, MRR)")
print("  • products   — 16 rows  (product breakdown)")
print("\nConnection string for the app:")
print("  sqlite:///./data/test_business.db")