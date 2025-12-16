-- =====================================================
-- VinRetail Sample Data for Analytics
-- File: sample_data.sql
-- Description: Comprehensive sample data for testing and analytics
-- Note: Excludes users, roles, permissions (handled in rbac.sql)
-- =====================================================

USE vinretail;

SET FOREIGN_KEY_CHECKS = 0;

-- =====================================================
-- MASTER DATA
-- =====================================================

-- Departments
INSERT INTO departments (department_name) VALUES
('Sales & Marketing'),
('Operations & Logistics'),
('Human Resources'),
('Information Technology'),
('Finance & Accounting'),
('Customer Service'),
('Procurement'),
('Quality Assurance'),
('Business Development'),
('Legal & Compliance');

-- Brands (50 brands)
INSERT INTO brands (brand_name) VALUES
('Samsung'), ('Apple'), ('LG'), ('Sony'), ('Panasonic'),
('Nike'), ('Adidas'), ('Puma'), ('New Balance'), ('Under Armour'),
('Vinamilk'), ('TH True Milk'), ('Dutch Lady'), ('Nestle'), ('Coca-Cola'),
('Pepsi'), ('Lavie'), ('Aquafina'), ('Unilever'), ('P&G'),
('Gucci'), ('Louis Vuitton'), ('Chanel'), ('Prada'), ('Hermès'),
('Zara'), ('H&M'), ('Uniqlo'), ('Mango'), ('Forever 21'),
('Canon'), ('Nikon'), ('Fujifilm'), ('GoPro'), ('DJI'),
('Dell'), ('HP'), ('Lenovo'), ('Acer'), ('Asus'),
('Toyota'), ('Honda'), ('Yamaha'), ('Suzuki'), ('Kawasaki'),
('Bitis'), ('Juno'), ('Vascara'), ('MLB'), ('Converse');

-- Loyalty Levels
INSERT INTO loyalty_levels (level_name, min_total_spent) VALUES
('Bronze', 0),
('Silver', 5000000),
('Gold', 15000000),
('Platinum', 50000000),
('Diamond', 100000000),
('VIP', 250000000);

-- Payment Methods
INSERT INTO payment_methods (method_name) VALUES
('Cash'),
('Credit Card'),
('Debit Card'),
('Bank Transfer'),
('MoMo'),
('ZaloPay'),
('VNPay'),
('ShopeePay'),
('Installment 3 months'),
('Installment 6 months'),
('Installment 12 months'),
('COD');

-- =====================================================
-- EMPLOYEES (80 employees across departments)
-- =====================================================

-- Top Management
INSERT INTO employees (first_name, last_name, email, gender, department_id, role, hire_date, phone, supervisor_id) VALUES
('Nguyễn', 'Văn Anh', 'nguyenvananh@vinretail.com', 'M', 1, 'Admin', '2015-01-01', '0901000001', NULL),
('Trần', 'Thị Bình', 'tranthbinh@vinretail.com', 'F', 2, 'Admin', '2015-01-01', '0901000002', NULL),
('Lê', 'Văn Cường', 'levancuong@vinretail.com', 'M', 3, 'Manager', '2016-03-15', '0901000003', 1);

-- Sales Staff (30 employees)
INSERT INTO employees (first_name, last_name, email, gender, department_id, role, hire_date, phone, supervisor_id) VALUES
('Phạm', 'Thị Lan', 'phamthilan@vinretail.com', 'F', 1, 'Manager', '2017-06-01', '0901000004', 1),
('Hoàng', 'Văn Nam', 'hoangvannam@vinretail.com', 'M', 1, 'Staff', '2018-01-15', '0901000005', 4),
('Vũ', 'Thị Hương', 'vuthihuong@vinretail.com', 'F', 1, 'Staff', '2018-02-20', '0901000006', 4),
('Đỗ', 'Văn Hùng', 'dovanhung@vinretail.com', 'M', 1, 'Staff', '2018-03-10', '0901000007', 4),
('Bùi', 'Thị Mai', 'buithimai@vinretail.com', 'F', 1, 'Staff', '2018-04-05', '0901000008', 4),
('Đặng', 'Văn Quân', 'dangvanquan@vinretail.com', 'M', 1, 'Staff', '2018-05-12', '0901000009', 4),
('Đinh', 'Thị Nga', 'dinhthinga@vinretail.com', 'F', 1, 'Staff', '2018-06-18', '0901000010', 4),
('Dương', 'Văn Tài', 'duongvantai@vinretail.com', 'M', 1, 'Staff', '2018-07-22', '0901000011', 4),
('Hồ', 'Thị Oanh', 'hothioanh@vinretail.com', 'F', 1, 'Staff', '2018-08-30', '0901000012', 4),
('Lý', 'Văn Phong', 'lyvanphong@vinretail.com', 'M', 1, 'Staff', '2019-01-10', '0901000013', 4),
('Mai', 'Thị Quỳnh', 'maithiquynh@vinretail.com', 'F', 1, 'Staff', '2019-02-14', '0901000014', 4),
('Ngô', 'Văn Sơn', 'ngovanson@vinretail.com', 'M', 1, 'Staff', '2019-03-20', '0901000015', 4),
('Phan', 'Thị Tâm', 'phanthitam@vinretail.com', 'F', 1, 'Staff', '2019-04-25', '0901000016', 4),
('Tô', 'Văn Uy', 'tovanuy@vinretail.com', 'M', 1, 'Staff', '2019-05-30', '0901000017', 4),
('Võ', 'Thị Vân', 'vothivan@vinretail.com', 'F', 1, 'Staff', '2019-07-05', '0901000018', 4),
('Châu', 'Văn Xuân', 'chauvanxuan@vinretail.com', 'M', 1, 'Staff', '2020-01-10', '0901000019', 4),
('Kiều', 'Thị Yến', 'kieuthiyen@vinretail.com', 'F', 1, 'Staff', '2020-02-15', '0901000020', 4),
('Lưu', 'Văn An', 'luuvanan@vinretail.com', 'M', 1, 'Staff', '2020-03-20', '0901000021', 4),
('Mạc', 'Thị Bảo', 'macithibao@vinretail.com', 'F', 1, 'Staff', '2020-04-25', '0901000022', 4),
('Ninh', 'Văn Cảnh', 'ninhvancanh@vinretail.com', 'M', 1, 'Staff', '2020-06-01', '0901000023', 4),
('Ông', 'Thị Dung', 'ongthidung@vinretail.com', 'F', 1, 'Staff', '2021-01-05', '0901000024', 4),
('Phùng', 'Văn Em', 'phungvanem@vinretail.com', 'M', 1, 'Staff', '2021-02-10', '0901000025', 4),
('Quách', 'Thị Giang', 'quachthigiang@vinretail.com', 'F', 1, 'Staff', '2021-03-15', '0901000026', 4),
('Sử', 'Văn Hải', 'suvanhai@vinretail.com', 'M', 1, 'Staff', '2021-04-20', '0901000027', 4),
('Tạ', 'Thị Lan', 'tathilan@vinretail.com', 'F', 1, 'Staff', '2021-06-01', '0901000028', 4),
('Ứng', 'Văn Minh', 'ungvanminh@vinretail.com', 'M', 1, 'Staff', '2022-01-10', '0901000029', 4),
('Văn', 'Thị Nhung', 'vanthinhung@vinretail.com', 'F', 1, 'Staff', '2022-03-15', '0901000030', 4),
('Xa', 'Văn Phú', 'xavanphu@vinretail.com', 'M', 1, 'Staff', '2022-06-01', '0901000031', 4),
('Yên', 'Thị Quế', 'yenthique@vinretail.com', 'F', 1, 'Staff', '2023-01-10', '0901000032', 4),
('Lâm', 'Văn Toàn', 'lamvantoan@vinretail.com', 'M', 1, 'Staff', '2023-06-01', '0901000033', 4);

