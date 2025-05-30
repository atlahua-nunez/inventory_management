import io
import pandas as pd
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from forms import ArticleForm
import csv
from io import TextIOWrapper


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
    code: Mapped[str] = mapped_column(String, nullable=False)
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

@app.route('/parts/<string:article_code>', methods=['GET'])
def view_material(article_code):
    # Si viene un nuevo code en los parametros GET, redirige a la nueva URL
    new_code = request.args.get('code')
    if new_code:
        return redirect(url_for('view_material', article_code=new_code.lower()))

    # Buscar el material al dar clic en el nombre del numero de parte, si el material existe redirije a parts.html
    material = db.session.execute(db.select(Article).where(Article.code.ilike(article_code))).scalar()
    if not material:
        flash('Material not found', 'danger')
        return redirect(url_for('home'))
    return render_template('parts.html', article=material)


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

@app.route('/edit/<string:article_code>', methods=["GET", "POST"])
def edit(article_code):
    article = Article.query.filter_by(code=article_code).first_or_404()
    if request.method == "POST":
        article.quantity = float(request.form["quantity"])
        article.unit_price = float(request.form["unit_price"])
        db.session.commit()
        flash("Article updated correctly", "update")
        return redirect(url_for('home'))
    return render_template("edit.html", article=article)



@app.route('/delete/<string:article_code>')
def delete(article_code):
    article = db.get_or_404(Article, article_code)
    db.session.delete(article)
    db.session.commit()
    flash("Article deleted successfully", "success")
    return redirect(url_for('home'))

@app.route('/import', methods=['GET', 'POST'])
def import_csv():
    if request.method == 'POST':
        file = request.files.get('file')

        if not file or not file.filename.endswith('.csv'):
            flash('Not a valid file, please use a valid CSV file.')
            return redirect(url_for('home'))

        try:
            df = pd.read_csv(file)
            required_columns = {'code', 'name', 'description', 'quantity', 'unit_price'}
            if not required_columns.issubset(df.columns):
                flash('File must have titles for each column: code, name, description, quantity, unit_price')
                return redirect(url_for('import.html'))

            added = 0
            for _,row in df.iterrows():
                try:
                    code = str(row['code']).strip()
                    name = str(row['name']).strip()
                    description = str(row['description']).strip()
                    quantity = int(row['quantity'])
                    unit_price = float(row['unit_price'])

                    existing = Article.query.filter_by(code=code).first()
                    if not existing:
                        new_article = Article(
                            code=code,
                            name=name,
                            description=description,
                            quantity=quantity,
                            unit_price=unit_price,
                        )
                        db.session.add(new_article)
                        added += 1
                except Exception as e:
                    flash(f"Error trying to process the row: {e}")
                    continue

            db.session.commit()
            flash(f"{added} succesfully imported articles.")
            return redirect(url_for('home'))

        except Exception as e:
            flash(f"Error trying to read the file: {e}")
            return redirect(url_for('home'))
    return render_template('import.html')


if __name__ == '__main__':
    app.run(debug=True)

