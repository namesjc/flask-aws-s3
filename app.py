from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    Response,
    session,
)
from werkzeug.utils import secure_filename
from filters import datetimeformat, file_type
from resources import (
    get_bucket,
    get_buckets_list,
    _get_s3_client,
    generate_presigned_url,
    get_bucket_folder,
)

app = Flask(__name__)
app.secret_key = "secret"
app.jinja_env.filters["datetimeformat"] = datetimeformat
app.jinja_env.filters["file_type"] = file_type
app.jinja_env.filters["generate_presigned_url"] = generate_presigned_url
app.jinja_env.filters["get_bucket_folder"] = get_bucket_folder


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        bucket = request.form["bucket"]
        session["bucket"] = bucket
        return redirect(url_for("files"))
    else:
        buckets = get_buckets_list()
        return render_template("index.html", buckets=buckets)


@app.route("/create", methods=["POST"])
def create():
    if request.method == "POST":
        req = request.form
        bucket_name = req.get("bucketname")
        buckets = get_buckets_list()
        current_bucket_names = [bucket["Name"] for bucket in buckets]
        if bucket_name not in current_bucket_names:
            s3_client = _get_s3_client()
            s3_client.create_bucket(Bucket=bucket_name)
        flash(f"{bucket_name} is created successfully", "success")
    return redirect(url_for("index"))


@app.route("/delete_bucket", methods=["POST"])
def delete_bucket():
    if request.method == "POST":
        req = request.form
        bucket = req.get("bucket")
        s3_client = _get_s3_client()
        s3_client.delete_bucket(Bucket=bucket)
        flash(f"{bucket} is deleted successfully", "success")
    return redirect(url_for("index"))


@app.route("/upload", methods=["POST"])
def upload():
    req = request.form
    folder_name = req.get("folder_name")
    file = request.files["file"]
    if file:
        filename = secure_filename(file.filename)
        my_bucket = get_bucket()
        if folder_name != "":
            my_bucket.Object(f"{folder_name}/{filename}").put(Body=file)
        else:
            my_bucket.Object(filename).put(Body=file)
        flash("File uploaded successfully", "success")
    return redirect(url_for("files"))


@app.route("/download", methods=["POST"])
def download():
    key = request.form["key"]

    my_bucket = get_bucket()

    file_obj = my_bucket.Object(key).get()

    return Response(
        file_obj["Body"].read(),
        mimetype="text/plain",
        headers={"Content-Disposition": "attachment;filename={}".format(key)},
    )


@app.route("/delete", methods=["POST"])
def delete():
    key = request.form["key"]
    my_bucket = get_bucket()
    my_bucket.Object(key).delete()

    flash("File deleted successfully", "success")
    return redirect(url_for("files"))


@app.route("/files")
def files():

    my_bucket = get_bucket()
    summaries = my_bucket.objects.all()
    return render_template("files.html", my_bucket=my_bucket, files=summaries)


# @app.route("/upload", methods=["post"])
# def upload():
#     if request.method == "POST":
#         # s3_client.create_bucket(Bucket=BUCKET_NAME)
#         print(s3_client.list_buckets())
#         my_bucket = s3_resource.Bucket(BUCKET_NAME)
#         summaries = my_bucket.objects.all()
#         print(my_bucket)
#         print(summaries)
#         img = request.files["file"]
#         if img:
#             filename = secure_filename(img.filename)
#             img.save(filename)
#             s3_client.upload_file(filename, BUCKET_NAME, filename)
#             url = s3_client.generate_presigned_url(
#                 "get_object",
#                 Params={"Bucket": BUCKET_NAME, "Key": filename},
#                 ExpiresIn=300,
#             )

#     return render_template("file_upload_to_s3.html", url=url, files=summaries)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=8080)
