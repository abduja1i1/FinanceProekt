from functools import wraps
from flask import session, flash, redirect, url_for

def login_required(required=True):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if required and not session.get('id'):
                flash('You must be logged in!', 'danger')
                return redirect(url_for('login'))
            if not required and session.get('id'):
                flash('You are already logged in!', 'info')
                return redirect(url_for('home'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator