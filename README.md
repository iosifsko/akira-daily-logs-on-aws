# Akira Daily Logs on AWS

A step-by-step guide to host a private WordPress log system using EC2, RDS, and a custom subdomain (`logs.bistrawp.io`).

---

## ✅ Stack Overview

- **EC2** (Amazon Linux 2023) running Apache + PHP + WordPress
- **RDS** (MySQL) for database backend
- **Namecheap DNS** pointing subdomain to EC2 IP
- **S3 + Lambda** integration to auto-publish daily log files to WordPress

---

## 🧱 Setup Steps

### 1. Launch EC2
- Amazon Linux 2023 (t3.micro)
- Open ports 80 (HTTP), 22 (SSH)

### 2. Install WordPress on EC2
```bash
sudo yum update -y
sudo yum install -y httpd php php-mysqlnd wget
sudo systemctl start httpd
sudo systemctl enable httpd

cd /var/www/html
sudo wget https://wordpress.org/latest.tar.gz
sudo tar -xzf latest.tar.gz
sudo cp -r wordpress/* .
sudo chown -R apache:apache /var/www/html

### 3. Create RDS (MySQL)

- Use MySQL 8.x
- Public access: Yes
- Storage: 20 GiB
- DB Identifier: `akira-logs-db`
- Master username: `admin`
- Connect it to the same VPC as your EC2

After creation:
- Go to the RDS security group
- Add inbound rule:
  - Type: MySQL/Aurora
  - Port: 3306
  - Source: EC2 security group (`launch-wizard-4`)

Test connection from EC2:
```bash
mysql -h your-rds-endpoint.amazonaws.com -u admin -p
# Then: CREATE DATABASE wordpress;

