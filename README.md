# secure_flask_api

Work1: Secure REST API Development with CI/CD and Real CVE Vulnerability Analysis

GitHub Repository: [https://github.com/YinJiayi23320105/secure_flask_api](https://github.com/YinJiayi23320105/secure_flask_api)
Last successful CI pipeline run: [https://github.com/YinJiayi23320105/secure_flask_api/actions/runs/39242061848](https://github.com/YinJiayi23320105/secure_flask_api/actions/runs/39242061848)

## Project Description

Secure Flask REST‑API implements OWASP Top10 protections, integrated GitHub Actions SAST & SCA security scanning.
Implemented 3 API endpoints:

1. `POST /auth/login` — User authentication, return JWT access‑token. Accept username and password in JSON body.
2. `GET /api/data` — Protected resource, **valid JWT token required in Authorization header**. Returns sample user list data.
3. `GET /api/public` — Custom public endpoint for XSS input test, accepts GET parameter `q`.

Test account:

- username: `testuser`
- password: `test123`

### How to call the API

1. Login to get JWT token

```
curl -X POST -H "Content-Type: application/json" -d '{"username":"testuser","password":"test123"}' http://127.0.0.1:5000/auth/login
```

2. Access protected `/api/data` with Bearer JWT token

```
curl -H "Authorization: Bearer YOUR_TOKEN" http://127.0.0.1:5000/api/data
```

3. Access public test endpoint

```
curl http://127.0.0.1:5000/api/public?q=test
```

## Implemented Security Measures

1. **SQL Injection protection**
Using SQLAlchemy ORM for database operations. No manual string concatenation for building SQL queries. ORM automatically generates parameterized queries to prevent SQL‑injection risk.
2. **XSS protection**
User‑supplied input is sanitized by `markupsafe.escape()` before returning in API JSON responses. HTML and script symbols will be escaped to plain text. Test payload `<script>alert(1)</script>` is escaped and cannot execute javascript.
3. **Broken Authentication mitigation**

- Password is hashed by bcrypt before saving to SQLite `users.db`. Plain‑text passwords are never stored.
- After successful login, server issues short‑lived JWT access‑token for client.
- `@jwt_required()` middleware decorator for protected routes, every request validates JWT signature and expiration. Requests without valid token get access denied.

## CI/CD Security Scanning

GitHub‑Actions workflow `.github/workflows/security‑scan.yml` will run on every push / pull request:

1. SAST: **Bandit** static source‑code security scan for insecure coding patterns.
2. SCA: **Safety** dependency vulnerability scan for third‑party library known vulnerabilities.

> 
> All screenshots for SAST/SCA scan, vulnerability reproduction and fix‑verification are attached in submitted PDF lab report. Raw scan logs can be viewed in GitHub Actions run page.

---

# CVE‑2018‑1000656 Jinja2 SSTI Vulnerability

## Vulnerability brief description

CVE‑2018‑1000656 is Server‑Side Template Injection(SSTI) in Flask Jinja2. User‑controlled GET parameter `name` is directly concatenated into template source code. Attackers inject Jinja2 `{{ }}` expressions to execute Python code, traverse object subclass chain and invoke `subprocess.Popen` to achieve remote command execution and arbitrary file read.

## Vulnerability Reproduction Sequence

1. Start vulnerable service, access `http://127.0.0.1:5001`
2. SSTI detection payload: `http://127.0.0.1:5001/?name={{7*7}}`
Vulnerable server outputs `Hello 49`, proves template expression can be executed.
3. Traverse object inheritance chain to find subprocess.Popen class.
4. Remote command execution payload:
`/?name={{''.__class__.__bases__[0].__subclasses__()[200]('whoami',shell=True,stdout=-1).communicate()[0].decode()}}`
5. Use payload to list directory, read source‑code and docker‑compose.yml configuration file.

## Root‑cause Analysis

Vulnerability comes from unsafe code: `t = Template("Hello " + name)`.
Untrusted user input `name` is directly concatenated to Jinja2 template source string. Everything passed into Template() constructor will be parsed as template source code, including attacker‑injected `{{ }}` expressions. There is no separation between static template source and user‑provided variable data, leads to SSTI and remote‑code‑execution.

## Applied Fix

Do **not concatenate user input into template source**. Keep template source static fixed string; pass user‑input as render‑time named variable.

> 
> Vulnerable original code snippet

```
t = Template("Hello " + name)
return t.render()
```

> 
> Fixed secure code snippet

```
t = Template("Hello {{ name }}")
return t.render(name=name)
```

User‑supplied values passed in `render()` are treated as plain‑text data. Any `{{ }}` syntax inside user input will NOT be parsed as template expression.

Fixed source file stored in repository folder: `/cve_fix/app.py`

## Proof of Vulnerability Elimination

1. Test SSTI payload `/?name={{7*7}}`
Fixed application outputs literal string `Hello {{7*7}}`. Expression `7*7` will **not be calculated**.
2. Full RCE payload returns raw payload text; system commands will not execute.
3. Regression test normal access: `/?name=student` returns `Hello student`. Main business function works normally after patch, no regression bug.
