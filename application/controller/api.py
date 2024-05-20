from urllib.parse import urljoin
from flask_restful import Resource, Api
from flask_restful import fields, marshal_with
from flask_restful import reqparse
from application.utils.validation import *
from application.data.models import *
from application.data.database import db
from flask import current_app as app
from flask import jsonify,request
import werkzeug
from flask import abort
from sqlalchemy import and_
from werkzeug.utils import secure_filename
import uuid as uuid
import os
from werkzeug.datastructures import FileStorage
from flask_jwt_extended import jwt_required
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity, get_current_user
from flask_jwt_extended import  verify_jwt_in_request
from flask_jwt_extended import JWTManager
import base64
from application.data.data_access import *
from application.controller.controllers import current_user
def url(picc,ifpic=False):
    if ifpic==False:
        return os.path.join(app.config['POST_FOLDER'],picc)
    else:
        return os.path.join(app.config['POST_FOLDER'],picc)
        


create_user_parser = reqparse.RequestParser()
create_user_parser.add_argument('name', type=str, help="name Required",required=True)
create_user_parser.add_argument('username', type=str, help="username Required",required=True)
create_user_parser.add_argument('email', type=str, help="email Required",required=True)
create_user_parser.add_argument('password', type=str, help="password Required",required=True)
create_user_parser.add_argument('about', type=str, help="about Required")

update_user_parser = reqparse.RequestParser()
update_user_parser.add_argument('name', type=str, help="name of user")
update_user_parser.add_argument('username', type=str, help="username of user")
update_user_parser.add_argument('email', type=str, help="email of user")
update_user_parser.add_argument('password', type=str, help="password of user")
update_user_parser.add_argument('about', type=str, help="about of user")


resource_fields = {
    'id' :  fields.Integer,
    'f1' :  fields.Integer,
    'f2' :  fields.Integer,
    'following' :  fields.Boolean,
    'username':    fields.String, 
    'name' :    fields.String,
    'email' :    fields.String,
    'about_author':    fields.String,
    'last_login': fields.String,
    'profile_pic':    fields.String,
}

class Search_User(Resource):
    @marshal_with(resource_fields)
    @jwt_required()
    def get(self):
        current_user=m()
        query=request.args.get('query')
        users = Users.query.filter(Users.name.like('%' + query + '%'))
        user = users.order_by(Users.name).all()
        for u in user:
            u.profile_pic=u.profile_pic
            u.f1 = u.followers.count()
            u.f2 = u.followed.count()
            if (current_user.is_following(u)):
                u.following=True
            else:
                u.following=False
        if user is None:
            raise NotFoundError(status_code=404)
        return user

class User_all(Resource):
    @marshal_with(resource_fields)
    @jwt_required()
    def get(self):
        user = Users.query.all()
        current_user=m()
        current_user=Users.query.filter_by(email=get_jwt_identity()).first()
        for u in user:
            u.profile_pic=u.profile_pic
            u.f1 = u.followers.count()
            u.f2 = u.followed.count()
            if (current_user.is_following(u)):
                u.following=True
            else:
                u.following=False
        if user is None:
            raise NotFoundError(status_code=404)
        return user

    @marshal_with(resource_fields)
    def post(self):
        args = create_user_parser.parse_args()
        username = args["username"]
        email = args["email"]
        name = args["name"]
        password = args["password"]
        about_author = args["about"]

        if username is None:
            raise UserValidationError(status_code=400, error_code="USR001", error_message="username is required")

        if email is None:
            raise UserValidationError(status_code=400, error_code="USR002", error_message="email is required")

        if "@" in email:
            pass
        else:
            raise UserValidationError(status_code=400, error_code="USR003", error_message="Invalid email")

        user = us(username)
        if user is not None:
            raise UserValidationError(status_code=400, error_code="USR004", error_message='Username Already Occupied.')

        user = Users.query.filter_by(email=email).first()
        if user is not None:
            raise UserValidationError(status_code=400, error_code="USR005", error_message='Please use a different email address.')

        user = Users.query.filter(and_(Users.username==username,Users.email==email))
        if user is None:
            raise AlreadyExistError(status_code=409)
        
        user = Users(name=name,username=username, email=email,about_author=about_author)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return user, 201       

