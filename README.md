# ThinkIt 🛒

An e-commerce application inspired by Blinkit. ThinkIt provides users with a seamless shopping experience, featuring a built-in cart system and digital wallet capabilities allowing users to effortlessly add items to their cart and seamlessly manage funds for checkout.




![Main Application UI](docs/main_ui_placeholder.png)
*Caption: Main Application User Interface*

![Django Admin Panel](docs/admin_panel_placeholder.png)
*Caption: Django Admin Panel*

## 🛠️ Technical Specifications

* **Python Version:** 3.14
* **Web Framework:** Django (App module: `phase1app`)
* **Database:** SQLite (Local)

## 📋 Requirements

This project relies on the dependencies explicitly defined in `requirements.txt`:
* `asgiref==3.12.1`[cite: 1]
* `Django==6.1`[cite: 1]
* `sqlparse==0.5.5`[cite: 1]

## 🔑 Environment Configuration

Create a `.env` file in the root directory of your project to manage your environment variables securely. You can use the following `.env.example` as a template:

```env
# .env.example
SECRET_KEY=your_secret_key_here
DEBUG=True
DB_NAME=db.sqlite3
DB_USER=
DB_PASSWORD=