-- Warehouse Staff (20 employees)
INSERT INTO employees (first_name, last_name, email, gender, department_id, role, hire_date, phone, supervisor_id) VALUES
('Cao', 'Văn Kiên', 'caovankien@vinretail.com', 'M', 2, 'Manager', '2017-02-01', '0902000001', 2),
('Hà', 'Thị Linh', 'hathilinh@vinretail.com', 'F', 2, 'Warehouse', '2018-03-15', '0902000002', 34),
('Khương', 'Văn Mạnh', 'khuongvanmanh@vinretail.com', 'M', 2, 'Warehouse', '2018-06-20', '0902000003', 34),
('La', 'Thị Nhi', 'lathinhi@vinretail.com', 'F', 2, 'Warehouse', '2018-09-10', '0902000004', 34),
('Ma', 'Văn Ông', 'mavanonh@vinretail.com', 'M', 2, 'Warehouse', '2019-01-15', '0902000005', 34),
('Nhan', 'Thị Phượng', 'nhanthiphuong@vinretail.com', 'F', 2, 'Warehouse', '2019-04-20', '0902000006', 34),
('Ô', 'Văn Quốc', 'ovanquoc@vinretail.com', 'M', 2, 'Warehouse', '2019-07-25', '0902000007', 34),
('Phó', 'Thị Rạng', 'phothirang@vinretail.com', 'F', 2, 'Warehouse', '2019-10-30', '0902000008', 34),
('Quang', 'Văn Sang', 'quangvansang@vinretail.com', 'M', 2, 'Warehouse', '2020-02-05', '0902000009', 34),
('Rạng', 'Thị Tú', 'rangthitu@vinretail.com', 'F', 2, 'Warehouse', '2020-05-10', '0902000010', 34),
('Sơn', 'Văn Uy', 'sonvanuy@vinretail.com', 'M', 2, 'Warehouse', '2020-08-15', '0902000011', 34),
('Tào', 'Thị Vui', 'taothivui@vinretail.com', 'F', 2, 'Warehouse', '2020-11-20', '0902000012', 34),
('Ung', 'Văn Xuân', 'ungvanxuan@vinretail.com', 'M', 2, 'Warehouse', '2021-02-25', '0902000013', 34),
('Vi', 'Thị Yến', 'vithiyen@vinretail.com', 'F', 2, 'Warehouse', '2021-05-30', '0902000014', 34),
('Xa', 'Văn Anh', 'xavananh@vinretail.com', 'M', 2, 'Warehouse', '2021-09-05', '0902000015', 34),
('Yên', 'Thị Bích', 'yenthibich@vinretail.com', 'F', 2, 'Warehouse', '2022-01-10', '0902000016', 34),
('Âu', 'Văn Cường', 'auvancuong@vinretail.com', 'M', 2, 'Warehouse', '2022-04-15', '0902000017', 34),
('Bành', 'Thị Duyên', 'banhthiduyen@vinretail.com', 'F', 2, 'Warehouse', '2022-07-20', '0902000018', 34),
('Cái', 'Văn Em', 'caivanem@vinretail.com', 'M', 2, 'Warehouse', '2022-10-25', '0902000019', 34),
('Đái', 'Thị Phương', 'daithiphuong@vinretail.com', 'F', 2, 'Warehouse', '2023-02-01', '0902000020', 34);

-- Delivery Staff (20 employees)
INSERT INTO employees (first_name, last_name, email, gender, department_id, role, hire_date, phone, supervisor_id) VALUES
('Tống', 'Văn Đức', 'tongvanduc@vinretail.com', 'M', 2, 'Delivery', '2018-01-10', '0903000001', 34),
('Trịnh', 'Văn Hải', 'trinhvanhai@vinretail.com', 'M', 2, 'Delivery', '2018-04-15', '0903000002', 34),
('Trương', 'Văn Long', 'truongvanlong@vinretail.com', 'M', 2, 'Delivery', '2018-07-20', '0903000003', 34),
('Ưng', 'Văn Minh', 'ungvanminh@vinretail.com', 'M', 2, 'Delivery', '2018-10-25', '0903000004', 34),
('Vương', 'Văn Nam', 'vuongvannam@vinretail.com', 'M', 2, 'Delivery', '2019-02-01', '0903000005', 34),
('Xung', 'Văn Phong', 'xungvanphong@vinretail.com', 'M', 2, 'Delivery', '2019-05-10', '0903000006', 34),
('An', 'Văn Quân', 'anvanquan@vinretail.com', 'M', 2, 'Delivery', '2019-08-15', '0903000007', 34),
('Bàng', 'Văn Sơn', 'bangvanson@vinretail.com', 'M', 2, 'Delivery', '2019-11-20', '0903000008', 34),
('Cầm', 'Văn Tài', 'camvantai@vinretail.com', 'M', 2, 'Delivery', '2020-03-01', '0903000009', 34),
('Đàm', 'Văn Uy', 'damvanuy@vinretail.com', 'M', 2, 'Delivery', '2020-06-10', '0903000010', 34),
('Gia', 'Văn Vinh', 'giavanvinh@vinretail.com', 'M', 2, 'Delivery', '2020-09-15', '0903000011', 34),
('Hàn', 'Văn Xuân', 'hanvanxuan@vinretail.com', 'M', 2, 'Delivery', '2020-12-20', '0903000012', 34),
('Khổng', 'Văn Yên', 'khongvanyen@vinretail.com', 'M', 2, 'Delivery', '2021-03-25', '0903000013', 34),
('Lục', 'Văn An', 'lucvanan@vinretail.com', 'M', 2, 'Delivery', '2021-07-01', '0903000014', 34),
('Mã', 'Văn Bình', 'mavanbinh@vinretail.com', 'M', 2, 'Delivery', '2021-10-10', '0903000015', 34),
('Nhữ', 'Văn Cường', 'nhuvancuong@vinretail.com', 'M', 2, 'Delivery', '2022-02-15', '0903000016', 34),
('Ổ', 'Văn Đạt', 'ovandat@vinretail.com', 'M', 2, 'Delivery', '2022-05-20', '0903000017', 34),
('Phí', 'Văn Hùng', 'phivanhung@vinretail.com', 'M', 2, 'Delivery', '2022-08-25', '0903000018', 34),
('Quý', 'Văn Khang', 'quyvankhang@vinretail.com', 'M', 2, 'Delivery', '2022-11-30', '0903000019', 34),
('Rùa', 'Văn Lâm', 'ruavanlam@vinretail.com', 'M', 2, 'Delivery', '2023-03-01', '0903000020', 34);

-- HR & Other Staff (10 employees)
INSERT INTO employees (first_name, last_name, email, gender, department_id, role, hire_date, phone, supervisor_id) VALUES
('Thi', 'Thị Giang', 'thithigiang@vinretail.com', 'F', 3, 'Manager', '2017-05-01', '0904000001', 3),
('Ung', 'Văn Hà', 'ungvanha@vinretail.com', 'M', 4, 'Manager', '2017-06-01', '0904000002', 1),
('Vân', 'Thị Lan', 'vanthilan@vinretail.com', 'F', 5, 'Manager', '2017-07-01', '0904000003', 1),
('Xá', 'Văn Minh', 'xavanminh@vinretail.com', 'M', 6, 'Manager', '2018-01-01', '0904000004', 1),
('Yết', 'Thị Nga', 'yetthinga@vinretail.com', 'F', 7, 'Staff', '2019-01-15', '0904000005', 1),
('Âu Dương', 'Văn Phong', 'auduongvanphong@vinretail.com', 'M', 8, 'Staff', '2019-06-01', '0904000006', 2),
('Bạch', 'Thị Quỳnh', 'bachthiquynh@vinretail.com', 'F', 9, 'Staff', '2020-01-10', '0904000007', 1),
('Cung', 'Văn Sơn', 'cungvanson@vinretail.com', 'M', 10, 'Staff', '2020-06-15', '0904000008', 1),
('Đan', 'Thị Tâm', 'danthitam@vinretail.com', 'F', 3, 'Staff', '2021-01-20', '0904000009', 74),
('Giang', 'Văn Tuấn', 'giangvantuan@vinretail.com', 'M', 4, 'Staff', '2021-06-25', '0904000010', 75);

