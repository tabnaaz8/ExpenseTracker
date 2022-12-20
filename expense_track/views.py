from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_required, current_user

from . import db
from .models import Budget, Expense
from datetime import datetime, timedelta, date

views = Blueprint("views", __name__)

categories = ["Domestic", "Donation", "Education", "Grocery", "Family", "Maintenance", "Medical", "Miscellaneous",
              "Personal", "Rent", "Services"]

months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November",
          "December"]

years = ["2021", "2022", "2023", "2024", "2025", "2026", "2027", "2028", "2029", "2030"]


@views.route("/", methods=['POST', 'GET'])
@views.route("/home", methods=['POST', 'GET'])
@login_required
def home():
    if request.method == 'POST':
        month = request.form.get("month_name");
        year = request.form.get("year1");
        print("Month " + month, "Year " + year)
        monthly_budget = get_monthly_budget(month, year)

        mnum = datetime.strptime(month, '%B').month
        print(mnum)
        monthly_expenses = get_monthly_expense(int(mnum), int(year))
        return render_template("home.html", user=current_user, budget=monthly_budget, expense=monthly_expenses,
                               months=months, years=years, selected_month=month, selected_year=year)
    else:
        currentDate = datetime.now()
        print('Month full name:', str(currentDate.strftime('%B')))

        monthly_budget = get_monthly_budget(str(currentDate.strftime('%B')), currentDate.year)

        monthly_expenses = get_monthly_expense(currentDate.month, currentDate.year)

        return render_template("home.html", user=current_user, budget=monthly_budget, expense=monthly_expenses,
                               months=months, years=years, selected_month=str(currentDate.strftime('%B')),
                               selected_year=currentDate.year)


@views.route("/setbudget/<month>/<year>", methods=['GET', 'POST'])
@login_required
def set_budget(month, year):
    if request.method == 'POST':
        month = request.form.get("month")
        year = request.form.get("year")
        amount = request.form.get("amount")
        if float(amount) <= 0:
            flash("Budget amount should be greater than 0")
        else:
            entry = Budget(month=month, year=year, amount=float(amount), user=current_user)
            db.session.add(entry)
            db.session.commit()
            flash("Budget set!", category='success')
            return redirect(url_for('views.home'))
    else:
        # current_date = date.today()
        # mon = current_date.month
        # year = current_date.year
        return render_template("set_budget.html", user=current_user, month=month,
                               year=year)


@views.route("/update-budget/<id>/<month>/<year>", methods=['GET', 'POST'])
@login_required
def update_budget(id, month, year):
    budget = Budget.query.filter_by(budget_id=id).first()
    if request.method == "POST":
        budget.amount = request.form.get("amount")

        print("Month ", month)
        print("Year ", year)

        mnum = datetime.strptime(month, '%B').month

        expense = get_monthly_expense(int(mnum), int(year))
        sum_expense = 0.0
        for expense in expense:
            sum_expense = expense.amount + sum_expense

        if float(budget.amount) <= 0:
            flash("Budget amount should be greater than 0", category="error")

        elif float(budget.amount) < sum_expense:
            flash("Budget limit cannot be less than total expense amount", category="error")
        else:
            db.session.commit()
            flash('Budget updated successfully', category="success")
            return redirect(url_for('views.home'))
        return redirect(url_for('views.home'))
    else:
        return render_template("update_budget.html", user=current_user, budget=budget, month=month, year=year)


@views.route("/add-expense/<month>/<year>", methods=['GET', 'POST'])
@login_required
def add_expense(month, year):
    if request.method == 'POST':
        category = request.form.get("category")
        comments = request.form.get("note")
        try:
            amount = float(request.form.get("amount"))
        except ValueError:
            flash("Amount should be a number ", category="error");
        date = request.form.get("datepicker")

        print("Date " + date)

        dt_object = datetime.strptime(
            date, '%m/%d/%Y')

        print("Formatted date", dt_object)

        budget = get_monthly_budget(str(dt_object.strftime('%B')), dt_object.year)
        expense = get_monthly_expense(dt_object.month, dt_object.year)
        sum_expense = 0.0
        for expense in expense:
            sum_expense = expense.amount + sum_expense

        if amount <= 0:
            flash("Expense amount should be greater than 0", category="error")
        elif (sum_expense + float(amount)) > budget.amount:
            flash("Expense exceeding budget limit ", category="error");
        elif float(amount) > budget.amount:
            flash("Expense amount cannot be greater than budget amount", category="error");
        else:
            entry = Expense(category=category, comments=comments, expense_date=dt_object, amount=float(amount),
                            user=current_user, budget=budget.budget_id)
            db.session.add(entry)
            db.session.commit()
            flash("Expense added!", category='success')
            return redirect(url_for('views.home'))
        return render_template("add_expense.html", user=current_user, category=categories)
    else:
        start_date = get_start_date(int(datetime.strptime(month, '%B').month), int(year))
        end_date = get_end_date(int(datetime.strptime(month, '%B').month), int(year))
        return render_template("add_expense.html", user=current_user, category=categories, start_date=start_date,
                               end_date=end_date)


