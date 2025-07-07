# Gemini Code Guru
The Gemini Code Guru is a github app meticulously examines every line of code, ensuring adherence to best practices, identifying potential bugs, and promoting maintainable and scalable solutions. Their keen eye and deep understanding of software architecture are crucial for upholding our high-quality standards.

In short I created this just to learn how we can create a review assistant using github apis and gemini.

## Instructions
- Clone this repo.
- Create `.env` file with keys listed in the `.env.example` file
- Install (uv package manager)[https://github.com/astral-sh/uv]
- Install the required packages.
```sh
    uv sync
```
- Run the fastapi server
```sh
    fastapi dev main.py
```
- Install smee client for port forwarding all webhook request to our fastapi server
```sh
    npm install --global smee-client
    smee -u <webhook-url> -P /webhook -p <port-number>
```