class User(Resource):
    @marshal_with(resource_fields)
    @jwt_required()
    def get(self, username):
        current_user=m()
        u = us(username)
        xx=u.profile_pic
        u.profile_pic=xx
        u.f1 = u.followers.count()
        u.f2 = u.followed.count()
        if (current_user.is_following(u)):
            u.following=True
        else:
            u.following=False
        if u is None:
            raise NotFoundError(status_code=404)
        return u
        
    @marshal_with(resource_fields)
    def put(self, username):
        args = update_user_parser.parse_args()
        userp = us(username)
        if userp is None:
            raise NotFoundError(status_code=404)

        user = Users.query.filter(and_(Users.username==args.get("username"),Users.username!=username)).first()
        if user is not None:
            raise UserValidationError(status_code=400, error_code="USR004", error_message='Username Already Occupied.')

        user = Users.query.filter(and_(Users.email==args.get("email"),Users.email!=userp.email)).first()
        if user is not None:
            raise UserValidationError(status_code=400, error_code="USR005", error_message='Please use a different email address.')
        
        if args.get("username"):
            userp.username = args.get("username")
        if args.get("email"):
            if '@' in args.get("email"):
                userp.email = args.get("email")
            else:
                raise UserValidationError(status_code=400, error_code="USR003", error_message="Invalid email")
            
        if args.get("name"):
            userp.name = args.get("name")
        if args.get("password"):
            userp.password = args.get("password")
        if args.get("about"):
            userp.about_author = args.get("about")
        db.session.commit()
        return userp       
    @jwt_required()
    def delete(self, username):
        user = us(username)
        if user is None:
            raise NotFoundError(status_code=404)
        db.session.delete(user)
        db.session.commit()
        return ''    

class Myfollowers(Resource):
    @marshal_with(resource_fields)
    @jwt_required()
    def get(self,username):
        current_user=m()
        if current_user.username == username:
            user=current_user.followers.all()
            for u in user:
                u.profile_pic=u.profile_pic
                u.f1 = u.followers.count()
                u.f2 = u.followed.count()
                if (current_user.is_following(u)):
                    u.following=True
                else:
                    u.following=False
            if user is None:
                raise NotFoundError(status_code=404)
            return user
        else:
            return {"error":"cannot view others followers"}


class Myfollowing(Resource):
    @marshal_with(resource_fields)
    @jwt_required()
    def get(self,username):
        current_user=m()
        if current_user.username == username:
            user=current_user.followed.all()
            for u in user:
                u.profile_pic=u.profile_pic
                u.f1 = u.followers.count()
                u.f2 = u.followed.count()
                if (current_user.is_following(u)):
                    u.following=True
                else:
                    u.following=False
            if user is None:
                raise NotFoundError(status_code=404)
            return user
        else:
            return {"error":"cannot view others following"}

create_post_parser = reqparse.RequestParser()
create_post_parser.add_argument('title', type=str, help="title Required",required=True)
create_post_parser.add_argument('content', type=str, help="content Required",required=True)
create_post_parser.add_argument('slug', type=str, help="slug Required",required=True)

update_post_parser = reqparse.RequestParser()
update_post_parser.add_argument('title', type=str, help="title of post")
update_post_parser.add_argument('content', type=str, help="content of post")
update_post_parser.add_argument('slug', type=str, help="slug of post")

post_fields = {
    'id' :  fields.Integer,
    'lik' :  fields.Integer,
    'liked' :  fields.Boolean,
    'commen' :  fields.Integer,
    'title':    fields.String, 
    'content' :    fields.String,
    'timestamp' :    fields.String,
    'slug':    fields.String,
    'thumbnail': fields.String,
    'poster_id' :  fields.Integer,
    'poster':fields.Nested(resource_fields)
}

class Feed(Resource):
    @marshal_with(post_fields)
    @jwt_required()
    def get(self):  
        current_user=m() 
        posts = current_user.followed_posts().all()
        # posts = Posts.query.filter_by(poster_id=current_user.id).all()
        for p in posts:
            p.thumbnail=p.thumbnail
            p.lik=len(p.likes)
            p.commen=len(p.comments)
            # u=p.poster.username
            p.liked=bool(Like.query.filter(and_(Like.author==current_user.id,Like.post_id==p.id)).first())
            p.poster.profile_pic=p.poster.profile_pic
        return posts

        
class SearchFeed(Resource):
    @marshal_with(post_fields)
    @jwt_required()
    def get(self):  
        query=request.args.get('query')
        current_user=m()  
        posts = current_user.followed_posts().filter(Posts.title.like('%' + query + '%')).all()
        # posts = posts.filter_by(posts.title.like('%' + query + '%'))
        # posts = Posts.query.filter_by(poster_id=current_user.id).all()
        for p in posts:
            p.thumbnail=p.thumbnail
            p.lik=len(p.likes)
            p.commen=len(p.comments)
            # u=p.poster.username
            p.liked=bool(Like.query.filter(and_(Like.author==current_user.id,Like.post_id==p.id)).first())
            p.poster.profile_pic=p.poster.profile_pic
        return posts

class Myposts(Resource):
    @marshal_with(post_fields)
    @jwt_required()
    def get(self):  
        id=request.args.get('id') 
        current_user=m()  
        posts = Posts.query.filter_by(poster_id=id).all()
        # posts = current_user.followed_posts().all()
        # posts = Posts.query.filter_by(poster_id=current_user.id).all()
        for p in posts:
            p.thumbnail=p.thumbnail
            p.lik=len(p.likes)
            p.commen=len(p.comments)
            # u=p.poster.username
            p.liked=bool(Like.query.filter(and_(Like.author==current_user.id,Like.post_id==p.id)).first())
            p.poster.profile_pic=p.poster.profile_pic
        return posts

        
