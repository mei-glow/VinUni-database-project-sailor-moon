# VinUni-database-project-sailor-moon
# OmniRetail Management System
**A Unified System for Inventory, Ordering, Fulfillment & Delivery Operations**

---

## Project Description
OmniRetail is an integrated retail management system designed to handle the full operational workflow of a multi-store retail business.

The system solves key challenges such as:

- Managing thousands of products across categories and departments  
- Handling customer profiles, loyalty levels, and purchase behavior  
- Processing sales orders from creation → fulfillment → delivery  
- Tracking stock transfers between warehouses and stores  
- Managing promotions, employee bonuses, and delivery performance

This system aims to provide a structured database foundation for real-time retail operations.

---

## Functional Requirements

### 1. Product & Inventory Management
- Store master data of items, categories, and departments  
- Track inventory by warehouse/store location  
- Manage stock transfers between locations

### 2. Customer & Loyalty Management
- Maintain customer profiles  
- Track loyalty level and reward eligibility

### 3. Sales Order Processing
- Create and manage sales orders  
- Add and manage order items  
- Apply promotions

### 4. Fulfillment & Delivery
- Assign shipping vendors and delivery methods  
- Track delivery vehicles  
- Manage packing and fulfillment workflows

### 5. Sales & Performance Tracking
- Record completed sales  
- Apply employee sales bonuses  
- Track delivery bonus performance

---

## Non-Functional Requirements
- **Reliability:** ACID-compliant transactions for sales and inventory updates  
- **Scalability:** Support growth in stores, customers, and daily orders  
- **Security:** Role-based access (employees, managers, warehouse operators)  
- **Performance:** Optimized queries with indexing on large tables (sales, items)  
- **Maintainability:** Clean modular database schema

---

## Planned Core Entities

| Entity                    | Purpose                                          |
|--------------------------:|:-------------------------------------------------|
| `di_item`                 | Product master data                               |
| `di_class`                | Product category                                  |
| `di_department`           | Internal department managing categories           |
| `di_locations`            | Retail stores & warehouses                        |
| `di_customers`            | Customer profiles                                 |
| `loyalty_level`           | Customer tiers for membership rewards             |
| `di_employee`             | Employee master data                              |
| `di_promotion`            | Promotion & discount programs                     |
| `sa_salesorder`           | Sales order before fulfillment                    |
| `sa_salesorder_item`      | Items included in a sales order                   |
| `item_fulfillment`        | Order fulfillment & packing workflow              |
| `item_fulfillment_item`   | Items handled during fulfillment                  |
| `sa_sales`                | Completed sale record                             |
| `sa_sales_item`           | Final items included in a completed sale          |
| `di_ship_vendor`          | Third-party shipping vendors                      |
| `di_delivery_method`      | Delivery types                                    |
| `di_delivery_vehicle`     | Vehicles used for delivery                        |
| `di_bonus_sales`          | Bonus rules for employee sales                    |
| `di_delivery_bonus`       | Bonus rules for deliveries                        |
| `warehouse_transfer`      | Transfer request between locations                |
| `warehouse_transfer_item` | Items in a warehouse transfer                     |

---

## Tech Stack
- **Database:** MySQL 8.x  
- **Backend (planned):** Node.js (Express) *or* Python Flask  
- **Tools:** MySQL Workbench, GitHub, Draw.io (for ERD)

---

## Team Members & Roles

| Name                 | Role                                      |
|---------------------:|:------------------------------------------|
| Tran Phuong Mai      | Team Lead / Database Architect / Frontend |
| Do Phuong An         | Data Modeling / SQL Developer             |
| Nguyen Khanh Ngoc    | Backend / API Developer                   |

---

## Project Timeline

| Week    | Milestone                                              |
|--------:|:-------------------------------------------------------|
| Week 11 | Checkpoint 1 — Topic, README, Repo Setup               |
| Week 12 | ERD Diagram + Normalization                            |
| Week 13 | SQL Schema + Constraints + Sample Data                 |
| Week 14 | Core Queries + Stored Procedures + Views               |
| Week 15 | Application Demo + Final Documentation                 |


