<h1 align="center"><img src="logo.png" alt="LiteDBox Icon" height="30"> LiteDBox</h1>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Active-brightgreen" alt="Status">
  <img src="https://img.shields.io/badge/Version-1.0-blue" alt="Version">
  <img src="https://img.shields.io/badge/License-MIT-orange" alt="License">
</p>

<p align="center">
  <strong>Your alternative lightweight database solution for simplified data management</strong><br>
  <em>Fast • Local • JSON-powered</em>
</p>

<p align="center">
  <a href="#-features">✨ Features</a> •
  <a href="#-getting-started">🚀 Get Started</a> •
  <a href="#-file-format">📂 File Format</a> •
  <a href="#-contributing">🙌 Contributing</a> •
  <a href="#-support">❤️ Support</a>
</p>

<hr>

<div align="center">  
  <i>Lightweight. Local. Lightning-fast.</i>
</div>

## 💡 About LiteDBox

**LiteDBox** is a lightweight database solution built for simplicity and efficiency. It runs entirely **locally** using a **JSON file format**, enabling you to manage structured data without setting up a traditional RDBMS.

Whether you're prototyping, building a small app, or learning SQL basics, LiteDBox keeps your workflow fast and flexible.

> ⚠️ Basic SQL knowledge is recommended to get the most out of LiteDBox.

<hr>

## ✨ Features

<table>
  <tr>
    <td>✅ <b>Simple</b></td>
    <td>Minimal configuration, intuitive commands</td>
  </tr>
  <tr>
    <td>⚡ <b>Lightweight</b></td>
    <td>Fast performance with low resource usage</td>
  </tr>
  <tr>
    <td>🔒 <b>Secure</b></td>
    <td>Local storage with zero external connections</td>
  </tr>
  <tr>
    <td>🧠 <b>Familiar Syntax</b></td>
    <td>Use SQL-like commands to interact with your data</td>
  </tr>
  <tr>
    <td>🗃 <b>Portable</b></td>
    <td>Runs via a single local file</td>
  </tr>
</table>

<hr>

## 🚀 Getting Started

### 1. Installation

Download and install the **LiteDBox SQL Studio Tool** on your device.

### 2. Creating a Database

Launch the tool and create a database with:

```sql
create database db_name
```

### 3. Using Your Database

Select your database for use:

```sql
use db_name
```

> 🔁 **Note:** You must reselect your database with use db_name each time you open LiteDBox.

### 4. Creating Tables

Define your schema like this:

```sql
create table users (id, name, email)
```

### 5. Working with Data

<details>
<summary>View Common Commands</summary>

Retrieve all data:
```sql
select * from users
```

Update a value:
```sql
update users set name = "John" where id = 1
```

Delete a row:
```sql
delete from users where id = 1
```

Drop table or database:
```sql
drop table users
drop database db_name
```
</details>

## 🛠 Example

```sql
create database testdb
use testdb
create table tasks (id, title, done)
insert into tasks values (1, "Write README", false)
select * from tasks
```

<div align="center">
</div>

## 📂 File Format

All data is stored in structured JSON files, offering human-readable and easily portable storage.

<hr>

## 🙌 Contributing

<div align="center">
</div>

Contributions are welcome! Feel free to fork the repository, open issues, or submit pull requests.

## ❤️ Support

If you enjoy using LiteDBox, consider starring ⭐ the repo and sharing it with others!

<div align="center">
  <p>Made with simplicity in mind.</p>
  <p>© 2025 LiteDBox</p>
</div>
