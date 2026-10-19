# secure_flask_api
Work1: Secure REST API Development with CI/CD and Real CVE Vulnerability Analysis

## Project Description
Secure Flask REST API implementing OWASP Top10 protections, integrated GitHub Actions SAST+SCA security scanning.
Implemented three API endpoints:
1. `POST /auth/login` : User authentication, return JWT access‑token
2. `GET /api/data` : Protected resource, valid JWT required
3. `GET /api/public?q=` : Custom public endpoint for XSS test

Test account:
- username: `testuser`
- password: `test123`

Security countermeasures implemented：
1. **SQL Injection protection**: Use SQLAlchemy ORM, no manual string concatenation for SQL statements.
2. **XSS protection**: Use `markupsafe.escape()` sanitize all user‑supplied input before return in responses.
3. **Broken Authentication mitigation**:
   - Password stored as bcrypt hash, plaintext password never persisted.
   - JWT token issued after successful login.
   - JWT middleware `@jwt_required()` valid token for protected routes.

## Environment
Python3.6+
Dependencies in `requirements.txt`

## Local run
```bash
git clone https://github.com/YinJiayi23320105/secure_flask_api.git
cd secure_flask_api
pip install -r requirements.txt
python3 app.py

