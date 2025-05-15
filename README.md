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

### 4. Configure WordPress to Use RDS

1. SSH into your EC2 instance.

2. Copy the sample config file:

```bash
    cd /var/www/html
    sudo cp wp-config-sample.php wp-config.php

3. Edit wp-config.php

    sudo nano wp-config.php

4. Replace the database settings with your RDS info

    define( 'DB_NAME', 'wordpress' );
    define( 'DB_USER', 'admin' );
    define( 'DB_PASSWORD', 'YourPasswordHere' );
    define( 'DB_HOST', 'yourRDSendpoint.rds.amazonaws.com' );

5. Save and exit (CTRL+O -> ENTER -> CTRL+X).

6. In your EC2 terminal, connect to RDS:

    mysql -h yourRDSendpoint.rds.amazonaws.com -u admin -p

7. Inside the MySQL prompt:

    CREATE DATABASE wordpress;
    EXIT;

8. Visit your EC2 public IP in a browser to complete WordPress setup.

### 5. Set Up Subdomain (logs.bistrawp.io)

1. Log into your **Namecheap account**
2. Go to **Domain List → bistrawp.io → Advanced DNS**
3. Add an A record:
   - **Type**: A
   - **Host**: `logs`
   - **Value**: `52.13.114.237`  ← (replace with your EC2 Elastic IP)
   - **TTL**: Automatic

---

### Apache Virtual Host Setup on EC2

1. SSH into your EC2 instance

2. Create a new Apache vhost config:
```bash
sudo nano /etc/httpd/conf.d/logs.bistrawp.io.conf

3. <VirtualHost *:80>
    ServerName logs.bistrawp.io
    DocumentRoot /var/www/html

    <Directory /var/www/html>
        AllowOverride All
        Require all granted
    </Directory>
</VirtualHost>

4. Restart Apache:

sudo systemctl restart httpd

5. After DNS propagates, visiting your subdomain (e.g. `http://logs.yoursite.com`) should load your WordPress site, as long as your A record points to your EC2 IP and your Apache config matches the domain.

### 6. Create an S3 Bucket for Log Files

1. Go to **S3 → Create Bucket**
   - Bucket name: `akira-daily-logs` (or anything you prefer)
   - Region: Same as EC2 (e.g., us-west-2)
   - Uncheck **Block all public access** (optional, if Lambda only needs access)

2. Inside the bucket, upload a sample log file:
   - `2024-05-14.txt`
   - Content: Your daily summary or blog post text

This bucket will be read by Lambda to publish logs automatically.

### 7. Create a Lambda Function to Auto-Post Logs

This Lambda will:
- Read a `.txt` file from S3 (e.g. `2024-05-14.txt`)
- Format it as a WordPress blog post
- Post to your site via the WordPress REST API

You must:
- Upload daily logs to S3
- Generate a WordPress Application Password
- Provide your WP username, app password, and site URL as environment variables

#### Sample Lambda code coming next


