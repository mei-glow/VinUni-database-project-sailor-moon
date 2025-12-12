# VinUni Database Project – VinRetail Management System

VinRetail is a database-centric retail management system designed to support end-to-end operations of a multi-store retail business.  
The project focuses on robust relational database design, business rule enforcement at the database layer, and scalability for real-world retail workloads.

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

- Reliability: ACID-compliant transactions and referential integrity  
- Scalability: Optimized indexing and partitioning strategies  
- Security: Role-based access and audit logging  
- Performance: Indexed transactional tables and derived reporting views  
- Maintainability: Modular schema and centralized business logic  

---

## Core Database Entities

### Master Data
- departments  
- locations  
- brands  
- product_class  
- products  
- customers  
- customer_preferences  
- loyalty_levels  
- employees  
- payment_methods  

### Inventory & Audit
- inventory  
- inventory_history  

### Sales & Transactions
- sales_orders  
- sales_order_items  
- sales  
- sales_items  

### Promotions
- promotions  
- promotions_campaigns  

### Delivery & Fulfillment
- delivery_vendors  
- delivery_vehicles  
- deliveries  
- delivery_status_history  

### Performance & Governance
- employee_bonus_rules  
- delivery_bonus_rules  
- customer_loyalty  
- audit_logs  

---

## Database Draft Diagram

<img width="3040" height="1873" alt="Blank diagram (6)" src="https://github.com/user-attachments/assets/5096f994-b352-4af1-ad8d-a8fc8f5ca558" />



---

## Tech Stack
- **Database:** MySQL 8.x  
- **Backend (planned):** Node.js (Express) *or* Python Flask  
- **Tools:** MySQL Workbench, GitHub, Draw.io (for ERD)

---

## Team Members & Roles

| Name              | Student ID | Role                                      |
|------------------:|:-----------|:------------------------------------------|
| Tran Phuong Mai   | V202401760 | Team Lead / Database Architect / Frontend |
| Do Phuong An      | V202401391 | Data Modeling / SQL Developer             |
| Nguyen Khanh Ngoc | V202401528 | Backend / API Developer                   |


---

## Project Timeline

| Week    | Milestone                                              |
|--------:|:-------------------------------------------------------|
| Week 11 | Checkpoint 1 — Topic, README, Repo Setup               |
| Week 12 | ERD Diagram + Normalization                            |
| Week 13 | SQL Schema + Constraints + Sample Data                 |
| Week 14 | Core Queries + Stored Procedures + Views               |
| Week 15 | Application Demo + Final Documentation                 |


