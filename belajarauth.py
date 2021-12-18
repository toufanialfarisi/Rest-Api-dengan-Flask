# import library flask dan lainnya
from flask import Flask, request, make_response, jsonify
from flask_restful import Resource, Api

# import PyJWT
import jwt 
import datetime 

# import library untuk membuat decorator
from functools import wraps

# inisialisasi objek flask dkk
app = Flask(__name__) #flask
api = Api(app) # restfull
app.config['SECRET_KEY'] = "inirahasianegara"

# decorator untuk kunci endpoint / authentikasi
def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        # token akan diparsing melalui parameter di endpoint
        token = request.args.get('token')

        # cek token ada atau tidak
        if not token:
            return make_response(jsonify({"msg":"tokennya nggak ada bro"}), 404)

        # decode token yang diterima 
        try:
            output = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        except:
            return make_response(jsonify({"msg":"token nggak bener / invalid"}))
        return f(*args, **kwargs)
    return decorator 


#1 Membuat endpoint untuk login
class LoginUser(Resource):
    def post(self):
        # butuh multipart form untuk transmisi data
        username = request.form.get('username')
        password = request.form.get('password')

        # membuat kondisi pengecekan password 
        if username and password == 'superadmin':
            # hasilkan nomor token
            token = jwt.encode(
                {
                    "username":username, 
                    "exp":datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
                }, app.config['SECRET_KEY'], algorithm="HS256"
            )
            return jsonify({
                "token":token,
                "msg":"Anda berhasil login !"
            })
        
        return jsonify({"msg":"Silahkan login !"})

# Halaman yang di-protected 
class Dashboard(Resource):
    # menambahkan decorator untuk mengunci halaman ini
    @token_required
    def get(self):
        return jsonify({"msg":"ini adalah halaman dashboard, butuh login untuk mengaksesnya"})


# halaman yang tidak di-protected / semua user bebas mengakses
class HomePage(Resource):
    def get(self):
        return jsonify({"msg":"ini adalah halaman umum/public"})

api.add_resource(LoginUser, "/api/login", methods=["POST"])
api.add_resource(Dashboard, "/api/dashboard", methods=["GET"])
api.add_resource(HomePage, "/api", methods=["GET"])

if __name__ == "__main__":
    app.run(debug=True)
