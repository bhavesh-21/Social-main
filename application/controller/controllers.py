from flask import Flask, request
from flask import render_template, jsonify, send_from_directory
from flask import current_app as app
from application.data.models import *
from flask import Flask, render_template, flash, request, redirect, url_for
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime,timedelta
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
import uuid as uuid
from application.data.data_access import *
import os
from sqlalchemy import and_
from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required, verify_jwt_in_request

current_user=None

@app.route('/static/images/<path:path>')
def serve_static(path):
    return send_from_directory('static/images/', path)

@app.route("/log", methods=["POST"])
def log():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    print(email,password)
    user = Users.query.filter_by(email=email).first()
    if user is None:
        return jsonify({"msg": "Email Not Found"}), 401
    elif not user.verify_password(password):
        return jsonify({"msg": "Invalid Password"}), 403
    else:
        access_token = create_access_token(identity=email,expires_delta=timedelta(days=10))
        user.last_login = datetime.utcnow()
        db.session.commit()
        login_user(user)
        return jsonify(access_token=access_token)


# Protect a route with jwt_required, which will kick out requests
# without a valid JWT present.
@app.route("/current-user", methods=["GET"])
@jwt_required()
def current_usr():
    # Access the identity of the current user with get_jwt_identity
    verify_jwt_in_request()
    user=Users.query.filter_by(email=get_jwt_identity()).first()
    global current_user
    current_user=user
    return jsonify(id=user.id,username=user.username,name=user.name,email=user.email,about=user.about_author,last_login=user.last_login,profile_pic=user.profile_pic), 200

@app.route("/logou", methods=["GET"])
@jwt_required()
def logou():
    user=m()
    user.last_login = datetime.utcnow()
    return jsonify(msg="logout successfilly"), 200

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# Create Search Function
@app.route('/users/search/', methods=["GET"])
def search_user():
    if(request.method == "GET"):
        query = request.json.get("search", None)
        if  query != '':
            current_user=m()
            users = Users.query.filter(and_(Users.email != current_user.email, Users.name.like('%' + query + '%')))
            users = users.order_by(Users.name).all()
            return jsonify(users=users)
        else:
            return jsonify({"msg":"Query Empty"}), 403
    return jsonify({"msg":"Method not allowed"}), 404

# Create Dashboard Page
@app.route('/update', methods=['POST'])
@jwt_required()
def update_user():
    user=m()
    id = user.id
    if request.method == "POST":
        # print(request.form['about'])
        user.about_author = request.form['about']
        user.name = request.form['name']
        user.username = request.form['username']
        user.set_password(request.form['password'])
        try:
            pic = request.files['profile_pic']
            pic_filename = secure_filename(pic.filename)
            pic_unique_name = str(uuid.uuid1()) + "_" + pic_filename
            user.profile_pic = pic_unique_name
            db.session.commit()
            pic.save(os.path.join(
                app.config['PIC_FOLDER'], pic_unique_name))
            return {"msg":"User Updated Successfully! with image upload"}
        except:
            db.session.commit()
            return {"Error":"Looks like there was a problem...try again!"}


@app.route('/posts/delete/<int:id>')
@jwt_required()
def delete_post(id):
    current_user=m()
    post_to_delete = Posts.query.get_or_404(id)
    id = current_user.id
    if id == post_to_delete.poster_id:
        try:
            db.session.delete(post_to_delete)
            db.session.commit()

            return {"msg":"Blog Post Was Deleted!"}

        except:
            return {"msg":"There was a problem deleting post..."}
    else:
        return {"msg":"You Aren't Authorized To Delete That Post!"}


@app.route('/comment/<int:id>', methods=['POST'])
@jwt_required()
def post(id):
    current_user=m()
    poster = current_user.id
    comment = Comment(text=request.json.get("comment", None), post_id=id, author=poster)
    db.session.add(comment)
    db.session.commit()
    return {"msg":"Commented Successfully!"}

@app.route('/remove-comment/<int:id>')
@jwt_required()
def remove_comment(id):
    current_user=m()
    c = Comment.query.get_or_404(id)
    if c.author == current_user.id or c.post.poster.id == current_user.id:
        db.session.delete(c)
        db.session.commit()
        return {"msg":"Comment Deleted Successfully!!"}
    else:
        return {"msg":"Can't Delete Someone else comment or Comment on someone else post!"}

