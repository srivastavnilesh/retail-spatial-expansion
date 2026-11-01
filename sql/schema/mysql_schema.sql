CREATE DATABASE IF NOT EXISTS monday_coffee
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
  
  use monday_coffee;
  
  drop table if exists sales_fact;
  drop table if exists customer_dim;
  drop table if exists product_dim;
  drop table if exists city_dim;
  
  -- 1: City Dimensions
  create table city_dim (
	city_id INT auto_increment primary key,
    city_name varchar(100) not null unique,
    population int,
    estimated_rent decimal(10,2),
    city_rank int
) engine=innoDB;

-- 2: Product Dimension
  create table product_dim (
  product_id int auto_increment primary key,
  product_name varchar(100) not null,
  price decimal(10,2)
) engine=innoDB;

-- 3: Customer Dimention
create table customer_dim (
	customer_id int auto_increment primary key,
    customer_name varchar(100) not null,
    city_id int,
    constraint fk_customer_city
		foreign key (city_id) references city_dim(city_id)
) engine=innoDB;

-- 4: Sales Fact Table
create table sales_fact (
	sale_id int auto_increment primary key,
    sale_date date not null,
    product_id int,
    customer_id int,
    total decimal(10,2),
    rating int,
    constraint fk_sales_product
		foreign key (product_id) references product_dim(product_id),
	constraint fk_sales_customer
		foreign key (customer_id) references customer_dim(customer_id),
	constraint chk_rating check (rating between 1 and 5)
) engine = innoDB;

-- Performances Indexes
create index idx_sales_date on sales_fact(sale_date);
create index idx_customer_city on customer_dim(city_id);