-- =====================================================
-- LOCATIONS (25 locations)
-- =====================================================

INSERT INTO locations (location_name, location_type, address, city, region, channel, store_manager_id, opening_date) VALUES
-- North Region Stores
('VinRetail Hà Nội Tràng Tiền', 'STORE', '12 Tràng Tiền, Hoàn Kiếm', 'Hà Nội', 'North', 'Offline', 4, '2018-01-15'),
('VinRetail Hà Nội Times City', 'STORE', '458 Minh Khai, Hai Bà Trưng', 'Hà Nội', 'North', 'Offline', 4, '2018-06-20'),
('VinRetail Hà Nội Royal City', 'STORE', '72A Nguyễn Trãi, Thanh Xuân', 'Hà Nội', 'North', 'Offline', 4, '2019-01-10'),
('VinRetail Hà Nội Aeon Mall', 'STORE', 'Aeon Mall, Long Biên', 'Hà Nội', 'North', 'Offline', 4, '2019-07-15'),
('VinRetail Hà Nội Vincom Mega Mall', 'STORE', '458 Minh Khai', 'Hà Nội', 'North', 'Offline', 4, '2020-01-20'),
('VinRetail Hải Phòng', 'STORE', '10 Trần Phú, Ngô Quyền', 'Hải Phòng', 'North', 'Offline', 4, '2019-03-10'),
('VinRetail Quảng Ninh', 'STORE', '25 Hạ Long, Bãi Cháy', 'Quảng Ninh', 'North', 'Offline', 4, '2020-06-15'),
('VinRetail Nam Định', 'STORE', '88 Trần Hưng Đạo', 'Nam Định', 'North', 'Offline', 4, '2021-01-05'),

-- South Region Stores
('VinRetail TPHCM Nguyễn Huệ', 'STORE', '135 Nguyễn Huệ, Q1', 'TP.HCM', 'South', 'Offline', 4, '2018-02-01'),
('VinRetail TPHCM Vincom Center', 'STORE', '72 Lê Thánh Tôn, Q1', 'TP.HCM', 'South', 'Offline', 4, '2018-08-10'),
('VinRetail TPHCM Crescent Mall', 'STORE', '101 Tôn Dật Tiên, Q7', 'TP.HCM', 'South', 'Offline', 4, '2019-03-15'),
('VinRetail TPHCM Aeon Mall Tân Phú', 'STORE', '30 Bờ Bao Tân Thắng, Tân Phú', 'TP.HCM', 'South', 'Offline', 4, '2019-09-20'),
('VinRetail TPHCM SC VivoCity', 'STORE', '1058 Nguyễn Văn Linh, Q7', 'TP.HCM', 'South', 'Offline', 4, '2020-03-25'),
('VinRetail Đà Nẵng Trần Phú', 'STORE', '123 Trần Phú, Hải Châu', 'Đà Nẵng', 'South', 'Offline', 4, '2019-02-15'),
('VinRetail Đà Nẵng Vincom Plaza', 'STORE', '910A Ngô Quyền', 'Đà Nẵng', 'South', 'Offline', 4, '2020-07-20'),
('VinRetail Cần Thơ', 'STORE', '42 Hai Bà Trưng, Ninh Kiều', 'Cần Thơ', 'South', 'Offline', 4, '2020-10-05'),
('VinRetail Nha Trang', 'STORE', '18 Trần Phú, Nha Trang', 'Khánh Hòa', 'South', 'Offline', 4, '2021-03-10'),
('VinRetail Vũng Tàu', 'STORE', '55 Quang Trung', 'Bà Rịa-Vũng Tàu', 'South', 'Offline', 4, '2021-08-15'),

-- Online Channels
('VinRetail Online Store North', 'STORE', 'E-commerce Platform', 'Hà Nội', 'North', 'Online', 4, '2018-01-01'),
('VinRetail Online Store South', 'STORE', 'E-commerce Platform', 'TP.HCM', 'South', 'Online', 4, '2018-01-01'),
('VinRetail Shopee Mall', 'STORE', 'Shopee Platform', 'TP.HCM', 'South', 'Ecommerce', 4, '2019-01-01'),
('VinRetail Lazada Mall', 'STORE', 'Lazada Platform', 'TP.HCM', 'South', 'Ecommerce', 4, '2019-01-01'),
('VinRetail Tiki Official', 'STORE', 'Tiki Platform', 'TP.HCM', 'South', 'Ecommerce', 4, '2019-06-01'),

-- Warehouses
('VinRetail Warehouse North', 'WAREHOUSE', 'KCN Quang Minh, Mê Linh', 'Hà Nội', 'North', 'Warehouse', 34, '2017-12-01'),
('VinRetail Warehouse South', 'WAREHOUSE', 'KCN Tân Bình', 'TP.HCM', 'South', 'Warehouse', 34, '2017-12-01');

-- =====================================================
-- PRODUCT CLASSES (100 classes across categories)
-- =====================================================

INSERT INTO product_class (class_name, brand_id, product_group) VALUES
-- Electronics (Samsung, Apple, LG, Sony, Panasonic)
('Samsung Galaxy Smartphone', 1, 'electronics'),
('Samsung Galaxy Tab', 1, 'electronics'),
('Apple iPhone', 2, 'electronics'),
('Apple iPad', 2, 'electronics'),
('Apple MacBook', 2, 'electronics'),
('LG Smart TV', 3, 'home_appliances'),
('LG Refrigerator', 3, 'home_appliances'),
('Sony Bravia TV', 4, 'home_appliances'),
('Sony Headphones', 4, 'electronics'),
('Panasonic Air Conditioner', 5, 'home_appliances'),

-- Footwear & Sportswear (Nike, Adidas, Puma, New Balance, Under Armour)
('Nike Running Shoes', 6, 'footwear'),
('Nike Training Shoes', 6, 'footwear'),
('Nike Sportswear', 6, 'clothing'),
('Adidas Ultraboost', 7, 'footwear'),
('Adidas Superstar', 7, 'footwear'),
('Adidas Sportswear', 7, 'clothing'),
('Puma Running', 8, 'footwear'),
('Puma Casual', 8, 'footwear'),
('New Balance Sneakers', 9, 'footwear'),
('Under Armour Sports', 10, 'clothing'),

-- Food & Beverages (Vinamilk, TH, Dutch Lady, Nestle, Coca-Cola, Pepsi, Lavie, Aquafina)
('Vinamilk Fresh Milk', 11, 'food'),
('Vinamilk Yogurt', 11, 'food'),
('TH True Milk', 12, 'food'),
('Dutch Lady Milk', 13, 'food'),
('Nestle Coffee', 14, 'beverages'),
('Coca-Cola Drinks', 15, 'beverages'),
('Pepsi Drinks', 16, 'beverages'),
('Lavie Water', 17, 'beverages'),
('Aquafina Water', 18, 'beverages'),

-- Beauty & Personal Care (Unilever, P&G)
('Unilever Shampoo', 19, 'beauty_personal_care'),
('Unilever Skincare', 19, 'beauty_personal_care'),
('P&G Toothpaste', 20, 'beauty_personal_care'),
('P&G Detergent', 20, 'beauty_personal_care'),

