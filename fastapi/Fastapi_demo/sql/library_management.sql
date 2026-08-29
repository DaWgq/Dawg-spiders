-- ============================================================
-- 图书管理系统 数据库初始化脚本
-- 适用数据库: MySQL 5.7+ / 8.0
-- 使用方式: 在 Navicat 中新建查询后直接执行整个脚本
-- 默认管理员账号: admin / admin123
-- ============================================================

CREATE DATABASE IF NOT EXISTS library_db DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE library_db;

SET FOREIGN_KEY_CHECKS = 0;

-- ------------------------------------------------------------
-- 1. 用户表 (系统登录账号)
-- ------------------------------------------------------------
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id            INT AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID',
    username      VARCHAR(50)  NOT NULL UNIQUE COMMENT '登录用户名',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希(bcrypt)',
    real_name     VARCHAR(50)  DEFAULT '' COMMENT '真实姓名',
    role          VARCHAR(20)  NOT NULL DEFAULT 'admin' COMMENT '角色',
    created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT = '系统用户表';

-- ------------------------------------------------------------
-- 2. 图书分类表
-- ------------------------------------------------------------
DROP TABLE IF EXISTS categories;
CREATE TABLE categories (
    id   INT AUTO_INCREMENT PRIMARY KEY COMMENT '分类ID',
    name VARCHAR(50) NOT NULL UNIQUE COMMENT '分类名称'
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT = '图书分类表';

-- ------------------------------------------------------------
-- 3. 图书表
-- ------------------------------------------------------------
DROP TABLE IF EXISTS books;
CREATE TABLE books (
    id               INT AUTO_INCREMENT PRIMARY KEY COMMENT '图书ID',
    isbn             VARCHAR(20)  NOT NULL UNIQUE COMMENT 'ISBN',
    title            VARCHAR(200) NOT NULL COMMENT '书名',
    author           VARCHAR(100) NOT NULL COMMENT '作者',
    publisher        VARCHAR(100) DEFAULT '' COMMENT '出版社',
    category_id      INT          DEFAULT NULL COMMENT '分类ID',
    location         VARCHAR(50)  DEFAULT '' COMMENT '馆藏位置(排架号)',
    total_copies     INT          NOT NULL DEFAULT 1 COMMENT '总馆藏数量',
    available_copies INT          NOT NULL DEFAULT 1 COMMENT '在馆可借数量',
    created_at       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    CONSTRAINT fk_books_category FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE SET NULL
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT = '图书表';

-- ------------------------------------------------------------
-- 4. 读者表
-- ------------------------------------------------------------
DROP TABLE IF EXISTS readers;
CREATE TABLE readers (
    id         INT AUTO_INCREMENT PRIMARY KEY COMMENT '读者ID',
    reader_no  VARCHAR(20) NOT NULL UNIQUE COMMENT '读者编号',
    name       VARCHAR(50) NOT NULL COMMENT '姓名',
    gender     VARCHAR(10) NOT NULL DEFAULT '其他' COMMENT '性别(男/女/其他)',
    phone      VARCHAR(20) DEFAULT '' COMMENT '手机号',
    email      VARCHAR(100) DEFAULT '' COMMENT '邮箱',
    status     VARCHAR(10) NOT NULL DEFAULT '正常' COMMENT '状态(正常/冻结)',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT = '读者表';

-- ------------------------------------------------------------
-- 5. 借阅记录表
-- ------------------------------------------------------------
DROP TABLE IF EXISTS borrow_records;
CREATE TABLE borrow_records (
    id          INT AUTO_INCREMENT PRIMARY KEY COMMENT '记录ID',
    reader_id   INT      NOT NULL COMMENT '读者ID',
    book_id     INT      NOT NULL COMMENT '图书ID',
    borrow_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '借出时间',
    due_date    DATETIME NOT NULL COMMENT '应还日期',
    return_date DATETIME DEFAULT NULL COMMENT '归还时间',
    status      VARCHAR(20) NOT NULL DEFAULT '借出中' COMMENT '状态(借出中/已归还/逾期)',
    CONSTRAINT fk_borrow_reader FOREIGN KEY (reader_id) REFERENCES readers (id),
    CONSTRAINT fk_borrow_book   FOREIGN KEY (book_id)   REFERENCES books (id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT = '借阅记录表';

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================
-- 初始化数据 (Seed Data)
-- ============================================================

-- 默认管理员: admin / admin123
INSERT INTO users (username, password_hash, real_name, role) VALUES
('admin', '$2b$12$w20RwwrR/I6ZLIZDuOMtcOblUscXrso/wJgH.rZ2QMNozx6MFHmRO', '系统管理员', 'admin');

-- 图书分类
INSERT INTO categories (name) VALUES
('计算机/IT'), ('文学小说'), ('历史传记'), ('科学技术'), ('其他');

-- 图书 (available_copies 已与下方借阅记录保持一致)
INSERT INTO books (isbn, title, author, publisher, category_id, location, total_copies, available_copies) VALUES
('9787111544937', '深入理解计算机系统 (原书第3版)', 'Randal E.Bryant', '机械工业出版社', 1, 'A区-01架-01层', 5, 4),
('9787115428028', 'Python编程：从入门到实践', 'Eric Matthes', '人民邮电出版社', 1, 'A区-01架-02层', 10, 9),
('9787536692930', '三体 (全三册)', '刘慈欣', '重庆出版社', 2, 'B区-02架-01层', 8, 8),
('9787508647357', '人类简史：从动物到上帝', '尤瓦尔·赫拉利', '中信出版社', 3, 'C区-01架-03层', 12, 11),
('9787208061644', '追风筝的人', '卡勒德·胡赛尼', '上海人民出版社', 2, 'B区-02架-02层', 6, 6),
('9787544270878', '百年孤独', '加西亚·马尔克斯', '南海出版公司', 2, 'B区-02架-03层', 6, 5),
('9787111213826', '设计模式：可复用面向对象软件的基础', 'GoF', '机械工业出版社', 1, 'A区-01架-04层', 8, 7),
('9787020002207', '红楼梦', '曹雪芹', '人民文学出版社', 2, 'B区-03架-01层', 10, 10),
('9787115175214', '深入浅出设计模式', 'Eric Freeman', '电子工业出版社', 1, 'A区-02架-01层', 5, 5),
('9787302519595', 'Python 3网络爬虫开发实战', '崔庆才', '清华大学出版社', 1, 'A区-02架-02层', 4, 4),
('9787508660752', '未来简史', '尤瓦尔·赫拉利', '中信出版社', 3, 'C区-01架-04层', 8, 8),
('9787302557771', 'MySQL必知必会', 'Ben Forta', '人民邮电出版社', 1, 'A区-02架-03层', 6, 6);

-- 读者
INSERT INTO readers (reader_no, name, gender, phone, email, status) VALUES
('R001', '张三', '男', '13800000001', 'zhangsan@example.com', '正常'),
('R002', '李四', '女', '13800000002', 'lisi@example.com', '正常'),
('R003', '王五', '男', '13800000003', 'wangwu@example.com', '正常'),
('R004', '赵六', '男', '13800000004', 'zhaoliu@example.com', '正常'),
('R005', '孙七', '女', '13800000005', 'sunqi@example.com', '正常');

-- 借阅记录 (使用相对当前时间的日期, 保证"逾期"数据始终存在)
INSERT INTO borrow_records (reader_id, book_id, borrow_date, due_date, return_date, status) VALUES
(1, 3, DATE_SUB(NOW(), INTERVAL 40 DAY), DATE_SUB(NOW(), INTERVAL 10 DAY), DATE_SUB(NOW(), INTERVAL 12 DAY), '已归还'),  -- 张三 还 三体
(2, 1, DATE_SUB(NOW(), INTERVAL 10 DAY), DATE_ADD(NOW(), INTERVAL 20 DAY), NULL, '借出中'),                                -- 李四 借 CSAPP
(1, 4, DATE_SUB(NOW(), INTERVAL 3 DAY),  DATE_ADD(NOW(), INTERVAL 27 DAY), NULL, '借出中'),                                -- 张三 借 人类简史
(3, 2, DATE_SUB(NOW(), INTERVAL 35 DAY), DATE_SUB(NOW(), INTERVAL 5 DAY),  NULL, '借出中'),                                -- 王五 借 Python编程 (逾期)
(4, 6, DATE_SUB(NOW(), INTERVAL 2 DAY),  DATE_ADD(NOW(), INTERVAL 28 DAY), NULL, '借出中'),                                -- 赵六 借 百年孤独
(5, 7, DATE_SUB(NOW(), INTERVAL 8 DAY),  DATE_ADD(NOW(), INTERVAL 22 DAY), NULL, '借出中'),                                -- 孙七 借 设计模式
(2, 9, DATE_SUB(NOW(), INTERVAL 25 DAY), DATE_SUB(NOW(), INTERVAL 5 DAY),  DATE_SUB(NOW(), INTERVAL 3 DAY), '已归还'),     -- 李四 还 深入浅出设计模式
(3, 5, DATE_SUB(NOW(), INTERVAL 15 DAY), DATE_ADD(NOW(), INTERVAL 15 DAY), DATE_SUB(NOW(), INTERVAL 2 DAY), '已归还'),     -- 王五 还 追风筝的人
(5, 8, DATE_SUB(NOW(), INTERVAL 5 DAY),  DATE_ADD(NOW(), INTERVAL 25 DAY), NULL, '借出中');                                -- 孙七 借 红楼梦
