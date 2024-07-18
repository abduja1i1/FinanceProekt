from operator import or_, and_

from app import app, bcrypt, db
from flask import render_template, flash, redirect, url_for, request, session
from datetime import datetime, timedelta
from app.decarators import login_required
from app.forms import RegistrationForm, LoginForm, TransferForm, TransferHistoryForm, ConfirmDeleteForm
from app.models import Users, Transfer


@app.route('/')
@login_required(required=False)
def home():
    return render_template("home.html")


@app.route('/user_menu')
@login_required(required=True)
def user_menu():
    return render_template('user_menu/user_menu.html')


@app.route("/logout")
@login_required(required=True)
def logout():
    session.pop("id")
    session.pop("card_number")
    session.pop("password")
    name=session.pop("name")
    session.pop("email")

    flash(f"{name} user successfully logged out", "success")
    return redirect(url_for("home"))


@app.route('/show_balance', methods=['GET', 'POST'])
@login_required(required=True)
def show_balance():
    user = Users.query.filter_by(id=session['id']).first()
    if request.method == 'GET':
        return render_template("user_menu/show_balance.html", user=user)
    elif request.method == 'POST':
        return redirect(url_for('user_menu'))


@app.route('/login', methods=['GET', 'POST'])
# @login_required(required=True)
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = Users.query.filter_by(email=form.email.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                session['name'] = user.first_name
                session['email'] = user.email
                session['id'] = user.id
                session['card_number'] = user.card_number
                session['password'] = user.password
                flash('You are now logged in!', 'success')
                return redirect(url_for('user_menu'))
            else:
                flash("Invalid email or password", "danger")
                return redirect(url_for('login'))
    return render_template('auth/login.html', form=form)


@app.route('/delete', methods=['GET', 'POST'])
@login_required(required=True)
def delete():
    form = ConfirmDeleteForm()

    if form.validate_on_submit():
        if form.confirm.data:
            user_id = session['id']
            user = Users.query.filter_by(id=user_id).first()
            db.session.delete(user)
            db.session.commit()
            flash('Your account has been deleted successfully.', 'success')
            return redirect(url_for('home'))
        elif form.cancel.data:
            return redirect(url_for('user_menu'))

    return render_template('user_menu/delete.html', form=form)




@app.route('/register', methods=['GET', 'POST'])
@login_required(required=False)
def register():
    form = RegistrationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            session["password"] = form.password.data
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = Users(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                phone_number=form.phone_number.data,
                email=form.email.data,
                card_number=form.card_number.data,
                card_balance=form.card_balance.data,
                password=hashed_password
            )
            db.session.add(user)
            db.session.commit()
            flash('You are now registered!', 'success')
            return redirect(url_for('login'))
    return render_template('auth/register.html', form=form)




@app.route('/add_balance', methods=['GET', 'POST'])
@login_required(required=True)
def add_balance():
    user = Users.query.filter_by(id=session['id']).first()
    if request.method == 'GET':
        return render_template("user_menu/add_balance.html")
    elif request.method == 'POST':
        num = request.form.get('num')
        num = int(num)
        if num < 0:
            flash('Please enter a positive number', 'danger')
        elif num:
            user.card_balance += num
            db.session.commit()
            flash('Balance successfully added!', 'success')
        return redirect(url_for('user_menu'))


@app.route('/transfer_money', methods=['GET', 'POST'])
@login_required(required=True)
def transfer_money():
    transfer = TransferForm()
    recipient = None

    if transfer.validate_on_submit():
        if 'confirm_transfer' not in request.form:
            recipient = Users.query.filter_by(card_number=transfer.recipient_card.data).first()

            if not recipient:
                flash('Recipient card number is not valid.', 'danger')
                return redirect(url_for('transfer_money'))

            sender = Users.query.filter_by(id=session['id']).first()

            if sender.card_number == transfer.recipient_card.data:
                flash('Invalid card number!', 'danger')
                return redirect(url_for('transfer_money'))

            if sender.card_balance < transfer.balance.data:
                flash('Insufficient balance to complete the transfer.', 'danger')
                return redirect(url_for('transfer_money'))


            flash(f'Please confirm the transfer to {recipient.first_name} {recipient.last_name}.', 'info')
        else:
            sender = Users.query.filter_by(id=session['id']).first()
            recipient = Users.query.filter_by(card_number=transfer.recipient_card.data).first()

            if not recipient or sender.card_number == transfer.recipient_card.data or sender.card_balance < transfer.balance.data:
                flash('Transfer could not be completed. Please try again.', 'danger')
                return redirect(url_for('transfer_money'))

            sender.card_balance -= transfer.balance.data
            recipient.card_balance += transfer.balance.data

            new_transfer = Transfer(
                sender_card=sender.card_number,
                recipient_card=recipient.card_number,
                balance=transfer.balance.data
            )
            db.session.add(new_transfer)
            db.session.commit()

            flash('Transfer successful!', 'success')
            return redirect(url_for('user_menu'))

    return render_template("user_menu/transfer_money.html", transfer=transfer, recipient=recipient)


@app.route("/transfer_history", methods=["GET", "POST"])
@login_required(required=True)
def transfer_history():
    kirim = []
    chiqim = []

    if request.method == 'POST':
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')

        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1)

            user_id = session.get('id')
            user = Users.query.get(user_id)

            transfers = Transfer.query.filter(
                or_(
                    Transfer.sender_card == user.card_number,
                    Transfer.recipient_card == user.card_number
                ),
                and_(
                    Transfer.transfer_time >= start_date,
                    Transfer.transfer_time < end_date
                )
            ).all()

            kirim = [t for t in transfers if t.recipient_card == user.card_number]
            chiqim = [t for t in transfers if t.sender_card == user.card_number]

            return render_template("user_menu/transfer_history.html", kirim=kirim, chiqim=chiqim)

    return render_template("user_menu/transfer_history.html")