-- Luxury Fashion (Gucci, LV, Chanel, Prada, Hermès)
('Gucci Handbags', 21, 'fashion_accessories'),
('Gucci Sunglasses', 21, 'fashion_accessories'),
('Louis Vuitton Bags', 22, 'fashion_accessories'),
('Louis Vuitton Wallets', 22, 'fashion_accessories'),
('Chanel Perfume', 23, 'beauty_personal_care'),
('Chanel Bags', 23, 'fashion_accessories'),
('Prada Bags', 24, 'fashion_accessories'),
('Hermès Bags', 25, 'fashion_accessories'),

-- Fashion Retail (Zara, H&M, Uniqlo, Mango, Forever 21)
('Zara Men Clothing', 26, 'clothing'),
('Zara Women Clothing', 26, 'clothing'),
('H&M Basics', 27, 'clothing'),
('H&M Kids', 27, 'baby_kids'),
('Uniqlo Heattech', 28, 'clothing'),
('Uniqlo Airism', 28, 'clothing'),
('Mango Dresses', 29, 'clothing'),
('Forever 21 Casual', 30, 'clothing'),

-- Electronics & Cameras (Canon, Nikon, Fujifilm, GoPro, DJI)
('Canon DSLR', 31, 'electronics'),
('Canon Lenses', 31, 'electronics'),
('Nikon DSLR', 32, 'electronics'),
('Fujifilm Instax', 33, 'electronics'),
('GoPro Action Camera', 34, 'electronics'),
('DJI Drones', 35, 'electronics'),

-- Computers (Dell, HP, Lenovo, Acer, Asus)
('Dell Laptop', 36, 'electronics'),
('Dell Desktop', 36, 'office_equipment'),
('HP Laptop', 37, 'electronics'),
('HP Printer', 37, 'office_equipment'),
('Lenovo ThinkPad', 38, 'electronics'),
('Acer Gaming', 39, 'electronics'),
('Asus ROG', 40, 'electronics'),

-- Automotive & Bikes (Toyota, Honda, Yamaha, Suzuki, Kawasaki)
('Toyota Accessories', 41, 'automotive'),
('Honda Motorcycle', 42, 'automotive'),
('Yamaha Motorcycle', 43, 'automotive'),
('Suzuki Motorcycle', 44, 'automotive'),
('Kawasaki Motorcycle', 45, 'automotive'),

-- Vietnamese Brands (Bitis, Juno, Vascara, MLB, Converse)
('Bitis Hunter', 46, 'footwear'),
('Bitis Casual', 46, 'footwear'),
('Juno Handbags', 47, 'fashion_accessories'),
('Juno Shoes', 47, 'footwear'),
('Vascara Shoes', 48, 'footwear'),
('Vascara Bags', 48, 'fashion_accessories'),
('MLB Streetwear', 49, 'clothing'),
('Converse Sneakers', 50, 'footwear');

-- =====================================================
-- PRODUCTS (200+ products)
-- =====================================================

-- Electronics (30 products)
INSERT INTO products (product_name, class_id, unit_price, cost, status, color) VALUES
('Samsung Galaxy S24 Ultra', 1, 29990000, 22000000, 'ACTIVE', 'Titanium Black'),
('Samsung Galaxy S24 Plus', 1, 25990000, 19000000, 'ACTIVE', 'Cream'),
('Samsung Galaxy S24', 1, 21990000, 16000000, 'ACTIVE', 'Onyx Black'),
('Samsung Galaxy Tab S9', 2, 18990000, 14000000, 'ACTIVE', 'Graphite'),
('iPhone 15 Pro Max', 3, 32990000, 24000000, 'ACTIVE', 'Natural Titanium'),
('iPhone 15 Pro', 3, 28990000, 21000000, 'ACTIVE', 'Blue Titanium'),
('iPhone 15', 3, 24990000, 18000000, 'ACTIVE', 'Pink'),
('iPad Pro 12.9', 4, 29990000, 22000000, 'ACTIVE', 'Space Gray'),
('iPad Air', 4, 15990000, 12000000, 'ACTIVE', 'Purple'),
('MacBook Pro 14', 5, 49990000, 37000000, 'ACTIVE', 'Space Gray'),
('MacBook Air M2', 5, 29990000, 22000000, 'ACTIVE', 'Midnight'),
('LG OLED TV 65"', 6, 45990000, 34000000, 'ACTIVE', 'Black'),
('LG Smart TV 55"', 6, 18990000, 14000000, 'ACTIVE', 'Black'),
('LG Inverter Refrigerator', 7, 15990000, 12000000, 'ACTIVE', 'Silver'),
('Sony Bravia XR 75"', 8, 59990000, 44000000, 'ACTIVE', 'Black'),
('Sony WH-1000XM5', 9, 8990000, 6500000, 'ACTIVE', 'Black'),
('Panasonic Inverter AC 1.5HP', 10, 12990000, 9500000, 'ACTIVE', 'White'),
('Canon EOS R6', 51, 55990000, 41000000, 'ACTIVE', 'Black'),
('Canon RF 24-70mm', 52, 28990000, 21000000, 'ACTIVE', 'Black'),
('Nikon Z6 II', 53, 49990000, 37000000, 'ACTIVE', 'Black'),
('Fujifilm Instax Mini 12', 54, 1890000, 1400000, 'ACTIVE', 'Pink'),
('GoPro Hero 12', 55, 12990000, 9500000, 'ACTIVE', 'Black'),
('DJI Mini 3 Pro', 56, 19990000, 14500000, 'ACTIVE', 'Gray'),
('Dell XPS 13', 57, 32990000, 24000000, 'ACTIVE', 'Platinum Silver'),
('Dell Latitude 5420', 58, 24990000, 18000000, 'ACTIVE', 'Black'),
('HP Pavilion 15', 59, 18990000, 14000000, 'ACTIVE', 'Silver'),
('HP LaserJet Pro', 60, 5990000, 4400000, 'ACTIVE', 'White'),
('Lenovo ThinkPad X1', 61, 35990000, 26000000, 'ACTIVE', 'Black'),
('Acer Predator Helios', 62, 32990000, 24000000, 'ACTIVE', 'Black'),
('Asus ROG Strix G15', 63, 29990000, 22000000, 'ACTIVE', 'Gray');

