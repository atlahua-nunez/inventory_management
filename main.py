from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from forms import ArticleForm

class Base(DeclarativeBase):
    pass

#Create Object
db = SQLAlchemy(model_class = Base)

# create the app
app = Flask(__name__)
bootstrap = Bootstrap5(app)
app.config['SECRET_KEY'] = 'supersecretkey'
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///inventory_project.db"
# initialize the app with the extension
db.init_app(app)

# Define Model
class Article(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(250), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)

#Create Tables
with app.app_context():
    db.create_all()

# Si opción == "Agregar Producto":
#
# Pedir nombre del producto
#
# Pedir cantidad
#
# Pedir precio
#
# Guardar en la base de datos
#
# Volver al menú

# CRUD
@app.route('/')
def home():
    #constructs a query to select data from the database, select Article, ordered by 'id'
    '''.scalars() 👉 Devuelve solo los registros, no toda la información de la consulta.
    .all() 👉 Convierte todos los registros en una lista de objetos Book.'''
    all_parts = db.session.execute(db.select(Article).order_by(Article.code)).scalars().all()
    return render_template('index.html', parts=all_parts)


# Create
@app.route('/add', methods=['GET', 'POST'])
def add():
    form = ArticleForm()
    if form.validate_on_submit():
        new_article = Article(
            code=form.code.data,
            name=form.name.data,
            description=form.description.data,
            quantity=form.quantity.data,
            unit_price=form.unit_price.data,
        )
        db.session.add(new_article)
        db.session.commit()
        flash("Article added successfully","success")
        return redirect(url_for('home'))
    return render_template('/add.html', form=form)

@app.route('/edit/<int:article_code>', methods=["GET", "POST"])
def edit(article_code):
    article = db.get_or_404(Article, article_code)
    if request.method == "POST":
        article.quantity = float(request.form["quantity"])
        article.unit_price = float(request.form["unit_price"])
        db.session.commit()
        flash("Article updated correctly", "update")
        return redirect(url_for('home'))
    return render_template("edit.html", article=article)



@app.route('/delete/<int:article_code>')
def delete(article_code):
    article = db.get_or_404(Article, article_code)
    db.session.delete(article)
    db.session.commit()
    flash("Article deleted successfully", "success")
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)

