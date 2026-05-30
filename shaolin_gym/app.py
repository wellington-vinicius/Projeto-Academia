from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "shaolin_gym_secret"


def conectar():
    return sqlite3.connect("database.db")


def criar_banco():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS aulas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descricao TEXT NOT NULL,
            categoria TEXT NOT NULL,
            nivel TEXT NOT NULL,
            duracao TEXT NOT NULL,
            dia TEXT NOT NULL,
            horario TEXT NOT NULL
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO usuarios (nome, email, senha)
            VALUES ('João', 'joao@email.com', '123')
        """)

    cursor.execute("SELECT COUNT(*) FROM aulas")
    if cursor.fetchone()[0] == 0:
        aulas = [
            ("Kung Fu Básico", "Aprenda os fundamentos do Kung Fu Shaolin.", "Kung Fu", "Iniciante", "45 min", "Hoje", "19:00 - 19:45"),
            ("Formas Shaolin", "Estudo das formas tradicionais para disciplina e técnica.", "Kung Fu", "Intermediário", "60 min", "Amanhã", "18:00 - 19:00"),
            ("Meditação e Qi Gong", "Práticas para equilíbrio mental e controle da respiração.", "Meditação", "Todos os níveis", "30 min", "Sexta-feira", "07:00 - 07:30"),
            ("Armas Tradicionais", "Treinamento com bastão, espada e outras armas.", "Avançado", "Intermediário", "60 min", "Sábado", "10:00 - 11:00")
        ]

        cursor.executemany("""
            INSERT INTO aulas 
            (titulo, descricao, categoria, nivel, duracao, dia, horario)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, aulas)

    conn.commit()
    conn.close()


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE email = ? AND senha = ?", (email, senha))
        usuario = cursor.fetchone()
        conn.close()

        if usuario:
            session["usuario_id"] = usuario[0]
            session["usuario_nome"] = usuario[1]
            return redirect(url_for("aulas"))

        return render_template("login.html", erro="E-mail ou senha inválidos.")

    return render_template("login.html")


@app.route("/aulas")
def aulas():
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    busca = request.args.get("busca", "")

    conn = conectar()
    cursor = conn.cursor()

    if busca:
        cursor.execute("""
            SELECT * FROM aulas 
            WHERE titulo LIKE ? OR categoria LIKE ? OR nivel LIKE ?
        """, (f"%{busca}%", f"%{busca}%", f"%{busca}%"))
    else:
        cursor.execute("SELECT * FROM aulas")

    aulas = cursor.fetchall()
    conn.close()

    return render_template("aulas.html", aulas=aulas)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    criar_banco()
    app.run(debug=True)