-- Footwear & Sports (40 products)
INSERT INTO products (product_name, class_id, unit_price, cost, status, color) VALUES
('Nike Air Max 270', 11, 3890000, 2800000, 'ACTIVE', 'White'),
('Nike React Infinity Run', 11, 4290000, 3100000, 'ACTIVE', 'Black'),
('Nike Pegasus 40', 11, 3590000, 2600000, 'ACTIVE', 'Blue'),
('Nike Metcon 8', 12, 4190000, 3000000, 'ACTIVE', 'Gray'),
('Nike Air Force 1', 12, 2890000, 2100000, 'ACTIVE', 'White'),
('Nike Dri-FIT Tee', 13, 690000, 500000, 'ACTIVE', 'Black'),
('Nike Tech Fleece', 13, 2490000, 1800000, 'ACTIVE', 'Navy'),
('Nike Swoosh Leggings', 13, 1290000, 950000, 'ACTIVE', 'Black'),
('Adidas Ultraboost 23', 14, 4790000, 3500000, 'ACTIVE', 'White'),
('Adidas Ultraboost Light', 14, 4390000, 3200000, 'ACTIVE', 'Black'),
('Adidas Samba OG', 15, 2790000, 2000000, 'ACTIVE', 'White/Black'),
('Adidas Superstar', 15, 2490000, 1800000, 'ACTIVE', 'White'),
('Adidas Essentials Tee', 16, 590000, 430000, 'ACTIVE', 'White'),
('Adidas 3-Stripes Shorts', 16, 890000, 650000, 'ACTIVE', 'Black'),
('Puma Velocity Nitro', 17, 3290000, 2400000, 'ACTIVE', 'Red'),
('Puma Deviate Nitro', 17, 3990000, 2900000, 'ACTIVE', 'Yellow'),
('Puma RS-X', 18, 2790000, 2000000, 'ACTIVE', 'White'),
('Puma Suede Classic', 18, 2290000, 1650000, 'ACTIVE', 'Black'),
('New Balance 1080v13', 19, 4590000, 3300000, 'ACTIVE', 'Blue'),
('New Balance 574', 19, 2490000, 1800000, 'ACTIVE', 'Gray'),
('Under Armour Hovr Phantom', 20, 3690000, 2700000, 'ACTIVE', 'Black'),
('Under Armour HeatGear Tee', 20, 790000, 580000, 'ACTIVE', 'White'),
('Bitis Hunter 2k23', 71, 890000, 650000, 'ACTIVE', 'Black'),
('Bitis Hunter Street', 71, 990000, 720000, 'ACTIVE', 'White'),
('Bitis Classic', 72, 590000, 430000, 'ACTIVE', 'Navy'),
('Bitis Sport', 72, 690000, 500000, 'ACTIVE', 'Red'),
('Juno Tote Bag', 73, 1290000, 950000, 'ACTIVE', 'Brown'),
('Juno Crossbody', 73, 990000, 720000, 'ACTIVE', 'Black'),
('Juno High Heels', 74, 1190000, 870000, 'ACTIVE', 'Black'),
('Juno Sandals', 74, 790000, 580000, 'ACTIVE', 'Beige'),
('Vascara Pump Heels', 75, 1390000, 1000000, 'ACTIVE', 'Red'),
('Vascara Loafers', 75, 990000, 720000, 'ACTIVE', 'Black'),
('Vascara Shoulder Bag', 76, 1190000, 870000, 'ACTIVE', 'Brown'),
('MLB NY Yankees Cap', 77, 690000, 500000, 'ACTIVE', 'Black'),
('MLB LA Dodgers Tee', 77, 890000, 650000, 'ACTIVE', 'Blue'),
('Converse Chuck 70', 78, 1990000, 1450000, 'ACTIVE', 'Black'),
('Converse All Star Low', 78, 1590000, 1150000, 'ACTIVE', 'White'),
('Converse Chuck Taylor High', 78, 1790000, 1300000, 'ACTIVE', 'Red'),
('Converse Run Star Hike', 78, 2290000, 1650000, 'ACTIVE', 'Black'),
('Converse One Star', 78, 1890000, 1370000, 'ACTIVE', 'Purple');

-- Food & Beverages (40 products)
INSERT INTO products (product_name, class_id, unit_price, cost, status) VALUES
('Vinamilk Tươi Nguyên Chất 1L', 21, 36000, 26000, 'ACTIVE'),
('Vinamilk Ít Đường 1L', 21, 34000, 24500, 'ACTIVE'),
('Vinamilk Có Đường 180ml', 21, 8000, 5800, 'ACTIVE'),
('Vinamilk Yogurt Uống 180ml', 22, 9000, 6500, 'ACTIVE'),
('Vinamilk Yogurt Hộp 100g', 22, 7000, 5000, 'ACTIVE'),
('Vinamilk Probi 65ml', 22, 6000, 4300, 'ACTIVE'),
('TH True Milk Tươi 1L', 23, 42000, 30000, 'ACTIVE'),
('TH True Milk Organic 1L', 23, 52000, 37500, 'ACTIVE'),
('Dutch Lady Canxi 180ml', 24, 8500, 6100, 'ACTIVE'),
('Dutch Lady Uống Liền 1L', 24, 38000, 27500, 'ACTIVE'),
('Nescafe Classic 200g', 25, 95000, 68500, 'ACTIVE'),
('Nescafe Gold 100g', 25, 135000, 97000, 'ACTIVE'),
('Coca-Cola 390ml', 26, 12000, 8700, 'ACTIVE'),
('Coca-Cola 1.5L', 26, 22000, 15900, 'ACTIVE'),
('Coca-Cola Zero 390ml', 26, 12000, 8700, 'ACTIVE'),
('Pepsi Cola 390ml', 27, 11000, 7900, 'ACTIVE'),
('Pepsi Cola 1.5L', 27, 21000, 15100, 'ACTIVE'),
('Pepsi Zero 390ml', 27, 11000, 7900, 'ACTIVE'),
('Lavie 350ml', 28, 4000, 2900, 'ACTIVE'),
('Lavie 1.5L', 28, 8000, 5800, 'ACTIVE'),
('Lavie 6L', 28, 25000, 18000, 'ACTIVE'),
('Aquafina 500ml', 29, 5000, 3600, 'ACTIVE'),
('Aquafina 1.5L', 29, 10000, 7200, 'ACTIVE'),
('Aquafina 19L', 29, 55000, 39500, 'ACTIVE');

-- Beauty & Personal Care (30 products)
INSERT INTO products (product_name, class_id, unit_price, cost, status) VALUES
('Sunsilk Dầu Gội 650ml', 30, 85000, 61000, 'ACTIVE'),
('Clear Men 650ml', 30, 125000, 90000, 'ACTIVE'),
('Dove Dầu Gội 650ml', 30, 165000, 119000, 'ACTIVE'),
('Dove Kem Dưỡng Thể 400ml', 31, 185000, 133000, 'ACTIVE'),
('Ponds Kem Dưỡng Trắng 50g', 31, 125000, 90000, 'ACTIVE'),
('Simple Nước Tẩy Trang 400ml', 31, 145000, 104500, 'ACTIVE'),
('P/S Kem Đánh Răng 230g', 32, 42000, 30000, 'ACTIVE'),
('Colgate Total 230g', 32, 58000, 41800, 'ACTIVE'),
('Close Up 230g', 32, 48000, 34600, 'ACTIVE'),
('Ariel Matic 3.8kg', 33, 285000, 205000, 'ACTIVE'),
('OMO Matic 3.7kg', 33, 245000, 176500, 'ACTIVE'),
('Tide Matic 3.8kg', 33, 255000, 183500, 'ACTIVE'),
('Chanel No. 5 EDP 50ml', 35, 3290000, 2370000, 'ACTIVE'),
('Chanel Chance EDT 100ml', 35, 3590000, 2590000, 'ACTIVE'),
('Chanel Coco Mademoiselle 50ml', 35, 3490000, 2515000, 'ACTIVE');

-- Luxury Fashion (30 products)
INSERT INTO products (product_name, class_id, unit_price, cost, status, color) VALUES
('Gucci Marmont Bag', 34, 52000000, 37500000, 'ACTIVE', 'Black'),
('Gucci Dionysus Small', 34, 58000000, 41800000, 'ACTIVE', 'Red'),
('Gucci Aviator Sunglasses', 35, 12000000, 8650000, 'ACTIVE', 'Gold'),
('Gucci Square Sunglasses', 35, 10500000, 7570000, 'ACTIVE', 'Black'),
('LV Neverfull MM', 36, 45000000, 32400000, 'ACTIVE', 'Monogram'),
('LV Speedy 30', 36, 39000000, 28100000, 'ACTIVE', 'Damier'),
('LV Zippy Wallet', 37, 18000000, 12960000, 'ACTIVE', 'Black'),
('LV Card Holder', 37, 9500000, 6850000, 'ACTIVE', 'Epi'),
('Chanel Classic Flap', 38, 185000000, 133300000, 'ACTIVE', 'Black'),
('Chanel Boy Bag', 38, 95000000, 68500000, 'ACTIVE', 'Navy'),
('Prada Galleria', 39, 68000000, 49000000, 'ACTIVE', 'Saffiano'),
('Prada Re-Nylon', 39, 42000000, 30300000, 'ACTIVE', 'Black'),
('Hermès Birkin 30', 40, 295000000, 212500000, 'ACTIVE', 'Orange'),
('Hermès Kelly 28', 40, 285000000, 205300000, 'ACTIVE', 'Black');

