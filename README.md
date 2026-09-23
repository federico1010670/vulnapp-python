# vulnapp-python

Intentional Vulnerable Python Application - Used only for tests in AquilaX

## Purpose

This repository serves as a test target for the AquilaX security scanner suite. It contains intentional vulnerabilities and license violations to verify scanner detection capabilities.

---

## Security Vulnerabilities

The application includes the following **code-level vulnerabilities**:

| Vulnerability | Location | Description |
|---------------|----------|-------------|
| **SQL Injection** | `/add_post` route | User input directly inserted into SQL query without sanitization |
| **XSS (Cross-Site Scripting)** | `/view_post/<id>` route | User input rendered without proper escaping |
| **Hardcoded Credentials** | `app.py` | Admin credentials hardcoded in source code |
| **Path Traversal** | `/exec_command` route | Input not sanitized, allows arbitrary path access |
| **Code Injection** | `/exec_command` route | Executes user-supplied input as system command |
| **XSRF** | All forms | No CSRF protection implemented |

### `portal/` (FastAPI service)

`portal/` is a FastAPI + SQLAlchemy + asyncpg service with 41 intentional weaknesses: SQL injection, insecure deserialization, directory traversal, weak input validation, sensitive data exposure, access control, authentication, certificate and signature validation, cookie flags, SSRF, XSS, template and command injection, and open redirect. Several are reached only across functions or modules. Each has a safe twin that must not be reported.

---

## Docker Container

The `Dockerfile` includes:
- Python 3.11 slim base image
- System packages with various licenses (bash, coreutils - GPL)
- All Python dependencies from `requirements.txt`

---

## Running the Application

```bash
# Local development
pip install -r requirements.txt
python app.py

# Docker
docker build -t vulnapp-python .
docker run -p 5000:5000 vulnapp-python
```

---

## Scanner Testing

Install AquilaX CLI: [Docs](https://docs.aquilax.ai/user-manual/devtools/aquilax-cli#install)

```bash
# Run AquilaX scan
aquilax scan https://github.com/AquilaX-AI/vulnapp-python --sync
```

---

⚠️ **WARNING**: This application is intentionally vulnerable. Do NOT deploy in production environments.