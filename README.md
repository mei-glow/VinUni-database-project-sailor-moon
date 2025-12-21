# VinUni Database Project – VinRetail Management System

VinRetail is a database-centric retail management system designed to support end-to-end operations of a multi-store retail business. The project focuses on robust relational database design, business rule enforcement at the database layer, and scalability for real-world retail workloads.

---

## Project Description
VinRetail manages the full retail lifecycle, including:
- Product and inventory management across stores and warehouses
- Customer profiles, loyalty programs, and purchase behavior tracking
- Sales order creation, invoice processing, and returns handling
- Fulfillment, delivery, and stock transfers between locations
- Promotions, employee performance bonuses, and delivery incentives
- Audit logging for data governance and security

The system is implemented using MySQL 8.x and is designed following normalization up to Third Normal Form (3NF).

---

## Functional Requirements
### 1. Product & Inventory Management
- Maintain product master data, brands, and product classes
- Track inventory quantities per location
- Record inventory movements with a complete audit trail

### 2. Customer & Loyalty Management
- Store customer profiles and preferences
- Manage loyalty levels and loyalty points
- Automatically update loyalty points after purchases

### 3. Sales Order & Transaction Processing
- Create and manage sales orders
- Apply promotions at item level
- Generate invoices and handle returns
- Calculate final amounts with VAT and rounding rules

### 4. Fulfillment & Delivery
- Support order fulfillment, stock transfers, and customer returns
- Assign delivery vendors, vehicles, and delivery personnel
- Track delivery status changes throughout the delivery lifecycle

### 5. Performance & Gamification
- Track employee sales performance
- Apply sales bonus rules by product class or KPI
- Apply delivery bonus rules based on delivery volume and type

---

## Non-Functional Requirements
- **Reliability:** ACID-compliant transactions and referential integrity  
- **Scalability:** Optimized indexing and partitioning strategies  
- **Security:** Role-based access and audit logging  
- **Performance:** Indexed transactional tables and derived reporting views  
- **Maintainability:** Modular schema and centralized business logic

---

## Core Database Entities

### Master Data
- **departments** - Organizational departments
- **brands** - Product brand master data
- **product_class** - Product classification with 22 product groups (electronics, clothing, food, beverages, etc.)
- **products** - Product master data with pricing, dimensions, and status
- **locations** - Stores and warehouses with geographic data
- **customers** - Customer profiles and contact information
- **customer_preferences** - Customer product class preferences
- **loyalty_levels** - Loyalty tier definitions (bronze, silver, gold, etc.)
- **customer_loyalty** - Customer loyalty status, points, and expiration
- **employees** - Employee master data with roles and hierarchy
- **payment_methods** - Payment method definitions

### Inventory Management
- **inventory** - Current stock levels by product and location
- **inventory_history** - Complete audit trail of inventory movements (IN, OUT, TRANSFER, ADJUST)

### Sales & Transactions
- **sales_orders** - Sales order headers with customer, employee, and location
- **sales_order_items** - Order line items with promotions applied
- **sales** - Invoice and return transactions
- **sales_items** - Invoice/return line items with quantity and pricing

### Promotions & Campaigns
- **promotions_campaigns** - Marketing campaign definitions
- **promotions** - Promotion rules (PERCENT, FIXED, BUY_X_GET_Y) with product-level application

### Delivery & Fulfillment
- **delivery_vendors** - Delivery vendor master data (INTERNAL, THIRD_PARTY, DROPSHIPPING)
- **delivery_vehicles** - Vehicle fleet management
- **deliveries** - Delivery records (FULFILLMENT, TRANSFER, RETURN)
- **delivery_status_history** - Complete delivery status change audit trail

### Performance & Incentives
- **employee_bonus_rules** - Sales bonus rules (PERCENT, FIXED, KPI) by product class
- **delivery_bonus_rules** - Delivery bonus rules by count, class, or delivery type

### Security & Access Control (RBAC)
- **users** - System user accounts with authentication
- **roles** - Role definitions (ADMIN, SALES, WAREHOUSE, DELIVERY, HR, MANAGER, ANALYST)
- **user_roles** - User-role assignments
- **permissions** - Permission codes (VIEW_SALES_DASHBOARD, CREATE_ORDER, etc.)
- **role_permissions** - Role-permission mappings

### Audit & Governance
- **audit_logs** - Complete audit trail of all data changes (INSERT, UPDATE, DELETE)