@app.route('/follow/<username>', methods=['GET'])
@jwt_required()
def follow(username):
    current_user=m()
    current_user=m()
    user = Users.query.filter_by(username=username).first()
    if user is None:
        return {'msg':'User {} not found.'.format(username)}
    if username == current_user.username:
        print("<<<",current_user.username,username,">>>")
        return {'msg':'You cannot follow yourself!'}
    current_user.follow(user)
    db.session.commit()
    return {'msg':'ok'}

@app.route('/unfollow/<username>', methods=['GET'])
@jwt_required()
def unfollow(username):
    current_user=m()
    
    user = Users.query.filter_by(username=username).first()
    if user is None:
        return {'msg':'User {} not found.'.format(username)}
    if username == current_user.username:
        print("<<<",current_user.username,username,">>>")
        return {'msg':'You cannot follow yourself!'}
    current_user.unfollow(user)
    db.session.commit()
    return {'msg':'ok'}

@app.route('/block/<username>', methods=['GET'])
@jwt_required()
def block(username):
    current_user=m()
    
    user = Users.query.filter_by(username=username).first()
    if user is None:
        return {'msg':'User {} not found.'.format(username)}
    if username == current_user.username:
        print("<<<",current_user.username,username,">>>")
        return {'msg':'You cannot follow yourself!'}
    user.unfollow(current_user)
    db.session.commit()
    return {'msg':'ok'}

@app.route('/like-post/<int:id>')
@jwt_required()
def like(id):
    current_user=m()
    post = Posts.query.filter_by(id=id)
    like = Like.query.filter_by(author=current_user.id, post_id=id).first()

    if not post:
        return {'error':'Post not exist!'},404
    elif like:
        db.session.delete(like)
        db.session.commit()

    else:
        like = Like(author=current_user.id, post_id=id)
        db.session.add(like)
        db.session.commit()

    return {"msg":"ok"},201

@app.route('/edit-post/<int:id>', methods=['POST'])
@jwt_required()
def edit_post(id):
    post = Posts.query.get_or_404(id)
    # return {"msg":"ghj"}
    current_user=m()
    if request.method == "POST":
        print(post.title)
        post.title = request.form['title']
        post.content = request.form['content']
        post.slug = request.form['slug']
        try:
            thumbnail_image = request.files['thumbnail']
            thumbnail_secure = secure_filename(thumbnail_image.filename)
            thumbnail_unique_name = str(uuid.uuid1()) + "_" + thumbnail_secure
            old_thumbnail = os.path.join(app.config['POST_FOLDER'], post.thumbnail)
            thumbnail_image.save(os.path.join(
            app.config['POST_FOLDER'], thumbnail_unique_name))
            post.thumbnail = thumbnail_unique_name
            if os.path.exists(old_thumbnail) and old_thumbnail!="default_thumbnail.jpg":
                os.remove(old_thumbnail)
            db.session.commit()
            return {"msg":'Blog Post edited Successfully with Image Upload!'}
        except:
            db.session.commit()
            return {"msg":"Blog Post edited Successfully without Image Upload!"}

@app.route('/add-post', methods=['POST'])
@jwt_required()
def add_post():
    current_user=m()
    id = current_user.id
    if request.method == "POST":
        title = request.form['title']
        content = request.form['content']
        slug = request.form['slug']
        try:
            thumbnail_image = request.files['thumbnail']
            print("---------with image")
            thumbnail_secure = secure_filename(thumbnail_image.filename)
            thumbnail_unique_name = str(uuid.uuid1()) + "_" + thumbnail_secure
            post = Posts(title=title,content=content,poster_id=current_user.id, slug=slug,thumbnail=thumbnail_unique_name)
            thumbnail_image.save(os.path.join(app.config['POST_FOLDER'], thumbnail_unique_name))
            db.session.add(post)
            db.session.commit()
            return {"msg":'Blog Post Submitted Successfully with Image Upload!'}
        except:
            print("---------without image")
            post = Posts(title=title,poster_id=current_user.id,slug=slug,content=content)
            db.session.add(post)
            db.session.commit()
            return {"msg":"Blog Post Submitted Successfully without Image Upload!"}

@app.route('/delete/<username>')
@jwt_required()
def delete(username):
    current_user=m()
    if username == current_user.username:
        user = Users.query.filter_by(username=username).first_or_404()
        try:
            db.session.delete(user)
            db.session.commit()
            return {"msg":"User Deleted Successfully!!"}
        except:
            return {"msg":"There was a problem deleting user..."},401
    else:
        return {"msg":"You can't Delete Someone Else Account!"},404

@app.route('/')
def index():
    return render_template("base.html")

@app.errorhandler(404)
def page_not_fou(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500