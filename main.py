import io
from statistics import quantiles

import pandas as pd
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Float, Date, ForeignKey
from forms import ArticleForm
import csv
from io import TextIOWrapper
from datetime import datetime, timedelta, date
import random
import matplotlib.pyplot as plt
import base64


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
    __tablename__ = "articles"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(250), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)

    sales: Mapped[list["Sale"]] = relationship("Sale", back_populates="article")

#Sales model
class Sale(db.Model):
    __tablename__ = "sales"
    id: Mapped[int] = mapped_column(primary_key=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id"))
    date: Mapped[date] = mapped_column(Date)
    quantity: Mapped[int] = mapped_column()

    article: Mapped["Article"] = relationship("Article", back_populates="sales")

#Create Tables
with app.app_context():
    db.create_all()

def generate_sales(article: Article, days_back=1825):
    today = datetime.today().date()
    start_date = today - timedelta(days=days_back)

    current = start_date
    while current <= today:
        if random.random() < 0.2: # 20% chance de venta
            quantity = random.randint(1, 5)
            sale = Sale(article_id=article.id, date=current, quantity=quantity)
            db.session.add(sale)
        current += timedelta(days=1)
    db.session.commit()

def generate_sales_plot(sales_df):
    df = pd.DataFrame(sales_df)
    fig, ax = plt.subplots(figsize=(15, 4))
    ax.plot(df['period'], df['quantity'], marker='o')
    ax.set_title('Sales per month')
    ax.set_xlabel('Period')
    ax.set_ylabel('Qty sold')
    plt.xticks(rotation=45)

    buf = io.BytesIO()
    plt.tight_layout()
    fig.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')
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

    # Procesar ventas
    sales_data = {sale.date.strftime('%Y-%m'): 0 for sale in material.sales}
    for sale in material.sales:
        key = sale.date.strftime('%Y-%m')
        sales_data[key] += sale.quantity

    df = pd.DataFrame(list(sales_data.items()), columns=['period', 'quantity'])
    df.sort_values('period', inplace=True)

    chart = generate_sales_plot(df.to_dict(orient='records'))
    return render_template('parts.html', article=material, chart=chart)




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

@app.route('/seed_sales')
def seed_sales():
    articles = db.session.execute(db.select(Article)).scalars().all()
    for article in articles:
        generate_sales(article)
    flash('Ventas ficticias generadas con éxito', 'success')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)

