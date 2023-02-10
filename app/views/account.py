from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import current_user, login_required
from app.forms import ProfileForm, SearchForm
from app.models import db, Article, History, Profile
from app.recommender import base

account = Blueprint("account", __name__)
ROWS_PER_PAGE = 10


@account.route("/home")
@login_required
def home():
    form = SearchForm()
    page = request.args.get("page", 1, type=int)
    articles = Article.query.order_by(Article.id).paginate(
        page=page, per_page=ROWS_PER_PAGE
    )

    return render_template(
        "account/home.html", form=form, articles=articles, link="account.home"
    )


@account.route("/<article_id>")
@login_required
def description(article_id):
    article = Article.query.get(article_id)

    # Create history
    history = History(
        profile_id=current_user.id, article_id=article_id, article_title=article.title
    )
    db.session.add(history)
    db.session.commit()

    # Get recommendations
    obj = base.Recommender(article.id)
    results = obj.get_similar_articles()  # Get index of similar articles
    recommendations = []
    for i in results:
        tmp = Article.query.filter_by(id=int(i)).first()
        if tmp:  # Check if article exist in db
            recommendations.append(tmp)

    return render_template(
        "account/description.html", article=article, recommendations=recommendations
    )


@account.route("/history")
@login_required
def history():
    form = SearchForm()
    page = request.args.get("page", 1, type=int)
    bookmarks = (
        History()
        .query.filter_by(profile_id=current_user.id)
        .order_by(History.seen_on.desc())
    )
    bookmarks = bookmarks.paginate(page=page, per_page=ROWS_PER_PAGE)

    return render_template(
        "account/history.html", form=form, bookmarks=bookmarks, link="account.history"
    )


@account.route("/history/delete")
@login_required
def delete_history():
    nbr_records_deleted = History.query.filter_by(profile_id=current_user.id).delete()
    db.session.commit()
    flash("%d enregistrements ont été supprimés avec succès." % nbr_records_deleted)

    return redirect(url_for("account.history"))


@account.route("/profile", methods=("GET", "POST"))
@login_required
def profile():
    form = ProfileForm(request.form, obj=current_user)

    if request.method == "POST" and form.validate():
        try:
            # Check if the email already exists
            if form.email.data != current_user.email:
                user = Profile.query.filter_by(email=form.email.data).first()  
                if user:
                    raise Exception(
                        "L'e-mail donné est pris. veuillez choisir une autre adresse e-mail."
                    )

            form.populate_obj(current_user)
            db.session.commit()
        except Exception as e:
            flash(str(e), "error")
        else:
            flash("Votre profil a été mis à jour avec succés.", "success")
    else:
        for err in form.errors.values():
            flash(err[0], "error")

    return render_template("account/profile.html", form=form)


@account.route("/search/article")
@login_required
def article_search():
    page = request.args.get("page", 1, type=int)
    search_query = request.args.get("q")

    if search_query is None:
        search_query = session["search"]
    else:
        session["search"] = search_query  # To use for the next request of pagination

    form = SearchForm(q=search_query)

    if form.validate():
        results = Article.query.filter(Article.title.like("%" + search_query + "%"))
        results = results.paginate(page=page, per_page=ROWS_PER_PAGE)
    else:
        for err in form.errors.values():
            flash(err[0], "error")

    return render_template(
        "account/home.html", form=form, articles=results, link="account.article_search"
    )


@account.route("/search/history")
@login_required
def history_search():
    page = request.args.get("page", 1, type=int)
    search_query = request.args.get("q")

    if search_query is None:
        search_query = session["search"]
    else:
        session["search"] = search_query

    form = SearchForm(q=search_query)

    if form.validate():
        results = History.query.filter(
            History.article_title.like("%" + search_query + "%")
        )
        results = results.paginate(page=page, per_page=ROWS_PER_PAGE)
    else:
        for err in form.errors.values():
            flash(err[0], "error")

    return render_template(
        "account/history.html",
        form=form,
        bookmarks=results,
        link="account.history_search",
    )
