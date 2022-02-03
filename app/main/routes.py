from pydoc import render_doc
from app import db
from app.main.forms import addCourseForm, DeleteProfileForm, EmptyForm, EditProfileForm
from flask import render_template, flash, redirect, url_for, request
from app.models import User, Course
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime
from app.main import bp



"""
This entire file contains view functions(or functions that handle all tasks that 
are requested by the user. i.e the homepage, the add course page, profile page and many more) 
Any view function that uses the @login_required decorator requires login before the 
user can view the page associated with it.
"""


@bp.before_request
def before_request():
    """ 
    This function  registers the time the user log ins.
    It then adds the last seen time to the database.
    Note that this function should be the first to be called.
    """
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@bp.route('/', methods = ['GET', 'POST'])
@bp.route('/index', methods = ['GET', 'POST'])
@login_required 
def scheduleView():
    """ 
    This view function displays the schedule of the user.
    Note that it requires the user of the web app to be logged in.
    This is accomplished by using the @login_required decorater
    """
    courseList = current_user.getCourses().all()
    courseListAll = current_user.followed_courses().all()
    if not courseList:
        flash("There are no courses to display!")
    return render_template('index.html', title = 'Home',  courseList = courseList)

def datetime_sqlalchemy(value):
    return datetime.strptime(value, "%H:%M:%S")      

@bp.route('/add', methods = ['GET', 'POST'])
@login_required
def addCourse():
    """ 
    This view function handles the add requests of the user.
    It displays a form that the user populates with the course they want to add.
    It then adds the course to the database
    """
    form = addCourseForm()
    if form.validate_on_submit():
        course = Course(course = form.course.data, building = 
        form.building.data, timestamp = datetime_sqlalchemy(str(form.time.data)), 
        author = current_user)
        db.session.add(course)
        db.session.commit()
        flash('Your course has been added to the schedule')
        return redirect(url_for('addCourse'))
        
    return render_template('add.html', title = 'AddCourse', form = form)


@bp.route('/user/<username>')
@login_required
def user(username):
    """ 
    This view function allows the user to view their profiles.
    It simply returns a list of the courses they have registered in the database
    """
    form = EmptyForm()
    user = User.query.filter_by(username = username).first_or_404()
    courses = current_user.getCourses().all()
    if not courses:
        flash("You have not added any courses to your ScheduLit")
    return render_template('user.html', user=user, courses = courses, form =form)
@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """ 
    This view function allows the user edit their profiles.
    
    """
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved')
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title= 'Edit Profile', form = form)



@bp.route('/deleteProfile/<int:id>', methods = ['POST', 'GET'])
def deleteProfile(id):
    """ This view function allows the user to delete  the profile and 
    the data associated with it in the database
    """
    form = DeleteProfileForm()
    to_delete = User.query.get_or_404(id)
    if request.method == 'POST' and form.validate_on_submit():
        if form.username.data == to_delete.username and to_delete.check_password(form.password.data): 
            courseList = current_user.getCourses().all()
            db.session.delete(to_delete)
            for course in courseList:
                db.session.delete(course)
            
            db.session.commit()      
            flash("We are sad to see you go!")
            logout_user()
        return redirect(url_for('main.scheduleView'))
    return render_template('deleteProfile.html', form = form)
@bp.route('/removeCourse/<item>', methods =['POST','GET'] )
def removeCourse(item):
    to_remove = Course.query.filter_by(course = item).first()
    db.session.delete(to_remove)
    db.session.commit()

    return redirect(url_for('scheduleView'))

@bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('main.scheduleView'))
        if user == current_user:
            flash('You cannot follow yourself!')
            return redirect(url_for('main.user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash('You are now following {}!'.format(username))
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.scheduleView'))

@bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('main.scheduleView'))
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('main.user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash('You are no longer following {}.'.format(username))
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.scheduleView'))
@bp.route('/explore')
@login_required
def explore():
    """ This view function allows the user to explore the courses of the people 
    they are following """
    followerCourses = Course.query.order_by(Course.timestamp.desc()).all()
    return render_template('explore.html', title='Explore', courses=followerCourses)