---

## Database ERD Diagram

![ER Diagram](https://github.com/user-attachments/assets/1bd0bafa-42c4-4739-a99a-e7e893f5934a)
---

## Tech Stack

### Backend & Database
- **Database:** MySQL 8.x with InnoDB engine
- **ORM:** SQLAlchemy 2.0+ for database abstraction
- **Database Driver:** PyMySQL for MySQL connectivity
- **Connection Management:** Custom session management with connection pooling

### Frontend & UI
- **Framework:** Streamlit 1.52+ for web application interface
- **Visualization:** Plotly and Altair for interactive charts and dashboards
- **Styling:** Custom CSS with modern gradient designs

### Data Processing
- **Data Manipulation:** Pandas for data processing and analysis
- **Numerical Computing:** NumPy for numerical operations

### Authentication & Security
- **Password Hashing:** Argon2-cffi and bcrypt for secure password storage
- **Authentication:** Custom RBAC (Role-Based Access Control) implementation
- **Session Management:** Streamlit session state with secure user sessions

### Configuration & Environment
- **Environment Variables:** python-dotenv for configuration management
- **Database Initialization:** Automated schema creation and migration

### Development Tools
- **Version Control:** Git & GitHub
- **Database Tools:** MySQL Workbench for schema design and management
- **Diagramming:** Draw.io for ERD creation

---

## Team Members & Roles
| Name              | Role                                        |
|-------------------|---------------------------------------------|
| Tran Phuong Mai   | Team Lead / Database Architect / Frontend   |
| Do Phuong An      | Data Modeling / SQL Developer               |
| Nguyen Khanh Ngoc | Backend / API Developer                     |

---

# 🚀 Getting Started / How to Replicate This Project

## Step 1. Environment Setup
1. **Copy the example environment file:**
    ```bash
    cp .env_example .env
    ```
2. **Edit your new `.env` file:**
    - Fill in your actual MySQL and admin credentials (e.g. DB_HOST, DB_USER, ADMIN_USERNAME, etc).
    - _**Never commit your `.env` file to GitHub! Only `.env_example` is safe to share.**_

---

## Step 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Step 3A. Easiest Way: One-Click Streamlit Initialization (RECOMMENDED)

Just run:
```bash
streamlit run streamlit_app/app.py
```
- The app will auto-detect if the database is fresh and perform all initialization (schema, triggers, sample data, admin user) for you.
- Make sure MySQL is running and `.env` matches your MySQL setup.

---

## Step 3B. Option 2: Manual Database Setup (Workbench/CLI + Python)
If you want full control (e.g., for classroom demo, debugging, or advanced troubleshooting):

1. Run these SQL files in order using MySQL Workbench or CLI:
    - `sql_scripts_for_workbench/01_ddl.sql`  _(all tables)_
    - `sql_scripts_for_workbench/02_rbac.sql` _(roles/permissions)_
    - `sql_scripts_for_workbench/03_sample_data.sql` _(sample data)_
    - `sql_scripts_for_workbench/04_triggers.sql` _(triggers: run all as a block)_
    - `sql_scripts_for_workbench/05_generate_tran_data.sql` _(optional)_
    - `sql_scripts_for_workbench/06_views.sql` _(views)_
    - `sql_scripts_for_workbench/07_stored_procedures.sql` _(stored procedures)_
    - `sql_scripts_for_workbench/08_indexing_and_compare.sql` _(index and performance comparison)_
2. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3. **Seed the first admin user** (env vars must be already in `.env`):
    ```bash
    python streamlit_app/config/seed_admin.py
    ```
4. **Launch the Streamlit app**:
    ```bash
    streamlit run streamlit_app/app.py
    ```

---

## Troubleshooting
- **Database connection issues:** Double-check `.env` matches your MySQL service.
- **MySQL not running:** Start MySQL service (`Services → MySQL80 → Start` on Windows).
- **Streamlit crashes at init step:** Details and further troubleshooting steps appear in the app interface.

---

## Security Note
- **Never commit any `.env` file with real secrets or passwords! Use ONLY `.env_example` for sharing or version control.**

---

## Summary
- **Normal users:** Copy `.env_example` → fill `.env` → `pip install -r requirements.txt` → `streamlit run streamlit_app/app.py` (let it initialize!👩‍💻)
- **Power users:** Run step-by-step as described above for total control and demo workflows.

---