-- Fashion Retail (40 products)
INSERT INTO products (product_name, class_id, unit_price, cost, status, color) VALUES
('Zara Blazer Nam', 41, 1890000, 1360000, 'ACTIVE', 'Black'),
('Zara Jeans Nam', 41, 1290000, 930000, 'ACTIVE', 'Blue'),
('Zara T-Shirt Nam', 41, 590000, 425000, 'ACTIVE', 'White'),
('Zara Váy Nữ', 42, 1490000, 1070000, 'ACTIVE', 'Red'),
('Zara Áo Nữ', 42, 890000, 640000, 'ACTIVE', 'Black'),
('Zara Quần Nữ', 42, 990000, 710000, 'ACTIVE', 'Beige'),
('H&M Basic Tee', 43, 299000, 215000, 'ACTIVE', 'White'),
('H&M Hoodie', 43, 799000, 575000, 'ACTIVE', 'Gray'),
('H&M Jeans', 43, 699000, 503000, 'ACTIVE', 'Black'),
('H&M Kids Tee', 44, 199000, 143000, 'ACTIVE', 'Pink'),
('H&M Kids Dress', 44, 499000, 359000, 'ACTIVE', 'Blue'),
('Uniqlo Heattech Inner', 45, 399000, 287000, 'ACTIVE', 'Black'),
('Uniqlo Heattech Leggings', 45, 499000, 359000, 'ACTIVE', 'Gray'),
('Uniqlo Airism Tee', 46, 299000, 215000, 'ACTIVE', 'White'),
('Uniqlo Airism Polo', 46, 499000, 359000, 'ACTIVE', 'Navy'),
('Mango Dress', 47, 1290000, 930000, 'ACTIVE', 'Floral'),
('Mango Blazer', 47, 1690000, 1217000, 'ACTIVE', 'Camel'),
('Forever 21 Crop Top', 48, 290000, 209000, 'ACTIVE', 'Pink'),
('Forever 21 Jeans', 48, 590000, 425000, 'ACTIVE', 'Blue');

-- =====================================================
-- CUSTOMERS (150 customers)
-- =====================================================

INSERT INTO customers (first_name, last_name, gender, date_of_birth, address, email, phone) VALUES
('Nguyễn', 'Văn An', 'M', '1990-01-15', '123 Láng Hạ, Ba Đình, Hà Nội', 'nguyenvanan@email.com', '0912000001'),
('Trần', 'Thị Bình', 'F', '1985-03-20', '456 Điện Biên Phủ, Q1, TP.HCM', 'tranthbinh@email.com', '0912000002'),
('Lê', 'Văn Cường', 'M', '1992-05-10', '789 Hùng Vương, Hải Châu, Đà Nẵng', 'levancuong@email.com', '0912000003'),
('Phạm', 'Thị Dung', 'F', '1988-07-22', '321 Nguyễn Trãi, Thanh Xuân, Hà Nội', 'phamthidung@email.com', '0912000004'),
('Hoàng', 'Văn Em', 'M', '1995-09-15', '654 Cách Mạng T8, Q3, TP.HCM', 'hoangvanem@email.com', '0912000005'),
('Vũ', 'Thị Phương', 'F', '1987-11-08', '987 Lê Duẩn, Hải Châu, Đà Nẵng', 'vuthiphuong@email.com', '0912000006'),
('Đỗ', 'Văn Giang', 'M', '1993-02-28', '147 Kim Mã, Ba Đình, Hà Nội', 'dovangiang@email.com', '0912000007'),
('Bùi', 'Thị Hà', 'F', '1991-04-12', '258 Đồng Khởi, Q1, TP.HCM', 'buithiha@email.com', '0912000008'),
('Đặng', 'Văn Inh', 'M', '1989-06-30', '369 Phan Châu Trinh, Hải Châu, Đà Nẵng', 'dangvaninh@email.com', '0912000009'),
('Đinh', 'Thị Kim', 'F', '1994-08-18', '741 Giải Phóng, Đống Đa, Hà Nội', 'dinhthikim@email.com', '0912000010');

-- Generate 140 more customers with diverse data
INSERT INTO customers (first_name, last_name, gender, date_of_birth, address, email, phone) VALUES
('Dương', 'Văn Long', 'M', '1986-10-25', '852 Lê Lợi, Q1, TP.HCM', 'duongvanlong@email.com', '0912000011'),
('Hồ', 'Thị Minh', 'F', '1996-12-05', '963 Trần Phú, Hải Châu, Đà Nẵng', 'hothiminh@email.com', '0912000012'),
('Lý', 'Văn Nghĩa', 'M', '1990-03-17', '159 Tây Sơn, Đống Đa, Hà Nội', 'lyvannghia@email.com', '0912000013'),
('Mai', 'Thị Oanh', 'F', '1988-05-29', '357 Nguyễn Huệ, Q1, TP.HCM', 'maithioanh@email.com', '0912000014'),
('Ngô', 'Văn Phú', 'M', '1992-07-14', '486 Bạch Đằng, Hải Châu, Đà Nẵng', 'ngovanphu@email.com', '0912000015'),
('Phan', 'Thị Quỳnh', 'F', '1987-09-22', '573 Hoàng Diệu, Hai Bà Trưng, Hà Nội', 'phanthiquynh@email.com', '0912000016'),
('Tô', 'Văn Sang', 'M', '1995-11-03', '684 Võ Văn Tần, Q3, TP.HCM', 'tovansang@email.com', '0912000017'),
('Võ', 'Thị Tâm', 'F', '1991-01-26', '795 Lý Thường Kiệt, Hải Châu, Đà Nẵng', 'vothitam@email.com', '0912000018'),
('Châu', 'Văn Uy', 'M', '1989-04-08', '816 Nguyễn Thái Học, Ba Đình, Hà Nội', 'chauvanuy@email.com', '0912000019'),
('Kiều', 'Thị Vân', 'F', '1993-06-19', '927 Phan Đình Phùng, Q3, TP.HCM', 'kieuthivan@email.com', '0912000020'),
('Lưu', 'Văn Xuân', 'M', '1986-08-31', '138 Nguyễn Công Trứ, Hải Châu, Đà Nẵng', 'luuvanxuan@email.com', '0912000021'),
('Mạc', 'Thị Yến', 'F', '1994-10-13', '249 Phạm Ngọc Thạch, Đống Đa, Hà Nội', 'macithiyen@email.com', '0912000022'),
('Ninh', 'Văn An', 'M', '1988-12-24', '350 Hai Bà Trưng, Q1, TP.HCM', 'ninhvanan@email.com', '0912000023'),
('Ông', 'Thị Bích', 'F', '1992-02-07', '461 Lê Duẩn, Hải Châu, Đà Nẵng', 'ongthibich@email.com', '0912000024'),
('Phùng', 'Văn Cường', 'M', '1990-04-20', '572 Trần Hưng Đạo, Hoàn Kiếm, Hà Nội', 'phungvancuong@email.com', '0912000025'),
('Quách', 'Thị Duyên', 'F', '1987-06-11', '683 Đặng Văn Ngữ, Q10, TP.HCM', 'quachthiduyen@email.com', '0912000026'),
('Sử', 'Văn Em', 'M', '1995-08-23', '794 Hoàng Diệu, Hải Châu, Đà Nẵng', 'suvanem@email.com', '0912000027'),
('Tạ', 'Thị Giang', 'F', '1991-10-04', '815 Láng, Đống Đa, Hà Nội', 'tathigiang@email.com', '0912000028'),
('Ứng', 'Văn Hải', 'M', '1989-12-16', '926 Pasteur, Q1, TP.HCM', 'ungvanhai@email.com', '0912000029'),
('Văn', 'Thị Lan', 'F', '1993-02-27', '137 Ngô Quyền, Hải Châu, Đà Nẵng', 'vanthilan@email.com', '0912000030'),
('Xa', 'Văn Minh', 'M', '1985-05-15', '248 Xã Đàn, Đống Đa, Hà Nội', 'xavanminh@email.com', '0912000031'),
('Yên', 'Thị Nga', 'F', '1990-07-20', '359 Trần Hưng Đạo, Q5, TP.HCM', 'yenthinga@email.com', '0912000032'),
('Âu', 'Văn Phong', 'M', '1992-09-25', '460 Điện Biên Phủ, Hải Châu, Đà Nẵng', 'auvanphong@email.com', '0912000033'),
('Bành', 'Thị Quỳnh', 'F', '1988-11-30', '571 Nguyễn Chí Thanh, Đống Đa, Hà Nội', 'banhthiquynh@email.com', '0912000034'),
('Cái', 'Văn Sơn', 'M', '1986-01-05', '682 Lê Văn Sỹ, Q3, TP.HCM', 'caivanson@email.com', '0912000035'),
('Đái', 'Thị Tâm', 'F', '1994-03-10', '793 Nguyễn Văn Linh, Hải Châu, Đà Nẵng', 'daithitam@email.com', '0912000036'),
('Gia', 'Văn Tuấn', 'M', '1991-05-15', '814 Thái Hà, Đống Đa, Hà Nội', 'giavantuan@email.com', '0912000037'),
('Hàn', 'Thị Uyên', 'F', '1989-07-20', '925 Đinh Tiên Hoàng, Q1, TP.HCM', 'hanthiuyen@email.com', '0912000038'),
('Khổng', 'Văn Vinh', 'M', '1987-09-25', '136 Trưng Nữ Vương, Hải Châu, Đà Nẵng', 'khongvanvinh@email.com', '0912000039'),
('Lục', 'Thị Xuân', 'F', '1995-11-30', '247 Giảng Võ, Ba Đình, Hà Nội', 'lucthixuan@email.com', '0912000040');

