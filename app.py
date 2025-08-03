from flask import Flask, request, jsonify
from supabase import create_client, Client
import hashlib
import os

app = Flask(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route("/register", methods=["POST"])
def register_user():
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"success": False, "message": "Email and password are required"}), 400

        existing_user = supabase.table("users").select("id").eq("email", email).execute()
        if existing_user.data:
            return jsonify({"success": False, "message": "User already exists"}), 409

        supabase.table("users").insert({
            "email": email,
            "password": hash_password(password)
        }).execute()

        return jsonify({"success": True, "message": "User registered successfully"}), 201

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/login", methods=["POST"])
def login_user():
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"success": False, "message": "Email and password are required"}), 400

        user_data = supabase.table("users").select("*").eq("email", email).execute()
        if not user_data.data:
            return jsonify({"success": False, "message": "User not found"}), 404

        stored_password = user_data.data[0]['password']
        if stored_password != hash_password(password):
            return jsonify({"success": False, "message": "Incorrect password"}), 401

        return jsonify({"success": True, "message": "Login successful"}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
