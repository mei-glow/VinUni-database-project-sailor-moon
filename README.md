# VinUni-database-project-sailor-moon
# VinRetail Management System
**A all-in-one system for Inventory, Ordering, Fulfillment & Delivery Operations**

---

## Project Description
VinRetail is an integrated retail management system designed to manage the entire operational workflow of a multi-store retail business.

The system solves key challenges such as:

- Managing thousands of products across categories and departments  
- Handling customer profiles, loyalty levels, and purchase behavior  
- Processing sales orders from creation → fulfillment → delivery  
- Monitoring stock transfers between warehouses and stores  
- Managing promotions, employee rewards, and delivery performance

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
| `DI_ITEMS`                | Product master data                               |
| `DI_CLASS`                | Product category                                  |
| `DI_DEPARTMENT`           | Department managing employees                     |
| `DI_LOCATIONS`            | Retail stores & warehouses                        |
| `DI_CUSTOMERS`            | Customer profiles                                 |
| `DI_LOYALTY_LEVEL`        | Customer tiers for membership rewards             |
| `DI_EMPLOYEES`            | Employee master data                              |
| `DI_PROMOTION`            | Promotion & discount programs                     |
| `SA_SALEORDERS`           | Sales order before fulfillment                    |
| `SA_SALEORDERS_ITEM`      | Items included in a sales order                   |
| `ITEM_FULFILMENT`         | Order Delivery                                    |
| `ITEM_FULFILMENT_ITEM`    | Order Delivery with Item                          |
| `SA_SALES`                | Completed sale record                             |
| `SA_SALES_ITEM`           | Sale record lines with item                       |
| `DI_SHIPPING_VENDOR`      | Third-party shipping vendors                      |
| `DI_DELIVERY_METHOD`      | Delivery types                                    |
| `DI_DELIVERY_VEHICLES`    | Vehicles used for delivery                        |
| `DI_BONUS_SALES`          | Bonus rules for employee sales                    |
| `DI_DELIVERY_BONUS`       | Bonus rules for deliveries                        |
| `DI_PAYMENT_METHOD`       | Payment methods of customers                      |

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
| Nguyen Khanh Ngoc |            | Backend / API Developer                   |


---

## Project Timeline

| Week    | Milestone                                              |
|--------:|:-------------------------------------------------------|
| Week 11 | Checkpoint 1 — Topic, README, Repo Setup               |
| Week 12 | ERD Diagram + Normalization                            |
| Week 13 | SQL Schema + Constraints + Sample Data                 |
| Week 14 | Core Queries + Stored Procedures + Views               |
| Week 15 | Application Demo + Final Documentation                 |


