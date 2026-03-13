# cPanel Installation Guide for Church LMS

**For: Pastors, Church Administrators, and Non-Technical Users**

This guide will walk you through installing the Community LMS on your church's web hosting account. We assume you have never used cPanel before. Every step includes detailed explanations and descriptions of what you will see on screen.

---

## Table of Contents

1. [Getting Started](#1-getting-started)
2. [Creating a Database](#2-creating-a-database)
3. [Uploading Files](#3-uploading-files)
4. [Setting Up the Node.js Application](#4-setting-up-the-nodejs-application)
5. [Domain and Subdomain Setup](#5-domain-and-subdomain-setup)
6. [SSL Certificate Setup](#6-ssl-certificate-setup)
7. [Troubleshooting Common Issues](#7-troubleshooting-common-issues)
8. [Budget Hosting Recommendations](#8-budget-hosting-recommendations)

---

## 1. Getting Started

### What is cPanel?

**cPanel** is a control panel that helps you manage your website hosting. Think of it like the "settings app" for your website. Instead of typing complicated commands, you can click buttons and fill in forms to:

- Create databases (where your LMS stores information)
- Upload files (your LMS application)
- Set up website addresses
- Install security certificates

**You do NOT need programming knowledge to use cPanel.** This guide will tell you exactly what to click.

---

### How to Access cPanel

Your web hosting company (like GoDaddy, Bluehost, HostGator, or Namecheap) gives you access to cPanel. Here is how to find it:

#### GoDaddy

1. Go to [godaddy.com](https://www.godaddy.com) and click **Sign In** (top right corner)
2. Enter your GoDaddy username and password
3. Click **My Products** in the menu
4. Find your hosting plan and click **Manage**
5. Scroll down and click **cPanel Admin** button

**What you will see:** A page with the GoDaddy logo at the top, then a large button that says "cPanel Admin" or "Launch cPanel"

#### Bluehost

1. Go to [bluehost.com](https://www.bluehost.com) and click **Login** (top right)
2. Enter your Bluehost username and password
3. From your dashboard, click **Advanced** in the left sidebar
4. This takes you directly to cPanel

**What you will see:** After clicking "Advanced," the cPanel interface loads with a blue Bluehost header at the top

#### HostGator

1. Go to [hostgator.com](https://www.hostgator.com) and click **Portal Login**
2. Enter your HostGator email and password
3. Click on your hosting package name
4. Click the **cPanel** button (looks like an orange and white icon)

**What you will see:** A button with the cPanel logo (two overlapping circles forming a C and P shape)

#### Namecheap

1. Go to [namecheap.com](https://www.namecheap.com) and click **Sign In**
2. Enter your Namecheap username and password
3. Click **Hosting List** in the left menu
4. Find your hosting package and click **Go to cPanel**

**What you will see:** A green button labeled "Go to cPanel" next to your hosting package

---

### Quick Tour of the cPanel Interface

When cPanel opens, you will see a page divided into sections. Here is what each section contains:

**What you will see:** A page with a search bar at the top, then multiple boxes/sections below with icons and labels. The page has a light background (usually white or gray) with colorful icons.

The main sections you will use are:

| Section Name | Icon | What It Does |
|--------------|------|--------------|
| **Databases** | Cylinder/barrel shape | Create and manage databases |
| **Files** | Folder icon | Upload and manage website files |
| **Domains** | Globe icon | Manage website addresses |
| **Software** | Gear or wrench icon | Install applications like Node.js |
| **Security** | Lock or shield icon | Install SSL certificates |

**Tip:** There is a **search bar** at the top of cPanel. You can type what you are looking for (like "MySQL" or "File Manager") and it will show you the matching tools.

---

## 2. Creating a Database

A **database** is where your LMS stores all its information: user accounts, courses, lessons, progress tracking, and more. Think of it like a digital filing cabinet that the LMS uses automatically.

### Step 2.1: Find MySQL Databases

1. Log into cPanel (see Section 1 for instructions)
2. Look for the **Databases** section on the main page
3. Click on **MySQL Databases** (it has an icon that looks like a cylinder or barrel)

**Alternative:** Type "MySQL" in the search bar at the top and click **MySQL Databases**

**What you will see:** A page titled "MySQL Databases" with sections for creating databases, creating users, and adding users to databases.

---

### Step 2.2: Create a New Database

1. On the MySQL Databases page, look for the section titled **Create New Database**
2. You will see a text box with your username already filled in, followed by an underscore

**What you will see:** A text field that looks like: `yourname_` followed by an empty box where you type

3. In the empty box, type a name for your database. Use a simple name like:
   - `lms`
   - `churchlms`
   - `courses`

**Important naming rules:**
- Use only letters and numbers (no spaces or special characters)
- Keep it short (under 16 characters)
- Make it something you will remember

**Example:** If your hosting username is "gracefc" and you type "lms", your full database name will be: `gracefc_lms`

4. Click the **Create Database** button

**What you will see:** A green success message saying "Added the database [your database name]"

5. Click **Go Back** or scroll down to continue

**Write this down - Database Name:** `________________` (example: gracefc_lms)

---

### Step 2.3: Create a Database User

Now you need to create a "user account" that your LMS will use to access the database. Think of this like creating a key for the filing cabinet.

1. Scroll down to the section titled **MySQL Users - Add New User**
2. You will see two text boxes:
   - **Username:** Type a name like `lmsuser` or `admin`
   - **Password:** Create a strong password

**What you will see:** Two text fields - one for username (with your hosting username prefix) and two for password (password and confirm password)

3. For the password, you have two options:
   - **Option A:** Click the **Password Generator** button to create a secure password automatically
   - **Option B:** Create your own password (must include uppercase, lowercase, numbers, and symbols)

**If using Password Generator:**
   - Click **Password Generator** button
   - A box appears with a randomly generated password
   - Check the box that says "I have copied this password in a secure location"
   - Click **Use Password**

4. Click **Create User** button

**What you will see:** A green success message saying "You have successfully created the MySQL user"

**Write this down - Database Username:** `________________` (example: gracefc_lmsuser)

**Write this down - Database Password:** `________________` (keep this SECRET and SAFE)

---

### Step 2.4: Give the User Access to the Database

Right now, you have a database and a user, but they are not connected. You need to give the user permission to access the database.

1. Scroll down to the section titled **Add User To Database**
2. You will see two dropdown menus:
   - **User:** Click this dropdown and select the user you just created
   - **Database:** Click this dropdown and select the database you just created

**What you will see:** Two dropdown menus side by side, with a button labeled "Add" below them

3. Click the **Add** button

4. A new page appears titled **Manage User Privileges**

**What you will see:** A page with many checkboxes listing different permissions (SELECT, INSERT, UPDATE, DELETE, etc.)

5. Check the box at the very top that says **ALL PRIVILEGES**
   - This automatically checks all the other boxes

6. Click the **Make Changes** button at the bottom

**What you will see:** A green success message saying "You have given the user all privileges on the database"

**Congratulations!** Your database is ready. You now have:
- **Database Name:** (what you wrote down in Step 2.2)
- **Database Username:** (what you wrote down in Step 2.3)
- **Database Password:** (what you wrote down in Step 2.3)
- **Database Host:** Usually `localhost` (your hosting company may tell you differently)

---

### PostgreSQL Alternative (If Your Host Supports It)

Some hosting companies offer PostgreSQL instead of (or in addition to) MySQL. PostgreSQL is a more powerful database that this LMS works well with.

**To check if your host supports PostgreSQL:**
1. In cPanel, look for "PostgreSQL Databases" in the Databases section
2. If you see it, your host supports PostgreSQL

**If you see PostgreSQL Databases:**

Follow the same steps as MySQL above, but click **PostgreSQL Databases** instead:

1. Click **PostgreSQL Databases** in the Databases section
2. Create a new database (same naming rules as MySQL)
3. Create a new user with a strong password
4. Add the user to the database with all privileges

**The process is nearly identical to MySQL.** Write down your database name, username, and password the same way.

---

## 3. Uploading Files

Now you need to upload the LMS application files to your hosting. There are two ways to do this.

### Option A: Using cPanel File Manager (Easier)

This method uses your web browser - no extra software needed.

#### Step 3.1: Open File Manager

1. In cPanel, find the **Files** section
2. Click on **File Manager** (icon looks like a folder)

**What you will see:** A file browser that looks similar to Windows Explorer or Mac Finder. You will see folders listed on the left side and file contents in the main area.

#### Step 3.2: Navigate to public_html

1. In the folder list on the left side, click on **public_html**

**What you will see:** The contents of the public_html folder. This might show existing files like "index.html" or "cgi-bin" folder.

**What is public_html?** This is the "root" folder of your website. Files placed here are accessible from your website address.

#### Step 3.3: Create a Folder for the LMS (Optional but Recommended)

If you want the LMS on a subdomain (like lms.yourchurch.org), create a folder:

1. Click the **+ Folder** button in the top toolbar
2. Type a folder name: `lms` (or whatever you want to call it)
3. Click **Create New Folder**
4. Double-click the new folder to open it

**What you will see:** A popup asking for the folder name, then the new empty folder

#### Step 3.4: Upload the LMS ZIP File

1. Click the **Upload** button in the top toolbar

**What you will see:** A new browser tab/window opens with an upload area. It shows a large box that says "Select File" or "Drop files here"

2. Click **Select File** button
3. Navigate to where you saved the LMS ZIP file on your computer
4. Select the ZIP file and click **Open**
5. Wait for the upload to complete (you will see a progress bar)

**What you will see:** A progress bar showing the upload percentage. When complete, it shows "Complete" or a green checkmark.

6. Close the upload window (click the X or click **Go Back to...** link)

#### Step 3.5: Extract (Unzip) the Files

The ZIP file needs to be "extracted" (unzipped) so the individual files are usable.

1. Find the ZIP file you just uploaded in the file list
2. Click on it once to select it (it will be highlighted)
3. Click the **Extract** button in the top toolbar

**What you will see:** A popup asking where to extract the files

4. Leave the default location (current folder)
5. Click **Extract Files** button
6. Wait for extraction to complete

**What you will see:** A progress indicator, then a success message listing the extracted files

7. Click **Close** on the extraction result window

**Your files are now uploaded!** You should see folders like `client`, `server`, and files like `package.json` in the file list.

---

### Option B: Using FTP Client (FileZilla)

FTP (File Transfer Protocol) is a more reliable way to upload large files. This requires installing free software on your computer.

#### Step 3.6: Find Your FTP Credentials in cPanel

1. In cPanel, find the **Files** section
2. Click on **FTP Accounts**

**What you will see:** A page listing FTP accounts. There is usually one account created automatically with your hosting username.

3. Look at the table showing existing FTP accounts
4. Write down or note:
   - **FTP Username:** (usually your cPanel username)
   - **FTP Server/Host:** (shown in the table, something like `ftp.yourchurch.org`)

**What you will see:** A table with columns: FTP Account, Login, Directory, Quota, Manage

**Your FTP password is the same as your cPanel password** (unless you created a separate FTP account).

**Write this down - FTP Host:** `________________` (example: ftp.gracefc.org)

**Write this down - FTP Username:** `________________` (example: gracefc)

**FTP Password:** Same as your cPanel password

#### Step 3.7: Download and Install FileZilla

1. Go to [filezilla-project.org](https://filezilla-project.org)
2. Click **Download FileZilla Client**
3. Download the version for your computer (Windows or Mac)
4. Run the installer and follow the prompts (click Next, Accept, Install)

**What you will see:** The FileZilla website with a large green "Download" button. The installer is a standard Windows/Mac installer.

#### Step 3.8: Connect FileZilla to Your Hosting

1. Open FileZilla
2. At the top, you will see four text boxes:
   - **Host:** Enter your FTP server (from Step 3.6)
   - **Username:** Enter your FTP username
   - **Password:** Enter your cPanel password
   - **Port:** Leave empty or enter `21`

**What you will see:** FileZilla's main window with the connection bar at the top, a message log below it, and two file panels side by side.

3. Click **Quickconnect** button

4. If a popup appears asking about the certificate:
   - Check "Always trust certificate in future sessions"
   - Click **OK**

**What you will see:** The right side panel (Remote site) now shows folders from your hosting, including "public_html"

#### Step 3.9: Upload Files via FileZilla

1. **Left panel (Local site):** Navigate to where the LMS files are on your computer
2. **Right panel (Remote site):** Double-click `public_html` to open it
3. If you want a subfolder for the LMS:
   - Right-click in the right panel
   - Click **Create directory**
   - Name it `lms` and click OK
   - Double-click the new folder to open it

4. **To upload:** Select all the LMS files/folders in the left panel, then drag them to the right panel

**What you will see:** A progress bar at the bottom showing files being transferred. The "Queued files" section shows pending transfers.

5. Wait for all transfers to complete (this may take 5-20 minutes depending on your internet speed)

**What you will see:** "Queued files" shows 0 when complete, and all files appear in the right panel

---

## 4. Setting Up the Node.js Application

**What is Node.js?** Node.js is the software that runs the LMS on your server. It is like the "engine" that powers the application.

**Important:** Not all web hosts support Node.js. Check Section 8 for recommended hosts that do support it.

### Step 4.1: Find the Node.js Setup Tool

1. In cPanel, find the **Software** section
2. Look for **Setup Node.js App** or **Node.js Selector**
3. Click on it

**What you will see:** A page titled "Node.js Selector" or "Setup Node.js App" with a button to create a new application.

**If you do NOT see this option:** Your hosting does not support Node.js. You will need to upgrade your hosting plan or switch hosts (see Section 8).

---

### Step 4.2: Create a New Node.js Application

1. Click the **Create Application** button (or **+ Create Application**)

**What you will see:** A form with several fields to fill out

2. Fill in the form as follows:

| Field | What to Enter | Explanation |
|-------|---------------|-------------|
| **Node.js Version** | Select `18.x` or `20.x` | Choose the highest version starting with 18 or 20 |
| **Application Mode** | Select `Production` | This makes it run efficiently |
| **Application Root** | `/home/yourusername/public_html/lms` | The folder where you uploaded the files |
| **Application URL** | `lms.yourchurch.org` or `/lms` | How people will access it |
| **Application Startup File** | `server/server.js` | The main file that starts the application |

**What you will see:** Dropdown menus for Node.js version and mode, text fields for the paths and startup file

3. **Application Root explained:**
   - If your cPanel username is "gracefc"
   - And you uploaded files to a folder called "lms" inside public_html
   - Your Application Root would be: `/home/gracefc/public_html/lms`

4. Click **Create** button

**What you will see:** A green success message and your new application appearing in the list

---

### Step 4.3: Configure Environment Variables

Environment variables are settings that tell your LMS how to connect to the database and other services. Think of them as the LMS's "settings."

1. Find your newly created application in the list
2. Click the **pencil/edit icon** or click on the application name

**What you will see:** The application details page with sections for settings and environment variables

3. Scroll down to find **Environment Variables** section
4. Click **Add Variable** for each of the following:

| Variable Name | Variable Value | What It Does |
|---------------|----------------|--------------|
| `NODE_ENV` | `production` | Tells the app to run in production mode |
| `PORT` | `5000` | The port the application uses internally |
| `DATABASE_URL` | `mysql://username:password@localhost/dbname` | Connects to your database |
| `JWT_SECRET` | `your-secret-key-here-make-it-long` | Security key (make this random and long) |

**For DATABASE_URL, replace:**
- `username` with your database username (from Step 2.3)
- `password` with your database password (from Step 2.3)
- `dbname` with your database name (from Step 2.2)

**Example DATABASE_URL:**
```
mysql://gracefc_lmsuser:MyP@ssw0rd123!@localhost/gracefc_lms
```

**For PostgreSQL, use:**
```
postgresql://gracefc_lmsuser:MyP@ssw0rd123!@localhost/gracefc_lms
```

**For JWT_SECRET:** Type any random phrase, like:
```
mychurch-secret-key-2024-make-this-very-long-and-random-abc123xyz
```

**What you will see:** A table of environment variables with Name and Value columns, and an "Add Variable" button

5. After adding all variables, click **Save** or **Update**

---

### Step 4.4: Install Dependencies and Start the Application

The application needs to download its required components (called "dependencies") before it can run.

1. On your application's page in Node.js Selector, look for **Run NPM Install** button
2. Click **Run NPM Install**

**What you will see:** A loading indicator or progress message. This may take 2-5 minutes.

3. Wait for it to complete (you will see a success message)

4. Click **Start App** or **Restart** button

**What you will see:** The application status changes from "Stopped" to "Started" or shows a green indicator

---

### Step 4.5: Verify the Application is Running

1. Look for the status indicator next to your application - it should show "Started" or green
2. Click on the **Application URL** link (or open it in a new browser tab)

**What you will see:** If everything is working, you will see the LMS login page or homepage

If you see an error, proceed to Section 7 (Troubleshooting).

---

### Step 4.6: View Application Logs

If something goes wrong, logs help you figure out what happened.

1. In the Node.js Selector, find your application
2. Look for a **Logs** button or **View Logs** link
3. Click it

**What you will see:** A text display showing messages from your application. Look for lines that say "Error" to identify problems.

---

## 5. Domain and Subdomain Setup

### Understanding Domain Options

You have two choices for your LMS web address:

**Option 1: Main Domain**
- Address: `www.yourchurch.org` or `yourchurch.org`
- Use this if the LMS is your main church website
- Example: `gracefc.org` shows the LMS

**Option 2: Subdomain (Recommended)**
- Address: `lms.yourchurch.org` or `learn.yourchurch.org`
- Use this if you already have a church website
- Example: `lms.gracefc.org` shows the LMS, while `gracefc.org` shows your church website

**We recommend Option 2 (subdomain)** so your existing church website remains unchanged.

---

### Step 5.1: Create a Subdomain

1. In cPanel, find the **Domains** section
2. Click on **Subdomains**

**What you will see:** A page with a form to create subdomains and a list of existing subdomains (if any)

3. Fill in the form:

| Field | What to Enter |
|-------|---------------|
| **Subdomain** | Type `lms` (or `learn` or `courses`) |
| **Domain** | Select your domain from the dropdown |
| **Document Root** | This auto-fills, but change it to match your LMS folder (example: `/public_html/lms`) |

**What you will see:** The subdomain field, a dropdown for your domain, and a document root field that auto-populates

4. Click **Create** button

**What you will see:** A success message saying the subdomain was created

---

### Step 5.2: Point the Subdomain to Your Node.js App

If you already set up the Node.js application with the subdomain URL (in Step 4.2), you may not need to do anything else.

If your subdomain shows a "default" page instead of your LMS:

1. Go back to **Software** > **Setup Node.js App**
2. Click to edit your application
3. Update the **Application URL** field to match your subdomain (example: `lms.yourchurch.org`)
4. Save and restart the application

---

## 6. SSL Certificate Setup

**What is SSL?** SSL (Secure Sockets Layer) adds the "padlock" icon to your website and changes the address from `http://` to `https://`. This encrypts data between visitors and your server, protecting passwords and personal information.

**SSL is essential** for any website with user logins.

---

### Step 6.1: Find the SSL Tool

Different hosts name this differently. Look for one of these in cPanel:

- **SSL/TLS** (in the Security section)
- **Let's Encrypt** or **Let's Encrypt SSL**
- **SSL/TLS Status**
- **AutoSSL**

**What you will see:** A page about SSL certificates with options to install or manage them

---

### Step 6.2: Install a Free SSL Certificate

Most hosting companies now offer free SSL certificates through Let's Encrypt. Here is how to install one:

**Method A: Using AutoSSL (If Available)**

1. Click on **SSL/TLS Status** in the Security section
2. Look for your domain and subdomain in the list
3. If they show "AutoSSL Domain Validated," SSL is already active
4. If not, click **Run AutoSSL** button

**What you will see:** A list of your domains with checkboxes and status indicators (green checkmarks for secured, yellow/red for unsecured)

**Method B: Using Let's Encrypt**

1. Click on **Let's Encrypt SSL** in the Security section
2. Find your domain/subdomain in the list
3. Click **Issue** next to your domain

**What you will see:** A list of domains with "Issue" buttons next to each one

4. On the next page, make sure both `yourchurch.org` and `www.yourchurch.org` are checked
5. Click **Issue** button

6. Wait 1-2 minutes for the certificate to be issued

**What you will see:** A progress indicator, then a success message

---

### Step 6.3: Force HTTPS Redirect

After installing SSL, you want to force all visitors to use the secure version (https://).

1. In cPanel, go to **Domains** section
2. Click on **Domains** or **Domain Settings**
3. Find your domain/subdomain
4. Look for a toggle or checkbox labeled **Force HTTPS** or **Force HTTPS Redirect**
5. Enable it (turn it on / check the box)

**What you will see:** A toggle switch or checkbox that you can click to enable

**Alternative method using .htaccess:**

If you do not see a Force HTTPS option:

1. Go to **File Manager**
2. Navigate to your LMS folder (or public_html)
3. Look for a file named `.htaccess`
   - If it does not exist, click **+ File** and create it
4. Click on `.htaccess` and click **Edit**
5. Add these lines at the very top:

```
RewriteEngine On
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
```

6. Click **Save Changes**

---

## 7. Troubleshooting Common Issues

### "502 Bad Gateway" Error

**What it means:** The web server cannot connect to your Node.js application.

**What you will see:** A white page with "502 Bad Gateway" or "Bad Gateway" message

**How to fix:**

1. Go to **Software** > **Setup Node.js App**
2. Check if your application shows "Stopped"
3. Click **Start App** or **Restart**
4. If it stops immediately, check the logs:
   - Click **View Logs**
   - Look for error messages
5. Common causes:
   - Wrong startup file path (should be `server/server.js`)
   - Missing environment variables
   - Port conflict (try changing PORT to 3000 or 8080)

---

### "Database Connection Failed" Error

**What it means:** The LMS cannot connect to your database.

**What you will see:** An error message mentioning "database," "connection," "ECONNREFUSED," or "Access denied"

**How to fix:**

1. Double-check your DATABASE_URL environment variable:
   - Username spelled correctly?
   - Password correct (no typos)?
   - Database name correct?
   - Using `localhost` as the host?

2. Verify the user has database permissions:
   - Go to **Databases** > **MySQL Databases**
   - Scroll to "Current Databases"
   - Check that your user is listed under "Privileged Users" for your database

3. Test the database connection:
   - Go to **Databases** > **phpMyAdmin**
   - Try logging in with your database username and password
   - If it fails, your credentials are wrong

---

### "Permission Denied" Error

**What it means:** The application does not have permission to read or write files.

**What you will see:** An error mentioning "EACCES," "permission denied," or "cannot write"

**How to fix:**

1. Go to **File Manager**
2. Navigate to your LMS folder
3. Right-click on the folder and select **Change Permissions**
4. Set permissions to `755` for folders
5. Set permissions to `644` for files

**What you will see:** A popup with checkboxes for Read, Write, Execute permissions for User, Group, and World

**Quick fix:** Most hosts have a "Reset Permissions" option. Look for it in File Manager's toolbar.

---

### "Cannot Upload Large Files" Error

**What it means:** There is a file size limit set by your hosting.

**What you will see:** Upload fails or shows "File too large" or "413 Request Entity Too Large"

**How to fix:**

1. In cPanel, search for **PHP Settings** or **MultiPHP INI Editor**
2. Select your domain
3. Find these settings and increase them:
   - `upload_max_filesize` = `64M`
   - `post_max_size` = `64M`
   - `max_execution_time` = `300`
4. Click **Apply** or **Save**

**What you will see:** A list of PHP settings with text fields or dropdowns to change values

---

### Application Will Not Start

**What it means:** Something is preventing Node.js from starting.

**How to fix:**

1. **Check the logs first:**
   - Go to Node.js Selector
   - Click View Logs for your application
   - Look for error messages at the bottom

2. **Common log errors and fixes:**

   | Error Message | Solution |
   |---------------|----------|
   | "Cannot find module..." | Run NPM Install again |
   | "Port already in use" | Change PORT environment variable to 3000 |
   | "ENOENT: no such file or directory" | Check Application Root path is correct |
   | "SyntaxError" or "Unexpected token" | Check Node.js version (use 18.x or higher) |

3. **Try reinstalling dependencies:**
   - In Node.js Selector, click **Run NPM Install**
   - Wait for it to complete
   - Then click **Restart**

---

### SSL Certificate Not Working

**What it means:** HTTPS is not active or shows warnings.

**What you will see:** Browser warning about "connection not secure" or "certificate error"

**How to fix:**

1. Wait 10-15 minutes after installing SSL (it takes time to activate)
2. Try accessing your site in a private/incognito browser window
3. If still not working:
   - Go back to SSL/TLS Status
   - Check for any error messages
   - Try running AutoSSL again
4. Make sure your domain DNS is pointing to your hosting server

---

## 8. Budget Hosting Recommendations

### Hosts CONFIRMED to Work with This LMS

These hosting companies support Node.js and have been tested:

| Host | Plan | Monthly Cost | Node.js Support | Notes |
|------|------|--------------|-----------------|-------|
| **A2 Hosting** | Turbo Boost | ~$7-12/month | Yes | Fast, good support |
| **Hostinger** | Business Web Hosting | ~$4-6/month | Yes | Budget-friendly |
| **Cloudways** | DigitalOcean 1GB | ~$14/month | Yes | Best performance |
| **HostGator** | Business Plan | ~$6-10/month | Yes (add-on) | Contact support to enable |
| **Namecheap** | Stellar Plus | ~$5-8/month | Yes | Good value |

**For Churches on Tight Budgets:** Hostinger Business plan offers the best value with Node.js support.

**For Better Performance:** Cloudways with DigitalOcean provides the smoothest experience.

---

### Hosts to AVOID (No Node.js Support)

These popular hosts do NOT support Node.js on their basic plans:

| Host | Issue |
|------|-------|
| **GoDaddy Economy/Deluxe** | No Node.js on basic shared hosting |
| **Bluehost Basic** | No Node.js on shared plans |
| **HostGator Hatchling/Baby** | No Node.js on lower tiers |
| **SiteGround StartUp/GrowBig** | No Node.js on shared hosting |
| **WordPress.com** | No custom Node.js apps |

**Important:** If you are already with one of these hosts, you may need to upgrade to a VPS plan or switch hosts.

---

### Minimum Requirements vs Recommended Specs

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| **Node.js Version** | 16.x | 18.x or 20.x |
| **RAM** | 512 MB | 1 GB or more |
| **Storage** | 5 GB | 20 GB or more |
| **Database** | MySQL 5.7 | PostgreSQL 13+ or MySQL 8.0 |
| **SSL** | Required | Required |

---

### Estimated Monthly Costs

For a small to medium church (under 500 members):

| Item | Cost Range |
|------|------------|
| **Web Hosting** | $5-15/month |
| **Domain Name** | $10-15/year (one-time) |
| **SSL Certificate** | Free (Let's Encrypt) |
| **Email (optional)** | $0-6/month |
| **Total** | $5-20/month |

**Tip for Churches:** Many hosting companies offer nonprofit discounts. Contact their support and ask about ministry or nonprofit pricing.

---

## Quick Reference Card

Keep this information handy after setup:

```
LMS Web Address: https://________________

Database Information:
- Host: localhost
- Name: ________________
- Username: ________________
- Password: ________________

FTP Information:
- Host: ________________
- Username: ________________
- Password: (same as cPanel)

cPanel Login:
- URL: ________________
- Username: ________________
- Password: ________________

Node.js Application:
- Location: /home/________/public_html/________
- Startup File: server/server.js
```

---

## Need Help?

If you get stuck:

1. **Check this guide again** - The solution is often in the troubleshooting section
2. **Contact your hosting support** - They can help with cPanel-specific issues
3. **Search the error message** - Copy the exact error and search online
4. **Ask in church tech communities** - Many churches share hosting tips

---

**Document Version:** 1.0
**Last Updated:** January 2026
**Applies to:** Community LMS for Churches

