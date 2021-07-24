from flask import Flask, render_template, request, redirect, url_for
import flask_sqlalchemy
import random
import string

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///urls.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = flask_sqlalchemy.SQLAlchemy(app)


class Url(db.Model):
    id_no = db.Column("id_no", db.Integer, primary_key=True)
    long_url = db.Column("long_url", db.String())
    short_url = db.Column("short_url", db.String(3))

    def __init__(self, long_url, short_url):
        self.long_url = long_url
        self.short_url = short_url


@app.before_first_request
def create_table():
    db.create_all()  # inbuilt function to built db


@app.route("/", methods=["POST", "GET"])
def home():
    if request.method == "POST":
        url = request.form["nm"]
        if not url:
            return "NO URL GIVEN"
        # first we search in db, if url is already present we return the short_url
        temp = Url.query.filter_by(long_url=url).first()
        if temp:
            return redirect(url_for("display_url", url=temp.short_url))
        else:
            # we have to create a new short_url
            new_short_url = generate_short_url()
            # add this to data base and commit
            db.session.add(Url(url, new_short_url))
            db.session.commit()
            return redirect(url_for("display_url", url=new_short_url))

    else:
        return render_template("index.html")


def generate_short_url():
    letters = string.ascii_uppercase + string.ascii_lowercase + string.digits
    while True:
        random_letters = random.choices(letters, k=3)
        new_url = "".join(random_letters)
        if not Url.query.filter_by(short_url=new_url).first():
            return new_url


@app.route("/output/<url>")
def display_url(url):
    return render_template('output.html', output=url)


@app.route("/<output_url>")
def redirection(output_url):
    temp = Url.query.filter_by(short_url=output_url).first()
    if temp:
        return redirect(temp.long_url)
    else:
        return "URL doesnot exist"


if __name__ == "__main__":
    app.run(debug=True)