-- Continue with 110 more customers (total 150)
-- Adding customers 41-150 with varied demographics
INSERT INTO customers (first_name, last_name, gender, date_of_birth, address, phone) VALUES
('Mã', 'Văn Anh', 'M', '1990-01-01', '100 Trần Đại Nghĩa, Hai Bà Trưng, Hà Nội', '0912000041'),
('Nhữ', 'Thị Bảo', 'F', '1991-02-02', '101 Nguyễn Thị Minh Khai, Q1, TP.HCM', '0912000042'),
('Ổ', 'Văn Cảnh', 'M', '1992-03-03', '102 Lê Lợi, Hải Châu, Đà Nẵng', '0912000043'),
('Phó', 'Thị Diễm', 'F', '1993-04-04', '103 Hoàng Hoa Thám, Tây Hồ, Hà Nội', '0912000044'),
('Quang', 'Văn Đức', 'M', '1994-05-05', '104 Bùi Viện, Q1, TP.HCM', '0912000045'),
('Rạng', 'Thị Hằng', 'F', '1995-06-06', '105 Lê Hồng Phong, Hải Châu, Đà Nẵng', '0912000046'),
('Sơn', 'Văn Khánh', 'M', '1996-07-07', '106 Đê La Thành, Đống Đa, Hà Nội', '0912000047'),
('Tào', 'Thị Linh', 'F', '1985-08-08', '107 Lý Tự Trọng, Q1, TP.HCM', '0912000048'),
('Ung', 'Văn Nam', 'M', '1986-09-09', '108 Nguyễn Chí Thanh, Hải Châu, Đà Nẵng', '0912000049'),
('Vi', 'Thị Oanh', 'F', '1987-10-10', '109 Cát Linh, Đống Đa, Hà Nội', '0912000050');

-- 100 more customers (51-150) with realistic data
INSERT INTO customers (first_name, last_name, gender, date_of_birth, phone) 
SELECT 
    CASE WHEN MOD(n, 5) = 0 THEN 'Nguyễn'
         WHEN MOD(n, 5) = 1 THEN 'Trần'
         WHEN MOD(n, 5) = 2 THEN 'Lê'
         WHEN MOD(n, 5) = 3 THEN 'Phạm'
         ELSE 'Hoàng' END AS first_name,
    CASE WHEN MOD(n, 3) = 0 THEN CONCAT('Khách ', n)
         WHEN MOD(n, 3) = 1 THEN CONCAT('Hàng ', n)
         ELSE CONCAT('VIP ', n) END AS last_name,
    CASE WHEN MOD(n, 2) = 0 THEN 'M' ELSE 'F' END AS gender,
    DATE_ADD('1980-01-01', INTERVAL MOD(n * 137, 15000) DAY) AS date_of_birth,
    CONCAT('09120', LPAD(n, 5, '0')) AS phone
FROM (
    SELECT (@row_number:=@row_number + 1) + 50 AS n
    FROM products, (SELECT @row_number:=0) AS t
    LIMIT 100
) nums;

-- =====================================================
-- CUSTOMER LOYALTY (All 150 customers)
-- =====================================================

INSERT INTO customer_loyalty (customer_id, loyalty_id, loyalty_points, loyalty_points_expired_date)
SELECT 
    customer_id,
    CASE 
        WHEN customer_id <= 10 THEN 5  -- Diamond
        WHEN customer_id <= 25 THEN 4  -- Platinum
        WHEN customer_id <= 50 THEN 3  -- Gold
        WHEN customer_id <= 100 THEN 2  -- Silver
        ELSE 1  -- Bronze
    END AS loyalty_id,
    CASE 
        WHEN customer_id <= 10 THEN FLOOR(100000 + RAND() * 50000)
        WHEN customer_id <= 25 THEN FLOOR(50000 + RAND() * 30000)
        WHEN customer_id <= 50 THEN FLOOR(15000 + RAND() * 20000)
        WHEN customer_id <= 100 THEN FLOOR(5000 + RAND() * 10000)
        ELSE FLOOR(RAND() * 5000)
    END AS loyalty_points,
    DATE_ADD(CURDATE(), INTERVAL 365 DAY) AS loyalty_points_expired_date
FROM customers;

-- =====================================================
-- INVENTORY (Stock all products in all locations)
-- =====================================================

-- Warehouse North (Location 24) - High stock
INSERT INTO inventory (product_id, location_id, quantity)
SELECT 
    product_id,
    24 AS location_id,
    FLOOR(500 + RAND() * 1500) AS quantity
FROM products;

-- Warehouse South (Location 25) - High stock
INSERT INTO inventory (product_id, location_id, quantity)
SELECT 
    product_id,
    25 AS location_id,
    FLOOR(600 + RAND() * 1400) AS quantity
FROM products;

-- Physical Stores (Locations 1-18) - Medium stock
INSERT INTO inventory (product_id, location_id, quantity)
SELECT 
    p.product_id,
    l.location_id,
    FLOOR(20 + RAND() * 80) AS quantity
FROM products p
CROSS JOIN (SELECT location_id FROM locations WHERE location_type = 'STORE' AND location_id <= 18) l
WHERE RAND() < 0.6;  -- Only 60% of products in each store

-- =====================================================
-- DELIVERY VENDORS & VEHICLES
-- =====================================================

INSERT INTO delivery_vendors (vendor_name, vendor_type) VALUES
('VinRetail Logistics', 'INTERNAL'),
('Giao Hàng Nhanh', 'THIRD_PARTY'),
('Viettel Post', 'THIRD_PARTY'),
('VNPOST', 'THIRD_PARTY'),
('J&T Express', 'THIRD_PARTY'),
('Grab Express', 'THIRD_PARTY'),
('Be Delivery', 'THIRD_PARTY'),
('Ninja Van', 'THIRD_PARTY'),
('AhaMove', 'THIRD_PARTY'),
('Shopee Express', 'DROPSHIPPING'),
('Lazada Express', 'DROPSHIPPING'),
('Tiki Now', 'DROPSHIPPING');