@views.route("/update-expense/<id>/<month>/<year>", methods=['GET', 'POST'])
@login_required
def update_expense(id, month, year):
    expense = Expense.query.filter_by(expense_id=id).first()
    if request.method == "POST":
        expense.category = request.form.get("category")
        expense.comments = request.form.get("note")
        try:
            expense.amount = float(request.form.get("amount"))
        except ValueError:
            flash("Amount should be a number ", category="error");
        budget = get_monthly_budget(month, year)
        mnum = datetime.strptime(month, '%B').month
        expenses = get_monthly_expense(int(mnum), int(year))
        sum_expense = 0.0

        for e in expenses:
            sum_expense = float(e.amount) + sum_expense

        sum_expense = sum_expense - expense.amount
        if expense.amount <= 0:
            flash("Expense amount should be greater than 0", category="error")
        elif float(expense.amount) > budget.amount:
            flash("Expense amount cannot be greater than budget amount", category="error");

        elif (sum_expense + float(expense.amount)) > budget.amount:
            flash("Expense exceeding budget limit ", category="error");

        else:
            db.session.commit()
            flash('Expense updated successfully', category="success")
            return redirect(url_for('views.home'))
        return render_template("update_expense.html", user=current_user, expense=expense, month=month, year=year)
    else:
        return render_template("update_expense.html", user=current_user, expense=expense, month=month, year=year)


@views.route("/delete-expense/<id>", methods=['GET', 'POST'])
@login_required
def delete_expense(id):
    expense = Expense.query.filter_by(expense_id=id).first()
    # if request.method == 'POST':
    db.session.delete(expense)
    db.session.commit()
    return redirect(url_for('views.home'))
    # else :
    # return render_template("confirm_modal.html", user=current_user)


@views.route("/expense-history")
@login_required
def expense_history():
    expense = Expense.query.filter(Expense.author == current_user.id).all()
    return render_template("expense_history.html", expense=expense, user=current_user)


@views.route("/expense-category")
@login_required
def get_expense_by_category():
    expense = Expense.query.filter(Expense.author == current_user.id).all()
    return render_template("expense_category.html", expense=expense, user=current_user)


@views.route("/savings")
@login_required
def get_savings():
    expense = Expense.query.filter(Expense.author == current_user.id).all()
    budget = Budget.query.filter(Budget.author == current_user.id).all()
    return render_template("savings.html", expense=expense, budget=budget, user=current_user)


@login_required
def get_monthly_expense(month, year):
    start_date = get_start_date(month, year)
    end_date = get_end_date(month, year)
    # Expense.query.filter(Expense.author == current_user.id).all()
    result = (Expense.query
              .filter(Expense.author == current_user.id)
              .filter(Expense.expense_date >= start_date)
              .filter(Expense.expense_date <= end_date)
              ).all()
    print(result)
    return result


def get_end_date(month, year):
    if month == 12:
        last_date = datetime(year, month, 31)
    else:
        last_date = datetime(year, month + 1, 1) + timedelta(days=-1)

    end_date = last_date.strftime("%Y-%m-%d")
    print(end_date)
    return end_date


def get_start_date(month, year):
    first_date = datetime(year, month, 1)
    start_date = first_date.strftime("%Y-%m-%d")
    print(start_date)
    return start_date


@login_required
def get_monthly_budget(month, year):
    # current_date = datetime.date.today()
    # budget = Budget.query.filter_by(author=current_user.id,).all()
    budget = (Budget.query
              .filter(Budget.month == month)
              .filter(Budget.year == year)
              .filter(Budget.author == current_user.id)
              ).first()
    print(budget)
    return budget
