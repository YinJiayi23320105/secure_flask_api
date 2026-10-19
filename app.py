from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
import bcrypt
from markupsafe import escape

app = Flask(__name__)
# 配置
app.config["JWT_SECRET_KEY"] = "super-secret-key-change-me-in-prod"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

jwt = JWTManager(app)
db = SQLAlchemy(app)

# 用户模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.LargeBinary, nullable=False)

with app.app_context():
    db.create_all()
    # 初始化测试用户，密码: test123
    test_user = User.query.filter_by(username="testuser").first()
    if not test_user:
        hash_pw = bcrypt.hashpw(b"test123", bcrypt.gensalt())
        new_u = User(username="testuser", password_hash=hash_pw)
        db.session.add(new_u)
        db.session.commit()


# 1.POST /auth/login
@app.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or "username" not in data or "password" not in data:
        return jsonify({"msg":"missing username/password"}),400
    user = User.query.filter_by(username=data["username"]).first()
    if user and bcrypt.checkpw(data["password"].encode("utf-8"), user.password_hash):
        token = create_access_token(identity=user.username)
        return jsonify(access_token=token),200
    return jsonify({"msg":"invalid credentials"}),401

# 2.GET /api/data 受保护接口，必须携带JWT
@app.route("/api/data", methods=["GET"])
@jwt_required()
def get_data():
    current_user = get_jwt_identity()
    # XSS防护：escape用户输出
    safe_user = escape(current_user)
    resp = {
        "username": safe_user,
        "user_data": ["item1","item2","item3"]
    }
    return jsonify(resp)

# 3.自定义接口 GET /api/public
@app.route("/api/public",methods=["GET"])
def public_api():
    q = request.args.get("q","")
    safe_q = escape(q)
    return jsonify({"query":safe_q,"note":"public endpoint no auth required"})

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)