class SearchMyposts(Resource):
    @marshal_with(post_fields)
    @jwt_required()
    def get(self): 
        id=request.args.get('id') 
        query=request.args.get('query')
        current_user=m()  
        posts = Posts.query.filter_by(poster_id=id).filter(Posts.title.like('%' + query + '%')).all()
        # posts = posts.filter_by(posts.title.like('%' + query + '%'))
        # posts = Posts.query.filter_by(poster_id=current_user.id).all()
        for p in posts:
            p.thumbnail=p.thumbnail
            p.lik=len(p.likes)
            p.commen=len(p.comments)
            # u=p.poster.username
            p.liked=bool(Like.query.filter(and_(Like.author==current_user.id,Like.post_id==p.id)).first())
            p.poster.profile_pic=p.poster.profile_pic
        return posts

commenter_fields = {
    'profile_pic':    fields.String,
}

comment_fields = {
    'id' :  fields.Integer,
    'text':    fields.String, 
    'date_created' :    fields.String,
    'author' :    fields.Integer,
    'user':fields.Nested(commenter_fields)
}

postt_fields = {
    'id' :  fields.Integer,
    'lik' :  fields.Integer,
    'liked' :  fields.Boolean,
    'commen' :  fields.Integer,
    'title':    fields.String, 
    'content' :    fields.String,
    'timestamp' :    fields.String,
    'slug':    fields.String,
    'thumbnail': fields.String,
    'poster_id' :  fields.Integer,
    'poster':fields.Nested(resource_fields),
    'comments':fields.Nested(comment_fields)
}


class Post(Resource):
    @marshal_with(postt_fields)
    @jwt_required()
    def get(self,postid):  
        p = Posts.query.filter_by(id=postid).first()
        if p is None:
            raise NotFoundError(status_code=404)
        current_user=m()  
        p.thumbnail=p.thumbnail
        p.lik=len(p.likes)
        p.commen=len(p.comments)
        p.commen=len(p.comments)
        p.liked=bool(Like.query.filter(and_(Like.author==current_user.id,Like.post_id==p.id)).first())
        p.poster.profile_pic=p.poster.profile_pic
        
        return p
    @jwt_required()
    @marshal_with(post_fields)
    def put(self, postid):
        args = update_post_parser.parse_args()
        post = Posts.query.filter_by(id=postid).first()
        if post is None:
            raise NotFoundError(status_code=404)
        if args.get("title"):
            post.title = args.get("title")
        if args.get("content"):
            post.content = args.get("content")
        if args.get("slug"):
            post.slug = args.get("slug")
        db.session.commit()
        return post       
    @jwt_required()
    def delete(self, postid):
        post = Posts.query.filter_by(id=postid).first()
        if post is None:
            raise NotFoundError(status_code=404)
        db.session.delete(post)
        db.session.commit()
        return ''  

class Postofuser(Resource):
    @jwt_required()
    @marshal_with(post_fields)
    def get(self, username):
        userp = us(username)
        user = userp.posts.all()
        if user is None:
            raise NotFoundError(status_code=404)
        return user
    @marshal_with(post_fields)
    @jwt_required()
    def post(self, username):
        user = us(username)
        if user is None:
            raise NotFoundError(status_code=404)
        args = create_post_parser.parse_args()
        title = args["title"]
        content = args["content"]
        slug = args["slug"]


        post = Posts(title=title, content=content,poster_id=user.id, slug=slug)
        
        db.session.add(post)
        db.session.commit()
        return post, 201

comment_fields = {
    'id' :  fields.Integer,
    'text':    fields.String, 
    'date_created' :    fields.String,
    'user_name' :    fields.String,
    'user_profile_pic' :    fields.String,
    'author' :    fields.Integer,
    'post_id':    fields.Integer
}

class commentofpost(Resource):
    @jwt_required()
    @marshal_with(comment_fields)
    def get(self, postid):
        postp = Posts.query.filter_by(id=postid).first()
        if postp is None:
            raise NotFoundError(status_code=404)
        post=postp.comments
        for c in post:
            commenter=Users.query.filter_by(id=c.author).first()
            c.user_name=commenter.name
            c.user_profile_pic=commenter.profile_pic
        return post

class likepost(Resource):
    @jwt_required()
    def get(self, postid):
        postp = Posts.query.filter_by(id=postid).first()
        if postp is None:
            raise NotFoundError(status_code=404)
        likes=postp.likes
    
        return {'likes':len(likes)}

class followersinfo(Resource):
    @jwt_required()
    def get(self, username):
        userp = us(username)
        follower = userp.followers.count()
        followed = userp.followed.count()
        # if userp is None:
        #     raise NotFoundError(status_code=404)
        return {'followers':follower,'followed':followed}

class followinginfo(Resource):
    @jwt_required()
    def get(self, username):
        userp = us(username)
        user = userp.followed.count()
        if userp is None:
            raise NotFoundError(status_code=404)
        return {'following':user}


