
-- 1. 用户表
CREATE TABLE user_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_name VARCHAR(50) NOT NULL UNIQUE COMMENT '管理员姓名',
    user_code VARCHAR(64) NOT NULL COMMENT '加密后的管理员编号（密码）',
    salt VARCHAR(32) NOT NULL COMMENT '加密盐值',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
);

-- 2. 疫苗基础信息表
CREATE TABLE vaccine_info (
    vaccine_num VARCHAR(50) PRIMARY KEY COMMENT '疫苗批号（唯一）',
    vaccine_name VARCHAR(100) NOT NULL COMMENT '疫苗名称',
    company_name VARCHAR(100) NOT NULL COMMENT '生产企业名称',
    company_num VARCHAR(50) NOT NULL COMMENT '企业编号',
    size VARCHAR(50) NOT NULL COMMENT '规格（如：1ml/支）',
    buy_price DECIMAL(10,2) NOT NULL COMMENT '进价',
    pre_sale_price DECIMAL(10,2) NOT NULL COMMENT '预售价',
    limit_up INT NOT NULL COMMENT '企业上限（最大库存）',
    limit_down INT NOT NULL COMMENT '企业下限（最小库存）',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
);

-- 3. 疫苗分配信息表
CREATE TABLE vaccine_distr_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vaccine_distr_num VARCHAR(50) NOT NULL UNIQUE COMMENT '分配单号',
    date DATE NOT NULL COMMENT '分配日期',
    vaccine_num VARCHAR(50) NOT NULL COMMENT '疫苗批号',
    vaccine_name VARCHAR(100) NOT NULL COMMENT '疫苗名称',
    company_num VARCHAR(50) NOT NULL COMMENT '接收企业编号',
    operator_num VARCHAR(50) NOT NULL COMMENT '质检员编号',
    num INT NOT NULL COMMENT '分配数量',
    FOREIGN KEY (vaccine_num) REFERENCES vaccine_info(vaccine_num)
);

-- 4. 疫苗养护信息表
CREATE TABLE vaccine_maintain_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    maintain_num VARCHAR(50) NOT NULL UNIQUE COMMENT '养护记录编号',
    vaccine_num VARCHAR(50) NOT NULL COMMENT '疫苗批号',
    maintain_date DATE NOT NULL COMMENT '养护日期',
    staff_num VARCHAR(50) NOT NULL COMMENT '养护人员编号',
    storage_temp DECIMAL(5,2) NOT NULL COMMENT '存储温度（℃）',
    storage_humidity DECIMAL(5,2) NOT NULL COMMENT '存储湿度（%）',
    status VARCHAR(20) NOT NULL COMMENT '养护状态（正常/异常）',
    remark TEXT COMMENT '备注',
    FOREIGN KEY (vaccine_num) REFERENCES vaccine_info(vaccine_num)
);

-- 5. 接种人员信息表
CREATE TABLE vaccination_person (
    person_id VARCHAR(50) PRIMARY KEY COMMENT '人员编号',
    name VARCHAR(50) NOT NULL COMMENT '姓名',
    gender VARCHAR(10) NOT NULL COMMENT '性别',
    age INT NOT NULL COMMENT '年龄',
    id_card VARCHAR(18) NOT NULL UNIQUE COMMENT '身份证号',
    phone VARCHAR(11) NOT NULL COMMENT '联系电话',
    vaccine_num VARCHAR(50) NOT NULL COMMENT '接种疫苗批号',
    vaccine_date DATE NOT NULL COMMENT '接种日期',
    FOREIGN KEY (vaccine_num) REFERENCES vaccine_info(vaccine_num)
);