INSERT INTO delivery_vehicles (plate_number, capacity) VALUES
('29A-123.45', 500), ('29B-234.56', 800), ('29C-345.67', 1000),
('30A-456.78', 600), ('30B-567.89', 700), ('30C-678.90', 900),
('51A-789.01', 1200), ('51B-890.12', 500), ('51C-901.23', 800),
('79A-012.34', 600), ('79B-123.45', 1000), ('79C-234.56', 700),
('92A-345.67', 900), ('92B-456.78', 800), ('92C-567.89', 1100);

-- =====================================================
-- PROMOTIONS
-- =====================================================

INSERT INTO promotions_campaigns (department_id, campaign_name, campaign_description, start_date, end_date) VALUES
(1, 'Summer Sale 2024', 'Ưu đãi hè sôi động', '2024-06-01', '2024-08-31'),
(1, 'Back to School 2024', 'Ưu đãi tựu trường', '2024-08-15', '2024-09-30'),
(1, 'Black Friday 2024', 'Siêu sale Black Friday', '2024-11-25', '2024-11-30'),
(1, 'Year End Sale 2024', 'Đại tiệc cuối năm', '2024-12-01', '2024-12-31'),
(1, 'Tết 2025', 'Khuyến mãi Tết Nguyên Đán', '2025-01-15', '2025-02-28'),
(1, '8/3 Women Day', 'Ưu đãi Quốc tế Phụ nữ', '2025-03-01', '2025-03-10'),
(1, '30/4 Liberation Day', 'Sale lễ 30/4', '2025-04-25', '2025-05-05'),
(1, 'Mid Year Sale 2025', 'Đại hạ giá giữa năm', '2025-06-01', '2025-06-30');

INSERT INTO promotions (promotion_code, rule_type, discount_percent, status, campaign_id) VALUES
('SUMMER10', 'PERCENT', 10.00, 'EXPIRED', 1),
('SUMMER15', 'PERCENT', 15.00, 'EXPIRED', 1),
('SUMMER20', 'PERCENT', 20.00, 'EXPIRED', 1),
('SCHOOL5', 'PERCENT', 5.00, 'EXPIRED', 2),
('SCHOOL10', 'PERCENT', 10.00, 'EXPIRED', 2),
('BLACKFRIDAY25', 'PERCENT', 25.00, 'EXPIRED', 3),
('BLACKFRIDAY30', 'PERCENT', 30.00, 'EXPIRED', 3),
('BLACKFRIDAY50', 'PERCENT', 50.00, 'EXPIRED', 3),
('YEAREND20', 'PERCENT', 20.00, 'EXPIRED', 4),
('TET2025', 'PERCENT', 15.00, 'ACTIVE', 5),
('WOMEN10', 'PERCENT', 10.00, 'ACTIVE', 6),
('LIBERATION15', 'PERCENT', 15.00, 'ACTIVE', 7),
('MIDYEAR20', 'PERCENT', 20.00, 'ACTIVE', 8);

INSERT INTO promotions (promotion_code, rule_type, discount_value, status, campaign_id) VALUES
('FIXED50K', 'FIXED', 50000.00, 'ACTIVE', 5),
('FIXED100K', 'FIXED', 100000.00, 'ACTIVE', 5),
('FIXED200K', 'FIXED', 200000.00, 'ACTIVE', 5),
('FIXED500K', 'FIXED', 500000.00, 'ACTIVE', 5),
('FIXED1M', 'FIXED', 1000000.00, 'ACTIVE', 5);

SELECT 'Sample data inserted successfully!' AS status;
SELECT CONCAT('Total products: ', COUNT(*)) AS info FROM products;
SELECT CONCAT('Total customers: ', COUNT(*)) AS info FROM customers;
SELECT CONCAT('Total employees: ', COUNT(*)) AS info FROM employees;
SELECT CONCAT('Total locations: ', COUNT(*)) AS info FROM locations;
SELECT CONCAT('Total inventory records: ', COUNT(*)) AS info FROM inventory;


-- =====================================================
-- CUSTOMER PREFERENCES
-- =====================================================

INSERT INTO customer_preferences (customer_id, class_id)
SELECT
    c.customer_id,
    pc.class_id
FROM customers c
JOIN (
    SELECT class_id
    FROM product_class
    ORDER BY RAND()
    LIMIT 3
) pc
WHERE c.customer_id <= 150
AND RAND() < 0.6;
-- =====================================================
-- EMPLOYEE BONUS RULES
-- =====================================================

-- Percentage bonus by sales volume
INSERT INTO employee_bonus_rules (
    bonus_type,
    min_sales,
    bonus_percentage,
    start_date,
    end_date,
    class_id,
    fixed_bonus_class
)
SELECT
    'PERCENT',
    v.min_sales,
    v.bonus_percentage,
    '2024-01-01',
    '2025-12-31',
    pc.class_id,
    NULL
FROM (
    SELECT 50000000 AS min_sales, 2.0 AS bonus_percentage
    UNION ALL
    SELECT 100000000, 3.5
    UNION ALL
    SELECT 200000000, 5.0
) v
JOIN product_class pc
WHERE pc.product_group IN ('electronics', 'fashion_accessories', 'footwear');

-- Fixed bonus for high-margin classes
INSERT INTO employee_bonus_rules (
    bonus_type,
    min_sales,
    bonus_percentage,
    start_date,
    end_date,
    class_id,
    fixed_bonus_class
)
SELECT
    'FIXED',
    30000000,
    NULL,
    '2024-01-01',
    '2025-12-31',
    pc.class_id,
    500000
FROM product_class pc
WHERE pc.product_group IN ('beauty_personal_care', 'clothing');

-- =====================================================
-- DELIVERY BONUS RULES
-- =====================================================

-- Bonus by number of deliveries
INSERT INTO delivery_bonus_rules (
    rule_type,
    min_deliveries,
    bonus_amount,
    delivery_type,
    class_id,
    start_date,
    end_date
)
VALUES
('BY_COUNT', 50, 300000, NULL, NULL, '2024-01-01', '2025-12-31'),
('BY_COUNT', 100, 700000, NULL, NULL, '2024-01-01', '2025-12-31'),
('BY_COUNT', 200, 1500000, NULL, NULL, '2024-01-01', '2025-12-31');

-- Bonus by delivery type
INSERT INTO delivery_bonus_rules (
    rule_type,
    min_deliveries,
    bonus_amount,
    delivery_type,
    class_id,
    start_date,
    end_date
)
VALUES
('BY_DELIVERY_TYPE', NULL, 20000, 'FULFILLMENT', NULL, '2024-01-01', '2025-12-31'),
('BY_DELIVERY_TYPE', NULL, 30000, 'TRANSFER', NULL, '2024-01-01', '2025-12-31'),
('BY_DELIVERY_TYPE', NULL, 15000, 'RETURN', NULL, '2024-01-01', '2025-12-31');

-- Bonus for high-value product classes
INSERT INTO delivery_bonus_rules (
    rule_type,
    min_deliveries,
    bonus_amount,
    delivery_type,
    class_id,
    start_date,
    end_date
)
SELECT
    'BY_CLASS',
    NULL,
    50000,
    'FULFILLMENT',
    pc.class_id,
    '2024-01-01',
    '2025-12-31'
FROM product_class pc
WHERE pc.product_group IN ('electronics', 'fashion_accessories');

-- Re-enable foreign key checks
SET FOREIGN_KEY_CHECKS = 1;

SELECT '========================================' AS '';
SELECT 'Master data loaded successfully!' AS status;
SELECT '========================================' AS '';